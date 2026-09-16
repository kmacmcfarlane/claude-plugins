"""End-to-end hook tests: each hook is run as a subprocess with JSON on stdin
and CLAUDE_CONFIG_DIR pointed at a temp dir, the way Claude Code runs it."""
import json, os, subprocess, sys, tempfile, time, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)


def run_hook(name, payload, env=None):
    e = dict(os.environ)
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
            self.assertIn("/claude-kit:checkpoint", err)

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
        self.assertIn("CLAUDE_KIT_CONTEXT_WINDOW", out["hookSpecificOutput"]["additionalContext"])
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


if __name__ == "__main__":
    unittest.main()
