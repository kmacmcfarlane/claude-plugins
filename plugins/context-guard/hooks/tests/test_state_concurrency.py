"""The context-gate state file under concurrent writers: update_state's lock
keeps every writer's keys, temp names are unique so no torn file is ever
installed, session ids are confined to the state dir, and a lock that cannot
be taken fails open instead of blocking a session."""
import json, os, subprocess, sys, tempfile, textwrap, time, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)

try:
    import fcntl
except ImportError:
    fcntl = None

WORKER = textwrap.dedent("""
    import sys
    sys.path.insert(0, sys.argv[1])
    import lib_context as L
    L.LOCK_TIMEOUT_S = 5  # determinism: this test proves the lock, not the timeout
    key, n = sys.argv[2], int(sys.argv[3])
    def bump(st, i):
        st[key] = i
        st["count"] = int(st.get("count", 0)) + 1
    for i in range(n):
        L.update_state("race", lambda st: bump(st, i))
""")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, CLAUDE_CONFIG_DIR=self.tmp.name)
        os.environ["CLAUDE_CONFIG_DIR"] = self.tmp.name
        global L
        import lib_context as L
        self.saved_timeout, self.saved_fcntl = L.LOCK_TIMEOUT_S, L.fcntl
        self.gate = os.path.join(self.tmp.name, "claude-kit", "context-gate")

    def tearDown(self):
        L.LOCK_TIMEOUT_S, L.fcntl = self.saved_timeout, self.saved_fcntl
        self.tmp.cleanup()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    def all_files(self):
        out = []
        for root, _, files in os.walk(self.tmp.name):
            out += [os.path.join(root, f) for f in files]
        return out


@unittest.skipIf(fcntl is None, "fcntl.flock is POSIX-only")
class ConcurrentWriters(Base):
    def test_parallel_writers_lose_no_key_and_no_update(self):
        procs, n = 6, 40
        ps = [subprocess.Popen([sys.executable, "-c", WORKER, HOOKS, f"k{j}", str(n)],
                               env=self.env) for j in range(procs)]
        path = L.state_path("race")
        torn = 0
        while any(p.poll() is None for p in ps):
            try:
                with open(path) as f:
                    json.load(f)
            except FileNotFoundError:
                pass
            except ValueError:
                torn += 1
        for p in ps:
            self.assertEqual(p.wait(timeout=60), 0)
        self.assertEqual(torn, 0, "a reader saw corrupt JSON")
        with open(path) as f:
            st = json.load(f)
        for j in range(procs):
            self.assertEqual(st.get(f"k{j}"), n - 1)
        self.assertEqual(st["count"], procs * n, "a read-modify-write was lost")
        self.assertEqual([f for f in os.listdir(self.gate) if f.endswith(".tmp")], [])

    def test_status_line_never_undoes_an_epoch_or_checkpoint(self):
        # The live bug: the status line loaded, a compaction bumped the epoch,
        # and the status line wrote the stale epoch back.
        payload = json.dumps({"session_id": "s", "model": {"display_name": "M"},
                              "context_window": {"used_percentage": 10.0,
                                                 "context_window_size": 1_000_000,
                                                 "total_input_tokens": 100_000}})
        stop = time.monotonic() + 60
        lines = [subprocess.Popen([sys.executable, os.path.join(HOOKS, "statusline.py")],
                                  stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                  env=self.env) for _ in range(12)]
        for p in lines:
            p.stdin.write(payload.encode()); p.stdin.close()
        L.LOCK_TIMEOUT_S = 5
        resets = 0
        while any(p.poll() is None for p in lines) or resets < 20:
            L.reset_epoch("s")
            resets += 1
            self.assertLess(time.monotonic(), stop)
        L.mark_checkpoint("s")
        for p in lines:
            self.assertEqual(p.wait(timeout=60), 0)
        st = L.load_state("s")
        self.assertEqual(L.epoch(st), resets)
        self.assertEqual(st["checkpoint_epoch"], resets)

    def test_hook_writers_keep_each_others_keys(self):
        L.save_state("h", {})   # a live session has state; mark_checkpoint requires it
        procs = []
        for i in range(8):
            procs.append(subprocess.Popen(
                [sys.executable, os.path.join(HOOKS, "precompact_gate.py")],
                stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, env=self.env))
            procs[-1].stdin.write(json.dumps({"session_id": "h", "trigger": "manual",
                                              "custom_instructions": "keep"}).encode())
            procs[-1].stdin.close()
            procs.append(subprocess.Popen(
                [sys.executable, os.path.join(HOOKS, "mark_checkpoint.py"), "h"],
                # the temp config dir, not this checkout: the mark step stamps
                # the manifest it finds from its cwd
                cwd=self.tmp.name, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, env=self.env))
        for p in procs:
            self.assertEqual(p.wait(timeout=60), 0)
        st = L.load_state("h")
        self.assertEqual(st.get("custom_instructions"), "keep")
        self.assertEqual(st.get("checkpoint_epoch"), 0)
        self.assertEqual(st.get("last_compact_trigger"), "manual")


class TempNames(Base):
    def test_shared_tmp_name_is_not_used(self):
        # The old writer used <sid>.json.tmp; a directory squatting there
        # made every save fail. Unique O_EXCL temp names ignore it.
        os.makedirs(L.state_path("t") + ".tmp")
        L.save_state("t", {"a": 1})
        self.assertEqual(L.load_state("t"), {"a": 1})

    def test_failed_save_leaves_no_temp_file(self):
        L.save_state("t", {"bad": object()})  # not JSON-serialisable
        self.assertEqual(L.load_state("t"), {})
        self.assertEqual([f for f in os.listdir(self.gate) if f.endswith(".tmp")], [])


class SessionIdConfinement(Base):
    BAD = ["../../evil", "../evil", "..", ".", ".hidden", "a/b", "/abs/evil",
           "a\\b", "x" * 129, "nul\0byte", "sp ace", "é"]

    def test_unsafe_ids_stay_in_the_state_dir(self):
        gate = os.path.realpath(L._state_dir())
        for sid in self.BAD:
            p = os.path.realpath(L.state_path(sid))
            self.assertEqual(os.path.dirname(p), gate, sid)
            self.assertFalse(os.path.basename(p).startswith("."), sid)
            self.assertEqual(os.path.dirname(os.path.realpath(L.ledger_path(sid))),
                             os.path.realpath(os.path.join(self.tmp.name, "claude-kit", "ledger")))
            L.update_state(sid, lambda st: st.update(v=sid))
            self.assertEqual(L.load_state(sid)["v"], sid)
        for f in self.all_files():
            rel = os.path.relpath(f, self.tmp.name)
            self.assertTrue(rel.startswith(os.path.join("claude-kit", "context-gate")), rel)

    def test_distinct_unsafe_ids_do_not_collide(self):
        names = {L.safe_sid(s) for s in self.BAD}
        self.assertEqual(len(names), len(self.BAD))

    def test_safe_ids_pass_unchanged(self):
        for sid in ("0c7eafc7-18dc-4274-9add-93aa21324fb3", "s", "child_3.x"):
            self.assertEqual(os.path.basename(L.state_path(sid)), sid + ".json")
        self.assertEqual(L.safe_sid(None), "unknown")
        self.assertEqual(L.safe_sid(""), "unknown")
        self.assertTrue(L.safe_sid(123).startswith("sid-"))

    def test_status_line_with_traversal_id_writes_inside(self):
        outside = os.path.join(self.tmp.name, "evil.json")
        payload = {"session_id": "../../evil", "model": {"display_name": "M"},
                   "context_window": {"used_percentage": 10.0,
                                      "context_window_size": 1_000_000,
                                      "total_input_tokens": 100_000}}
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "statusline.py")],
                           input=json.dumps(payload), capture_output=True, text=True,
                           env=self.env, timeout=30)
        self.assertEqual(p.returncode, 0)
        self.assertFalse(os.path.exists(outside))
        self.assertEqual(L.load_state("../../evil")["exact"]["window"], 1_000_000)
        for f in self.all_files():
            self.assertTrue(os.path.relpath(f, self.tmp.name).startswith(
                os.path.join("claude-kit", "context-gate")), f)


class FailOpen(Base):
    @unittest.skipIf(fcntl is None, "fcntl.flock is POSIX-only")
    def test_lock_timeout_fails_open_and_bounded(self):
        L.save_state("f", {"keep": 1})
        fd = os.open(os.path.join(L._state_dir(), ".f.lock"), os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)  # a writer that never lets go
        try:
            L.LOCK_TIMEOUT_S = 0.05
            t0 = time.monotonic()
            st = L.update_state("f", lambda st: st.update(new=2))
            took = time.monotonic() - t0
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN); os.close(fd)
        self.assertLess(took, 0.5)
        self.assertEqual(st, {"keep": 1, "new": 2})
        self.assertEqual(L.load_state("f"), {"keep": 1, "new": 2})

    @unittest.skipIf(fcntl is None, "fcntl.flock is POSIX-only")
    def test_default_lock_wait_is_well_under_a_second(self):
        self.assertLessEqual(L.LOCK_TIMEOUT_S, 0.25)
        fd = os.open(os.path.join(L._state_dir(), ".g.lock"), os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            t0 = time.monotonic()
            L.mark_checkpoint("g")
            took = time.monotonic() - t0
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN); os.close(fd)
        self.assertLess(took, 0.6)
        self.assertEqual(L.load_state("g")["checkpoint_epoch"], 0)

    def test_lock_error_fails_open(self):
        os.makedirs(os.path.join(L._state_dir(), ".e.lock"))  # open() of it fails
        st = L.update_state("e", lambda st: st.update(x=1))
        self.assertEqual(st, {"x": 1})
        self.assertEqual(L.load_state("e"), {"x": 1})

    def test_no_fcntl_runs_unlocked(self):
        L.fcntl = None
        L.update_state("n", lambda st: st.update(x=1))
        L.update_state("n", lambda st: st.update(y=2))
        self.assertEqual(L.load_state("n"), {"x": 1, "y": 2})
        self.assertFalse(os.path.exists(os.path.join(L._state_dir(), ".n.lock")))

    def test_hung_lock_does_not_block_a_hook(self):
        if fcntl is None:
            self.skipTest("fcntl.flock is POSIX-only")
        fd = os.open(os.path.join(L._state_dir(), ".s.lock"), os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            p = subprocess.run([sys.executable, os.path.join(HOOKS, "context_warn.py")],
                               input=json.dumps({"session_id": "s", "prompt": "hi",
                                                 "transcript_path": "/nonexistent"}),
                               capture_output=True, text=True, env=self.env, timeout=30)
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN); os.close(fd)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(L.load_state("s")["prompt_n"], 1)


if __name__ == "__main__":
    unittest.main()
