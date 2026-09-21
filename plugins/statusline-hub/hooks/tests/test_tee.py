"""The tee on its own (no statusline plugin needed): stdin JSON in, the v1
sensor record out at <cfg>/statusline/sensor/<safe_sid>.json, nothing
printed, exit 0 whatever the input. The byte-for-byte agreement with the
statusline plugin's writer is test_parity.py's job."""
import json, os, stat, sys, time, unittest
from unittest import mock

import helpers
import tee as T


class Tee(helpers.Hermetic):
    def test_writes_the_record_and_prints_nothing(self):
        now = time.time()
        before = time.time()
        self.tee({"rate_limits": {"five_hour": {"used_percentage": 23.5,
                                                "resets_at": now + 3600}}})
        rec = self.read_sensor()
        self.assertEqual(set(rec), {"v", "exact", "rate_limits"})
        self.assertIs(type(rec["v"]), int)
        self.assertEqual({k: v for k, v in rec["exact"].items() if k != "at"},
                         {"pct": 42.0, "tokens": 420_000, "window": 1_000_000})
        self.assertEqual(rec["rate_limits"]["five_hour"],
                         {"used_percentage": 23.5, "resets_at": now + 3600})
        self.assertEqual(rec["exact"]["at"], rec["rate_limits"]["at"])
        self.assertGreaterEqual(rec["exact"]["at"], before)
        self.assertLessEqual(rec["exact"]["at"], time.time())

    def test_private_modes_and_nothing_else_written(self):
        self.tee({})
        p = self.sensor_file()
        self.assertEqual(stat.S_IMODE(os.stat(p).st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(p)).st_mode), 0o700)
        self.assertEqual(self.all_files(), [p])

    def test_merges_and_never_regresses(self):
        rl = {"five_hour": {"used_percentage": 5.0}, "at": 1.0}
        self.write_json(self.sensor_file(), {"v": 1, "rate_limits": rl})
        self.tee({})
        self.assertEqual(self.read_sensor()["rate_limits"], rl)
        newer = {"pct": 1.0, "tokens": 1, "window": 1_000_000, "at": time.time() + 30}
        self.write_json(self.sensor_file(), {"v": 1, "exact": newer})
        self.tee({})
        self.assertEqual(self.read_sensor()["exact"], newer)

    def test_bad_input_is_silent_and_writes_nothing(self):
        for raw in ("", "{not json", "[]", "null", "7", '"s"', "\x00\x01", "{" * 5000):
            with self.subTest(raw=raw[:10]):
                self.tee(raw=raw)
        for p in ({"session_id": None}, {"session_id": 7},
                  {"context_window": None, "rate_limits": "x"}):
            with self.subTest(p=p):
                self.tee(p)
        self.assertEqual(self.all_files(), [])

    def test_oversized_stdin_writes_nothing(self):
        payload = helpers.with_defaults({"pad": "x" * (T.READ_MAX + 10)})
        self.tee(raw=json.dumps(payload))
        self.assertEqual(self.all_files(), [])

    def test_arguments_are_ignored(self):
        self.tee({}, args=("--gauge", "--hook", "x"))
        self.assertEqual(self.read_sensor()["exact"]["window"], 1_000_000)

    def test_traversal_sid_stays_inside(self):
        sid = "../../evil"
        self.tee({"session_id": sid})
        for f in self.all_files():
            self.assertTrue(os.path.relpath(f, self.cfg).startswith(
                os.path.join("statusline", "sensor")), f)
        self.assertIsNotNone(self.read_sensor(T.safe_sid(sid)))

    def test_unwritable_dir_is_silent(self):
        os.makedirs(os.path.join(self.cfg, "statusline"))
        with open(os.path.join(self.cfg, "statusline", "sensor"), "w") as f:
            f.write("not a dir")
        self.tee({})

    def test_config_dir_rule(self):
        self.assertEqual(T.base_dir(), self.cfg)
        os.environ["CLAUDE_CONFIG_DIR"] = ""
        self.assertEqual(T.base_dir(), os.path.join(self.cfg, ".claude"))
        self.assertEqual(T.sensor_path("abc"), os.path.join(
            self.cfg, ".claude", "statusline", "sensor", "abc.json"))


class InProcess(helpers.Hermetic):
    def test_tee_returns_whether_it_wrote(self):
        self.assertTrue(T.tee(json.dumps(helpers.with_defaults({})), now=5.0))
        self.assertFalse(T.tee(json.dumps(helpers.with_defaults({})), now=4.0))  # older
        self.assertFalse(T.tee("{bad"))
        self.assertFalse(T.tee(None))

    def test_sensor_blocks_never_raises(self):
        self.assertEqual(T.sensor_blocks(None, 1.0), (None, None, None))
        with mock.patch.object(T, "limits_record", side_effect=RuntimeError):
            self.assertEqual(T.sensor_blocks({"session_id": "s"}, 1.0), (None, None, None))

    def test_tee_never_raises(self):
        with mock.patch.object(T, "write_sensor", side_effect=RuntimeError):
            self.assertFalse(T.tee(json.dumps(helpers.with_defaults({}))))

    def test_main_survives_a_broken_stdin(self):
        with mock.patch.object(sys, "stdin", None):
            T.main()
        self.assertEqual(self.all_files(), [])


if __name__ == "__main__":
    unittest.main()
