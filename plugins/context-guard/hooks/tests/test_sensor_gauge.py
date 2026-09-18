"""The context-guard side of the statusline sensor/gauge contract (3c48 F1):
ANCHORS, the dual-path sensor read, epoch_at demotion, and gauge.json.

Hermetic: CLAUDE_CONFIG_DIR and HOME both point at a temp dir, so an
expanduser fallback can never reach the real ~/.claude."""
import json, os, subprocess, sys, tempfile, time, unittest
from unittest import mock

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)


def old_thresholds(window):
    """thresholds() as it was before the ANCHORS refactor, verbatim."""
    w = max(int(window or 0), 1)
    lo_w, hi_w = 200_000, 1_000_000
    if w <= lo_w:
        return {"due": 70_000, "hard": 40_000}
    if w >= hi_w:
        return {"due": 150_000, "hard": 60_000}
    f = (w - lo_w) / (hi_w - lo_w)
    return {"due": int(70_000 + f * 80_000), "hard": int(40_000 + f * 20_000)}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = {"CLAUDE_CONFIG_DIR": self.tmp.name, "HOME": self.tmp.name}
        self._saved = {k: os.environ.get(k) for k in self.env}
        os.environ.update(self.env)
        global L
        import lib_context as L

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def write_sensor(self, sid, tokens=None, window=None, at=None, v=1, raw=None,
                     limits=None):
        p = L.sensor_path(sid)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if raw is None:
            rec = {"v": v} if v is not None else {}
            if tokens is not None:
                rec["exact"] = {"pct": 100.0 * tokens / window, "tokens": tokens,
                                "window": window,
                                "at": time.time() if at is None else at}
            if limits is not None:
                rec["rate_limits"] = limits
            raw = json.dumps(rec)
        with open(p, "w") as f:
            f.write(raw)
        return p

    def write_legacy(self, sid, tokens, window, at=None):
        def put(st):
            st["exact"] = {"pct": 100.0 * tokens / window, "tokens": tokens,
                           "window": window, "at": time.time() if at is None else at}
        L.update_state(sid, put)

    def write(self, path, text):
        with open(path, "w") as f:
            f.write(text)

    def read_json(self, path):
        with open(path) as f:
            return json.load(f)

    def assert_clean_exit(self, code, out, err, why):
        # 2 is a deliberate gate decision (HARD / deferred compaction) and
        # then stderr carries the gate's own message; anything else is 0.
        self.assertIn(code, (0, 2), (why, err))
        self.assertNotIn("Traceback", err, why)
        if code == 2:
            self.assertTrue(err.startswith("[context-guard"), (why, err))
        else:
            json.loads(out)

    def run_hook(self, name, payload):
        e = dict(os.environ)
        e.update(self.env)
        p = subprocess.run([sys.executable, os.path.join(HOOKS, name)],
                           input=json.dumps(payload), capture_output=True,
                           text=True, env=e, timeout=30)
        return p.returncode, p.stdout, p.stderr


class TestAnchors(Base):
    def test_thresholds_equal_old_implementation_on_every_window(self):
        grid = set(range(0, 2_100_001, 997))
        for a in (200_000, 1_000_000):
            grid.update(range(a - 50, a + 51))
        grid.update([None, -5, 1, 128_000, 199_999, 200_001, 600_000,
                     999_999, 1_000_001, 10**9])
        for w in sorted(grid, key=lambda x: -1 if x is None else x):
            self.assertEqual(L.thresholds(w), old_thresholds(w), w)

    def test_anchors_are_todays_policy(self):
        self.assertEqual(L.ANCHORS, ((200_000, 70_000, 40_000),
                                     (1_000_000, 150_000, 60_000)))
        for w, d, h in L.ANCHORS:
            self.assertEqual(L.thresholds(w), {"due": d, "hard": h})

    def test_thresholds_follow_the_constant(self):
        # One source: changing ANCHORS changes both the gate and the gauge.
        alt = ((100_000, 30_000, 10_000), (500_000, 90_000, 50_000),
               (2_000_000, 200_000, 80_000))
        with mock.patch.object(L, "ANCHORS", alt):
            self.assertEqual(L.thresholds(50_000), {"due": 30_000, "hard": 10_000})
            self.assertEqual(L.thresholds(300_000), {"due": 60_000, "hard": 30_000})
            self.assertEqual(L.thresholds(500_000), {"due": 90_000, "hard": 50_000})
            self.assertEqual(L.thresholds(1_250_000), {"due": 145_000, "hard": 65_000})
            self.assertEqual(L.thresholds(9_000_000), {"due": 200_000, "hard": 80_000})
            anchors = L.gauge_record()["thresholds"]["anchors"]
            self.assertEqual([(a["window"], a["due"], a["hard"]) for a in anchors],
                             list(alt))


class TestSensorPath(Base):
    def test_neutral_path_under_config_dir(self):
        self.assertEqual(L.sensor_path("abc-123"),
                         os.path.join(self.tmp.name, "statusline", "sensor",
                                      "abc-123.json"))

    def test_traversal_id_stays_inside(self):
        p = L.sensor_path("../../etc/passwd")
        self.assertEqual(os.path.dirname(p),
                         os.path.join(self.tmp.name, "statusline", "sensor"))
        self.assertTrue(os.path.basename(p).startswith("sid-"))

    def test_unset_or_empty_config_dir_means_home_dot_claude(self):
        for val in (None, ""):
            with mock.patch.dict(os.environ, {"HOME": self.tmp.name}):
                if val is None:
                    os.environ.pop("CLAUDE_CONFIG_DIR", None)
                else:
                    os.environ["CLAUDE_CONFIG_DIR"] = val
                self.assertEqual(L.sensor_path("s"),
                                 os.path.join(self.tmp.name, ".claude", "statusline",
                                              "sensor", "s.json"))

    def test_reader_never_creates_the_sensor_dir(self):
        L.depth("/nonexistent", "s")
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "statusline")))


class TestDualRead(Base):
    def test_new_path_only(self):
        self.write_sensor("s", 420_000, 1_000_000)
        tok, win, pct, src = L.depth("/nonexistent", "s")
        self.assertEqual((tok, win, pct, src), (420_000, 1_000_000, 42.0, "exact"))
        self.assertFalse(os.path.exists(L.state_path("s")))  # read-only: no state write

    def test_old_path_only(self):
        self.write_legacy("s", 300_000, 1_000_000)
        tok, win, pct, src = L.depth("/nonexistent", "s")
        self.assertEqual((tok, win, src), (300_000, 1_000_000, "exact"))

    def test_both_new_fresher_wins(self):
        now = time.time()
        self.write_legacy("s", 300_000, 1_000_000, at=now - 30)
        self.write_sensor("s", 420_000, 1_000_000, at=now - 5)
        self.assertEqual(L.depth("/nonexistent", "s")[0], 420_000)

    def test_both_old_fresher_wins(self):
        now = time.time()
        self.write_legacy("s", 300_000, 1_000_000, at=now - 5)
        self.write_sensor("s", 420_000, 1_000_000, at=now - 30)
        self.assertEqual(L.depth("/nonexistent", "s")[0], 300_000)

    def test_tie_goes_to_the_sensor_file(self):
        now = time.time()
        self.write_legacy("s", 300_000, 1_000_000, at=now)
        self.write_sensor("s", 420_000, 1_000_000, at=now)
        self.assertEqual(L.depth("/nonexistent", "s")[0], 420_000)

    def test_unknown_newer_version_ignored(self):
        self.write_legacy("s", 300_000, 1_000_000, at=time.time() - 30)
        self.write_sensor("s", 420_000, 1_000_000, v=2)
        self.assertEqual(L.depth("/nonexistent", "s")[0], 300_000)
        self.assertEqual(L.sensor_record("s"), {})

    def test_unknown_version_alone_is_absent(self):
        for v in (2, None, 0, "1", 1.0, True):
            self.write_sensor("s", 420_000, 1_000_000, v=v)
            tok, win, pct, src = L.depth("/nonexistent", "s")
            self.assertEqual(src, "inferred", v)
            self.assertEqual(tok, 0, v)

    def test_malformed_records_are_absent(self):
        self.write_legacy("s", 300_000, 1_000_000, at=time.time() - 30)
        bad = ["not json", "[]", "null", json.dumps({"v": 1, "exact": []}),
               json.dumps({"v": 1, "exact": {"pct": 5, "tokens": 5, "window": 0,
                                             "at": time.time()}}),
               json.dumps({"v": 1, "exact": {"pct": "x", "tokens": 5,
                                             "window": 1000, "at": time.time()}}),
               json.dumps({"v": 1, "exact": {"pct": 5, "tokens": 5,
                                             "window": 1000}}),
               '{"v": 1, "exact": {"pct": NaN, "tokens": 5, "window": 1000, "at": 1e12}}',
               json.dumps({"v": 1, "exact": {"pct": 5, "tokens": True,
                                             "window": 1000, "at": time.time()}})]
        for raw in bad:
            self.write_sensor("s", raw=raw)
            self.assertEqual(L.depth("/nonexistent", "s")[0], 300_000, raw)

    def test_sensor_dir_is_a_file_does_not_raise(self):
        os.makedirs(os.path.join(self.tmp.name, "statusline"))
        self.write(os.path.join(self.tmp.name, "statusline", "sensor"), "x")
        self.assertEqual(L.depth("/nonexistent", "s")[3], "inferred")

    def test_stale_new_record_pins_window_and_floors_tokens(self):
        self.write_sensor("s", 186_454, 1_000_000, at=time.time() - 3600)
        tok, win, pct, src = L.depth("/nonexistent", "s")
        self.assertEqual((tok, win, src),
                         (186_454, 1_000_000, "inferred, window from status line"))

    def test_rate_limits_readable(self):
        lim = {"five_hour": {"used_percentage": 23.5, "resets_at": 1.0}, "at": 1.0}
        self.write_sensor("s", 1, 1000, limits=lim)
        self.assertEqual(L.sensor_record("s")["rate_limits"], lim)

    def test_pct_clamped(self):
        self.write_sensor("s", raw=json.dumps({"v": 1, "exact": {
            "pct": 140.0, "tokens": 5, "window": 1000, "at": time.time()}}))
        self.assertEqual(L.depth("/nonexistent", "s")[2], 100.0)


class TestSensorHardening(Base):
    """F4: routed lows from the F1 review - a future `at` and a non-regular
    file at the sensor path."""

    def test_future_at_beyond_skew_is_rejected(self):
        self.write_sensor("s", 500_000, 1_000_000, at=time.time() + L.FUTURE_SKEW_S + 60)
        self.assertEqual(L._sensor_exact("s"), {})
        self.assertEqual(L.sensor("s"), {})
        tok, win, pct, src = L.depth("", "s")
        self.assertTrue(src.startswith("inferred"), src)

    def test_future_at_rejected_falls_back_to_legacy(self):
        self.write_legacy("s", 300_000, 1_000_000)
        self.write_sensor("s", 500_000, 1_000_000, at=time.time() + 3600)
        self.assertEqual(L.sensor("s")["tokens"], 300_000)

    def test_small_clock_skew_is_accepted(self):
        self.write_sensor("s", 500_000, 1_000_000, at=time.time() + 30)
        self.assertEqual(L.depth("", "s")[3], "exact")

    def _read_in_child(self, sid="s", timeout=10):
        """sensor_record in a subprocess, so a regression that blocks on a
        FIFO fails the test instead of hanging the suite."""
        code = ("import sys, json; sys.path.insert(0, %r); import lib_context as L; "
                "print(json.dumps([L.sensor_record(%r), L.sensor(%r)]))" % (HOOKS, sid, sid))
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                           env=dict(os.environ, **self.env), timeout=timeout)
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "no FIFOs on this platform")
    def test_fifo_at_sensor_path_neither_hangs_nor_reads(self):
        p = L.sensor_path("s")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        os.mkfifo(p)
        self.assertEqual(self._read_in_child(), [{}, {}])
        self.assertIsNone(L.read_json_file(p))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "no FIFOs on this platform")
    def test_context_warn_with_fifo_sensor_exits_clean(self):
        p = L.sensor_path("s")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        os.mkfifo(p)
        t = os.path.join(self.tmp.name, "t.jsonl")
        self.write(t, "")
        self.assert_clean_exit(*self.run_hook("context_warn.py", {
            "session_id": "s", "prompt": "hi", "transcript_path": t}), "fifo")

    def test_directory_and_device_at_sensor_path_are_absent(self):
        p = L.sensor_path("s")
        os.makedirs(p)                       # a directory where the file goes
        self.assertEqual(self._read_in_child(), [{}, {}])
        os.rmdir(p)
        if os.path.exists("/dev/zero"):
            os.symlink("/dev/zero", p)       # a character device via a link
            self.assertEqual(self._read_in_child(), [{}, {}])

    def test_symlink_to_a_regular_record_still_reads(self):
        real = os.path.join(self.tmp.name, "rec.json")
        self.write(real, json.dumps({"v": 1, "exact": {
            "pct": 50.0, "tokens": 500_000, "window": 1_000_000, "at": time.time()}}))
        p = L.sensor_path("s")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        os.symlink(real, p)
        self.assertEqual(L.sensor("s")["tokens"], 500_000)


class TestEpochDemotion(Base):
    def test_reset_stamps_epoch_at(self):
        before = time.time()
        st = L.reset_epoch("s")
        self.assertGreaterEqual(st["epoch_at"], before)

    def test_new_path_record_before_reset_is_window_only(self):
        self.write_sensor("s", 950_000, 1_000_000, at=time.time() - 60)
        L.reset_epoch("s")
        tok, win, pct, src = L.depth("/nonexistent", "s")
        self.assertEqual((tok, win), (0, 1_000_000))
        self.assertTrue(src.startswith("inferred"))
        # context-guard never wrote the other plugin's file
        self.assertEqual(self.read_json(L.sensor_path("s"))["exact"]["tokens"],
                         950_000)

    def test_race_record_written_after_reset_but_stamped_before(self):
        # Finding 4: payload read before the compaction, write lands after it.
        stamped = time.time()
        L.reset_epoch("s")
        self.write_sensor("s", 950_000, 1_000_000, at=stamped)
        self.assertEqual(L.depth("/nonexistent", "s")[:2], (0, 1_000_000))

    def test_legacy_race_is_demoted_too(self):
        stamped = time.time()
        L.reset_epoch("s")
        self.write_legacy("s", 950_000, 1_000_000, at=stamped)
        self.assertEqual(L.depth("/nonexistent", "s")[:2], (0, 1_000_000))

    def test_record_after_reset_is_exact(self):
        L.reset_epoch("s")
        epoch_at = L.load_state("s")["epoch_at"]
        self.write_sensor("s", 30_000, 1_000_000, at=epoch_at + 1)
        self.assertEqual(L.depth("/nonexistent", "s")[::3], (30_000, "exact"))

    def test_demoted_new_record_uses_post_boundary_transcript(self):
        self.write_sensor("s", 950_000, 1_000_000, at=time.time() - 10)
        L.reset_epoch("s")
        t = os.path.join(self.tmp.name, "t.jsonl")
        self.write(t, json.dumps({"message": {"usage": {
            "input_tokens": 40_000}}}) + "\n")
        self.assertEqual(L.depth(t, "s")[:2], (40_000, 1_000_000))

    def test_epoch_end_tokens_from_the_sensor(self):
        self.write_sensor("s", 777_000, 1_000_000, at=time.time() - 5)
        st = L.reset_epoch("s")
        self.assertEqual(st["epoch_end_tokens"], 777_000)

    def test_epoch_end_tokens_takes_the_fresher_record(self):
        now = time.time()
        self.write_sensor("s", 777_000, 1_000_000, at=now - 50)
        self.write_legacy("s", 800_000, 1_000_000, at=now - 5)
        self.assertEqual(L.reset_epoch("s")["epoch_end_tokens"], 800_000)

    def test_postcompact_hook_with_new_path_record(self):
        self.write_sensor("s", 900_000, 1_000_000, at=time.time() - 5)
        code, out, err = self.run_hook("postcompact_epoch.py",
                                       {"session_id": "s", "hook_event_name": "PostCompact",
                                        "compact_summary": "x"})
        self.assertEqual((code, json.loads(out)), (0, {}))
        st = L.load_state("s")
        self.assertEqual((st["epoch"], st["epoch_end_tokens"]), (1, 900_000))
        self.assertEqual(L.depth("/nonexistent", "s")[:2], (0, 1_000_000))


class TestGauge(Base):
    def test_shape_and_version(self):
        self.assertTrue(L.publish_gauge())
        g = self.read_json(L.gauge_path())
        self.assertEqual(L.gauge_path(), os.path.join(
            self.tmp.name, "claude-kit", "context-gate", "gauge.json"))
        self.assertEqual(g, {
            "v": 1, "writer": "context-guard",
            "thresholds": {"unit": "tokens_remaining", "interp": "linear_clamped",
                           "anchors": [{"window": 200000, "due": 70000, "hard": 40000},
                                       {"window": 1000000, "due": 150000, "hard": 60000}]},
            "labels": {"due": "checkpoint DUE", "hard": "HARD gate"}})

    def test_idempotent(self):
        L.publish_gauge()
        m = os.stat(L.gauge_path()).st_mtime_ns
        os.utime(L.gauge_path(), ns=(m - 10**9, m - 10**9))
        self.assertFalse(L.publish_gauge())
        self.assertEqual(os.stat(L.gauge_path()).st_mtime_ns, m - 10**9)

    def test_rewritten_when_different_or_corrupt(self):
        os.makedirs(os.path.dirname(L.gauge_path()), exist_ok=True)
        for raw in ("{", json.dumps({"v": 1, "labels": {}}), ""):
            self.write(L.gauge_path(), raw)
            self.assertTrue(L.publish_gauge())
            self.assertEqual(self.read_json(L.gauge_path()), L.gauge_record())

    def test_atomic_failure_leaves_original_and_no_temp(self):
        os.makedirs(os.path.dirname(L.gauge_path()), exist_ok=True)
        self.write(L.gauge_path(), '{"v": 0}')
        with mock.patch.object(L.os, "replace", side_effect=OSError("boom")):
            self.assertFalse(L.publish_gauge())
        with open(L.gauge_path()) as f:
            self.assertEqual(f.read(), '{"v": 0}')
        d = os.path.dirname(L.gauge_path())
        self.assertEqual([n for n in os.listdir(d) if n.endswith(".tmp")], [])

    def test_never_raises(self):
        os.makedirs(os.path.join(self.tmp.name, "claude-kit", "context-gate",
                                 "gauge.json"))  # a dir where the file goes
        self.assertFalse(L.publish_gauge())

    def test_gauge_published_even_on_unparseable_input(self):
        # publish_gauge runs first in rehydrate main(), before the input parse
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "rehydrate.py")],
                           input="not json", capture_output=True, text=True,
                           env=dict(os.environ, **self.env), timeout=30)
        self.assertEqual((p.returncode, p.stdout.strip()), (0, "{}"))
        self.assertEqual(self.read_json(L.gauge_path()), L.gauge_record())

    def test_labels_match_the_status_line_hints(self):
        # context-guard's statusline.py (deprecated at F4) hard-codes its hint
        # words; the published labels must say the same thing.
        with open(os.path.join(HOOKS, "statusline.py")) as f:
            src = f.read()
        for label in L.GAUGE_LABELS.values():
            self.assertIn(f"·  {label}", src)

    def test_session_start_publishes_the_gauge(self):
        code, out, err = self.run_hook("rehydrate.py", {
            "session_id": "s", "source": "startup", "cwd": self.tmp.name})
        self.assertEqual(code, 0, err)
        json.loads(out)
        self.assertEqual(self.read_json(L.gauge_path()), L.gauge_record())


class TestHooksNeverRaise(Base):
    GARBAGE = ["not json", "[]", json.dumps({"v": 1, "exact": "x"}),
               json.dumps({"v": 1, "exact": {"window": "1e6", "tokens": [],
                                             "pct": {}, "at": None}}),
               json.dumps({"v": 99, "exact": {"window": 1}})]

    def _all_hooks(self):
        t = os.path.join(self.tmp.name, "t.jsonl")
        self.write(t, "")
        return [("context_warn.py", {"session_id": "s", "prompt": "hi",
                                     "transcript_path": t}),
                ("precompact_gate.py", {"session_id": "s", "trigger": "auto",
                                        "transcript_path": t}),
                ("postcompact_epoch.py", {"session_id": "s",
                                          "hook_event_name": "PostCompact"}),
                ("rehydrate.py", {"session_id": "s", "source": "compact",
                                  "cwd": self.tmp.name})]

    def test_garbage_sensor_records(self):
        for raw in self.GARBAGE:
            self.write_sensor("s", raw=raw)
            for name, payload in self._all_hooks():
                self.assert_clean_exit(*self.run_hook(name, payload), (name, raw))

    def test_garbage_state_epoch_at(self):
        L.save_state("s", {"epoch_at": "soon", "exact": {"window": 1_000_000,
                                                         "tokens": 5, "pct": 0.0,
                                                         "at": time.time()}})
        self.write_sensor("s", 10, 1_000_000)
        for name, payload in self._all_hooks():
            self.assert_clean_exit(*self.run_hook(name, payload), name)

    def test_unwritable_gauge_location(self):
        os.makedirs(os.path.join(self.tmp.name, "claude-kit", "context-gate",
                                 "gauge.json"))
        code, out, err = self.run_hook("rehydrate.py", {
            "session_id": "s", "source": "startup", "cwd": self.tmp.name})
        self.assertEqual(code, 0)
        self.assertNotIn("Traceback", err)
        json.loads(out)


if __name__ == "__main__":
    unittest.main()
