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


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = self.tmp.name
        self.proj = os.path.join(self.cfg, "proj")
        os.makedirs(os.path.join(self.proj, ".claude"))
        os.environ["CLAUDE_CONFIG_DIR"] = self.cfg
        global L, R
        import lib_context as L
        import window_rules as R
        self.managed = mock.patch.object(R, "MANAGED_SETTINGS",
                                         (os.path.join(self.cfg, "managed.json"),))
        self.managed.start()
        self.t0 = time.time() - 3600
        self.tpath = os.path.join(self.cfg, "t.jsonl")

    def tearDown(self):
        self.managed.stop()
        self.tmp.cleanup()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    def environ(self, **kw):
        e = {k: v for k, v in os.environ.items() if not k.startswith(SCRUB)}
        e["CLAUDE_CONFIG_DIR"] = self.cfg
        e["CLAUDE_PROJECT_DIR"] = self.proj
        e.update({k: str(v) for k, v in kw.items()})
        return e

    def write(self, *recs, append=False):
        with open(self.tpath, "a" if append else "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        return self.tpath

    def session(self, model, tokens, *extra):
        """A transcript with one model line and one usage line, plus the
        SessionStart marker at offset 0 (a fresh process)."""
        self.write(model_line(model, self.t0), usage_line(tokens), *extra)
        L.save_state("s", {"proc": {"offset": 0, "key": None, "at": self.t0 + 1,
                                    "source": "startup"}})
        return self.tpath

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


class TestLatch(Base):
    def test_latch_after_process_start_resolves_200k(self):
        self.session("claude-opus-5", 150_000, credits_line(self.t0 + 5))
        d = self.measure()["derived"]
        self.assertEqual((d["window"], d["resolved"], d["rule"]), (200_000, True, "credits_latch"))

    def test_latch_before_process_start_is_ignored(self):
        self.write(model_line("claude-opus-5", self.t0), credits_line(self.t0 + 5))
        size = os.path.getsize(self.tpath)
        self.write(usage_line(150_000), append=True)
        L.save_state("s", {"proc": {"offset": size, "key": None, "at": self.t0 + 10}})
        d = self.measure()["derived"]
        self.assertEqual((d["window"], d["resolved"]), (1_000_000, True))

    def test_latch_without_marker_is_unresolved(self):
        self.write(model_line("claude-opus-5", self.t0), usage_line(150_000),
                   credits_line(self.t0 + 5))
        m = self.measure()
        self.assertEqual((m["derived"]["window"], m["derived"]["resolved"]), (200_000, False))
        self.assertTrue(m["source"].startswith("inferred"))

    def test_latch_carries_across_clear_through_the_process_record(self):
        key = "4242-99"
        self.session("claude-opus-5", 150_000, credits_line(self.t0 + 5))
        L.update_state("s", lambda st: st["proc"].update(key=key))
        self.assertEqual(self.measure()["derived"]["rule"], "credits_latch")
        self.assertTrue(L.load_state(L.PROC_PREFIX + key).get("latch"))
        # /clear: a new transcript and session in the same process.
        self.write(model_line("claude-opus-5", self.t0 + 20), usage_line(10_000))
        L.save_state("s2", {"proc": {"offset": 0, "key": key, "at": self.t0 + 20}})
        d = L.measure(self.tpath, "s2", environ=self.environ())["derived"]
        self.assertEqual((d["window"], d["resolved"], d["rule"]), (200_000, True, "credits_latch"))

    def test_api_error_without_the_phrase_is_not_a_latch(self):
        other = credits_line(self.t0 + 5)
        other.update(apiError="overloaded", errorDetails="529 overloaded")
        self.session("claude-opus-5", 150_000, other)
        self.assertEqual(self.measure()["derived"]["window"], 1_000_000)


class TestModelSwitch(Base):
    def test_alias_switch_newer_than_the_model_line_is_unresolved(self):
        self.session("claude-opus-5", 950_000)
        L.update_state("s", lambda st: st.__setitem__("model_switch", {
            "to_model": "haiku", "at": self.t0 + 30, "size": os.path.getsize(self.tpath)}))
        m = self.measure()
        self.assertEqual(m["derived"]["rule"], "model_switch_alias")
        self.assertTrue(m["source"].startswith("inferred"))

    def test_full_id_switch_replaces_the_model(self):
        self.session("claude-opus-5", 170_000)
        L.update_state("s", lambda st: st.__setitem__("model_switch", {
            "to_model": "claude-haiku-4-5", "at": self.t0 + 30,
            "size": os.path.getsize(self.tpath)}))
        m = self.measure()
        self.assertEqual((m["window"], m["source"]), (200_000, "derived"))

    def test_a_later_model_line_supersedes_the_switch(self):
        self.session("claude-opus-5", 170_000)
        L.update_state("s", lambda st: st.__setitem__("model_switch", {
            "to_model": "haiku", "at": self.t0 + 30, "size": os.path.getsize(self.tpath)}))
        self.write(model_line("claude-haiku-4-5-20251001", self.t0 + 40), usage_line(171_000),
                   append=True)
        m = self.measure()
        self.assertEqual((m["window"], m["source"]), (200_000, "derived"))


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
    def test_env_window_lowers_the_gate_and_may_block(self):
        self.session("claude-opus-5", 460_000)
        m = self.measure(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000)
        self.assertEqual((m["window"], m["block_window"], m["model_window"]),
                         (500_000, 500_000, 1_000_000))
        self.assertEqual(L.depth(self.tpath, "s")[1], 1_000_000)   # precompact's window
        self.assertIn("auto-compact window 500,000 (env)", m["note"])

    def test_settings_window_applies_to_exact_too(self):
        with open(os.path.join(self.proj, ".claude", "settings.local.json"), "w") as f:
            json.dump({"autoCompactWindow": 400000}, f)
        self.session("claude-opus-5", 100_000)
        self.set_exact(100_000, 1_000_000)
        m = self.measure()
        self.assertEqual((m["source"], m["window"], m["pct"], m["block_window"]),
                         ("exact", 400_000, 25.0, 400_000))

    def test_unresolved_window_warns_but_blocks_only_on_the_model_window(self):
        self.session("claude-sonnet-5", 460_000)
        m = self.measure(CLAUDE_CODE_ENTRYPOINT="local-agent")
        self.assertEqual((m["window"], m["block_window"]), (500_000, 1_000_000))
        self.assertIn("unresolved", m["note"])

    def test_nothing_configured_leaves_the_gate_alone(self):
        self.session("claude-opus-5", 460_000)
        m = self.measure()
        self.assertEqual((m["window"], m["block_window"], m["note"]), (1_000_000, 1_000_000, ""))


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


def run_hook(name, payload, env):
    p = subprocess.run([sys.executable, os.path.join(HOOKS, name)], input=json.dumps(payload),
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
        self.assertIn("model_switch_alias", out["hookSpecificOutput"]["additionalContext"])

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

    def test_auto_compact_env_window_blocks_below_the_model_window(self):
        self.session("claude-opus-5", 460_000)
        rc, _, err = self.warn(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000)
        self.assertEqual(rc, 2)
        self.assertIn("of 500,000 (derived) [auto-compact window 500,000 (env)]", err)
        self.assertEqual(self.warn()[0], 0)       # unset: 540K left of 1M

    def test_unresolved_auto_compact_window_warns_then_model_window_blocks(self):
        self.session("claude-sonnet-5", 470_000)
        rc, out, _ = self.warn(CLAUDE_CODE_ENTRYPOINT="local-agent")
        self.assertEqual(rc, 0)
        self.assertIn("UNRESOLVED", out["hookSpecificOutput"]["additionalContext"])
        self.session("claude-sonnet-5", 950_000)
        rc, _, err = self.warn(CLAUDE_CODE_ENTRYPOINT="local-agent")
        self.assertEqual(rc, 2)
        self.assertIn("50,000 tokens left of 1,000,000", err)

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
