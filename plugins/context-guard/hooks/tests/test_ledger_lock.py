"""H5 review r1: ledger writes lock the file the repo's way (LOCK_NB retried
until LOCK_TIMEOUT_S, then unlocked), so a stuck holder never stalls a hook,
and concurrent writers on a successor's new ledger lose nothing."""
import os, sys, tempfile, threading, time, unittest
from unittest import mock

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)
import fcntl  # noqa: E402


class LockCase(unittest.TestCase):
    def setUp(self):
        self.cfg = tempfile.TemporaryDirectory()
        self.old = os.environ.get("CLAUDE_CONFIG_DIR")
        os.environ["CLAUDE_CONFIG_DIR"] = self.cfg.name
        global L, ledger
        import lib_context as L
        import ledger

    def tearDown(self):
        self.cfg.cleanup()
        if self.old is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = self.old

    def read(self, sid="s"):
        with open(L.ledger_path(sid)) as fh:
            return fh.read()

    def test_held_lock_does_not_stall_writes_past_the_bound(self):
        with open(L.ledger_path("s"), "a") as holder:
            fcntl.flock(holder.fileno(), fcntl.LOCK_EX)
            for name, call in (
                    ("append", lambda: ledger.append("s", "D", "held line")),
                    ("epoch_header", lambda: ledger.epoch_header("s", 1, 0)),
                    ("successor_title", lambda: ledger.successor_title("s", "X"))):
                with self.subTest(call=name):
                    t0 = time.monotonic()
                    call()
                    self.assertLess(time.monotonic() - t0, L.LOCK_TIMEOUT_S + 0.5)
            # The appends went through unlocked; the rewrite was skipped.
            before = self.read()
            self.assertFalse(ledger.successor_title("s", "X"))
            self.assertEqual(self.read(), before)
        self.assertIn("- D held line", before)
        self.assertIn("## epoch 1", before)
        self.assertNotIn("successor of", before)
        self.assertTrue(ledger.successor_title("s", "X"))      # released
        self.assertTrue(self.read().startswith("# ledger s (successor of X)\n"))

    def test_no_fcntl_writes_unlocked(self):
        with mock.patch.object(L, "fcntl", None):
            self.assertTrue(ledger.append("s", "D", "no lock here"))
            ledger.epoch_header("s", 2, 0)
            self.assertTrue(ledger.successor_title("s", "X"))
        text = self.read()
        self.assertTrue(text.startswith("# ledger s (successor of X)\n"), text)
        self.assertIn("- D no lock here", text)
        self.assertIn("## epoch 2", text)

    def test_concurrent_writers_lose_nothing(self):
        n = 200
        start = threading.Event()

        def writer():
            start.wait()
            for i in range(n):
                ledger.append("s", "P", f"pointer {i:04d}")

        def title():
            start.wait()
            time.sleep(0.005)
            ledger.successor_title("s", "X")

        ts = [threading.Thread(target=writer), threading.Thread(target=title)]
        for t in ts:
            t.start()
        start.set()
        for t in ts:
            t.join()
        lines = self.read().splitlines()
        self.assertEqual(lines[0], "# ledger s (successor of X)")
        self.assertEqual(sum(1 for ln in lines if ln.startswith("- P pointer")), n)


if __name__ == "__main__":
    unittest.main()
