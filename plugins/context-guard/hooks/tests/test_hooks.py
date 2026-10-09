"""End-to-end hook tests: each hook is run as a subprocess with JSON on stdin
and CLAUDE_CONFIG_DIR pointed at a temp dir, the way Claude Code runs it."""
import importlib, io, json, os, shlex, subprocess, sys, tempfile, time, unittest
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

    def put_exact(self, sid, block):
        """The status line's exact block for `sid`, as its sensor record."""
        p = L.sensor_path(sid)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump({"v": 1, "exact": block}, f)

    def set_exact(self, sid, tokens, window):
        st = L.load_state(sid)
        # A render of the new epoch: live, it follows the epoch's first
        # response, well past sensor()'s EPOCH_GRACE_S demotion window.
        at = time.time()
        cut = L._finite(st.get("epoch_at"))
        if cut is not None:
            at = max(at, cut + L.EPOCH_GRACE_S + 1)
        self.put_exact(sid, {"pct": 100.0 * tokens / window, "tokens": tokens,
                             "window": window, "at": at})

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
        for prompt in ("/checkpoint", "/context-guard:checkpoint",
                       "/context-guard:checkpoint continue — 2: nothing more 3: ok",
                       "/claude-kit:checkpoint",
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
        self.put_exact("s", {"pct": 18.6, "tokens": 186_454, "window": 1_000_000,
                             "at": time.time() - 700})
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
        self.put_exact("u", {"pct": 95.0, "tokens": 950_000, "window": 1_000_000,
                             "at": time.time() - 700})
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
        self.put_exact("s", {"pct": 95.0, "tokens": 950_000, "window": 1_000_000,
                             "at": time.time() - 700})
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
        self.put_exact(sid, {"pct": 95.0, "tokens": 950_000, "window": 1_000_000,
                             "at": time.time() - 300})   # fresh (< EXACT_MAX_AGE_S)

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
        self.assertEqual(L.sensor("s")["tokens"], 950_000)


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

    def test_auto_allows_after_checkpoint_at_or_under_due(self):
        # 1M: due 150K, hard 60K. 100K left is under due; at exactly due too.
        for tokens in (900_000, 850_000):
            L.save_state("s", {})
            L.mark_checkpoint("s")
            self.set_exact("s", tokens, 1_000_000)
            rc, out, _ = self.gate("s", "auto")
            self.assertEqual(rc, 0, tokens)
            self.assertFalse(L.load_state("s").get("compact_deferred"))

    def test_auto_defers_above_due_even_after_checkpoint(self):
        # 22b2: an idle auto attempt at ~28% fill after a checkpoint went
        # through; above the due line it is deferred, checkpoint or not.
        for checkpointed in (True, False):
            L.save_state("s", {})
            if checkpointed:
                L.mark_checkpoint("s")
            for tokens in (280_000, 849_999):
                self.set_exact("s", tokens, 1_000_000)
                rc, out, err = self.gate("s", "auto")
                self.assertEqual(rc, 2, (checkpointed, tokens))
                self.assertIn("deferred", err)
                self.assertIn("above the due line of 150,000", err)
                self.assertNotIn("Run the checkpoint skill", err)
                # not a deferral a checkpoint would release
                self.assertFalse(L.load_state("s").get("compact_deferred"))

    def test_auto_defers_at_or_under_due_until_checkpoint(self):
        self.set_exact("s", 850_000, 1_000_000)
        rc, out, err = self.gate("s", "auto")
        self.assertEqual(rc, 2)
        self.assertTrue(L.load_state("s").get("compact_deferred"))
        self.assertIn("Run the checkpoint skill", err)
        L.mark_checkpoint("s")
        rc, out, _ = self.gate("s", "auto")
        self.assertEqual(rc, 0)
        self.assertFalse(L.load_state("s").get("compact_deferred"))

    def test_auto_allows_under_hard_checkpoint_or_not(self):
        for checkpointed in (False, True):
            L.save_state("s", {})
            if checkpointed:
                L.mark_checkpoint("s")
            for tokens in (940_000, 970_000):   # 60K left is the hard line
                self.set_exact("s", tokens, 1_000_000)
                rc, out, _ = self.gate("s", "auto")
                self.assertEqual((rc, out), (0, {}), (checkpointed, tokens))
                self.assertFalse(L.load_state("s").get("compact_deferred"))

    def test_manual_untouched_at_any_fill(self):
        for checkpointed in (False, True):
            L.save_state("s", {})
            if checkpointed:
                L.mark_checkpoint("s")
            for tokens in (100_000, 900_000, 990_000):
                self.set_exact("s", tokens, 1_000_000)
                rc, out, err = self.gate("s", "manual")
                self.assertEqual((rc, out, err), (0, {}, ""), (checkpointed, tokens))
                self.assertFalse(L.load_state("s").get("compact_deferred"))

    def test_inferred_depth_past_hard_allows(self):
        # No sensor record: the depth is inferred from the transcript, whose
        # window guess here is 200K (due 70K, hard 40K); 170K is past hard.
        L.mark_checkpoint("s")
        p = {"session_id": "s", "trigger": "auto",
             "transcript_path": self.transcript(170_000)}
        rc, out, _ = run_hook("precompact_gate.py", p,
                              dict(self.env, CONTEXT_GUARD_DERIVE="off"))
        self.assertEqual((rc, out), (0, {}))
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
        L.save_state("s", {"epoch": 1, "tokens": 900_000})
        self.put_exact("s", {"pct": 95.0, "tokens": 950_000,
                             "window": 1_000_000, "at": time.time()})
        rc, out, _ = run_hook("postcompact_epoch.py",
                              {"session_id": "s", "hook_event_name": "PostCompact",
                               "trigger": "auto"}, self.env)
        self.assertEqual(rc, 0)
        self.assertEqual(L.sensor("s"), {"window": 1_000_000, "at": 0})
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
            L.save_state(sid, {"epoch": 1, "tokens": 123_456})
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

    def test_silent_above_due_even_after_a_deferral(self):
        # 22b2: a low-fill deferral used to relay a checkpoint request, whose
        # mark released the next idle auto compaction. Above due: nothing.
        st = L.load_state("s"); st["compact_deferred"] = True; L.save_state("s", st)
        for tokens in (280_000, 849_999):
            self.set_exact("s", tokens, 1_000_000)
            rc, out, _ = self.relay("s")
            self.assertNotIn("checkpoint", json.dumps(out), tokens)
        self.assertNotIn("relay_epoch", L.load_state("s"))

    def test_relays_at_due_once_per_epoch(self):
        self.set_exact("s", 850_000, 1_000_000)   # exactly at due
        rc, out, _ = self.relay("s")
        self.assertIn("150,000 tokens remain", json.dumps(out))
        self.assertNotIn("was deferred", json.dumps(out))
        self.set_exact("s", 860_000, 1_000_000)
        rc, out, _ = self.relay("s")
        self.assertNotIn("checkpoint", json.dumps(out))   # single fire

    def test_relay_names_a_deferral_at_due(self):
        st = L.load_state("s"); st["compact_deferred"] = True; L.save_state("s", st)
        self.set_exact("s", 900_000, 1_000_000)
        rc, out, _ = self.relay("s")
        self.assertIn("was deferred by the context gate", json.dumps(out))

    def test_silent_after_checkpoint(self):
        L.save_state("s", {})
        L.mark_checkpoint("s")
        self.set_exact("s", 900_000, 1_000_000)
        rc, out, _ = self.relay("s")
        self.assertNotIn("checkpoint", json.dumps(out))

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


class TestFutureSkew(Base):
    """73a6: an exact block stamped beyond FUTURE_SKEW_S is not exact for any
    consumer - the prompt gate's HARD block, the PreCompact deferral and the
    Stop relay - while a fresh one still is. (73a6 found it on the in-state
    block the deprecated status-line copy wrote; that copy and that read are
    gone since a95a, and the rule holds for the sensor record.)"""

    def put_skewed(self, sid, tokens, window, ahead):
        self.put_exact(sid, {"pct": 100.0 * tokens / window, "tokens": tokens,
                             "window": window, "at": time.time() + ahead})

    SKEW = 3600

    def test_prompt_gate_does_not_hard_block_on_a_skewed_block(self):
        self.put_skewed("s", 950_000, 1_000_000, self.SKEW)
        rc, out, err = self.warn("s", "please do more work")
        self.assertEqual(rc, 0, err)
        self.assertNotIn("HARD STOP", err)

    def test_prompt_gate_still_hard_blocks_on_a_fresh_block(self):
        self.put_skewed("s", 950_000, 1_000_000, 0)
        rc, out, err = self.warn("s", "please do more work")
        self.assertEqual(rc, 2)
        self.assertIn("HARD STOP", err)

    def test_prompt_gate_small_skew_is_still_exact(self):
        self.put_skewed("s", 950_000, 1_000_000, 30)
        rc, out, err = self.warn("s", "please do more work")
        self.assertEqual(rc, 2)

    def gate(self, sid):
        return run_hook("precompact_gate.py",
                        {"session_id": sid, "trigger": "auto",
                         "transcript_path": "/nonexistent"}, self.env)

    def test_precompact_does_not_defer_on_a_skewed_block(self):
        self.put_skewed("s", 900_000, 1_000_000, self.SKEW)
        rc, out, err = self.gate("s")
        self.assertEqual(rc, 0, err)
        self.assertFalse(L.load_state("s").get("compact_deferred"))

    def test_precompact_still_defers_on_a_fresh_block(self):
        self.put_skewed("s", 900_000, 1_000_000, 0)
        rc, out, err = self.gate("s")
        self.assertEqual(rc, 2)

    def relay(self, sid):
        return run_hook("stop_relay.py",
                        {"session_id": sid, "transcript_path": "/nonexistent",
                         "stop_hook_active": False, "last_assistant_message": ""},
                        self.env)

    def test_stop_relay_ignores_a_skewed_block(self):
        self.put_skewed("s", 900_000, 1_000_000, self.SKEW)
        rc, out, _ = self.relay("s")
        self.assertEqual(out, {})

    def test_stop_relay_still_reads_a_fresh_block(self):
        self.put_skewed("s", 900_000, 1_000_000, 0)
        rc, out, _ = self.relay("s")
        self.assertIn("checkpoint", json.dumps(out))


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
                self.assertIn("Run /context-guard:checkpoint first", err)
                self.assertNotIn("no longer fits", err)
                self.assertIn("please do more work", err)

    def test_exact_below_the_minimum_points_at_clear_then_compact(self):
        for left in (self.MIN - 1, 1_062, 0):  # 1,062: the 2026-09-03 live case
            with self.subTest(left=left):
                rc, out, err = self.exact_hard(left)
                self.assertEqual(rc, 2)  # the block itself is unchanged
                self.assertIn(f"A checkpoint no longer fits in {left:,} tokens", err)
                self.assertNotIn("Run /context-guard:checkpoint", err)
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
            self.put_exact(sid, {"pct": 50.0, "tokens": window // 2, "window": window,
                                 "at": time.time() - 700})
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
        self.assertEqual(cmd, "python3 %s s" % shlex.quote(os.path.join(HOOKS, "mark_checkpoint.py")))
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

    def test_hatch_path_survives_bash_history_expansion(self):
        # ! inside double quotes is history-expanded by an interactive bash
        # (set -H, history on); with a space and a ' as well, the path must
        # still come back whole.
        import context_warn as CW
        odd = "/p a/it's!x/!!/hooks/context_warn.py"
        with mock.patch.object(CW, "__file__", odd):
            cmd = CW.mark_checkpoint_command("s")
        p = subprocess.run(["bash", "-c", "set -H -o history\n" + cmd.replace("python3", "printf %s", 1)],
                           capture_output=True, text=True)
        self.assertEqual((p.returncode, p.stdout), (0, "/p a/it's!x/!!/hooks/mark_checkpoint.pys"))

    def snippet(self):
        with open(PLAYBOOK, encoding="utf-8") as f:
            text = f.read()
        block = text.split("```bash\nP=", 1)[1].split("```", 1)[0]
        return "P=" + block.replace("<session_id>", "sid-1")

    def fake_script(self, d, tag):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "mark_checkpoint.py"), "w") as f:
            f.write("import sys; print(%r, sys.argv[1])\n" % tag)

    def run_snippet(self, cwd=None):
        e = dict(os.environ, CLAUDE_CONFIG_DIR=self.tmp.name)
        p = subprocess.run(["bash", "-c", self.snippet()], capture_output=True,
                           text=True, env=e, timeout=30, cwd=cwd or self.tmp.name)
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

    def test_playbook_picks_the_install_by_scope_not_position(self):
        plugins = os.path.join(self.tmp.name, "plugins")
        proj, other = (os.path.join(self.tmp.name, n) for n in ("proj", "other"))
        os.makedirs(os.path.join(proj, "sub"))
        os.makedirs(other)
        inst = {}
        for tag in ("other", "project", "local", "user"):
            inst[tag] = os.path.join(plugins, "cache", "kmacmcfarlane", "context-guard", tag)
            self.fake_script(os.path.join(inst[tag], "hooks"), tag)
        # a newer data dir, taken only when no record entry applies
        self.fake_script(os.path.join(plugins, "data", "context-guard-zzz",
                                      "current-hooks"), "data")

        def record(*entries):
            with open(os.path.join(plugins, "installed_plugins.json"), "w") as f:
                json.dump({"version": 2, "plugins": {
                    "context-guard@kmacmcfarlane": list(entries)}}, f)

        other_e = {"scope": "project", "projectPath": other, "installPath": inst["other"]}
        proj_e = {"scope": "project", "projectPath": proj, "installPath": inst["project"]}
        local_e = {"scope": "local", "projectPath": proj, "installPath": inst["local"]}
        user_e = {"scope": "user", "installPath": inst["user"]}
        record(other_e, user_e)          # [0] is another project's install
        self.assertEqual(self.run_snippet(proj), "user sid-1")
        self.assertEqual(self.run_snippet(other), "other sid-1")
        record(other_e, user_e, proj_e)  # this project's, also from a subdirectory
        self.assertEqual(self.run_snippet(proj), "project sid-1")
        self.assertEqual(self.run_snippet(os.path.join(proj, "sub")), "project sid-1")
        record(proj_e, local_e, user_e)  # local before project at the same path
        self.assertEqual(self.run_snippet(proj), "local sid-1")
        record(other_e)                  # nothing applies here: the data dir
        self.assertEqual(self.run_snippet(proj), "data sid-1")

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
