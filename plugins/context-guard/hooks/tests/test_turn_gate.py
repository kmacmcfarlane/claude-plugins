"""turn_gate.py, the mid-turn PostToolUse depth check: silent unless the depth
could hard-block, the HARD mid-turn marker if and only if
lib_context.hard_applies(block_window, tokens), never a block, and no
transcript read when nothing could be said."""
import contextlib, io, json, os, sys, time, unittest
from unittest import mock

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lib_context as L
from test_hooks import Base as HookBase, run_hook
from test_window_mirror import Base as MirrorBase, model_line, usage_line

MARKER = "[context-guard context gate] HARD, mid-turn"


def ctx(out):
    return (out.get("hookSpecificOutput") or {}).get("additionalContext", "")


class TestTurnGate(HookBase):
    """The hook as Claude Code runs it: a subprocess, an exact depth."""

    def gate(self, sid="s", transcript="/nonexistent", **extra):
        payload = {"session_id": sid, "transcript_path": transcript,
                   "hook_event_name": "PostToolUse", "tool_name": "Bash",
                   "tool_input": {"command": "ls"}}
        payload.update(extra)
        return run_hook("turn_gate.py", payload, self.env)

    def test_bad_input_is_quiet(self):
        for raw in ("not json", "[]", "null"):
            with self.subTest(raw=raw):
                import subprocess
                p = subprocess.run([sys.executable, os.path.join(HOOKS, "turn_gate.py")],
                                   input=raw, capture_output=True, text=True,
                                   env=dict(os.environ, **self.env), timeout=30)
                self.assertEqual((p.returncode, json.loads(p.stdout)), (0, {}))

    def test_silent_when_shallow(self):
        self.set_exact("s", 700_000, 1_000_000)
        self.assertEqual(self.gate()[:2], (0, {}))
        self.assertNotIn("turn_gate", L.load_state("s"))

    def test_due_fires_once_then_every_25k(self):
        self.set_exact("s", 860_000, 1_000_000)  # 140K left < due 150K
        rc, out, _ = self.gate()
        self.assertEqual(rc, 0)
        self.assertIn("DUE: 140,000 tokens left of 1,000,000 (exact), mid-turn", ctx(out))
        self.assertEqual(self.gate()[1], {})     # not on every tool call
        self.set_exact("s", 870_000, 1_000_000)
        self.assertEqual(self.gate()[1], {})     # +10K: still quiet
        self.set_exact("s", 886_000, 1_000_000)
        self.assertIn("DUE:", ctx(self.gate()[1]))  # +26K: re-fires

    def test_due_body(self):
        self.set_exact("s", 860_000, 1_000_000)
        text = ctx(self.gate()[1])
        # The body librarian-mode's ending-the-session.md keys on.
        self.assertRegex(text, r"DUE: [\d,]+ tokens left")
        self.assertIn("natural end", text)
        self.assertNotIn(MARKER, text)
        self.assertNotRegex(text, r"\bnow\b")
        self.assertNotIn("end the turn", text)
        self.assertNotIn("handoff", text)
        self.assertIn("60,000", text)            # names the hard line

    def test_hard_fires_on_crossing_and_once(self):
        self.set_exact("s", 900_000, 1_000_000)
        self.assertIn("DUE:", ctx(self.gate()[1]))
        self.set_exact("s", 945_000, 1_000_000)  # 55K left < hard 60K, only +45K
        text = ctx(self.gate()[1])
        self.assertTrue(text.startswith(
            MARKER + " (exact): 55,000 tokens left of 1,000,000."), text)
        self.assertIn("Start nothing new", text)
        self.assertIn("checkpoint skill now, in mode `handoff`", text)
        self.assertIn("names its own mode", text)
        self.assertNotIn("no longer fits", text)
        self.assertEqual(self.gate()[1], {})

    def test_hard_below_the_minimum_says_a_checkpoint_no_longer_fits(self):
        self.set_exact("s", 950_000, 1_000_000)
        self.assertIn("mode `handoff`", ctx(self.gate()[1]))
        # Crossing under CHECKPOINT_MIN_TOKENS re-fires with the new advice,
        # though the growth is under 25K.
        self.set_exact("s", 1_000_000 - 1_062, 1_000_000)
        text = ctx(self.gate()[1])
        self.assertTrue(text.startswith(MARKER + " (exact): 1,062 tokens left"), text)
        self.assertIn("A checkpoint no longer fits in 1,062 tokens", text)
        self.assertIn("three-line brief", text)
        self.assertNotIn("Run the checkpoint skill", text)
        self.assertLess(text.index("/clear"), text.index("/compact <"))
        self.assertEqual(self.gate()[1], {})

    def test_never_blocks(self):
        for tokens in (860_000, 950_000, 999_999, 1_000_000, 1_200_000):
            with self.subTest(tokens=tokens):
                self.set_exact(f"b{tokens}", tokens, 1_000_000)
                rc, out, err = self.gate(f"b{tokens}")
                self.assertEqual((rc, err), (0, ""))
                self.assertNotIn("decision", out)
                self.assertEqual(set(out.get("hookSpecificOutput", {})) - {
                    "hookEventName", "additionalContext"}, set())

    def test_silenced_by_checkpoint_and_rearms_next_epoch(self):
        self.set_exact("s", 950_000, 1_000_000)
        L.mark_checkpoint("s")
        self.assertEqual(self.gate()[1], {})
        L.reset_epoch("s")
        self.set_exact("s", 950_000, 1_000_000)
        self.assertIn(MARKER, ctx(self.gate()[1]))

    def test_rearms_in_a_new_epoch_at_the_same_depth(self):
        self.set_exact("s", 860_000, 1_000_000)
        self.assertIn("DUE:", ctx(self.gate()[1]))
        L.reset_epoch("s")
        self.set_exact("s", 860_000, 1_000_000)
        self.assertIn("DUE:", ctx(self.gate()[1]))

    def test_does_not_clobber_fresh_exact_or_the_prompt_gate_state(self):
        p = self.transcript(900_000)
        L.save_state("s", {"exact": {"pct": 90.0, "tokens": 900_000,
                                     "window": 1_000_000, "at": time.time()},
                           "due": {"prompt_n": 4, "tok": 1}, "prompt_n": 5})
        self.assertIn("DUE:", ctx(self.gate(transcript=p)[1]))
        st = L.load_state("s")
        self.assertEqual(st["exact"]["tokens"], 900_000)
        self.assertEqual((st["due"], st["prompt_n"]), ({"prompt_n": 4, "tok": 1}, 5))

    def test_skips_subagents_on_agent_id_only(self):
        self.set_exact("s", 950_000, 1_000_000)
        self.assertEqual(self.gate(agent_id="sub1", agent_type="Explore")[1], {})
        self.assertNotIn("turn_gate", L.load_state("s"))
        # The main thread of an --agent session carries agent_type alone: gated.
        self.assertIn(MARKER, ctx(self.gate(agent_type="reviewer")[1]))

    def test_replay_2026_09_16_guessed_200k_on_a_real_1m_session(self):
        # Stale exact {186,454 of 1M}; the transcript at the same depth.
        st = L.load_state("s")
        st["exact"] = {"pct": 18.6, "tokens": 186_454, "window": 1_000_000,
                       "at": time.time() - 700}
        L.save_state("s", st)
        self.assertEqual(self.gate(transcript=self.transcript(186_454))[:3], (0, {}, ""))
        # No record at all: the window is guessed at 200K. 150K is under the
        # guessed due line, and deeper is under its hard line: never a word.
        for tok in (150_000, 170_000, 190_000, 199_000):
            for env in ({}, {"CONTEXT_GUARD_DERIVE": "off"}):
                with self.subTest(tok=tok, env=env):
                    rc, out, err = run_hook("turn_gate.py", {
                        "session_id": f"t{tok}", "transcript_path": self.transcript(tok),
                        "tool_name": "Bash"}, dict(self.env, **env))
                    self.assertEqual((rc, out, err), (0, {}, ""))

    def test_derive_off_still_gates_a_fresh_exact_depth(self):
        self.set_exact("s", 950_000, 1_000_000)
        rc, out, _ = run_hook("turn_gate.py", {"session_id": "s",
                                               "transcript_path": "/nonexistent"},
                              dict(self.env, CONTEXT_GUARD_DERIVE="off"))
        self.assertIn(MARKER + " (exact)", ctx(out))


class TestCheck(HookBase):
    """turn_gate.py --check: the unattended checkpoint acts only on a marker
    the hook itself recorded this epoch - quoted or forged text cannot pass."""

    def check(self, sid="s"):
        import subprocess
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "turn_gate.py"),
                            "--check", sid], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL,  # a hook reading stdin fails fast
                           env=dict(os.environ, **self.env), timeout=30)
        return p.returncode, p.stdout.strip()

    def gate(self, sid="s"):
        return run_hook("turn_gate.py", {"session_id": sid,
                                         "transcript_path": "/nonexistent"}, self.env)

    def test_forged_marker_is_not_armed(self):
        # The marker text arriving any other way (a file, a diff, a tool
        # result) leaves no record: nothing to confirm.
        self.set_exact("s", 700_000, 1_000_000)
        self.assertEqual(self.gate()[1], {})
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertTrue(out.startswith("not armed:"), out)
        self.assertEqual(self.check("never-seen")[0], 1)

    def test_due_is_not_armed(self):
        self.set_exact("s", 860_000, 1_000_000)
        self.assertIn("DUE:", ctx(self.gate()[1]))
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("not HARD", out)

    def test_hard_is_armed_until_a_checkpoint_or_a_new_epoch(self):
        for tokens, tier in ((945_000, "hard"), (999_000, "hard_nofit")):
            with self.subTest(tier=tier):
                sid = f"h{tier}"
                self.set_exact(sid, tokens, 1_000_000)
                self.assertIn(MARKER, ctx(self.gate(sid)[1]))
                self.assertEqual(self.check(sid)[0], 0)
                self.assertTrue(self.check(sid)[1].startswith(f"armed: {tier}"))
        L.mark_checkpoint("hhard")
        self.assertEqual(self.check("hhard"), (1, "not armed: a checkpoint already ran this epoch"))
        L.reset_epoch("hhard_nofit")
        rc, out = self.check("hhard_nofit")
        self.assertEqual(rc, 1)
        self.assertIn("earlier epoch", out)

    def test_usage(self):
        import subprocess
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "turn_gate.py"), "--check"],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           timeout=30)
        self.assertEqual(p.returncode, 2)

    def standdown(self, sid="s"):
        import subprocess
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "turn_gate.py"),
                            "--checkpointing", sid], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL,
                           env=dict(os.environ, **self.env), timeout=30)
        return p.returncode, p.stdout.strip()

    def test_a_marker_mid_checkpoint_neither_restarts_nor_abandons(self):
        # 45K left is HARD, so the gate asks for a checkpoint. The checkpoint
        # itself spends tokens, and 27K in the tier would flip to hard_nofit -
        # whose text tells the session to abandon the very checkpoint it is
        # one step from finishing, in the gate's `handoff` rather than the
        # operator's mode. It must say nothing until the mark.
        self.set_exact("s", 955_000, 1_000_000)
        self.assertIn(MARKER, ctx(self.gate()[1]))
        self.assertTrue(self.check()[1].startswith("armed: hard"), self.check()[1])
        rc, out = self.standdown()
        self.assertEqual(rc, 0)
        self.assertIn("stood down", out)
        for tokens in (970_000, 982_000, 999_000):   # 30K, 18K, 1K left
            with self.subTest(left=1_000_000 - tokens):
                self.set_exact("s", tokens, 1_000_000)
                self.assertEqual(self.gate()[:2], (0, {}))
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("already underway", out)
        # and the record the marker was built on is untouched: the stand-down
        # suppresses, it does not rewrite history.
        self.assertEqual(L.load_state("s")["turn_gate"]["tier"], "hard")

    def test_the_mark_clears_the_stand_down(self):
        self.set_exact("s", 955_000, 1_000_000)
        self.assertIn(MARKER, ctx(self.gate()[1]))
        self.standdown()
        self.assertIn("checkpoint_started", L.load_state("s"))
        L.mark_checkpoint("s")
        self.assertNotIn("checkpoint_started", L.load_state("s"))
        self.assertEqual(self.gate()[:2], (0, {}))   # checkpoint_epoch holds it now
        self.assertEqual(self.check(),
                         (1, "not armed: a checkpoint already ran this epoch"))
        # A new epoch re-arms the gate with nothing left over from either flag.
        L.reset_epoch("s")
        self.set_exact("s", 955_000, 1_000_000)
        self.assertIn(MARKER, ctx(self.gate()[1]))

    def test_checkpointing_usage(self):
        import subprocess
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "turn_gate.py"),
                            "--checkpointing"], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=30)
        self.assertEqual(p.returncode, 2)

    def test_a_refused_stamp_still_disarms_the_gate(self):
        # mark_checkpoint.py stamps only a manifest written recently and owned
        # here; anything else is left alone with a warning. The gate must stand
        # down all the same - it keys on the state record, not on the stamp -
        # or an unattended turn would re-fire the marker after every tool call
        # with no way to ever silence it.
        import subprocess
        self.set_exact("s", 999_000, 1_000_000)
        self.assertIn(MARKER, ctx(self.gate()[1]))
        self.assertEqual(self.check()[0], 0)
        repo = os.path.join(self.tmp.name, "repo")
        os.makedirs(repo)
        stale = os.path.join(repo, "HANDOFF.md")
        with open(stale, "w") as fh:
            fh.write("---\nmode: handoff\nwritten: <stamped>\n"
                     "session: <stamped>\n---\n\n## Doing\nx\n")
        old = time.time() - 6 * 3600          # older than STAMP_WINDOW_S
        os.utime(stale, (old, old))
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "mark_checkpoint.py"), "s"],
                           capture_output=True, text=True, cwd=repo,
                           env=dict(os.environ, **self.env), timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("checkpoint recorded", p.stdout)
        self.assertIn("not stamped", p.stdout + p.stderr)
        self.assertEqual(self.check(), (1, "not armed: a checkpoint already ran this epoch"))
        self.assertEqual(self.gate()[1], {})

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignores modes")
    def test_unwritable_state_is_silent_not_a_marker_on_every_call(self):
        # The record cannot land, so no cadence and nothing for --check to
        # confirm: the hook stays silent rather than repeat the marker.
        self.set_exact("s", 950_000, 1_000_000)
        d = L._state_dir()
        os.chmod(d, 0o555)
        try:
            for _ in range(3):
                rc, out, err = self.gate()
                self.assertEqual((rc, out), (0, {}))
            self.assertEqual(self.check()[0], 1)
        finally:
            os.chmod(d, 0o755)
        self.assertIn(MARKER, ctx(self.gate()[1]))   # writable again: it fires


class InProcess(MirrorBase):
    """turn_gate.main() in this process, with the window mirror's fixtures
    (a verified Claude Code process, model lines, settings)."""

    def setUp(self):
        super().setUp()
        global TG
        import turn_gate as TG

    def gate(self, sid="s", **extra):
        payload = {"session_id": sid, "transcript_path": self.tpath,
                   "cwd": self.proj, "tool_name": "Read"}
        payload.update(extra)
        buf = io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), \
                contextlib.redirect_stdout(buf):
            TG.main()
        return json.loads(buf.getvalue())


class TestGuessedDepthIsSilent(InProcess):
    """No inferred or unresolved depth ever produces the unattended trigger:
    every such depth, from DUE down to 1K left, prints {}."""

    LEFTS = (70_000, 60_000, 40_000, 20_000, 1_000)

    def sweep(self, build, window=200_000, **env):
        for i, left in enumerate(self.LEFTS):
            with self.subTest(left=left, env=env):
                build(window - left)
                with mock.patch.dict(os.environ, {k: str(v) for k, v in env.items()}):
                    out = self.gate(f"g{i}")
                self.assertEqual(out, {})
                self.assertNotIn("turn_gate", L.load_state(f"g{i}"))

    def own(self, sid, tokens, *extra):
        self.write(model_line("claude-opus-5", self.t0), usage_line(tokens), *extra)
        L.save_state(sid, {"proc": {"offset": 0, "key": self.key, "at": self.t0 + 1}})

    def test_inferred_no_model_line(self):
        self.sweep(lambda tok: self.write(usage_line(tok)))

    def test_inferred_window_from_a_stale_record(self):
        def build(tok):
            self.write(usage_line(tok))
            for i in range(len(self.LEFTS)):
                L.save_state(f"g{i}", {"exact": {"window": 1_000_000, "tokens": tok,
                                                 "pct": 1.0, "at": time.time() - 700}})
        self.sweep(build, window=1_000_000)

    def test_derived_unresolved(self):
        # Bedrock: the native-1M rule does not resolve; the depth stays inferred.
        def build(tok):
            for i in range(len(self.LEFTS)):
                self.own(f"g{i}", tok)
        self.sweep(build, CLAUDE_CODE_USE_BEDROCK=1)

    def test_derived_on_a_distrusted_version(self):
        L.save_state(L.RULES_SID, {"distrust": {"2.1.277": {"at": 1}}})
        def build(tok):
            for i in range(len(self.LEFTS)):
                self.own(f"g{i}", tok)
        self.sweep(build, window=200_000)

    def test_derived_with_no_verified_process(self):
        self.proc = {"key": None, "observable": False}
        def build(tok):
            for i in range(len(self.LEFTS)):
                self.own(f"g{i}", tok)
        self.sweep(build)

    def test_derive_off_with_no_exact_record_reads_nothing(self):
        self.write(usage_line(199_000))
        boom = mock.Mock(side_effect=AssertionError("transcript read"))
        with mock.patch.dict(os.environ, {"CONTEXT_GUARD_DERIVE": "off"}), \
                mock.patch.object(L, "measure", boom), \
                mock.patch.object(L, "scan_usage", boom), \
                mock.patch.object(L, "scan_transcript", boom):
            self.assertEqual(self.gate(), {})
            # A stale record is not fresh either.
            self.set_exact(999_000, 1_000_000, at=time.time() - 700)
            self.assertEqual(self.gate(), {})
            # The operator's window pin turns the mirror off the same way.
            os.environ.pop("CONTEXT_GUARD_DERIVE")
            os.environ["CONTEXT_GUARD_CONTEXT_WINDOW"] = "200000"
            self.assertEqual(self.gate(), {})
        boom.assert_not_called()


class TestBlockingSources(InProcess):
    def test_derived_resolved_gates(self):
        self.session("claude-opus-5", 860_000)
        self.assertIn("DUE: 140,000 tokens left of 1,000,000 (derived), mid-turn",
                      ctx(self.gate()))
        self.session("claude-opus-5", 950_000)
        self.assertTrue(ctx(self.gate()).startswith(MARKER + " (derived): 50,000"))

    def test_exact_under_an_unresolved_auto_compact_window(self):
        # Gate window 500K (the env auto-compact window, unresolved), so a
        # hard stop is measured against the model window, 1M.
        os.environ["CLAUDE_CODE_AUTO_COMPACT_WINDOW"] = "500000"
        self.settings(autoCompactEnabled=True)
        self.session("claude-opus-5", 470_000)
        self.set_exact(470_000, 1_000_000)
        m = L.measure(self.tpath, "s", cwd=self.proj)
        self.assertEqual((m["window"], m["block_window"], m["source"]),
                         (500_000, 1_000_000, "exact"))
        # 30K left of the gate window: under its hard line, not the model's.
        text = ctx(self.gate())
        self.assertIn("DUE: 30,000 tokens left of 500,000 (exact), mid-turn", text)
        self.assertNotIn(MARKER, text)
        self.assertIn("60,000 left of 1,000,000", text)
        for tok in (480_000, 499_000, 600_000, 900_000):
            with self.subTest(tok=tok):
                self.set_exact(tok, 1_000_000)
                self.assertNotIn(MARKER, json.dumps(self.gate()))
        # Under the model window's hard line: the marker.
        self.set_exact(945_000, 1_000_000)
        self.assertTrue(ctx(self.gate()).startswith(MARKER + " (exact): 55,000 tokens "
                                                    "left of 1,000,000"))

    def test_marker_if_and_only_if_hard_applies(self):
        for i, (tok, win) in enumerate(((150_000, 200_000), (160_000, 200_000),
                                        (161_000, 200_000), (199_999, 200_000),
                                        (500_000, 600_000), (548_000, 600_000),
                                        (940_000, 1_000_000), (940_001, 1_000_000))):
            with self.subTest(tok=tok, win=win):
                L.save_state(f"p{i}", {"exact": {"pct": 100.0 * tok / win, "tokens": tok,
                                                 "window": win, "at": time.time()}})
                out = json.dumps(self.gate(f"p{i}", transcript_path="/nonexistent"))
                self.assertEqual(MARKER in out, L.hard_applies(win, tok))

    def test_scan_cache_is_saved_and_resumed(self):
        self.session("claude-opus-5", 100_000)
        self.assertEqual(self.gate(), {})
        cache = L.load_state("s").get("scan")
        self.assertTrue(cache)
        self.assertEqual(cache.get("size"), os.path.getsize(self.tpath))
        self.write(usage_line(860_000), append=True)
        seen = []
        real = L.scan_transcript
        def spy(path, c=None):
            seen.append(c)
            return real(path, c)
        with mock.patch.object(L, "scan_transcript", spy):
            self.assertIn("DUE:", ctx(self.gate()))
        self.assertEqual(seen[0], cache)
        self.assertEqual(L.load_state("s")["scan"]["size"], os.path.getsize(self.tpath))
        self.assertEqual(L.load_state("s")["derived"]["window"], 1_000_000)


class TestRegisteredInHooksJson(unittest.TestCase):
    """The hook runs after EVERY tool call, in its own PostToolUse group, and
    it takes nothing away from the groups already there. Pinned because this
    file is where the mid-turn gate and the manifest lineage meet: both add a
    PostToolUse group, so a merge that keeps only one side is silent at
    runtime."""

    def setUp(self):
        self.d = json.loads(open(os.path.join(HOOKS, "hooks.json")).read())["hooks"]
        self.post = self.d["PostToolUse"]

    def cmds(self, matcher):
        return [h["command"] for g in self.post if g["matcher"] == matcher
                for h in g["hooks"]]

    def test_turn_gate_runs_on_every_tool(self):
        self.assertIn('python3 "${CLAUDE_PLUGIN_ROOT}/hooks/turn_gate.py"', self.cmds(""))

    def test_turn_gate_has_a_timeout(self):
        hooks = [h for g in self.post if g["matcher"] == "" for h in g["hooks"]
                 if h["command"].endswith('turn_gate.py"')]
        self.assertEqual([h.get("timeout") for h in hooks], [10])

    def test_the_other_groups_are_untouched(self):
        self.assertIn('python3 "${CLAUDE_PLUGIN_ROOT}/hooks/ledger_pointer.py"',
                      self.cmds("Bash|Write|Edit"))
        self.assertIn('python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lineage.py"',
                      self.cmds("Read"))

    def test_the_gate_never_shares_a_group_with_another_hook(self):
        # An empty matcher matches every tool; lineage.py and ledger_pointer.py
        # must keep their own narrower groups rather than ride along here.
        self.assertEqual(self.cmds(""),
                         ['python3 "${CLAUDE_PLUGIN_ROOT}/hooks/turn_gate.py"'])


class TestCheckpointInFlight(unittest.TestCase):
    """The stand-down record is read defensively: every shape but a live one
    for this epoch leaves the gate speaking."""

    def rec(self, **kw):
        d = {"epoch": 1, "at": time.time()}
        d.update(kw)
        return {"epoch": 1, "checkpoint_started": d}

    def test_a_live_record_stands_the_gate_down(self):
        import turn_gate as TG
        self.assertTrue(TG.checkpoint_in_flight(self.rec()))

    def test_it_lapses_so_an_abandoned_checkpoint_cannot_silence_the_epoch(self):
        import turn_gate as TG
        now = time.time()
        self.assertTrue(TG.checkpoint_in_flight(
            self.rec(at=now - TG.CHECKPOINT_GRACE_S + 1), now=now))
        self.assertFalse(TG.checkpoint_in_flight(
            self.rec(at=now - TG.CHECKPOINT_GRACE_S - 1), now=now))

    def test_another_epoch_does_not_count(self):
        import turn_gate as TG
        self.assertFalse(TG.checkpoint_in_flight(
            {"epoch": 2, "checkpoint_started": {"epoch": 1, "at": time.time()}}))

    def test_a_future_stamp_does_not_count(self):
        import turn_gate as TG
        now = time.time()
        self.assertFalse(TG.checkpoint_in_flight(self.rec(at=now + 3600), now=now))

    def test_malformed_records_do_not_raise(self):
        import turn_gate as TG
        for cs in ("started", [], {}, {"epoch": 1}, {"epoch": 1, "at": None},
                   {"epoch": 1, "at": "soon"}, {"at": time.time()}):
            with self.subTest(cs=cs):
                self.assertFalse(TG.checkpoint_in_flight(
                    {"epoch": 1, "checkpoint_started": cs}))
        self.assertFalse(TG.checkpoint_in_flight({}))


class TestStateReadsFailSafe(unittest.TestCase):
    """The helpers the hook leans on before it reads anything: a malformed
    state must not traceback out of a hook, and the mirror-off early return
    must be right, since it decides whether the transcript is read at all."""

    def test_a_malformed_epoch_answers_not_armed_rather_than_crashing(self):
        # L.epoch raises on it by design (the status line degrades to `ctx --`
        # on that, rather than print a wrong epoch), so the gate catches it:
        # `--check` must answer, not hand its caller a traceback to read.
        import turn_gate as TG
        for bad in ("later", None, {}, []):
            with self.subTest(epoch=bad):
                st = {"epoch": bad,
                      "turn_gate": {"epoch": 1, "tier": "hard", "tok": 1}}
                ok, why = TG.armed(st)
                self.assertFalse(ok)
                self.assertIn("unreadable", why)
                self.assertFalse(TG.checkpoint_in_flight(
                    dict(st, checkpoint_started={"epoch": bad, "at": time.time()})))

    def test_mirror_off(self):
        self.assertFalse(L.mirror_off({}))
        self.assertTrue(L.mirror_off({"CONTEXT_GUARD_DERIVE": "off"}))
        self.assertFalse(L.mirror_off({"CONTEXT_GUARD_DERIVE": "on"}))
        self.assertTrue(L.mirror_off({"CONTEXT_GUARD_CONTEXT_WINDOW": "200000"}))
        self.assertFalse(L.mirror_off({"CONTEXT_GUARD_CONTEXT_WINDOW": "big"}))

    def test_exact_fresh(self):
        now = time.time()
        self.assertFalse(L.exact_fresh({}))
        self.assertFalse(L.exact_fresh({"at": now}))                  # no window
        self.assertTrue(L.exact_fresh({"window": 1_000_000, "at": now}))
        self.assertFalse(L.exact_fresh({"window": 1_000_000}))        # no timestamp
        self.assertTrue(L.exact_fresh({"window": 1_000_000,
                                       "at": now - L.EXACT_MAX_AGE_S + 5}))
        self.assertFalse(L.exact_fresh({"window": 1_000_000,
                                        "at": now - L.EXACT_MAX_AGE_S - 5}))


class TestHardApplies(unittest.TestCase):
    """The rule factored out of context_warn.decide, unchanged."""

    def test_rule(self):
        self.assertFalse(L.hard_applies(None, 999_000))
        self.assertFalse(L.hard_applies(0, 999_000))
        self.assertTrue(L.hard_applies(1_000_000, 940_000))    # 60K left: at the line
        self.assertFalse(L.hard_applies(1_000_000, 939_999))
        self.assertTrue(L.hard_applies(200_000, 250_000))      # overfull
        self.assertTrue(L.hard_applies(200_000, 160_000))
        self.assertFalse(L.hard_applies(200_000, 159_999))


if __name__ == "__main__":
    unittest.main()
