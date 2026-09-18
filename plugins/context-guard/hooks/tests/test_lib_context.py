import json, os, sys, tempfile, time, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["CLAUDE_CONFIG_DIR"] = self.tmp.name
        global L, ledger
        import lib_context as L
        import ledger

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)


class TestThresholds(Base):
    def test_anchors(self):
        self.assertEqual(L.thresholds(1_000_000), {"due": 150_000, "hard": 60_000})
        self.assertEqual(L.thresholds(200_000), {"due": 70_000, "hard": 40_000})

    def test_clamped_and_monotonic(self):
        self.assertEqual(L.thresholds(100_000), {"due": 70_000, "hard": 40_000})
        self.assertEqual(L.thresholds(2_000_000), {"due": 150_000, "hard": 60_000})
        mid = L.thresholds(600_000)
        self.assertTrue(70_000 < mid["due"] < 150_000)
        self.assertTrue(40_000 < mid["hard"] < 60_000)


class TestEpoch(Base):
    def test_reset_clears_due_and_deferred_keeps_checkpoint_history(self):
        L.save_state("s", {"epoch": 3, "compact_deferred": True,
                           "due": {"tok": 1}, "checkpoint_epoch": 3})
        st = L.reset_epoch("s")
        self.assertEqual(L.epoch(st), 4)
        self.assertNotIn("compact_deferred", st)
        self.assertNotIn("due", st)
        self.assertFalse(L.checkpointed_this_epoch(st))

    def test_mark_checkpoint_binds_to_current_epoch(self):
        L.save_state("s", {"epoch": 2})
        st = L.mark_checkpoint("s")
        self.assertTrue(L.checkpointed_this_epoch(st))
        st = L.reset_epoch("s")
        self.assertFalse(L.checkpointed_this_epoch(st))

    def test_compact_summary_saved(self):
        st = L.reset_epoch("s", compact_summary="the summary")
        self.assertEqual(st["compact_summary"], "the summary")

    def test_reset_demotes_fresh_exact_to_window_only(self):
        # A record written seconds before the boundary is still fresh after
        # it; the new epoch must not inherit its tokens, only its window.
        import time
        L.save_state("s", {"exact": {"pct": 95.0, "tokens": 950_000,
                                     "window": 1_000_000, "at": time.time() - 300}})
        st = L.reset_epoch("s")
        self.assertEqual(st["exact"], {"window": 1_000_000, "at": 0})
        self.assertEqual(L.load_state("s")["exact"], {"window": 1_000_000, "at": 0})
        # No transcript yet (status line not re-rendered): unknown, not 950K.
        tok, win, pct, src = L.depth("/nonexistent", "s")
        self.assertEqual((tok, win), (0, 1_000_000))
        self.assertTrue(src.startswith("inferred"))

    def test_reset_without_exact_record_is_a_noop_for_it(self):
        st = L.reset_epoch("s")
        self.assertNotIn("exact", st)


class TestDepth(Base):
    def _transcript(self, tokens):
        p = os.path.join(self.tmp.name, "t.jsonl")
        rec = {"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tokens - 2,
            "cache_creation_input_tokens": 0}}}
        open(p, "w").write(json.dumps(rec) + "\n")
        return p

    def test_exact_preferred_over_inference(self):
        import time
        L.save_state("s", {"exact": {"pct": 50.0, "tokens": 500_000,
                                     "window": 1_000_000, "at": time.time()}})
        tok, win, pct, src = L.depth(self._transcript(100_000), "s")
        self.assertEqual((tok, src), (500_000, "exact"))

    def test_stale_exact_keeps_window_and_token_floor(self):
        # Live-fired 2026-09-16: exact {186454 of 1M} older than EXACT_MAX_AGE_S
        # was discarded; inference guessed 200K and HARD-blocked a 1M session.
        L.save_state("s", {"exact": {"pct": 18.6, "tokens": 186_454,
                                     "window": 1_000_000, "at": 0}})
        tok, win, pct, src = L.depth(self._transcript(186_454), "s")
        self.assertTrue(src.startswith("inferred"))
        self.assertEqual(win, 1_000_000)          # window never shrinks
        self.assertEqual(tok, 186_454)
        self.assertLess(pct, 20)
        # transcript ahead of the stale record: transcript wins
        self.assertEqual(L.depth(self._transcript(300_000), "s")[0], 300_000)
        # transcript behind it: exact tokens are the floor
        self.assertEqual(L.depth(self._transcript(100_000), "s")[0], 186_454)

    def test_stale_exact_token_floor_dropped_after_boundary(self):
        L.save_state("s", {"exact": {"pct": 95.0, "tokens": 950_000,
                                     "window": 1_000_000, "at": 0}})
        p = os.path.join(self.tmp.name, "b.jsonl")
        rec = lambda tok: json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tok - 2,
            "cache_creation_input_tokens": 0}}})
        open(p, "w").write(rec(950_000) + "\n"
                           + json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n"
                           + rec(30_000) + "\n")
        tok, win, pct, src = L.depth(p, "s")
        self.assertEqual((tok, win), (30_000, 1_000_000))  # window kept, floor dropped
        self.assertTrue(src.startswith("inferred"))
        self.assertEqual(L.scan_usage(p), (30_000, 950_000, True))
        self.assertEqual(L.read_usage(p), (30_000, 950_000))

    def test_demoted_exact_after_clear_uses_transcript_only(self):
        # /clear starts a transcript with no compact_boundary line: the
        # demoted record must not floor the count even without a boundary.
        import time
        L.save_state("s", {"exact": {"pct": 95.0, "tokens": 950_000,
                                     "window": 1_000_000, "at": time.time() - 300}})
        L.reset_epoch("s")
        tok, win, pct, src = L.depth(self._transcript(30_000), "s")
        self.assertEqual((tok, win), (30_000, 1_000_000))
        self.assertLess(pct, 5)
        self.assertEqual(src, "inferred, window from status line")
        # A record written after the boundary is exact again.
        L.save_state("s", {"exact": {"pct": 3.0, "tokens": 30_000,
                                     "window": 1_000_000, "at": time.time()}})
        self.assertEqual(L.depth(self._transcript(30_000), "s")[3], "exact")

    def test_stale_exact_missing_transcript_still_reports(self):
        L.save_state("s", {"exact": {"pct": 50.0, "tokens": 500_000,
                                     "window": 1_000_000, "at": 0}})
        tok, win, pct, src = L.depth("/nonexistent", "s")
        self.assertEqual((tok, win), (500_000, 1_000_000))
        self.assertTrue(src.startswith("inferred"))

    def test_no_exact_record_is_plain_inferred(self):
        tok, win, pct, src = L.depth(self._transcript(100_000), "s")
        self.assertEqual((tok, win, src), (100_000, 200_000, "inferred"))

    def test_boundary_resets_current_keeps_peak(self):
        p = os.path.join(self.tmp.name, "b.jsonl")
        rec = lambda tok: json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 2, "cache_read_input_tokens": tok - 2,
            "cache_creation_input_tokens": 0}}})
        open(p, "w").write(rec(600_000) + "\n"
                           + json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n"
                           + rec(20_000) + "\n")
        tok, win, pct, src = L.depth(p)
        self.assertEqual((tok, win), (20_000, 1_000_000))  # fresh cur, old peak keeps window
        open(p, "a").write(json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n")
        self.assertEqual(L.depth(p)[0], 0)  # boundary with no usage yet -> unknown, not stale

    def test_window_inferred_from_peak(self):
        self.assertEqual(L.depth(self._transcript(100_000))[1], 200_000)
        self.assertEqual(L.depth(self._transcript(400_000))[1], 1_000_000)

    def test_window_floor(self):
        self.assertEqual(L.window(100_000), 200_000)
        self.assertEqual(L.window(100_000, floor=1_000_000), 1_000_000)
        self.assertEqual(L.window(400_000, floor=200_000), 1_000_000)  # floor never lowers
        self.assertEqual(L.window(100_000, floor=0), 200_000)

    def test_window_env_override(self):
        os.environ["CLAUDE_KIT_CONTEXT_WINDOW"] = "500000"
        try:
            self.assertEqual(L.window(100_000), 500_000)
            self.assertEqual(L.window(100_000, floor=1_000_000), 500_000)  # pin wins
            self.assertEqual(L.depth(self._transcript(100_000))[1], 500_000)
        finally:
            os.environ.pop("CLAUDE_KIT_CONTEXT_WINDOW", None)


class TestLedger(Base):
    def test_append_and_tail(self):
        self.assertTrue(ledger.append("s", "D", "chose X over Y", ref="a/b.md"))
        self.assertTrue(ledger.append("s", "X", "rejected Z"))
        self.assertFalse(ledger.append("s", "Z", "bad kind"))
        t = ledger.tail("s")
        self.assertIn("- D chose X over Y -> a/b.md", t)
        self.assertIn("- X rejected Z", t)

    def test_tail_bounded_newest_first(self):
        for i in range(200):
            ledger.append("s", "D", f"entry {i}")
        t = ledger.tail("s", max_chars=200)
        self.assertLessEqual(len(t), 220)
        self.assertIn("entry 199", t)
        self.assertNotIn("entry 0\n", t)



class TestSweep(Base):
    def d(self):
        return os.path.dirname(L.state_path("x"))

    def touch(self, name, age_days=0):
        p = os.path.join(self.d(), name)
        with open(p, "w") as fh:
            fh.write("{}")
        t = time.time() - age_days * 86400
        os.utime(p, (t, t))
        return p

    def test_sweeps_old_temp_and_dead_locks_only(self):
        self.touch(".a.1.abcdef012345.tmp", 2)       # old temp: gone
        self.touch(".b.1.abcdef012345.tmp", 0.1)     # young temp: kept
        self.touch("c.json", 31); self.touch(".c.lock", 31)   # dead session: lock gone
        self.touch("d.json", 1); self.touch(".d.lock", 60)    # live session: kept
        self.touch(".e.lock", 31)                    # orphan lock, no state: gone
        self.touch(".f.lock", 1)                     # young orphan lock: kept
        self.touch(".k.1.abcdef012345.tmp", 9); self.touch(".k.lock", 90)  # keep=k
        removed = L.sweep_stale(keep="k")
        self.assertEqual(sorted(removed), [".a.1.abcdef012345.tmp", ".c.lock", ".e.lock"])
        left = set(os.listdir(self.d()))
        for n in (".b.1.abcdef012345.tmp", "c.json", "d.json", ".d.lock", ".f.lock",
                  ".k.1.abcdef012345.tmp", ".k.lock"):
            self.assertIn(n, left)

    def test_held_lock_is_not_removed(self):
        import fcntl
        self.touch("h.json", 40)
        p = self.touch(".h.lock", 40)
        fd = os.open(p, os.O_RDWR)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            self.assertEqual(L.sweep_stale(), [])
        finally:
            os.close(fd)
        self.assertTrue(os.path.exists(p))

    def test_runs_at_most_once_a_day_and_never_raises(self):
        self.touch(".a.1.abcdef012345.tmp", 2)
        self.assertEqual(len(L.sweep_stale()), 1)
        self.touch(".b.1.abcdef012345.tmp", 2)
        self.assertEqual(L.sweep_stale(), [])        # stamped: skipped
        self.assertEqual(len(L.sweep_stale(now=time.time() + 2 * 86400)), 1)
        from unittest import mock
        with mock.patch.object(L.os, "listdir", side_effect=OSError("boom")):
            self.assertEqual(L.sweep_stale(now=time.time() + 9 * 86400), [])

    def test_lock_open_refuses_symlink(self):
        outside = os.path.join(self.tmp.name, "outside")
        os.symlink(outside, os.path.join(self.d(), ".y.lock"))
        L.update_state("y", lambda st: st.update(a=1))   # proceeds unlocked
        self.assertFalse(os.path.exists(outside))
        self.assertEqual(L.load_state("y")["a"], 1)

    def test_swept_stamp_symlink_is_not_followed(self):
        victim = os.path.join(self.tmp.name, "victim.txt")
        with open(victim, "w") as fh:
            fh.write("precious")
        os.symlink(victim, os.path.join(self.d(), ".swept"))
        self.touch(".a.1.abcdef012345.tmp", 2)
        L.sweep_stale()
        with open(victim) as fh:
            self.assertEqual(fh.read(), "precious")
        dangling = os.path.join(self.tmp.name, "nowhere.txt")
        os.remove(os.path.join(self.d(), ".swept"))
        os.symlink(dangling, os.path.join(self.d(), ".swept"))
        L.sweep_stale(now=time.time() + 9 * 86400)
        self.assertFalse(os.path.exists(dangling))

    def test_acquire_rejects_lock_on_orphaned_inode(self):
        # A waiter that opened the lock file before the sweep unlinked it wins
        # the flock on a dead inode; it must re-open the path, not trust it.
        from unittest import mock
        path = os.path.join(self.d(), ".o.lock")
        with open(path, "w"):
            pass
        orphan = os.open(path, os.O_RDWR)
        os.unlink(path)
        real_open, calls = os.open, []

        def fake_open(p, *a, **k):
            calls.append(p)
            return os.dup(orphan) if len(calls) == 1 else real_open(p, *a, **k)
        with mock.patch.object(L.os, "open", fake_open):
            fd = L._acquire("o")
        os.close(orphan)
        self.assertIsNotNone(fd)
        try:
            self.assertEqual(len(calls), 2)
            self.assertEqual(os.fstat(fd).st_ino, os.stat(path).st_ino)
        finally:
            L._release(fd)


class TestMarkCheckpointCli(Base):
    def run_cli(self, sid):
        import subprocess
        return subprocess.run([sys.executable, os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "mark_checkpoint.py"), sid], capture_output=True, text=True,
            env=dict(os.environ, CLAUDE_CONFIG_DIR=self.tmp.name), timeout=30)

    def test_refuses_unknown_session(self):
        p = self.run_cli("typo-sid")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("no context-gate state for session 'typo-sid'", p.stderr)
        self.assertFalse(os.path.exists(L.state_path("typo-sid")))

    def test_marks_known_session(self):
        L.save_state("live", {"epoch": 2})
        p = self.run_cli("live")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("checkpoint recorded for epoch 2", p.stdout)
        self.assertEqual(L.load_state("live")["checkpoint_epoch"], 2)


if __name__ == "__main__":
    unittest.main()
