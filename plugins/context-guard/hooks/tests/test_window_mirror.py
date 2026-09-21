"""The window mirror wired into the gate: depth precedence (exact > derived >
inferred), the credits latch and its process marker, the status-line cross
-check and its distrust list, the auto-compact window, the bookkeeping hook,
and the account file that must never be opened."""
import builtins, io, json, os, subprocess, sys, tempfile, time, unittest
from datetime import datetime, timezone
from unittest import mock

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)

SCRUB = ("CLAUDE_CODE_", "_CLAUDE_CODE_", "ANTHROPIC_", "DISABLE_", "CONTEXT_GUARD_",
         "CLAUDE_KIT_", "CLAUDE_PROJECT_DIR")
CREDITS = "429 {\"error\":{\"message\":\"Usage credits are required for long context requests\"}}"


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def model_line(mid, t, version="2.1.277"):
    return {"type": "attachment", "timestamp": iso(t), "version": version,
            "attachment": {"type": "model", "identity": {"modelId": mid,
                                                         "marketingName": "x"}}}


def usage_line(tokens, version="2.1.277"):
    return {"type": "assistant", "version": version, "message": {"usage": {
        "input_tokens": 2, "cache_read_input_tokens": tokens - 2,
        "cache_creation_input_tokens": 0}}}


def credits_line(t):
    return {"type": "assistant", "timestamp": iso(t), "version": "2.1.277",
            "isApiErrorMessage": True, "apiError": "long_context_credits_required",
            "error": "rate_limit", "errorDetails": CREDITS,
            "message": {"content": [{"type": "text", "text": "Usage credits required for 1M context"}]}}


def own_key():
    """This process's '<pid>-<starttime>', as proc_info() computes it for a
    hook whose parent is this process."""
    with open(f"/proc/{os.getpid()}/stat") as f:
        return f"{os.getpid()}-{int(f.read().rsplit(')', 1)[1].split()[19])}"


HAVE_PROC = os.path.exists(f"/proc/{os.getpid()}/stat")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = self.tmp.name
        self.proj = os.path.join(self.cfg, "proj")
        os.makedirs(os.path.join(self.proj, ".claude"))
        # Scrub the process environment too, not only the environ handed to
        # measure(): lib code that reads os.environ must not see a host pin
        # or CONTEXT_GUARD_DERIVE. Restored on cleanup.
        scrub = mock.patch.dict(os.environ)
        scrub.start()
        self.addCleanup(scrub.stop)
        for k in [k for k in os.environ if k.startswith(SCRUB)]:
            del os.environ[k]
        os.environ["CLAUDE_CONFIG_DIR"] = self.cfg
        global L, R
        import lib_context as L
        import window_rules as R
        self.patches = [
            mock.patch.object(R, "MANAGED_SETTINGS", (os.path.join(self.cfg, "managed.json"),)),
            mock.patch.object(R, "MANAGED_DROPINS", (os.path.join(self.cfg, "managed.d"),))]
        # The Claude Code process: for a hook subprocess it is this test
        # process (its parent), found through the session registry.
        self.key = own_key() if HAVE_PROC else "1-1"
        os.makedirs(os.path.join(self.cfg, "sessions"))
        with open(os.path.join(self.cfg, "sessions", f"{os.getpid()}.json"), "w") as f:
            f.write("{}")
        self.proc = {"key": self.key, "observable": True}
        self.patches.append(mock.patch.object(L, "proc_info", lambda: dict(self.proc)))
        for p in self.patches:
            p.start()
        self.t0 = time.time() - 3600
        self.tpath = os.path.join(self.cfg, "t.jsonl")

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    def environ(self, **kw):
        e = {k: v for k, v in os.environ.items() if not k.startswith(SCRUB)}
        e["CLAUDE_CONFIG_DIR"] = self.cfg
        e["_TEST_REKEY"] = self.key
        e["CLAUDE_PROJECT_DIR"] = self.proj
        e.update({k: str(v) for k, v in kw.items()})
        return e

    def write(self, *recs, append=False):
        with open(self.tpath, "a" if append else "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        return self.tpath

    def session(self, model, tokens, *extra, key=True):
        """A transcript with one model line and one usage line, plus the
        SessionStart marker of this process at offset 0 (a fresh process)."""
        self.write(model_line(model, self.t0), usage_line(tokens), *extra)
        L.save_state("s", {"proc": {"offset": 0, "key": self.key if key is True else key,
                                    "at": self.t0 + 1, "source": "startup"}})
        return self.tpath

    def settings(self, scope="user", **kv):
        p = os.path.join(self.cfg, "settings.json") if scope == "user" else \
            os.path.join(self.proj, ".claude", "settings.json" if scope == "project"
                         else "settings.local.json")
        with open(p, "w") as f:
            json.dump(kv, f)

    def measure(self, sid="s", **env):
        return L.measure(self.tpath, sid, environ=self.environ(**env))

    def set_exact(self, tokens, window, at=None):
        st = L.load_state("s")
        st["exact"] = {"pct": 100.0 * tokens / window, "tokens": tokens,
                       "window": window, "at": time.time() if at is None else at}
        L.save_state("s", st)


class TestPrecedence(Base):
    def test_derived_resolved_is_a_blocking_source(self):
        self.session("claude-opus-5", 950_000)
        m = self.measure()
        self.assertEqual((m["tokens"], m["window"], m["source"], m["block_window"]),
                         (950_000, 1_000_000, "derived", 1_000_000))
        self.assertIn("derived", L.BLOCKING_SOURCES)
        self.assertEqual(L.depth(self.tpath, "s")[1:], (1_000_000, 95.0, "derived"))

    def test_derived_haiku_scores_against_200k(self):
        self.session("claude-haiku-4-5-20251001", 170_000)
        m = self.measure()
        self.assertEqual((m["window"], m["source"]), (200_000, "derived"))

    def test_fresh_exact_wins_and_is_unchanged(self):
        self.session("claude-opus-5", 950_000)
        self.set_exact(420_000, 1_000_000)
        m = self.measure()
        self.assertEqual((m["tokens"], m["window"], m["pct"], m["source"], m["block_window"]),
                         (420_000, 1_000_000, 42.0, "exact", 1_000_000))

    def test_unresolved_keeps_the_inferred_depth_and_names_the_rule(self):
        self.session("claude-opus-5", 150_000)
        m = self.measure(CLAUDE_CODE_USE_BEDROCK=1)
        self.assertEqual((m["tokens"], m["window"], m["source"], m["block_window"]),
                         (150_000, 200_000, "inferred", None))
        self.assertIn("native_1m_3p", m["note"])
        self.assertIn("1,000,000 unresolved", m["note"])

    def test_no_model_line_is_plain_inferred(self):
        self.write(usage_line(100_000))
        m = self.measure()
        self.assertEqual((m["tokens"], m["window"], m["source"], m["note"]),
                         (100_000, 200_000, "inferred", ""))

    def test_kill_switch(self):
        self.session("claude-opus-5", 950_000)
        m = self.measure(CONTEXT_GUARD_DERIVE="off")
        self.assertEqual((m["source"], m["block_window"], m["derived"]), ("inferred", None, None))

    def test_boundary_resets_derived_tokens(self):
        self.session("claude-opus-5", 950_000, {"type": "system", "subtype": "compact_boundary"},
                     usage_line(30_000))
        m = self.measure()
        self.assertEqual((m["tokens"], m["source"]), (30_000, "derived"))


def generic_429(t):
    """The 429 path that does NOT latch (no apiError), carrying the same words."""
    return {"type": "assistant", "timestamp": iso(t), "version": "2.1.277",
            "isApiErrorMessage": True, "error": "rate_limit",
            "errorDetails": CREDITS,
            "message": {"content": [{"type": "text", "text":
                "API Error: Request rejected (429) · Usage credits are required for long context requests"}]}}


class TestLatch(Base):
    def test_latch_after_process_start_resolves_200k(self):
        self.session("claude-opus-5", 150_000, credits_line(self.t0 + 5))
        d = self.measure()["derived"]
        self.assertEqual((d["window"], d["resolved"], d["rule"]), (200_000, True, "credits_latch"))

    def test_latch_before_process_start_is_ignored(self):
        self.write(model_line("claude-opus-5", self.t0), credits_line(self.t0 + 5))
        size = os.path.getsize(self.tpath)
        self.write(usage_line(150_000), append=True)
        L.save_state("s", {"proc": {"offset": size, "key": self.key, "at": self.t0 + 10}})
        d = self.measure()["derived"]
        self.assertEqual((d["window"], d["resolved"]), (1_000_000, True))

    def test_latch_without_marker_is_unresolved(self):
        self.write(model_line("claude-opus-5", self.t0), usage_line(150_000),
                   credits_line(self.t0 + 5))
        m = self.measure()
        self.assertEqual((m["derived"]["window"], m["derived"]["resolved"]), (200_000, False))
        self.assertTrue(m["source"].startswith("inferred"))

    def test_generic_429_with_the_phrase_is_not_a_latch(self):
        # Reviewer case 17: the !O 429 path says the same words but never latches.
        self.session("claude-opus-5", 185_000, generic_429(self.t0 + 5))
        d = self.measure()["derived"]
        self.assertEqual((d["window"], d["resolved"], d["rule"]), (1_000_000, True, "native_1m"))

    def test_missing_or_stale_process_marker_leaves_the_latch_unknown(self):
        for label, key in (("no key", None), ("other process", "999999-1")):
            with self.subTest(label):
                self.session("claude-opus-5", 950_000, key=key)
                m = self.measure()
                self.assertEqual((m["derived"]["rule"], m["derived"]["resolved"]),
                                 ("latch_unknown", False))
                self.assertTrue(m["source"].startswith("inferred"))
        # The running process itself cannot be identified (no /proc, no registry).
        self.session("claude-opus-5", 950_000)
        self.proc = {"key": None, "observable": False}
        self.assertEqual(self.measure()["derived"]["rule"], "latch_unknown")

    def test_a_stale_marker_never_proves_a_latch(self):
        # Latch lines after an old process's offset: a maybe, not a 200K block.
        self.session("claude-opus-5", 185_000, credits_line(self.t0 + 5), key="999999-1")
        m = self.measure()
        self.assertEqual((m["derived"]["window"], m["derived"]["resolved"]), (200_000, False))
        self.assertTrue(m["source"].startswith("inferred"))

    def test_200k_windows_do_not_depend_on_the_latch(self):
        self.session("claude-haiku-4-5", 170_000, key=None)
        self.assertEqual(self.measure()["source"], "derived")

    def test_latch_carries_across_clear_through_the_process_record(self):
        self.session("claude-opus-5", 150_000, credits_line(self.t0 + 5))
        self.assertEqual(self.measure()["derived"]["rule"], "credits_latch")
        self.assertTrue(L.load_state(L.PROC_PREFIX + self.key).get("latch"))
        # /clear: a new transcript and session in the same process.
        self.write(model_line("claude-opus-5", self.t0 + 20), usage_line(10_000))
        L.save_state("s2", {"proc": {"offset": 0, "key": self.key, "at": self.t0 + 20}})
        d = L.measure(self.tpath, "s2", environ=self.environ())["derived"]
        self.assertEqual((d["window"], d["resolved"], d["rule"]), (200_000, True, "credits_latch"))

    def test_api_error_without_the_structured_field_is_not_a_latch(self):
        other = credits_line(self.t0 + 5)
        other.update(apiError="overloaded", errorDetails="529 overloaded")
        self.session("claude-opus-5", 150_000, other)
        self.assertEqual(self.measure()["derived"]["window"], 1_000_000)

    def sidechain(self, *recs):
        d = os.path.join(os.path.splitext(self.tpath)[0], "subagents")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "agent-a1.jsonl"), "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")

    def test_sidechain_latch_in_this_process(self):
        self.session("claude-opus-5", 185_000)
        self.sidechain(credits_line(time.time() - 5))
        d = self.measure()["derived"]
        self.assertEqual((d["window"], d["resolved"], d["rule"]), (200_000, True, "credits_latch"))

    def test_sidechain_latch_before_this_process_is_ignored(self):
        self.session("claude-opus-5", 185_000)
        self.sidechain(credits_line(self.t0 - 100))
        d = self.measure()["derived"]
        self.assertEqual((d["window"], d["resolved"]), (1_000_000, True))

    def test_sidechain_scan_is_cached_per_file(self):
        self.session("claude-opus-5", 185_000)
        self.sidechain(usage_line(10), usage_line(20))
        m = self.measure()
        c = m["side_cache"]
        ent = c["files"]["agent-a1.jsonl"]
        p = os.path.join(os.path.splitext(self.tpath)[0], "subagents", "agent-a1.jsonl")
        self.assertEqual(ent["off"], os.path.getsize(p))
        L.update_state("s", lambda st: st.__setitem__("sidechains", c))
        # Resumed from the cached offset: bytes before it are not read again
        # (a latch planted there is not seen), bytes after it are.
        size = os.path.getsize(p)
        with open(p, "r+") as f:
            f.write(" " * 5)                     # garbles the already-read part
        with open(p, "a") as f:
            f.write(json.dumps(credits_line(time.time())) + "\n")
        d = self.measure()["derived"]
        self.assertEqual((d["window"], d["rule"]), (200_000, "credits_latch"))
        self.assertGreater(self.measure()["side_cache"]["files"]["agent-a1.jsonl"]["off"], size)
        # Another process (a new SessionStart time) drops the cache.
        self.assertEqual(L._sidechain_latch(self.tpath, time.time() + 5, c)[2]["files"], {})

    def test_sidechain_latch_without_timestamp_is_unknown(self):
        self.session("claude-opus-5", 185_000)
        line = credits_line(time.time())
        del line["timestamp"]
        self.sidechain(line)
        d = self.measure()["derived"]
        self.assertEqual((d["rule"], d["resolved"]), ("latch_unknown", False))


class TestModelSwitch(Base):
    def test_switch_newer_than_the_model_line_is_unresolved(self):
        for to in ("haiku", "claude-haiku-4-5", "claude-opus-5[1m]"):
            with self.subTest(to=to):
                self.session("claude-opus-5", 950_000)
                L.update_state("s", lambda st: st.__setitem__("model_switch", {
                    "to_model": to, "at": self.t0 + 30, "size": os.path.getsize(self.tpath)}))
                m = self.measure()
                self.assertEqual(m["derived"]["rule"], "model_switch_pending")
                self.assertTrue(m["source"].startswith("inferred"))

    def test_switching_back_to_the_model_lines_model_clears_it(self):
        self.session("claude-opus-5", 950_000)
        size = os.path.getsize(self.tpath)
        for to, rule in (("haiku", "model_switch_pending"), ("claude-opus-5", "native_1m")):
            L.update_state("s", lambda st: st.__setitem__("model_switch", {
                "to_model": to, "at": self.t0 + 30, "size": size}))
            self.assertEqual(self.measure()["derived"]["rule"], rule, to)

    def test_a_usage_line_after_the_switch_does_not_clear_it(self):
        self.session("claude-haiku-4-5", 150_000)
        L.update_state("s", lambda st: st.__setitem__("model_switch", {
            "to_model": "opus", "at": self.t0 + 30, "size": os.path.getsize(self.tpath)}))
        self.write(usage_line(160_000), append=True)       # a response in flight
        self.assertEqual(self.measure()["derived"]["rule"], "model_switch_pending")

    def test_a_later_model_line_supersedes_the_switch(self):
        self.session("claude-opus-5", 170_000)
        L.update_state("s", lambda st: st.__setitem__("model_switch", {
            "to_model": "haiku", "at": self.t0 + 30, "size": os.path.getsize(self.tpath)}))
        self.write(model_line("claude-haiku-4-5-20251001", self.t0 + 40), usage_line(171_000),
                   append=True)
        m = self.measure()
        self.assertEqual((m["window"], m["source"]), (200_000, "derived"))


class TestScanCache(Base):
    def test_incremental_scan_equals_a_full_scan(self):
        self.write(model_line("claude-opus-5", self.t0), usage_line(100_000))
        first = L.scan_transcript(self.tpath)
        self.write(usage_line(120_000), {"type": "system", "subtype": "compact_boundary"},
                   usage_line(20_000), credits_line(self.t0 + 9), append=True)
        inc = L.scan_transcript(self.tpath, first["cache"])
        full = L.scan_transcript(self.tpath)
        for k in ("cur", "peak", "boundary", "model_id", "model_off", "latches", "size"):
            self.assertEqual(inc[k], full[k], k)
        self.assertEqual((inc["cur"], inc["peak"]), L.scan_usage(self.tpath)[:2])

    def test_unterminated_last_line_is_read_but_not_cached(self):
        self.write(model_line("claude-opus-5", self.t0))
        with open(self.tpath, "a") as f:
            f.write(json.dumps(usage_line(50_000)))          # no newline yet
        r = L.scan_transcript(self.tpath)
        self.assertEqual(r["cur"], L.scan_usage(self.tpath)[0])
        self.assertEqual(r["cache"]["cur"], 0)
        with open(self.tpath, "a") as f:
            f.write("\n")
        self.assertEqual(L.scan_transcript(self.tpath, r["cache"])["cur"], 50_000)

    def test_a_rewritten_file_is_rescanned(self):
        self.write(usage_line(100_000), usage_line(110_000))
        c = L.scan_transcript(self.tpath)["cache"]
        self.write(usage_line(900_000), usage_line(10_000))   # same length, other bytes
        self.assertEqual(L.scan_transcript(self.tpath, c)["peak"], 900_000)
        c["path"] = "/elsewhere"
        self.assertEqual(L.scan_transcript(self.tpath, c)["peak"], 900_000)


class TestCrossCheck(Base):
    def log(self):
        p = os.path.join(self.cfg, "claude-kit", "context-gate", L.MISMATCH_LOG)
        if not os.path.exists(p):
            return []
        with open(p) as f:
            return [json.loads(x) for x in f]

    def test_mismatch_logs_distrusts_and_demotes(self):
        self.session("claude-haiku-4-5", 170_000)
        self.set_exact(170_000, 1_000_000)     # the status line says 1M
        m = self.measure()
        self.assertEqual((m["source"], m["window"]), ("exact", 1_000_000))   # exact wins
        log = self.log()
        self.assertEqual(len(log), 1)
        self.assertEqual({k: log[0][k] for k in ("cc_version", "rules_version", "model",
                                                  "derived", "exact")},
                         {"cc_version": "2.1.277", "rules_version": R.RULES_CC_VERSION,
                          "model": "claude-haiku-4-5", "derived": 200_000, "exact": 1_000_000})
        self.assertIn("2.1.277", L.distrusted_versions())
        self.assertFalse(L.load_state("s")["window_mismatch"]["notified"])
        # Row 20: with the status line gone, this version's derived depth warns only.
        st = L.load_state("s")
        st.pop("exact")
        L.save_state("s", st)
        m = self.measure()
        self.assertTrue(m["source"].startswith("inferred"))
        self.assertTrue(m["derived"]["distrusted"])
        self.assertIn("distrusted", m["note"])
        self.assertEqual(len(self.log()), 1)            # logged once

    def test_agreement_logs_nothing(self):
        self.session("claude-opus-5", 170_000)
        self.set_exact(170_000, 1_000_000)
        self.measure()
        self.assertEqual(self.log(), [])
        self.assertEqual(L.distrusted_versions(), {})

    def test_model_change_after_the_record_is_not_a_mismatch(self):
        self.session("claude-opus-5", 170_000)
        self.set_exact(170_000, 1_000_000, at=self.t0 + 100)
        self.write(model_line("claude-haiku-4-5", self.t0 + 200), append=True)
        L.measure(self.tpath, "s", environ=self.environ())
        self.assertEqual(self.log(), [])

    def test_record_from_an_earlier_process_is_not_a_mismatch(self):
        self.session("claude-haiku-4-5", 170_000)
        L.update_state("s", lambda st: st["proc"].update(at=time.time()))
        self.set_exact(170_000, 1_000_000, at=time.time() - 30)
        self.measure()
        self.assertEqual(self.log(), [])

    def test_stale_record_that_disagrees_wins(self):
        self.session("claude-haiku-4-5", 170_000)
        self.set_exact(160_000, 1_000_000, at=time.time() - 3000)   # stale, this process
        m = self.measure()
        self.assertEqual((m["window"], m["source"]),
                         (1_000_000, "inferred, window from status line"))
        self.assertEqual(len(self.log()), 1)

    def test_log_is_capped(self):
        p = os.path.join(L._state_dir(), L.MISMATCH_LOG)
        for i in range(L.MISMATCH_KEEP + 5):
            L._append_capped(p, json.dumps({"i": i}), L.MISMATCH_KEEP)
        with open(p) as f:
            rows = [json.loads(x)["i"] for x in f]
        self.assertEqual(len(rows), L.MISMATCH_KEEP)
        self.assertEqual(rows[-1], L.MISMATCH_KEEP + 4)


class TestAutoCompactGate(Base):
    def all_hidden_layers_ruled_out(self):
        """What the rule would do if every hidden layer could be ruled out -
        the reader never reports that in 2.1.277 (remote policy)."""
        return mock.patch.object(R, "REMOTE_POLICY_RULED_OUT", True)

    def test_env_window_is_warn_only_in_this_version(self):
        self.session("claude-opus-5", 460_000)
        self.settings(autoCompactEnabled=True)
        m = self.measure(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000)
        self.assertEqual((m["window"], m["block_window"]), (500_000, 1_000_000))
        self.assertIn("auto-compact window 500,000 (env, unresolved)", m["note"])
        with self.all_hidden_layers_ruled_out():
            self.assertEqual(self.measure(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000)
                             ["block_window"], 500_000)

    def test_legacy_auto_compact_enabled_is_unobservable(self):
        # No observable layer sets autoCompactEnabled: warn at the window, block on the model's.
        self.session("claude-opus-5", 460_000)
        with self.all_hidden_layers_ruled_out():
            m = self.measure(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000)
        self.assertEqual((m["window"], m["block_window"]), (500_000, 1_000_000))
        self.assertIn("unresolved", m["note"])

    def test_a_flag_layer_makes_settings_unresolved(self):
        # Reviewer case 22 with --settings on the Claude Code command line.
        self.session("claude-opus-5", 270_000)
        self.set_exact(270_000, 1_000_000)
        self.settings("project", autoCompactWindow=300000, autoCompactEnabled=True)
        self.assertEqual(self.measure()["block_window"], 1_000_000)
        with self.all_hidden_layers_ruled_out():
            self.assertEqual(self.measure()["block_window"], 300_000)
            self.proc = {"key": self.key, "observable": False}
            m = self.measure()
        self.assertEqual((m["window"], m["block_window"]), (300_000, 1_000_000))

    def test_any_policy_tier_makes_settings_unresolved(self):
        # First-wins between policy tiers is not modelled: presence alone
        # (a managed file, a drop-in, the remote cache, the path env) is enough.
        self.session("claude-opus-5", 270_000)
        self.set_exact(270_000, 1_000_000)
        self.settings("project", autoCompactWindow=300000, autoCompactEnabled=True)
        dropins = os.path.join(self.cfg, "managed.d")
        os.makedirs(dropins)
        with self.all_hidden_layers_ruled_out():
            self.assertEqual(self.measure()["block_window"], 300_000)
            for label, path in (("managed file", os.path.join(self.cfg, "managed.json")),
                                ("drop-in", os.path.join(dropins, "a.json")),
                                ("remote cache", os.path.join(self.cfg, R.REMOTE_SETTINGS))):
                with self.subTest(label):
                    with open(path, "w") as f:
                        json.dump({"autoCompactWindow": 900000}, f)   # first-wins would pick it
                    m = self.measure()
                    self.assertEqual(m["block_window"], 1_000_000)
                    os.unlink(path)
            m = self.measure(CLAUDE_CODE_MANAGED_SETTINGS_PATH="/elsewhere")
            self.assertEqual(m["block_window"], 1_000_000)

    def test_out_of_range_setting_is_ignored(self):
        # Reviewer cases 23/24: 50000 is not a window Claude Code accepts.
        for scope in ("user", "project"):
            with self.subTest(scope=scope):
                self.session("claude-opus-5", 20_000)
                self.settings(scope, autoCompactWindow=50000, autoCompactEnabled=True)
                m = self.measure()
                self.assertEqual((m["window"], m["block_window"]), (1_000_000, 1_000_000))
                os.unlink(os.path.join(self.cfg, "settings.json") if scope == "user" else
                          os.path.join(self.proj, ".claude", "settings.json"))

    def test_unresolved_window_warns_but_blocks_only_on_the_model_window(self):
        self.session("claude-sonnet-5", 460_000)
        m = self.measure(CLAUDE_CODE_ENTRYPOINT="local-agent")
        self.assertEqual((m["window"], m["block_window"]), (500_000, 1_000_000))
        self.assertIn("unresolved", m["note"])

    def test_nothing_configured_leaves_the_gate_alone(self):
        self.session("claude-opus-5", 460_000)
        m = self.measure()
        self.assertEqual((m["window"], m["block_window"], m["note"]), (1_000_000, 1_000_000, ""))

    def test_escape_hatches_cover_an_auto_compact_bound_exact_block(self):
        import context_warn as CW
        m = {"acw": {"window": 300_000, "resolved": True, "source": "settings"},
             "block_window": 300_000}
        self.assertTrue(CW.mirror_bound(m, "exact"))
        self.assertFalse(CW.mirror_bound(dict(m, block_window=1_000_000), "exact"))
        self.assertTrue(CW.mirror_bound({"acw": {}, "block_window": 1_000_000}, "derived"))
        self.assertIn("CONTEXT_GUARD_DERIVE=off", CW.derived_hatches("s"))


@unittest.skipUnless(HAVE_PROC, "needs /proc")
class TestProcInfo(Base):
    """proc_info() itself (the Base patch is lifted): a hook two levels
    under a process, which may or may not be a verified Claude Code."""
    CHILD = ("import sys,json;sys.path.insert(0,sys.argv[1]);import lib_context as L;"
             "print(json.dumps(L.proc_info()))")
    # Register this (claude) process correctly, then run argv[1] as code.
    REGISTER_THEN = (
        "import json,os,sys;start=open(f'/proc/{os.getpid()}/stat').read().rsplit(')',1)[1]"
        ".split()[19];r=os.path.join(os.environ['CLAUDE_CONFIG_DIR'],'sessions');"
        "os.makedirs(r,exist_ok=True);json.dump({'pid':os.getpid(),'procStart':start},"
        "open(os.path.join(r,f'{os.getpid()}.json'),'w'));"
        "os.environ.update(CLAUDE_PID=str(os.getpid()),CLAUDE_CODE_CHILD_SESSION='1');")

    @property
    def CHILD_CMD(self):
        return ("import subprocess,sys;print(subprocess.run([sys.executable,'-c',"
                + repr(self.CHILD) + "," + repr(HOOKS) + "],capture_output=True,text=True).stdout)")

    def run_under(self, *argv, exe=None, entry="good", mid=None):
        """Run proc_info in a grandchild of `exe` (default: the `claude`
        link). `entry` is what `exe` writes into its registry entry: "good"
        (its pid and procStart), "none", "wrong-pid", "wrong-start"; `mid`
        adds a registered NON-claude process between them."""
        exe = exe or claude_link(self.cfg)
        code = r"""
import json, os, subprocess, sys
hooks, entry, mid, child = sys.argv[1:5]
start = open(f"/proc/{os.getpid()}/stat").read().rsplit(")", 1)[1].split()[19]
reg = os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "sessions")
os.makedirs(reg, exist_ok=True)
dom = "linux:" + (open("/etc/machine-id").read().strip() if os.path.exists("/etc/machine-id") else "") + ":" + os.readlink("/proc/self/ns/pid")
rec = {"good": {"pid": os.getpid(), "procStart": start},
       "same-domain": {"pid": os.getpid(), "procStart": start, "pidDomain": dom},
       "other-domain": {"pid": os.getpid(), "procStart": start, "pidDomain": "linux:x:pid:[1]"},
       "wrong-pid": {"pid": os.getpid() + 1, "procStart": start},
       "wrong-start": {"pid": os.getpid(), "procStart": str(int(start) + 7)}}.get(entry)
if rec is not None:
    json.dump(rec, open(os.path.join(reg, f"{os.getpid()}.json"), "w"))
os.environ.update(CLAUDE_PID=str(os.getpid()), CLAUDE_CODE_CHILD_SESSION="1")
inner = [sys.executable, "-c", child, hooks]
if mid == "1":   # a registered shell-like process between: must be walked past
    reg_mid = "import json,os,subprocess,sys;json.dump({'pid':os.getpid()},open(os.path.join(os.environ['CLAUDE_CONFIG_DIR'],'sessions',f'{os.getpid()}.json'),'w'));sys.stdout.write(subprocess.run(sys.argv[1:],capture_output=True,text=True).stdout)"
    inner = ["/usr/bin/env", "python3", "-c", reg_mid] + inner
print(subprocess.run(inner, capture_output=True, text=True).stdout)
"""
        p = subprocess.run([exe, "-c", code, HOOKS, entry, "1" if mid else "0", self.CHILD,
                            *argv], capture_output=True, text=True, env=self.environ(),
                           timeout=30)
        return json.loads(p.stdout.strip().splitlines()[-1])

    def test_flags_make_the_process_unobservable(self):
        clean = self.run_under("--model", "opus")
        self.assertTrue(clean["key"])
        self.assertTrue(clean["observable"])
        for flag in ("--settings", "--setting-sources=user", "--autocompact",
                     "--managed-settings", "--input-format"):
            with self.subTest(flag=flag):
                self.assertFalse(self.run_under(flag, "x")["observable"])

    def test_a_registered_process_that_is_not_claude_is_walked_past(self):
        # Reviewer finding 1: another sandbox's claude registered at the pid
        # of this hook's shell. The shell is registered but not claude.
        got = self.run_under(mid=True)
        self.assertTrue(got["key"])
        self.assertFalse(got["key"].startswith(str(os.getpid())))
        self.assertEqual(self.run_under(exe=sys.executable)["key"], None)

    def test_an_unregistered_first_claude_is_not_skipped(self):
        # A registered claude ABOVE an unregistered one (a nested claude):
        # the walk stops at the first claude and reports unverified.
        # The inner claude runs its child with ITS pid as CLAUDE_PID; a second
        # variant keeps the OUTER pid there (a hook env that is not the
        # inner's): neither may take the outer key.
        code = ("import os,subprocess,sys;link=os.path.join(os.environ['CLAUDE_CONFIG_DIR'],'bin','claude');"
                "own=sys.argv[2]=='own';"
                "inner='import os,subprocess,sys;'+('os.environ[\\'CLAUDE_PID\\']=str(os.getpid());' if own else '')"
                "+'print(subprocess.run([sys.executable,\\'-c\\',sys.argv[1]],capture_output=True,text=True).stdout)';"
                "print(subprocess.run([link,'-c',inner,sys.argv[1]],capture_output=True,text=True).stdout)")
        outer = self.run_under(exe=None, entry="good")
        self.assertTrue(outer["key"])
        for mode in ("own", "outer"):
            with self.subTest(mode=mode):
                p = subprocess.run([claude_link(self.cfg), "-c", self.REGISTER_THEN + code,
                                    self.CHILD_CMD, mode], capture_output=True, text=True,
                                   env=self.environ(), timeout=30)
                got = json.loads([l for l in p.stdout.strip().splitlines() if l][-1])
                self.assertEqual(got, {"key": None, "observable": False})

    def test_pid_domain_must_match(self):
        self.assertEqual(self.run_under(entry="other-domain"), {"key": None, "observable": False})
        self.assertTrue(self.run_under(entry="same-domain")["key"])

    def test_the_registry_entry_must_be_the_process_own(self):
        for entry in ("none", "wrong-pid", "wrong-start"):
            with self.subTest(entry=entry):
                self.assertEqual(self.run_under(entry=entry),
                                 {"key": None, "observable": False})


class TestNeverReadsTheAccountFile(Base):
    def test_no_hook_source_names_it(self):
        for name in os.listdir(HOOKS):
            if name.endswith(".py"):
                with open(os.path.join(HOOKS, name), encoding="utf-8") as f:
                    self.assertNotIn(".claude" + ".json", f.read(), name)

    def test_measure_never_opens_it(self):
        home = os.path.join(self.cfg, "home")
        os.makedirs(home)
        poison = os.path.join(home, ".claude" + ".json")
        with open(poison, "w") as f:
            json.dump({"s1mAccessCache": {"a": {"hasAccess": True}}, "apiKey": "sk-poison"}, f)
        opened = []
        real_open, real_osopen = builtins.open, os.open

        def spy_open(p, *a, **k):
            opened.append(str(p))
            return real_open(p, *a, **k)

        def spy_osopen(p, *a, **k):
            opened.append(str(p))
            return real_osopen(p, *a, **k)
        self.session("claude-opus-5", 950_000, credits_line(self.t0 + 5))
        self.set_exact(900_000, 1_000_000)
        with mock.patch.dict(os.environ, {"HOME": home}), \
                mock.patch("builtins.open", spy_open), mock.patch("os.open", spy_osopen):
            for env in ({}, {"CLAUDE_CONFIG_DIR": home}):
                L.measure(self.tpath, "s", environ=self.environ(HOME=home, **env))
        self.assertTrue(opened)
        self.assertFalse([p for p in opened if os.path.basename(p) == ".claude" + ".json"],
                         opened)


# A stand-in for the Claude Code process: python started through a link
# named `claude` (so /proc shows comm and argv0 `claude`), which registers
# itself in <config>/sessions/<pid>.json with its pid and procStart, adopts
# the test's session marker (a `proc.key` equal to _TEST_REKEY becomes its
# own key, as if its SessionStart had written it), then runs the hook as its
# child with the payload on stdin.
LAUNCHER = r"""
import json, os, subprocess, sys
cfg, hook = sys.argv[1], sys.argv[2]
start = open(f"/proc/{os.getpid()}/stat").read().rsplit(")", 1)[1].split()[19]
os.makedirs(os.path.join(cfg, "sessions"), exist_ok=True)
with open(os.path.join(cfg, "sessions", f"{os.getpid()}.json"), "w") as f:
    json.dump({"pid": os.getpid(), "procStart": start, "sessionId": "s"}, f)
old = os.environ.pop("_TEST_REKEY", None)
if old:
    p = os.path.join(cfg, "claude-kit", "context-gate", "s.json")
    if os.path.exists(p):
        with open(p) as f:
            st = json.load(f)
        if isinstance(st.get("proc"), dict) and st["proc"].get("key") == old:
            st["proc"]["key"] = f"{os.getpid()}-{start}"
            with open(p, "w") as f:
                json.dump(st, f)
cmd = [sys.executable, hook]
# The env Claude Code gives every command hook (RLe()): its own pid, and
# CLAUDE_CODE_CHILD_SESSION=1 always.
env = dict(os.environ, CLAUDE_PID=str(os.getpid()), CLAUDE_CODE_CHILD_SESSION="1")
if "_TEST_PID_OVERRIDE" in env:
    env["CLAUDE_PID"] = env.pop("_TEST_PID_OVERRIDE")
    if not env["CLAUDE_PID"]:
        del env["CLAUDE_PID"]
if os.environ.get("_TEST_NESTED"):
    # A claude started from this one's Bash tool: same binary, NOT registered,
    # and its hooks get ITS pid as CLAUDE_PID.
    env.pop("_TEST_NESTED")
    inner = ("import os,subprocess,sys;"
             "e=dict(os.environ,CLAUDE_PID=str(os.getpid()),CLAUDE_CODE_CHILD_SESSION='1');"
             "r=subprocess.run(sys.argv[1:],input=sys.stdin.read(),capture_output=True,text=True,env=e);"
             "sys.stdout.write(r.stdout);sys.stderr.write(r.stderr);sys.exit(r.returncode)")
    cmd = [os.path.join(cfg, "bin", "claude"), "-c", inner] + cmd
r = subprocess.run(cmd, input=sys.stdin.read(), capture_output=True, text=True, env=env)
sys.stdout.write(r.stdout); sys.stderr.write(r.stderr); sys.exit(r.returncode)
"""


def claude_link(cfg):
    d = os.path.join(cfg, "bin")
    link = os.path.join(d, "claude")
    if not os.path.exists(link):
        os.makedirs(d, exist_ok=True)
        os.symlink(sys.executable, link)
    return link


def run_hook(name, payload, env):
    link = claude_link(env["CLAUDE_CONFIG_DIR"])
    p = subprocess.run([link, "-c", LAUNCHER, env["CLAUDE_CONFIG_DIR"],
                        os.path.join(HOOKS, name)], input=json.dumps(payload),
                       capture_output=True, text=True, env=env, timeout=30)
    out = json.loads(p.stdout) if p.stdout.strip() else {}
    return p.returncode, out, p.stderr


class TestHooks(Base):
    def warn(self, prompt="do a thing", **env):
        return run_hook("context_warn.py", {"session_id": "s", "prompt": prompt,
                                            "transcript_path": self.tpath, "cwd": self.proj},
                        self.environ(**env))

    def start(self, source="startup", sid="s"):
        return run_hook("window_events.py", {"session_id": sid, "hook_event_name": "SessionStart",
                                             "source": source, "transcript_path": self.tpath},
                        self.environ())

    def test_derived_1m_session_is_hard_blocked(self):
        self.session("claude-opus-5", 950_000)
        rc, out, err = self.warn()
        self.assertEqual(rc, 2, (out, err))
        self.assertIn("50,000 tokens left of 1,000,000 (derived)", err)
        self.assertEqual(L.load_state("s")["derived"]["rule"], "native_1m")
        self.assertEqual(L.load_state("s")["derived"]["rules_version"], R.RULES_CC_VERSION)

    def test_whitelisted_prompt_passes(self):
        self.session("claude-opus-5", 950_000)
        self.assertEqual(self.warn("/checkpoint")[0], 0)

    def test_derived_haiku_is_hard_blocked_at_170k(self):
        self.session("claude-haiku-4-5-20251001", 170_000)
        self.assertEqual(self.warn()[0], 2)

    def test_unresolved_only_warns(self):
        self.session("claude-opus-5", 950_000)
        rc, out, err = self.warn(CLAUDE_CODE_USE_BEDROCK=1)
        self.assertEqual(rc, 0, err)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("NOT applied", ctx)
        self.assertIn("native_1m_3p", ctx)

    def test_alias_switch_only_warns(self):
        self.session("claude-opus-5", 950_000)
        rc, _, _ = run_hook("window_events.py", {
            "session_id": "s", "hook_event_name": "PostModelSwitch", "to_model": "opus",
            "transcript_path": self.tpath, "source": "command"}, self.environ())
        self.assertEqual(rc, 0)
        self.assertEqual(L.load_state("s")["model_switch"]["to_model"], "opus")
        rc, out, _ = self.warn()
        self.assertEqual(rc, 0)
        self.assertIn("model_switch_pending", out["hookSpecificOutput"]["additionalContext"])

    def test_session_start_records_the_process_offset(self):
        self.write(model_line("claude-opus-5", self.t0), usage_line(1000))
        size = os.path.getsize(self.tpath)
        for source, want in (("startup", size), ("resume", size), ("clear", 0)):
            with self.subTest(source=source):
                rc, out, _ = self.start(source)
                self.assertEqual((rc, out), (0, {}))
                proc = L.load_state("s")["proc"]
                self.assertEqual((proc["offset"], proc["source"]), (want, source))
        before = L.load_state("s")["proc"]
        self.start("compact")
        self.assertEqual(L.load_state("s")["proc"], before)

    def test_session_start_without_transcript(self):
        run_hook("window_events.py", {"session_id": "n", "hook_event_name": "SessionStart",
                                      "source": "startup"}, self.environ())
        self.assertEqual(L.load_state("n")["proc"]["offset"], 0)

    def test_bookkeeping_hook_survives_garbage(self):
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "window_events.py")],
                           input="not json", capture_output=True, text=True, env=self.environ())
        self.assertEqual((p.returncode, p.stdout.strip()), (0, "{}"))

    def test_auto_compact_env_window_only_warns_in_this_version(self):
        # Even with autoCompactEnabled set: remote policy cannot be ruled out.
        self.session("claude-opus-5", 460_000)
        self.settings(autoCompactEnabled=True)
        rc, out, _ = self.warn(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000)
        self.assertEqual(rc, 0)
        self.assertIn("auto-compact window 500,000 (env, unresolved)",
                      out["hookSpecificOutput"]["additionalContext"])

    def test_auto_compact_env_window_without_known_enabled_only_warns(self):
        self.session("claude-opus-5", 460_000)
        rc, out, _ = self.warn(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000)
        self.assertEqual(rc, 0)
        self.assertIn("auto-compact window 500,000 (env, unresolved)",
                      out["hookSpecificOutput"]["additionalContext"])

    def test_derived_hard_stop_names_the_escape_hatches(self):
        self.session("claude-opus-5", 950_000)
        rc, _, err = self.warn()
        self.assertEqual(rc, 2)
        for s_ in ("CONTEXT_GUARD_DERIVE=off", "mark_checkpoint.py\" s",
                   "operator-playbook.md", "If the gate blocks wrongly"):
            self.assertIn(s_, err)
        self.set_exact(950_000, 1_000_000)          # an exact block keeps main's text
        self.assertNotIn("CONTEXT_GUARD_DERIVE", self.warn()[2])

    def test_pin_beats_derivation(self):
        # Reviewer case 35: the window pin wins, as on main - under the
        # canonical name and under the deprecated alias alike.
        for name in ("CONTEXT_GUARD_CONTEXT_WINDOW", "CLAUDE_KIT_CONTEXT_WINDOW"):
            with self.subTest(name=name):
                self.session("claude-haiku-4-5", 185_000)
                rc, out, _ = self.warn(**{name: 1000000})
                self.assertEqual((rc, out), (0, {}))
                self.assertNotIn("derived", L.load_state("s"))

    def test_malformed_canonical_pin_falls_back_to_a_valid_alias(self):
        # A mistyped new name beside a working old-name pin must not switch
        # the pin off: that would turn derivation back on and could hard-block
        # (a false block). The valid alias pins; the haiku session is not
        # blocked, and derivation never ran.
        for bad in ("big", "1m", " 1000000", "1_000_000"):
            with self.subTest(bad=bad):
                self.session("claude-haiku-4-5", 185_000)
                rc, out, _ = self.warn(CONTEXT_GUARD_CONTEXT_WINDOW=bad,
                                       CLAUDE_KIT_CONTEXT_WINDOW=1000000)
                self.assertEqual((rc, out), (0, {}))
                self.assertNotIn("derived", L.load_state("s"))
                m = self.measure(CONTEXT_GUARD_CONTEXT_WINDOW=bad,
                                 CLAUDE_KIT_CONTEXT_WINDOW=1000000)
                self.assertEqual(m["model_window"], 1_000_000)
                self.assertIsNone(m["derived"])

    def test_pin_follows_the_callers_environ(self):
        # measure() scores the window from the environ it is handed, not
        # os.environ: the pin check and the pinned window read one source.
        self.session("claude-haiku-4-5", 185_000)
        with mock.patch.dict(os.environ, {"CONTEXT_GUARD_CONTEXT_WINDOW": "700000"}):
            m = self.measure(CONTEXT_GUARD_CONTEXT_WINDOW=500000)
        self.assertEqual(m["model_window"], 500_000)

    def test_non_default_port_on_the_anthropic_host_only_warns(self):
        # Reviewer case 31.
        self.session("claude-opus-5", 950_000)
        rc, out, _ = self.warn(ANTHROPIC_BASE_URL="https://api.anthropic.com:8443")
        self.assertEqual(rc, 0)
        self.assertIn("native_1m_3p", out["hookSpecificOutput"]["additionalContext"])

    def test_beta_model_on_vertex_only_warns(self):
        # Reviewer case 34.
        self.session("claude-sonnet-4-5", 185_000)
        rc, out, _ = self.warn(CLAUDE_CODE_USE_VERTEX=1)
        self.assertEqual(rc, 0)
        self.assertIn("beta_unobservable", out["hookSpecificOutput"]["additionalContext"])

    def test_generic_429_never_blocks(self):
        # Reviewer case 17.
        self.session("claude-opus-5", 185_000, generic_429(self.t0 + 5))
        self.assertEqual(self.warn(), (0, {}, ""))

    def test_stale_process_marker_never_blocks_a_1m_session_at_200k(self):
        self.session("claude-opus-5", 185_000, credits_line(self.t0 + 5), key="999999-1")
        rc, out, _ = self.warn()
        self.assertEqual(rc, 0)
        self.assertIn("NOT applied", out["hookSpecificOutput"]["additionalContext"])

    def test_nested_claude_never_shares_the_outer_session_state(self):
        # Reviewer round 3: a claude run from the outer claude's Bash tool is
        # the same binary but unregistered. Its hooks must not take the outer
        # key; a latch in either session must not HARD-block the other.
        self.session("claude-opus-5", 170_000)             # the outer session, marker keyed
        rc, out, err = self.warn()
        self.assertEqual((rc, err), (0, ""))
        # The inner session: SessionStart and a prompt under the nested claude.
        inner = os.path.join(self.cfg, "inner.jsonl")
        with open(inner, "w") as f:
            for r in (model_line("claude-opus-5", time.time()), usage_line(170_000),
                      credits_line(time.time() + 1)):
                f.write(json.dumps(r) + "\n")
        env = self.environ(_TEST_NESTED=1)
        run_hook("window_events.py", {"session_id": "inner", "hook_event_name": "SessionStart",
                                      "source": "startup", "transcript_path": inner},
                 dict(env))
        self.assertIsNone(L.load_state("inner")["proc"]["key"])
        rc, out, err = run_hook("context_warn.py", {"session_id": "inner", "prompt": "x",
                                                    "transcript_path": inner, "cwd": self.proj},
                                dict(env))
        self.assertEqual(rc, 0, err)                        # its own latch: a maybe, warn only
        self.assertEqual(L.load_state("inner")["derived"]["resolved"], False)
        self.assertFalse([f for f in os.listdir(os.path.join(self.cfg, "claude-kit",
                                                             "context-gate"))
                          if f.startswith(L.PROC_PREFIX)])
        # The outer session after the nested run: still 1M, still silent.
        # (each run_hook is a new stand-in process: re-adopt the outer marker)
        L.update_state("s", lambda st: st["proc"].update(key=self.key))
        rc, out, err = self.warn()
        self.assertEqual((rc, out, err), (0, {}, ""))
        self.assertEqual(L.load_state("s")["derived"]["window"], 1_000_000)

    def test_the_real_hook_env_still_verifies(self):
        # Claude Code sets CLAUDE_CODE_CHILD_SESSION=1 in EVERY hook env: it
        # must not unverify (the launcher sets it on every run).
        self.session("claude-opus-5", 950_000)
        rc, _, err = self.warn()
        self.assertEqual(rc, 2, err)
        self.assertIn("(derived)", err)

    def test_claude_pid_absent_or_foreign_is_unverified(self):
        for pid in ("", "1", "abc"):
            with self.subTest(pid=pid):
                self.session("claude-opus-5", 950_000)
                env = self.environ()
                # the stand-in hands the hook this CLAUDE_PID instead of its own
                p = subprocess.run(
                    [claude_link(self.cfg), "-c", LAUNCHER, self.cfg,
                     os.path.join(HOOKS, "context_warn.py")],
                    input=json.dumps({"session_id": "s", "prompt": "x",
                                      "transcript_path": self.tpath, "cwd": self.proj}),
                    capture_output=True, text=True,
                    env=dict(env, _TEST_PID_OVERRIDE=pid), timeout=30)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertIn("latch_unknown", p.stdout)

    def test_malformed_mismatch_record_never_raises(self):
        self.session("claude-opus-5", 100_000)
        L.update_state("s", lambda st: st.__setitem__(
            "window_mismatch", {"cc_version": 5, "derived": "x", "exact": None}))
        rc, out, err = self.warn()
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("derived ?, status line ?", out["systemMessage"])

    def test_precompact_never_defers_on_a_derived_window(self):
        # Derived says 1M (170K is far from full); the pre-mirror inferred
        # window is 200K, where 170K is past the hard line: allow, as main does.
        self.session("claude-opus-5", 170_000)
        self.assertEqual(L.depth(self.tpath, "s")[1:3], (1_000_000, 17.0))
        for env in ({}, {"CONTEXT_GUARD_DERIVE": "off"}):
            rc, out, _ = run_hook("precompact_gate.py", {
                "session_id": "s", "trigger": "auto", "transcript_path": self.tpath},
                self.environ(**env))
            self.assertEqual((rc, out), (0, {}), env)
            self.assertNotIn("compact_deferred", L.load_state("s"))

    def test_unresolved_auto_compact_window_warns_then_model_window_blocks(self):
        self.session("claude-sonnet-5", 470_000)
        rc, out, _ = self.warn(CLAUDE_CODE_ENTRYPOINT="local-agent")
        self.assertEqual(rc, 0)
        self.assertIn("UNRESOLVED", out["hookSpecificOutput"]["additionalContext"])
        self.session("claude-sonnet-5", 950_000)
        rc, _, err = self.warn(CLAUDE_CODE_ENTRYPOINT="local-agent")
        self.assertEqual(rc, 2)
        self.assertIn("50,000 tokens left of 1,000,000", err)

    def test_derived_hard_advice_fits_the_space_left(self):
        n = L.CHECKPOINT_MIN_TOKENS
        for left, fits in ((50_000, True), (n, True), (n - 1, False), (1_000, False)):
            with self.subTest(left=left):
                self.session("claude-opus-5", 1_000_000 - left)
                rc, out, err = self.warn()
                self.assertEqual(rc, 2, (out, err))
                self.assertIn(f"{left:,} tokens left of 1,000,000 (derived)", err)
                self.assertEqual("Run /checkpoint" in err, fits)
                self.assertEqual("checkpoint no longer fits" in err, not fits)
                self.assertIn("CONTEXT_GUARD_DERIVE=off", err)  # hatches kept

    def test_unresolved_auto_compact_window_advice_uses_the_model_window(self):
        # 10K left of the unresolved 480K gate window, 530K of the model's:
        # a checkpoint fits the window a hard stop is measured against.
        self.session("claude-sonnet-5", 470_000)
        rc, out, _ = self.warn(CLAUDE_CODE_ENTRYPOINT="local-agent")
        self.assertEqual(rc, 0)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("UNRESOLVED", ctx)
        self.assertIn("Run the checkpoint skill now", ctx)
        self.assertNotIn("no longer fits", ctx + out["systemMessage"])

    def test_mismatch_notice_once(self):
        self.session("claude-haiku-4-5", 100_000)
        self.set_exact(100_000, 1_000_000)
        rc, out, _ = self.warn()
        self.assertEqual(rc, 0)
        self.assertIn("disagreed with the status line on Claude Code 2.1.277",
                      out.get("systemMessage", ""))
        self.set_exact(100_000, 1_000_000)
        self.assertEqual(self.warn()[1], {})

    def test_kill_switch_restores_inferred(self):
        self.session("claude-opus-5", 950_000)
        rc, out, _ = self.warn(CONTEXT_GUARD_DERIVE="off")
        self.assertEqual(rc, 0)
        self.assertIn("INFERRED", out["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
