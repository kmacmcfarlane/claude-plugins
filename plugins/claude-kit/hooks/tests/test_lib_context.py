import json, os, sys, tempfile, unittest

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

    def test_stale_exact_falls_back(self):
        L.save_state("s", {"exact": {"pct": 50.0, "tokens": 500_000,
                                     "window": 1_000_000, "at": 0}})
        tok, win, pct, src = L.depth(self._transcript(100_000), "s")
        self.assertEqual(src, "inferred")
        self.assertEqual(tok, 100_000)

    def test_window_inferred_from_peak(self):
        self.assertEqual(L.depth(self._transcript(100_000))[1], 200_000)
        self.assertEqual(L.depth(self._transcript(400_000))[1], 1_000_000)


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


if __name__ == "__main__":
    unittest.main()
