"""Standalone vs publisher mode, and the colour rule at its boundaries.

Publisher mode needs BOTH a v1 gauge.json with valid anchors AND this
session's state file in the publisher's dir; anything else is standalone:
default anchors, no epoch, no band word."""
import copy, json, os, time, unittest

import helpers
from helpers import DEFAULT_GAUGE, PUB

GREEN, YELLOW, RED = "\033[32m", "\033[33m", "\033[31m"


def ctx(left, window=1_000_000):
    tok = window - left
    return {"used_percentage": 100.0 * tok / window, "context_window_size": window,
            "total_input_tokens": tok}


def gauge_with(**kw):
    g = copy.deepcopy(DEFAULT_GAUGE)
    for k, v in kw.items():
        if k == "anchors":
            g["thresholds"]["anchors"] = v
        else:
            g[k] = v
    return g


class Standalone(helpers.Hermetic):
    def colour(self, left, window=1_000_000):
        out = self.line({"context_window": ctx(left, window)})
        found = [c for c in (GREEN, YELLOW, RED) if c in out]
        self.assertEqual(len(found), 1, out)
        return found[0], out

    def test_no_epoch_no_words(self):
        out = self.line({})
        self.assertIn("42%  580k left", out)
        self.assertNotIn("e0", out)
        for word in ("DUE", "HARD", "checkpoint", "·  "):
            self.assertNotIn(word, out)

    def test_boundaries_1m_default_anchors(self):
        for left, want in ((150_001, GREEN), (150_000, YELLOW), (60_001, YELLOW),
                           (60_000, RED), (0, RED)):
            c, out = self.colour(left)
            self.assertEqual(c, want, (left, out))
            self.assertNotIn("·", out)

    def test_boundaries_200k_and_between(self):
        for window, left, want in ((200_000, 70_001, GREEN), (200_000, 70_000, YELLOW),
                                   (200_000, 40_000, RED), (100_000, 70_000, YELLOW),
                                   # 600K: due int(70000 + .5*80000) = 110000, hard 50000
                                   (600_000, 110_001, GREEN), (600_000, 110_000, YELLOW),
                                   (600_000, 50_001, YELLOW), (600_000, 50_000, RED),
                                   (2_000_000, 150_001, GREEN)):
            c, out = self.colour(left, window)
            self.assertEqual(c, want, (window, left, out))

    def test_gauge_alone_is_not_enough(self):
        self.publish(state=False)
        out = self.line({})
        self.assertNotIn("e0", out)

    def test_state_alone_is_not_enough(self):
        self.publish(gauge=False)
        self.assertNotIn("e0", self.line({}))

    def test_bad_gauges_mean_standalone(self):
        bads = [gauge_with(v=2), gauge_with(v="1"), gauge_with(v=True), gauge_with(v=1.0),
                {k: v for k, v in DEFAULT_GAUGE.items() if k != "v"},
                gauge_with(anchors=[]),
                gauge_with(anchors=[{"window": 1_000_000, "due": 1.5, "hard": 1}]),
                gauge_with(anchors=[{"window": 0, "due": 1, "hard": 1}]),
                gauge_with(anchors=[{"window": 10, "due": -1, "hard": 1}]),
                gauge_with(anchors=[{"window": 10, "due": True, "hard": 1}]),
                gauge_with(anchors=[{"window": 10, "due": 1, "hard": 1}] * 2),
                gauge_with(anchors=[{"window": 10 + i, "due": 1, "hard": 1}
                                    for i in range(17)]),
                gauge_with(anchors="lots"), gauge_with(anchors=[7]),
                gauge_with(thresholds={"unit": "percent", "anchors":
                                       DEFAULT_GAUGE["thresholds"]["anchors"]}),
                gauge_with(thresholds={"interp": "step", "anchors":
                                       DEFAULT_GAUGE["thresholds"]["anchors"]}),
                gauge_with(thresholds=None), [], "gauge", 7]
        for bad in bads:
            with self.subTest(bad=json.dumps(bad)[:80]):
                self.publish(gauge=bad)
                out = self.line({"context_window": ctx(100_000)})
                self.assertNotIn("e0", out)
                self.assertNotIn("DUE", out)
                self.assertIn(YELLOW, out)  # the default colour for 100K left of 1M

    def test_unreadable_gauge_means_standalone(self):
        for raw in ("{not json", "", "\x00\x01", "x" * (1 << 20 + 1),
                    '{"v": 1, "thresholds": ' + "[" * 5000 + "]" * 5000 + "}"):
            with self.subTest(raw=raw[:20]):
                self.publish(raw_gauge=raw)
                out = self.line({})
                self.assertIn("42%  580k left", out)
                self.assertNotIn("e0", out)

    def test_gauge_dir_is_a_file_or_missing(self):
        os.makedirs(os.path.join(self.cfg, PUB[0]))
        with open(os.path.join(self.cfg, *PUB), "w") as f:
            f.write("x")
        self.assertIn("580k left", self.line({}))


class PublisherMode(helpers.Hermetic):
    def test_epoch_and_labels_at_default_boundaries(self):
        self.publish(state={"epoch": 3, "checkpoint_epoch": 2, "other": [1]})
        for left, colour, word in ((150_001, GREEN, None), (150_000, YELLOW, "checkpoint DUE"),
                                   (60_001, YELLOW, "checkpoint DUE"), (60_000, RED, "HARD gate")):
            out = self.line({"context_window": ctx(left)})
            self.assertIn(colour, out, left)
            self.assertIn(f"k left  e3", out, left)
            if word:
                self.assertIn(f"k left  e3  ·  {word}", out, left)
            else:
                self.assertNotIn("·", out, left)

    def test_default_line(self):
        self.publish()
        self.assertIn("42%  580k left  e0", self.line({}))

    def test_missing_epoch_key_is_zero(self):
        self.publish(state={})
        self.assertIn("580k left  e0", self.line({}))

    def test_non_default_anchors_move_the_boundary(self):
        # Standalone, 580K left of 1M is green; one anchor at due 600K / hard
        # 500K makes it yellow - so the published anchors are what is read.
        self.publish(gauge=gauge_with(anchors=[{"window": 1_000_000, "due": 600_000,
                                                "hard": 500_000}]))
        out = self.line({})
        self.assertIn(YELLOW, out)
        self.assertIn("580k left  e0  ·  checkpoint DUE", out)
        self.publish(gauge=gauge_with(anchors=[{"window": 1_000_000, "due": 700_000,
                                                "hard": 580_000}]))
        self.assertIn("580k left  e0  ·  HARD gate", self.line({}))
        self.assertIn(RED, self.line({}))

    def test_unsorted_anchors_are_sorted(self):
        a = list(reversed(DEFAULT_GAUGE["thresholds"]["anchors"]))
        self.publish(gauge=gauge_with(anchors=a))
        self.assertIn("  ·  checkpoint DUE", self.line({"context_window": ctx(150_000)}))

    def test_labels_come_from_the_file(self):
        self.publish(gauge=gauge_with(labels={"due": "soon", "hard": "now"}))
        self.assertIn("left  e0  ·  soon", self.line({"context_window": ctx(100_000)}))
        self.assertIn("left  e0  ·  now", self.line({"context_window": ctx(10_000)}))

    def test_bad_labels_show_no_word_or_a_clean_one(self):
        for labels, shown in ((None, None), ({"due": 7}, None), ({"due": ""}, None),
                              ({"due": "a\x1b[31m\nb"}, "a [31m b"),
                              ({"due": "\u202eab\u200b"}, "ab"),
                              ({"due": "x" * 100}, "x" * 40)):
            with self.subTest(labels=labels):
                g = gauge_with(labels=labels) if labels is not None else \
                    {k: v for k, v in DEFAULT_GAUGE.items() if k != "labels"}
                self.publish(gauge=g)
                out = self.line({"context_window": ctx(100_000)})
                self.assertEqual(out.count("\n"), 1)
                self.assertIn("left  e0", out)
                if shown:
                    self.assertIn(f"left  e0  ·  {shown}\n", out)
                else:
                    self.assertNotIn("·", out)

    def test_bad_epoch_hides_the_epoch_only(self):
        for state in ({"epoch": "two"}, {"epoch": -1}, {"epoch": True}, {"epoch": 1.5}):
            with self.subTest(state=state):
                self.publish(state=state)
                out = self.line({"context_window": ctx(100_000)})
                self.assertNotRegex(out, r"left  e")
                self.assertIn("left  ·  checkpoint DUE", out)
        self.publish(state=False)
        self.write_json(os.path.join(self.cfg, *PUB, "s.json"), raw="{garbage")
        out = self.line({"context_window": ctx(100_000)})
        self.assertIn("left  ·  checkpoint DUE", out)

    def test_hashed_session_id_names_the_state_file(self):
        import sensor
        sid = "../../evil"
        self.publish(sid=sensor.safe_sid(sid), state={"epoch": 4})
        out = self.line({"session_id": sid})
        self.assertIn("580k left  e4", out)
        self.assertFalse(os.path.exists(os.path.join(self.cfg, "..", "evil.json")))

    def test_another_sessions_state_does_not_count(self):
        self.publish(sid="other")
        self.assertNotIn("e0", self.line({}))

    def test_publisher_files_are_never_written(self):
        self.publish(state={"epoch": 2})
        d = os.path.join(self.cfg, *PUB)

        def snap():
            out = {}
            for n in os.listdir(d):
                with open(os.path.join(d, n), "rb") as f:
                    out[n] = (os.stat(os.path.join(d, n)).st_mtime_ns, f.read())
            return out
        before = snap()
        for left in (500_000, 100_000, 10_000):
            self.line({"context_window": ctx(left), "rate_limits": {
                "five_hour": {"used_percentage": 5, "resets_at": time.time() + 3600}}})
        self.assertEqual(snap(), before)


if __name__ == "__main__":
    unittest.main()
