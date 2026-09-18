"""sensor.py in-process: the base-dir rule, safe_sid, interpolation, the
atomic merge-write, and the publisher read."""
import json, os, unittest
from unittest import mock

import helpers
import sensor as S


class BaseDir(helpers.Hermetic):
    def test_set_empty_unset(self):
        self.assertEqual(S.base_dir(), self.cfg)
        os.environ["CLAUDE_CONFIG_DIR"] = ""
        self.assertEqual(S.base_dir(), os.path.join(self.cfg, ".claude"))
        os.environ.pop("CLAUDE_CONFIG_DIR")
        self.assertEqual(S.base_dir(), os.path.join(self.cfg, ".claude"))
        os.environ["CLAUDE_CONFIG_DIR"] = "~/elsewhere"
        self.assertEqual(S.base_dir(), os.path.join(self.cfg, "elsewhere"))

    def test_paths(self):
        self.assertEqual(S.sensor_path("abc"),
                         os.path.join(self.cfg, "statusline", "sensor", "abc.json"))
        self.assertEqual(S.gauge_path(), os.path.join(self.cfg, *helpers.PUB, "gauge.json"))
        self.assertEqual(S.publisher_state_path("abc"),
                         os.path.join(self.cfg, *helpers.PUB, "abc.json"))


class SafeSid(unittest.TestCase):
    def test_tokens_pass_hostile_hash(self):
        self.assertEqual(S.safe_sid("0c7eafc7-18dc-4274-9add-93aa21324fb3"),
                         "0c7eafc7-18dc-4274-9add-93aa21324fb3")
        self.assertEqual(S.safe_sid(None), "unknown")
        self.assertEqual(S.safe_sid(""), "unknown")
        for bad in ("..", "../x", ".hidden", "a/b", "x" * 129, 123, "é"):
            out = S.safe_sid(bad)
            self.assertTrue(out.startswith("sid-") and len(out) == 36, (bad, out))
        self.assertEqual(S.safe_sid("x" * 128), "x" * 128)


class Thresholds(unittest.TestCase):
    def test_defaults(self):
        t = S.thresholds
        self.assertEqual(t(100_000), {"due": 70_000, "hard": 40_000})
        self.assertEqual(t(200_000), {"due": 70_000, "hard": 40_000})
        self.assertEqual(t(600_000), {"due": 110_000, "hard": 50_000})
        self.assertEqual(t(1_000_000), {"due": 150_000, "hard": 60_000})
        self.assertEqual(t(5_000_000), {"due": 150_000, "hard": 60_000})
        self.assertEqual(t(0), {"due": 70_000, "hard": 40_000})
        self.assertEqual(t(None), {"due": 70_000, "hard": 40_000})
        # truncation, not rounding: 70000 + (1/3)*80000 = 96666.66...
        w = 200_000 + 800_000 // 3
        self.assertEqual(t(w)["due"], int(70_000 + (w - 200_000) / 800_000 * 80_000))

    def test_three_anchors(self):
        a = ((100, 10, 5), (200, 30, 15), (400, 30, 25))
        self.assertEqual(S.thresholds(150, a), {"due": 20, "hard": 10})
        self.assertEqual(S.thresholds(300, a), {"due": 30, "hard": 20})
        self.assertEqual(S.thresholds(200, a), {"due": 30, "hard": 15})
        self.assertEqual(S.thresholds(1, a), {"due": 10, "hard": 5})
        self.assertEqual(S.thresholds(10 ** 9, a), {"due": 30, "hard": 25})

    def test_single_anchor(self):
        self.assertEqual(S.thresholds(5, ((10, 3, 1),)), {"due": 3, "hard": 1})
        self.assertEqual(S.thresholds(50, ((10, 3, 1),)), {"due": 3, "hard": 1})


class Write(helpers.Hermetic):
    EX = {"pct": 1.0, "tokens": 1, "window": 100, "at": 5.0}

    def test_nothing_to_write(self):
        self.assertFalse(S.write_sensor("s"))
        self.assertFalse(S.write_sensor(None, self.EX))
        self.assertFalse(S.write_sensor("", self.EX))
        self.assertEqual(self.all_files(), [])

    def test_merge_both_ways(self):
        self.assertTrue(S.write_sensor("s", exact=self.EX, now=5.0))
        rl = {"five_hour": {"used_percentage": 1.0}, "at": 6.0}
        self.assertTrue(S.write_sensor("s", rate_limits=rl, now=6.0))
        self.assertEqual(self.read_sensor(), {"v": 1, "exact": self.EX, "rate_limits": rl})
        ex2 = dict(self.EX, at=7.0)
        self.assertTrue(S.write_sensor("s", exact=ex2, now=7.0))
        self.assertEqual(self.read_sensor(), {"v": 1, "exact": ex2, "rate_limits": rl})

    def test_older_render_skips(self):
        S.write_sensor("s", exact=dict(self.EX, at=100.0), now=100.0)
        self.assertFalse(S.write_sensor("s", exact=dict(self.EX, at=99.0), now=99.0))
        self.assertEqual(self.read_sensor()["exact"]["at"], 100.0)
        # beyond the slack, the on-disk stamp is garbage, not a newer render
        self.assertTrue(S.write_sensor("s", exact=dict(self.EX, at=30.0), now=30.0))

    def test_failed_replace_leaves_original_and_no_temp(self):
        S.write_sensor("s", exact=self.EX, now=5.0)
        with mock.patch.object(S.os, "replace", side_effect=OSError("boom")):
            self.assertFalse(S.write_sensor("s", exact=dict(self.EX, at=9.0), now=9.0))
        self.assertEqual(self.read_sensor()["exact"]["at"], 5.0)
        self.assertEqual(os.listdir(S.sensor_dir()), ["s.json"])

    def test_read_ignores_other_versions(self):
        for rec in ({"v": 2}, {"v": "1"}, {"v": True}, {}, [1]):
            self.write_json(S.sensor_path("s"), rec)
            self.assertEqual(S.read_sensor("s"), {})
        self.write_json(S.sensor_path("s"), {"v": 1, "x": 1})
        self.assertEqual(S.read_sensor("s"), {"v": 1, "x": 1})


class Publisher(helpers.Hermetic):
    def test_none_without_sid_or_files(self):
        self.assertIsNone(S.publisher(None))
        self.assertIsNone(S.publisher("s"))
        self.publish()
        self.assertIsNone(S.publisher(""))

    def test_active(self):
        self.publish(state={"epoch": 7})
        p = S.publisher("s")
        self.assertEqual(p["anchors"], S.DEFAULT_ANCHORS)
        self.assertEqual(p["labels"], {"due": "checkpoint DUE", "hard": "HARD gate"})
        self.assertEqual(p["epoch"], 7)

    def test_state_file_that_is_a_dir_is_not_proof(self):
        os.makedirs(os.path.join(self.cfg, *helpers.PUB, "s.json"))
        self.publish(state=False)
        self.assertIsNone(S.publisher("s"))

    def test_never_raises(self):
        self.publish()
        with mock.patch.object(S, "_load", side_effect=RuntimeError):
            self.assertIsNone(S.publisher("s"))


if __name__ == "__main__":
    unittest.main()
