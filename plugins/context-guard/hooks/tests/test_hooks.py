"""End-to-end hook tests: each hook is run as a subprocess with JSON on stdin
and CLAUDE_CONFIG_DIR pointed at a temp dir, the way Claude Code runs it."""
import importlib, io, json, os, subprocess, sys, tempfile, time, unittest
from unittest import mock

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)


# Operator settings, canonical and deprecated alias: scrubbed so a stray value
# in the environment running the tests cannot leak into a hook.
OPERATOR_ENV = ("CONTEXT_GUARD_CONTEXT_WINDOW", "CLAUDE_KIT_CONTEXT_WINDOW",
                "CONTEXT_GUARD_LEDGER_EVERY", "CLAUDE_KIT_LEDGER_EVERY")


def run_hook(name, payload, env=None):
    e = {k: v for k, v in os.environ.items() if k not in OPERATOR_ENV}
    if env:
        e.update(env)
    p = subprocess.run([sys.executable, os.path.join(HOOKS, name)],
                       input=json.dumps(payload), capture_output=True,
                       text=True, env=e, timeout=30)
    out = {}
    if p.stdout.strip():
        try:
            out = json.loads(p.stdout)
        except Exception:
            out = {"_raw": p.stdout}
    return p.returncode, out, p.stderr


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = {"CLAUDE_CONFIG_DIR": self.tmp.name}
        scrub = mock.patch.dict(os.environ)
        scrub.start()
        self.addCleanup(scrub.stop)
        for k in OPERATOR_ENV:
            os.environ.pop(k, None)
        os.environ["CLAUDE_CONFIG_DIR"] = self.tmp.name
        global L
        import lib_context as L

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    def set_exact(self, sid, tokens, window):
        st = L.load_state(sid)
        st["exact"] = {"pct": 100.0 * tokens / window, "tokens": tokens,
                       "window": window, "at": time.time()}
        L.save_state(sid, st)

    def warn(self, sid, prompt="do a thing", transcript="/nonexistent"):
        return run_hook("context_warn.py",
                        {"session_id": sid, "prompt": prompt,
                         "transcript_path": transcript}, self.env)

    def transcript(self, tokens):
        p = os.path.join(self.tmp.name, "t.jsonl")
        rec = {"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tokens - 2,
            "cache_creation_input_tokens": 0}}}
        open(p, "w").write(json.dumps(rec) + "\n")
        return p


class TestContextWarn(Base):
    def test_scored_depth_is_dated(self):
        # reset_epoch takes the fresher of this and the exact record
        self.set_exact("s", 100_000, 1_000_000)
        before = time.time()
        self.warn("s")
        st = L.load_state("s")
        self.assertEqual(st["tokens"], 100_000)
        self.assertTrue(before - 1 <= st["tokens_at"] <= time.time() + 1)

    def test_silent_when_shallow(self):
        self.set_exact("s", 100_000, 1_000_000)
        rc, out, _ = self.warn("s")
        self.assertEqual((rc, out), (0, {}))

    def test_band_fires_once_per_epoch_and_latches_downward(self):
        self.set_exact("s", 780_000, 1_000_000)  # 78%, above both bands
        rc, out, _ = self.warn("s")
        self.assertEqual(rc, 0)
        self.assertIn("78%", out.get("systemMessage", ""))
        for _ in range(2):
            rc, out, _ = self.warn("s")
            self.assertEqual(out, {})
        L.reset_epoch("s")
        self.set_exact("s", 780_000, 1_000_000)
        rc, out, _ = self.warn("s")
        self.assertIn("systemMessage", out)  # re-fires in the new epoch

    def test_due_fires_and_refires_every_3_prompts(self):
        self.set_exact("s", 870_000, 1_000_000)  # 130K left < 150K due
        rc, out, _ = self.warn("s")
        self.assertIn("checkpoint is due", out.get("systemMessage", ""))
        hits = 0
        for _ in range(6):
            self.set_exact("s", 870_000, 1_000_000)
            rc, out, _ = self.warn("s")
            hits += 1 if out else 0
        self.assertEqual(hits, 2)  # every third prompt

    def test_due_silenced_by_checkpoint(self):
        self.set_exact("s", 870_000, 1_000_000)
        L.mark_checkpoint("s")
        self.set_exact("s", 870_000, 1_000_000)
        rc, out, _ = self.warn("s")
        self.assertEqual(out, {})

    def test_hard_blocks_and_whitelists(self):
        self.set_exact("s", 950_000, 1_000_000)  # 50K left < 60K hard
        rc, out, err = self.warn("s", "please do more work")
        self.assertEqual(rc, 2)
        self.assertIn("HARD STOP", err)
        self.assertIn("please do more work", err)
        self.set_exact("s", 950_000, 1_000_000)
        rc, out, err = self.warn("s", "/checkpoint land")
        self.assertEqual(rc, 0)
        L.mark_checkpoint("s")
        self.set_exact("s", 950_000, 1_000_000)
        rc, out, err = self.warn("s", "please do more work")
        self.assertEqual(rc, 0)  # checkpoint stands the gate down

    def test_hard_whitelist_accepts_plugin_prefixed_form(self):
        for prompt in ("/checkpoint", "/claude-kit:checkpoint",
                       "/claude-kit:checkpoint land", "/compact keep auth",
                       "/my-plugin:compact", "/clear", "/x:clear"):
            self.set_exact("s", 950_000, 1_000_000)
            rc, out, err = self.warn("s", prompt)
            self.assertEqual(rc, 0, prompt)
        for prompt in ("/checkpointx", "/claude-kit:checkpointx", "/checkpoint-x",
                       "/clear-all", "/claude-kit:checkpoint:x", "/checkpoint/x",
                       "checkpoint", "/clearance", "/kit:other"):
            self.set_exact("s", 950_000, 1_000_000)
            rc, out, err = self.warn("s", prompt)
            self.assertEqual(rc, 2, prompt)
            self.assertIn("/context-guard:checkpoint", err)

    def test_inferred_depth_never_hard_blocks(self):
        # Live-fired 2026-09-16: stale exact {186454 of 1M}; transcript at the
        # same depth; the old hook guessed 200K and blocked with 13,546 left.
        st = L.load_state("s")
        st["exact"] = {"pct": 18.6, "tokens": 186_454, "window": 1_000_000,
                       "at": time.time() - 700}
        L.save_state("s", st)
        rc, out, err = self.warn("s", "a long prompt", self.transcript(186_454))
        self.assertEqual((rc, out, err), (0, {}, ""))
        self.assertEqual(L.load_state("s")["window"], 1_000_000)
        # No record at all, transcript deep enough to be under hard on the
        # guessed 200K window: advisory, not a block.
        rc, out, err = self.warn("t", "a long prompt", self.transcript(170_000))
        self.assertEqual(rc, 0)
        self.assertIn("hookSpecificOutput", out)
        self.assertIn("NOT applied", out["hookSpecificOutput"]["additionalContext"])
        self.assertIn("CONTEXT_GUARD_CONTEXT_WINDOW", out["hookSpecificOutput"]["additionalContext"])
        self.assertIn("CONTEXT_GUARD_CONTEXT_WINDOW", out["systemMessage"])
        self.assertIn("inferred", out["systemMessage"])
        self.assertIn("not blocked", out["systemMessage"])
        # DUE cadence: silent on the next two prompts, fires on the third.
        for _ in range(2):
            rc, out, err = self.warn("t", "a long prompt", self.transcript(170_000))
            self.assertEqual((rc, out), (0, {}))
        rc, out, err = self.warn("t", "a long prompt", self.transcript(170_000))
        self.assertIn("hookSpecificOutput", out)
        # Stale exact record that is itself under hard: still exit 0.
        st = L.load_state("u")
        st["exact"] = {"pct": 95.0, "tokens": 950_000, "window": 1_000_000,
                       "at": time.time() - 700}
        L.save_state("u", st)
        rc, out, err = self.warn("u", "a long prompt")
        self.assertEqual(rc, 0)
        self.assertIn("inferred", out["hookSpecificOutput"]["additionalContext"])
        # Both messages print the same source label, not a hardcoded one.
        self.assertIn("(inferred, window from status line)",
                      out["hookSpecificOutput"]["additionalContext"])
        self.assertIn("(inferred, window from status line)", out["systemMessage"])
        # Exact still blocks.
        self.set_exact("v", 950_000, 1_000_000)
        self.assertEqual(self.warn("v", "a long prompt")[0], 2)

    def test_stale_exact_after_compaction_does_not_nag(self):
        st = L.load_state("s")
        st["exact"] = {"pct": 95.0, "tokens": 950_000, "window": 1_000_000,
                       "at": time.time() - 700}
        L.save_state("s", st)
        p = os.path.join(self.tmp.name, "c.jsonl")
        rec = lambda tok: json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tok - 2,
            "cache_creation_input_tokens": 0}}})
        open(p, "w").write(rec(950_000) + "\n"
                           + json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n"
                           + rec(30_000) + "\n")
        rc, out, err = self.warn("s", "a long prompt", p)
        self.assertEqual((rc, out), (0, {}))
        st = L.load_state("s")
        self.assertEqual((st["tokens"], st["window"]), (30_000, 1_000_000))

    def boundary_transcript(self, before=950_000, after=30_000):
        p = os.path.join(self.tmp.name, "c.jsonl")
        rec = lambda tok: json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tok - 2,
            "cache_creation_input_tokens": 0}}})
        open(p, "w").write(rec(before) + "\n"
                           + json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n"
                           + rec(after) + "\n")
        return p

    def _fresh_pre_boundary_record(self, sid):
        st = L.load_state(sid)
        st["exact"] = {"pct": 95.0, "tokens": 950_000, "window": 1_000_000,
                       "at": time.time() - 300}   # fresh (< EXACT_MAX_AGE_S)
        L.save_state(sid, st)

    def test_fresh_exact_from_before_compaction_cannot_gate_new_epoch(self):
        # 99cb reviewer: the status line wrote 95% seconds before an auto
        # compaction; the record was still fresh, so the next prompt of a 3%
        # session was HARD-blocked with the old numbers.
        self._fresh_pre_boundary_record("s")
        rc, out, _ = run_hook("postcompact_epoch.py",
                              {"session_id": "s", "hook_event_name": "PostCompact",
                               "trigger": "auto", "compact_summary": "sum"}, self.env)
        self.assertEqual(rc, 0)
        rc, out, err = self.warn("s", "a long prompt", self.boundary_transcript())
        self.assertEqual((rc, out, err), (0, {}, ""))
        st = L.load_state("s")
        self.assertEqual((st["tokens"], st["window"]), (30_000, 1_000_000))
        # Still exact-free until the status line re-renders: no stop, no
        # advisory on the following prompts either.
        for _ in range(3):
            rc, out, err = self.warn("s", "a long prompt", self.boundary_transcript())
            self.assertEqual((rc, out), (0, {}))

    def test_fresh_exact_from_before_clear_cannot_gate_new_epoch(self):
        self._fresh_pre_boundary_record("s")
        rc, out, _ = run_hook("postcompact_epoch.py",
                              {"session_id": "s", "hook_event_name": "SessionStart",
                               "source": "clear"}, self.env)
        self.assertEqual(rc, 0)
        rc, out, err = self.warn("s", "a long prompt", self.boundary_transcript())
        self.assertEqual((rc, out, err), (0, {}, ""))
        self.assertEqual(L.load_state("s")["window"], 1_000_000)
        # /clear's transcript carries no compact_boundary line at all: the
        # demoted record still must not floor the count.
        rc, out, err = self.warn("s", "a long prompt", self.transcript(30_000))
        self.assertEqual((rc, out), (0, {}))
        st = L.load_state("s")
        self.assertEqual((st["tokens"], st["window"]), (30_000, 1_000_000))

    def test_exact_written_after_boundary_is_still_exact(self):
        self._fresh_pre_boundary_record("s")
        run_hook("postcompact_epoch.py",
                 {"session_id": "s", "hook_event_name": "PostCompact",
                  "trigger": "auto"}, self.env)
        self.set_exact("s", 950_000, 1_000_000)   # status line re-rendered, deep again
        rc, out, err = self.warn("s", "a long prompt", self.boundary_transcript())
        self.assertEqual(rc, 2)
        self.assertIn("(exact)", err)

    def test_sessionstart_resume_keeps_fresh_exact(self):
        self._fresh_pre_boundary_record("s")
        run_hook("postcompact_epoch.py",
                 {"session_id": "s", "hook_event_name": "SessionStart",
                  "source": "resume"}, self.env)
        self.assertEqual(L.load_state("s")["exact"]["tokens"], 950_000)


class TestPrecompactGate(Base):
    def gate(self, sid, trigger, ci=None):
        p = {"session_id": sid, "trigger": trigger, "transcript_path": "/nonexistent"}
        if ci is not None:
            p["custom_instructions"] = ci
        return run_hook("precompact_gate.py", p, self.env)

    def test_manual_never_blocked_and_records_instructions(self):
        rc, out, _ = self.gate("s", "manual", ci="keep the auth thread")
        self.assertEqual(rc, 0)
        self.assertEqual(L.load_state("s")["custom_instructions"], "keep the auth thread")

    def test_auto_defers_when_proactive_and_unchecked(self):
        self.set_exact("s", 900_000, 1_000_000)  # < 940K -> proactive
        rc, out, err = self.gate("s", "auto")
        self.assertEqual(rc, 2)
        self.assertTrue(L.load_state("s").get("compact_deferred"))
        self.assertIn("deferred", err)

    def test_auto_allows_after_checkpoint(self):
        L.mark_checkpoint("s")
        self.set_exact("s", 900_000, 1_000_000)
        rc, out, _ = self.gate("s", "auto")
        self.assertEqual(rc, 0)
        self.assertFalse(L.load_state("s").get("compact_deferred"))

    def test_auto_allows_when_not_provably_proactive(self):
        self.set_exact("s", 970_000, 1_000_000)  # >= 940K: could be recovery
        rc, out, _ = self.gate("s", "auto")
        self.assertEqual(rc, 0)

    def test_auto_allows_when_depth_unknown(self):
        rc, out, _ = self.gate("s", "auto")
        self.assertEqual(rc, 0)


class TestPostcompactEpoch(Base):
    def test_postcompact_resets_and_saves_summary(self):
        L.save_state("s", {"epoch": 1, "compact_deferred": True, "tokens": 900_000})
        rc, out, _ = run_hook("postcompact_epoch.py",
                              {"session_id": "s", "hook_event_name": "PostCompact",
                               "trigger": "auto", "compact_summary": "sum"}, self.env)
        st = L.load_state("s")
        self.assertEqual((rc, L.epoch(st)), (0, 2))
        self.assertNotIn("compact_deferred", st)
        self.assertEqual(st["compact_summary"], "sum")

    def test_postcompact_demotes_exact_and_headers_pre_reset_tokens(self):
        L.save_state("s", {"epoch": 1, "tokens": 900_000,
                           "exact": {"pct": 95.0, "tokens": 950_000,
                                     "window": 1_000_000, "at": time.time()}})
        rc, out, _ = run_hook("postcompact_epoch.py",
                              {"session_id": "s", "hook_event_name": "PostCompact",
                               "trigger": "auto"}, self.env)
        self.assertEqual(rc, 0)
        self.assertEqual(L.load_state("s")["exact"], {"window": 1_000_000, "at": 0})
        self.assertIn("## epoch 2", open(L.ledger_path("s")).read())
        # the exact record's fill, captured under the lock before the demote
        self.assertIn("950,000 tok", open(L.ledger_path("s")).read())
        self.assertEqual(L.load_state("s")["epoch_end_tokens"], 950_000)

    def test_postcompact_header_tokens_come_from_locked_update(self):
        # tokens written between an unlocked pre-read and the reset would be
        # lost; the header must read the state reset_epoch itself returned
        L.save_state("s", {"epoch": 1})
        real = L.update_state

        def racing(sid, fn):
            L.save_state(sid, {"epoch": 1, "exact": {"tokens": 123_456,
                                                     "window": 200_000, "at": 1}})
            return real(sid, fn)
        with mock.patch.object(L, "update_state", racing), \
                mock.patch("sys.stdin", io.StringIO(json.dumps(
                    {"session_id": "s", "hook_event_name": "PostCompact"}))), \
                mock.patch("sys.stdout", io.StringIO()):
            sys.modules.pop("postcompact_epoch", None)
            importlib.import_module("postcompact_epoch")  # runs main() on import
        sys.modules.pop("postcompact_epoch", None)
        self.assertIn("123,456 tok", open(L.ledger_path("s")).read())

    def test_sessionstart_only_clear_resets(self):
        L.save_state("s", {"epoch": 1})
        run_hook("postcompact_epoch.py",
                 {"session_id": "s", "hook_event_name": "SessionStart",
                  "source": "resume"}, self.env)
        self.assertEqual(L.epoch(L.load_state("s")), 1)
        run_hook("postcompact_epoch.py",
                 {"session_id": "s", "hook_event_name": "SessionStart",
                  "source": "clear"}, self.env)
        self.assertEqual(L.epoch(L.load_state("s")), 2)


class TestStopRelay(Base):
    def relay(self, sid, last="", active=False):
        return run_hook("stop_relay.py",
                        {"session_id": sid, "transcript_path": "/nonexistent",
                         "stop_hook_active": active,
                         "last_assistant_message": last}, self.env)

    def test_relays_deferred_once_per_epoch(self):
        st = L.load_state("s"); st["compact_deferred"] = True; L.save_state("s", st)
        self.set_exact("s", 900_000, 1_000_000)
        rc, out, _ = self.relay("s")
        self.assertIn("checkpoint", json.dumps(out))
        rc, out, _ = self.relay("s")
        self.assertEqual(out, {})  # single fire
        L.reset_epoch("s")
        st = L.load_state("s"); st["compact_deferred"] = True; L.save_state("s", st)
        self.set_exact("s", 900_000, 1_000_000)
        rc, out, _ = self.relay("s")
        self.assertNotEqual(out, {})  # re-arms next epoch

    def test_honours_stop_hook_active(self):
        st = L.load_state("s"); st["compact_deferred"] = True; L.save_state("s", st)
        self.set_exact("s", 900_000, 1_000_000)
        rc, out, _ = self.relay("s", active=True)
        self.assertEqual(out, {})

    def test_ledger_nudge_and_skip_when_lines_present(self):
        self.set_exact("s", 100_000, 1_000_000)
        rc, out, _ = self.relay("s")           # baseline set at 100K
        self.assertEqual(out, {})
        self.set_exact("s", 170_000, 1_000_000)  # +70K growth
        rc, out, _ = self.relay("s", last="- D decided the thing")
        self.assertEqual(out, {})               # lines already present: silent
        self.set_exact("s", 240_000, 1_000_000)
        rc, out, _ = self.relay("s", last="just prose")
        self.assertIn("ledger", json.dumps(out))


    def ledger_every(self, **env):
        """Baseline at 100K, then +20K growth: True when the nudge fires."""
        self.env.update(env)
        self.set_exact("s", 100_000, 1_000_000)
        self.relay("s")
        self.set_exact("s", 120_000, 1_000_000)
        rc, out, _ = self.relay("s", last="just prose")
        return "ledger" in json.dumps(out)

    def test_ledger_every_default(self):
        self.assertFalse(self.ledger_every())       # 20K < 60K

    def test_ledger_every_canonical(self):
        self.assertTrue(self.ledger_every(CONTEXT_GUARD_LEDGER_EVERY="10000"))

    def test_ledger_every_deprecated_alias(self):
        self.assertTrue(self.ledger_every(CLAUDE_KIT_LEDGER_EVERY="10000"))

    def test_ledger_every_canonical_wins(self):
        self.assertFalse(self.ledger_every(CONTEXT_GUARD_LEDGER_EVERY="50000",
                                           CLAUDE_KIT_LEDGER_EVERY="10000"))

    def test_ledger_every_invalid_canonical_falls_to_valid_alias(self):
        # A mistyped new name beside a valid old one: the alias applies, and
        # the hook does not crash.
        self.assertTrue(self.ledger_every(CONTEXT_GUARD_LEDGER_EVERY="10k",
                                          CLAUDE_KIT_LEDGER_EVERY="10000"))

    def test_ledger_every_empty_canonical_falls_to_alias(self):
        self.assertTrue(self.ledger_every(CONTEXT_GUARD_LEDGER_EVERY="",
                                          CLAUDE_KIT_LEDGER_EVERY="10000"))


class TestLedgerPointer(Base):
    def point(self, payload):
        payload.setdefault("session_id", "s")
        return run_hook("ledger_pointer.py", payload, self.env)

    def read_ledger(self):
        try:
            return open(L.ledger_path("s")).read()
        except FileNotFoundError:
            return ""

    def test_commit_pointer(self):
        self.point({"tool_name": "Bash",
                    "tool_input": {"command": "git add x && git commit -m 'm'"},
                    "tool_response": {"stdout": "[main abc1234] m\n 1 file changed"}})
        self.assertIn("- P commit abc1234", self.read_ledger())

    def test_investigation_write_pointer_and_subagent_skip(self):
        self.point({"tool_name": "Write", "agent_id": "sub1",
                    "tool_input": {"file_path": "/r/.claude-sandbox/investigations/x/00_a.md"}})
        self.assertEqual(self.read_ledger(), "")
        self.point({"tool_name": "Write",
                    "tool_input": {"file_path": "/r/.claude-sandbox/investigations/x/00_a.md"}})
        self.assertIn("- P wrote 00_a.md", self.read_ledger())

    def test_quiet_commit_with_log_oneline(self):
        self.point({"tool_name": "Bash",
                    "tool_input": {"command": "git commit -q -m m && git log --oneline -1"},
                    "tool_response": {"stdout": "lint clean: 7 items\ndef4567 fixed: the thing\n"}})
        led = self.read_ledger()
        self.assertIn("- P commit def4567: def4567 fixed: the thing", led)

    def test_plain_bash_ignored(self):
        self.point({"tool_name": "Bash", "tool_input": {"command": "ls -la"},
                    "tool_response": {"stdout": "stuff"}})
        self.assertEqual(self.read_ledger(), "")


class TestStatusline(Base):
    CTX = {"used_percentage": 42.0, "context_window_size": 1_000_000,
           "total_input_tokens": 420_000}

    def line(self, payload):
        payload.setdefault("session_id", "s")
        payload.setdefault("context_window", dict(self.CTX))
        payload.setdefault("model", {"display_name": "Fable"})
        rc, out, err = run_hook("statusline.py", payload, self.env)
        return rc, out.get("_raw", ""), err

    def test_plan_usage_bars_both_windows(self):
        now = time.time()
        rc, line, _ = self.line({"rate_limits": {
            "five_hour": {"used_percentage": 23.5, "resets_at": now + 2 * 3600 + 600},
            "seven_day": {"used_percentage": 91.2, "resets_at": now + 3 * 86400}}})
        self.assertEqual(rc, 0)
        self.assertEqual(line.count("\n"), 1)
        self.assertIn("[Fable]", line)
        self.assertIn("42%  580k left  e0", line)
        self.assertIn("5h \033[32m██░░░░░░░░\033[0m 23% resets 2h10m", line)
        self.assertIn("7d \033[31m█████████░\033[0m 91% resets 3d", line)
        self.assertLess(line.index("580k left"), line.index("5h "))
        self.assertLess(line.index("5h "), line.index("7d "))

    def test_no_bars_without_rate_limits(self):
        rc, line, _ = self.line({})
        self.assertEqual(rc, 0)
        self.assertNotIn("resets", line)
        self.assertIn("42%  580k left  e0", line)
        rc, line, _ = self.line({"rate_limits": {}})
        self.assertEqual((rc, "resets" in line), (0, False))

    def test_window_with_past_reset_is_absent(self):
        now = time.time()
        rc, line, _ = self.line({"rate_limits": {
            "five_hour": {"used_percentage": 99.0, "resets_at": now - 60},
            "seven_day": {"used_percentage": 75.0, "resets_at": now + 86400}}})
        self.assertEqual(rc, 0)
        self.assertNotIn("5h ", line)
        self.assertIn("7d \033[33m███████░░░\033[0m 75% resets 1d", line)

    def test_malformed_rate_limits_do_not_crash(self):
        for bad in ("garbage", 7, ["five_hour"],
                    {"five_hour": "x", "seven_day": {"used_percentage": "no",
                                                     "resets_at": None}},
                    {"five_hour": {"used_percentage": 12.0}}):
            rc, line, err = self.line({"rate_limits": bad})
            self.assertEqual((rc, err), (0, ""), bad)
            self.assertNotIn("resets", line)
            self.assertIn("42%  580k left", line)

    def test_non_finite_and_bool_fields_are_skipped(self):
        now = time.time()
        for bad in ({"used_percentage": 5.0, "resets_at": float("nan")},
                    {"used_percentage": 5.0, "resets_at": float("inf")},
                    {"used_percentage": float("nan"), "resets_at": now + 100},
                    {"used_percentage": float("inf"), "resets_at": now + 100},
                    {"used_percentage": True, "resets_at": now + 100},
                    {"used_percentage": 5.0, "resets_at": True}):
            rc, line, err = self.line({"rate_limits": {
                "five_hour": bad,
                "seven_day": {"used_percentage": 1.0, "resets_at": now + 100}}})
            self.assertEqual((rc, err), (0, ""), bad)
            self.assertNotIn("5h ", line)
            self.assertIn("7d ", line)

    def test_reset_too_far_out_is_dropped(self):
        now = time.time()
        rc, line, err = self.line({"rate_limits": {
            "five_hour": {"used_percentage": 5.0, "resets_at": (now + 7200) * 1000},
            "seven_day": {"used_percentage": 5.0, "resets_at": now + 367 * 86400},
            "spend_limit": {"used_percentage": 5.0, "resets_at": now + 365 * 86400}}})
        self.assertEqual((rc, err), (0, ""))
        self.assertNotIn("5h ", line)
        self.assertNotIn("7d ", line)
        self.assertIn("$ \033[32m░░░░░░░░░░\033[0m 5% resets 365d", line)

    def test_spend_limit_is_third(self):
        now = time.time()
        rc, line, _ = self.line({"rate_limits": {
            "spend_limit": {"used_percentage": 10.0, "resets_at": now + 86400},
            "seven_day": {"used_percentage": 20.0, "resets_at": now + 86400},
            "five_hour": {"used_percentage": 30.0, "resets_at": now + 86400}}})
        self.assertEqual(rc, 0)
        self.assertIn("$ \033[32m█░░░░░░░░░\033[0m 10% resets 1d", line)
        self.assertLess(line.index("5h "), line.index("7d "))
        self.assertLess(line.index("7d "), line.index("$ "))
        self.assertEqual(line.count("resets"), 3)

    def test_clamping_and_threshold_boundaries(self):
        now = time.time()
        for used, want in ((150.0, "\033[31m██████████\033[0m 100%"),
                           (-5.0, "\033[32m░░░░░░░░░░\033[0m 0%"),
                           (69.9, "\033[32m██████░░░░\033[0m 69%"),
                           (70.0, "\033[33m███████░░░\033[0m 70%"),
                           (89.9, "\033[33m████████░░\033[0m 89%"),
                           (90.0, "\033[31m█████████░\033[0m 90%")):
            rc, line, _ = self.line({"rate_limits": {
                "five_hour": {"used_percentage": used, "resets_at": now + 100}}})
            self.assertEqual(rc, 0)
            self.assertIn("5h " + want, line, used)

    def test_countdown_rounds_up_to_the_minute(self):
        now = time.time()
        for ahead, want in ((59, "1m"), (60, "1m"), (90, "2m"),
                            (3600 + 5 * 60, "1h05m"), (3600, "1h"),
                            (86400 + 3600, "1d1h"), (2 * 86400, "2d")):
            rc, line, _ = self.line({"rate_limits": {
                "five_hour": {"used_percentage": 1.0, "resets_at": now + ahead}}})
            self.assertEqual(rc, 0)
            self.assertIn(f"1% resets {want}", line, ahead)

    def test_exact_state_still_written(self):
        rc, _, _ = self.line({"rate_limits": {
            "five_hour": {"used_percentage": 5.0, "resets_at": time.time() + 100}}})
        self.assertEqual(rc, 0)
        ex = L.load_state("s")["exact"]
        self.assertEqual((ex["pct"], ex["tokens"], ex["window"]),
                         (42.0, 420_000, 1_000_000))

    # The statusline is our direct child, so its parent pid is this process:
    # a registry entry at sessions/<our pid>.json is what it finds first. Our
    # own parent is its grandparent, one /proc hop up the ancestor walk.
    def registry(self, body, sid="s", pid=None):
        pid = os.getpid() if pid is None else pid
        d = os.path.join(self.tmp.name, "sessions")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, f"{pid}.json")
        if isinstance(body, str):
            open(p, "w").write(body)
        else:
            entry = {"pid": pid, "sessionId": sid, "name": "beta",
                     "nameSource": "peer"}
            entry.update(body)
            json.dump(entry, open(p, "w"))

    def grandparent(self):
        if not os.path.isdir("/proc") or os.getppid() <= 1:
            self.skipTest("ancestor walk needs /proc and a real parent")
        return os.getppid()

    def line_via_shell(self, payload):
        """Run the hook through `sh -c` so the real chain has depth 2."""
        payload.setdefault("session_id", "s")
        payload.setdefault("context_window", dict(self.CTX))
        payload.setdefault("model", {"display_name": "Fable"})
        e = dict(os.environ); e.update(self.env)
        p = subprocess.run(["sh", "-c", f'"$0" "$1"', sys.executable,
                            os.path.join(HOOKS, "statusline.py")],
                           input=json.dumps(payload), capture_output=True,
                           text=True, env=e, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def test_payload_session_name_shown(self):
        rc, line, err = self.line({"session_name": "alpha"})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (alpha)  ", line)

    def test_registry_name_when_payload_has_none(self):
        self.registry({})
        for payload in ({}, {"session_name": ""}, {"session_name": "   "},
                        {"session_name": None}, {"session_name": 7}):
            rc, line, err = self.line(dict(payload))
            self.assertEqual((rc, err), (0, ""), payload)
            self.assertIn("  (beta)  ", line, payload)

    def test_no_name_segment_without_any_source(self):
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertNotIn("(", line)
        self.assertTrue(line.startswith("[Fable]   "), line)

    def test_malformed_registry_does_not_crash(self):
        for bad in ("{not json", "", "[]", '"beta"', json.dumps({"name": "beta"}),
                    json.dumps({"sessionId": "s", "name": 7}),
                    json.dumps({"sessionId": "s", "name": "  "}),
                    json.dumps({"sessionId": "s"}), "x" * 70000):
            self.registry(bad)
            rc, line, err = self.line({})
            self.assertEqual((rc, err), (0, ""), bad[:40])
            self.assertNotIn("(", line, bad[:40])
            self.assertIn("42%  580k left", line)

    def test_registry_explicit_name_wins_over_payload_title(self):
        # /rename and an agent naming itself land in the registry first; the
        # payload lags (next render) or carries only the AI title.
        for src in ("user", "peer", "hook", "collision"):
            self.registry({"name": "set-by-" + src, "nameSource": src})
            rc, line, err = self.line({"session_name": "AI title"})
            self.assertEqual((rc, err), (0, ""), src)
            self.assertIn(f"  (set-by-{src})  ", line, src)
            self.assertNotIn("AI title", line, src)

    def test_registry_auto_name_is_skipped_for_payload_title(self):
        self.registry({"name": "hooks-3f", "nameSource": "auto"})
        rc, line, err = self.line({"session_name": "AI title"})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (AI title)  ", line)
        self.assertNotIn("hooks-3f", line)

    def test_registry_entry_for_another_session_is_ignored(self):
        self.registry({}, sid="someone-else")
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertNotIn("(", line)

    def test_derived_and_auto_default_names_are_never_shown(self):
        for src in ("derived", "auto", None, "bogus"):
            self.registry({"name": "hooks-3f", "nameSource": src})
            rc, line, err = self.line({})
            self.assertEqual((rc, err), (0, ""), src)
            self.assertNotIn("(", line, src)

    # -- names are sanitised to one printable line, whatever the source --

    HOSTILE = "ev\x1b[31mil\nsecond\x07 line\x7f\x85end"

    def test_registry_name_with_control_chars_stays_one_line(self):
        self.registry({"name": self.HOSTILE, "nameSource": "user"})
        rc, line, err = self.line({"session_name": "AI title"})
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(line.count("\n"), 1, repr(line))  # only the trailing one
        self.assertIn("  (ev [31mil second line end)  ", line)
        self.assertNotIn("AI title", line)

    def test_payload_name_with_control_chars_stays_one_line(self):
        rc, line, err = self.line({"session_name": self.HOSTILE})
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(line.count("\n"), 1, repr(line))
        self.assertIn("  (ev [31mil second line end)  ", line)

    def test_each_control_char_collapses_to_one_space(self):
        for raw, shown in (("a\x1bb", "a b"), ("a\nb", "a b"), ("a\x07b", "a b"),
                           ("a\x1b[0m\r\n\tb", "a [0m b"), ("a\x7f\x9fb", "a b"),
                           ("  a   b  ", "a b"), ("\x1b\x07\n", "")):
            self.registry({"name": raw, "nameSource": "user"})
            rc, line, err = self.line({})
            self.assertEqual((rc, err), (0, ""), repr(raw))
            if shown:
                self.assertIn(f"  ({shown})  ", line, repr(raw))
            else:
                self.assertNotIn("(", line, repr(raw))
            rc, line, err = self.line({"session_name": raw})
            self.assertEqual((rc, err), (0, ""), repr(raw))
            if shown:
                self.assertIn(f"  ({shown})  ", line, repr(raw))
            else:
                self.assertNotIn("(", line, repr(raw))

    def test_long_names_are_capped_with_an_ellipsis(self):
        long = "n" * 100
        for src in ("registry", "payload"):
            if src == "registry":
                self.registry({"name": long, "nameSource": "user"})
                rc, line, err = self.line({})
            else:
                rc, line, err = self.line({"session_name": long})
            self.assertEqual((rc, err), (0, ""), src)
            self.assertIn("  (" + "n" * 59 + "\u2026)  ", line, src)
            self.assertNotIn("n" * 60, line, src)
        self.registry({"name": "n" * 60, "nameSource": "user"})
        rc, line, _ = self.line({})
        self.assertIn("  (" + "n" * 60 + ")  ", line)  # exactly NAME_MAX is untouched

    # -- the ancestor walk: nearest entry for this session wins --

    def test_registry_match_at_the_grandparent(self):
        self.registry({}, pid=self.grandparent())
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (beta)  ", line)

    def test_walk_continues_past_a_parent_entry_for_another_session(self):
        self.registry({"name": "not-ours", "nameSource": "user"}, sid="someone-else")
        self.registry({}, pid=self.grandparent())
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (beta)  ", line)
        self.assertNotIn("not-ours", line)

    def test_nearest_matching_entry_wins(self):
        self.registry({"name": "near", "nameSource": "user"})
        self.registry({"name": "far", "nameSource": "user"}, pid=self.grandparent())
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (near)  ", line)
        self.assertNotIn("far", line)

    def test_nearer_auto_entry_stops_the_walk_for_the_payload_title(self):
        self.registry({"name": "hooks-3f", "nameSource": "auto"})
        self.registry({"name": "far", "nameSource": "user"}, pid=self.grandparent())
        rc, line, err = self.line({"session_name": "AI title"})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (AI title)  ", line)
        self.assertNotIn("far", line)
        self.assertNotIn("hooks-3f", line)

    def test_walk_reaches_the_session_through_an_intermediate_shell(self):
        # sh -c between us and the hook: our entry is now at its grandparent.
        if not os.path.isdir("/proc"):
            self.skipTest("ancestor walk needs /proc")
        self.registry({})
        rc, line, err = self.line_via_shell({"session_name": "AI title"})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (beta)  ", line)
        self.assertNotIn("AI title", line)


PLAYBOOK = os.path.join(os.path.dirname(HOOKS), "skills", "checkpoint", "references",
                        "operator-playbook.md")


class TestHardAdvice(Base):
    """Under CHECKPOINT_MIN_TOKENS left a checkpoint cannot fit, so the
    advice (never the block) turns to /clear or /compact. At the minimum it
    still fits."""
    MIN = None

    def setUp(self):
        super().setUp()
        self.MIN = L.CHECKPOINT_MIN_TOKENS

    def test_min_is_the_lean_checkpoint_cost_plus_a_margin(self):
        self.assertEqual(self.MIN, L.CHECKPOINT_LEAN_COST + L.CHECKPOINT_MARGIN)
        self.assertEqual(self.MIN, 20_000)
        # Under every window's hard line, so it only ever narrows HARD advice.
        for w in (200_000, 500_000, 1_000_000):
            self.assertLess(self.MIN, L.thresholds(w)["hard"])

    def exact_hard(self, left):
        self.set_exact("s", 1_000_000 - left, 1_000_000)
        return self.warn("s", "please do more work")

    def test_exact_above_and_at_the_minimum_recommends_checkpoint(self):
        for left in (50_000, self.MIN + 1, self.MIN):
            with self.subTest(left=left):
                rc, out, err = self.exact_hard(left)
                self.assertEqual(rc, 2)
                self.assertIn(f"HARD STOP: {left:,} tokens left of 1,000,000 (exact)", err)
                self.assertIn("Run /checkpoint (or /context-guard:checkpoint", err)
                self.assertNotIn("no longer fits", err)
                self.assertIn("please do more work", err)

    def test_exact_below_the_minimum_points_at_clear_then_compact(self):
        for left in (self.MIN - 1, 1_062, 0):  # 1,062: the 2026-09-03 live case
            with self.subTest(left=left):
                rc, out, err = self.exact_hard(left)
                self.assertEqual(rc, 2)  # the block itself is unchanged
                self.assertIn(f"A checkpoint no longer fits in {left:,} tokens", err)
                self.assertNotIn("Run /checkpoint", err)
                self.assertLess(err.index("/clear"), err.index("/compact <"))
                self.assertIn("the guidance steers what the summary keeps", err)
                self.assertIn("then re-send:\n  please do more work", err)

    def test_whitelist_still_passes_below_the_minimum(self):
        for prompt in ("/clear", "/compact keep auth", "/checkpoint"):
            self.set_exact("s", 999_000, 1_000_000)
            self.assertEqual(self.warn("s", prompt)[0], 0, prompt)

    def inferred(self, sid, left, window=200_000):
        # No fresh status-line record: the depth is inferred - against a
        # guessed 200K, or a stale record's window.
        if window != 200_000:
            st = L.load_state(sid)
            st["exact"] = {"pct": 50.0, "tokens": window // 2, "window": window,
                           "at": time.time() - 700}
            L.save_state(sid, st)
        rc, out, err = self.warn(sid, "a long prompt", self.transcript(window - left))
        self.assertEqual((rc, err), (0, ""))
        return (out["hookSpecificOutput"]["additionalContext"], out["systemMessage"])

    def test_inferred_above_and_at_the_minimum_recommends_checkpoint(self):
        for i, left in enumerate((30_000, self.MIN)):
            with self.subTest(left=left):
                ctx, msg = self.inferred(f"a{i}", left)
                self.assertIn("HARD threshold reached by an INFERRED depth", ctx)
                self.assertIn("Run the checkpoint skill now", ctx)
                self.assertIn("Checkpoint now", msg)
                self.assertNotIn("no longer fits", ctx + msg)

    def test_inferred_below_the_minimum_points_at_clear_then_compact(self):
        for i, (left, window) in enumerate(((self.MIN - 1, 200_000),
                                            (1_000, 1_000_000))):
            with self.subTest(left=left):
                ctx, msg = self.inferred(f"b{i}", left, window)
                self.assertIn(f"{left:,} tokens left of {window:,} (inferred", ctx)
                # The phrase librarian-mode's ending-the-session.md keys on.
                self.assertIn("HARD threshold reached by an INFERRED depth", ctx)
                self.assertIn("NOT applied", ctx)
                self.assertIn(f"checkpoint no longer fits in {left:,} tokens", ctx)
                self.assertNotIn("Run the checkpoint skill", ctx)
                # The model cannot run /clear or /compact: the operator does.
                self.assertIn("end the turn and tell the operator to run /clear", ctx)
                self.assertLess(ctx.index("/clear"), ctx.index("/compact <"))
                self.assertIn("CONTEXT_GUARD_CONTEXT_WINDOW", ctx)
                self.assertIn("A checkpoint no longer fits: /clear", msg)
                self.assertNotIn("Checkpoint now", msg)
                self.assertIn("not blocked", msg)
                self.assertIn("CONTEXT_GUARD_CONTEXT_WINDOW", msg)

    def test_fit_left_measures_against_the_would_be_block_window(self):
        import context_warn as CW
        m = {"block_window": 1_000_000, "window": 500_000, "model_window": 1_000_000,
             "acw": {"window": 500_000, "resolved": False}}
        self.assertEqual(CW.fit_left(m, 490_000), 510_000)
        # A depth that may not block: an unresolved lower window never
        # shrinks it (the checkpoint advice wins while in doubt)...
        m.update(block_window=None)
        self.assertEqual(CW.fit_left(m, 490_000), 510_000)
        # ...a resolved one does, as it would bound a hard stop.
        m["acw"]["resolved"] = True
        self.assertEqual(CW.fit_left(m, 490_000), 10_000)
        self.assertEqual(CW.fit_left({"block_window": None, "window": 200_000,
                                      "model_window": 200_000, "acw": {}}, 250_000), 0)


class TestStandDownCommand(Base):
    """The two ways an operator reaches mark_checkpoint.py by hand: the command
    a derived HARD STOP prints, and the playbook's resolver snippet."""

    def test_hatch_names_the_script_beside_the_hook(self):
        import context_warn as CW
        cmd = CW.mark_checkpoint_command("s")
        self.assertEqual(cmd, 'python3 "%s" s' % os.path.join(HOOKS, "mark_checkpoint.py"))
        self.assertIn(cmd, CW.derived_hatches("s"))
        self.assertNotIn("ls -td", CW.derived_hatches("s"))

    def test_hatch_path_is_shell_quoted(self):
        import context_warn as CW
        odd = '/p a/$x/`y`/"q"/b\\s/hooks/context_warn.py'
        with mock.patch.object(CW, "__file__", odd):
            cmd = CW.mark_checkpoint_command("s")
        out = subprocess.run(["sh", "-c", cmd.replace("python3", "printf %s", 1)],
                             capture_output=True, text=True).stdout
        self.assertEqual(out, '/p a/$x/`y`/"q"/b\\s/hooks/mark_checkpoint.pys')

    def snippet(self):
        with open(PLAYBOOK, encoding="utf-8") as f:
            text = f.read()
        block = text.split("```bash\nP=", 1)[1].split("```", 1)[0]
        return "P=" + block.replace("<session_id>", "sid-1")

    def fake_script(self, d, tag):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "mark_checkpoint.py"), "w") as f:
            f.write("import sys; print(%r, sys.argv[1])\n" % tag)

    def run_snippet(self):
        e = dict(os.environ, CLAUDE_CONFIG_DIR=self.tmp.name)
        p = subprocess.run(["bash", "-c", self.snippet()], capture_output=True,
                           text=True, env=e, timeout=30)
        return p.stdout.strip()

    def test_playbook_prefers_the_install_record(self):
        plugins = os.path.join(self.tmp.name, "plugins")
        inst = os.path.join(plugins, "cache", "kmacmcfarlane", "context-guard", "9.9.9")
        self.fake_script(os.path.join(inst, "hooks"), "record")
        # a newer data dir, which the old `ls -td | head -1` pick would take
        self.fake_script(os.path.join(plugins, "data", "context-guard-zzz",
                                      "current-hooks"), "data")
        with open(os.path.join(plugins, "installed_plugins.json"), "w") as f:
            json.dump({"version": 2, "plugins": {"context-guard@kmacmcfarlane": [
                {"scope": "user", "installPath": inst}]}}, f)
        self.assertEqual(self.run_snippet(), "record sid-1")

    def test_playbook_falls_back_to_the_data_dir(self):
        plugins = os.path.join(self.tmp.name, "plugins")
        self.fake_script(os.path.join(plugins, "data", "context-guard-kmacmcfarlane",
                                      "current-hooks"), "data")
        self.assertEqual(self.run_snippet(), "data sid-1")        # no record
        with open(os.path.join(plugins, "installed_plugins.json"), "w") as f:
            f.write("{not json")
        self.assertEqual(self.run_snippet(), "data sid-1")        # unreadable record


if __name__ == "__main__":
    unittest.main()
