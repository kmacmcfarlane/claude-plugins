"""Parity with the gauge publisher's own copy of the contract (see
skills/install-statusline/references/sensor-contract.md).

Runs only in the source repo, where the publisher plugin sits beside this one
(plugins/<publisher>/hooks/lib_context.py); an installed copy of this plugin
skips it. Its module is loaded from its file under a private name, so nothing
else of that plugin is importable here."""
import importlib.util, json, os, subprocess, sys, time, unittest

import helpers
import sensor as S

LIB = os.path.join(os.path.dirname(helpers.PLUGIN), "context-guard", "hooks", "lib_context.py")


def load_lib():
    spec = importlib.util.spec_from_file_location("publisher_lib_context", LIB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@unittest.skipUnless(os.path.isfile(LIB), "publisher plugin not beside this one")
class Contract(helpers.Hermetic):
    @classmethod
    def setUpClass(cls):
        cls.L = load_lib()

    CORPUS = ["0c7eafc7-18dc-4274-9add-93aa21324fb3", "s", "child_3.x", "A-b_c.d",
              "..", ".", "../../evil", "a/b", "a\\b", ".hidden", "-lead", "_lead",
              "x" * 128, "x" * 129, "", None, 0, 123, 1.5, ["s"], {"a": 1}, b"s",
              "été", "中", "a b", "a\nb", "\ud800", "sid-abc"]

    def test_safe_sid_parity(self):
        for sid in self.CORPUS:
            self.assertEqual(S.safe_sid(sid), self.L.safe_sid(sid), repr(sid))

    def test_paths_agree(self):
        for cfg in (self.cfg, "", None):
            with self.subTest(cfg=cfg):
                if cfg is None:
                    os.environ.pop("CLAUDE_CONFIG_DIR", None)
                else:
                    os.environ["CLAUDE_CONFIG_DIR"] = cfg
                self.assertEqual(S.base_dir(), self.L._base_dir())
                for sid in ("s", "../../evil", None):
                    self.assertEqual(S.sensor_path(sid), self.L.sensor_path(sid))
                    self.assertEqual(S.publisher_state_path(sid), self.L.state_path(sid))
                self.assertEqual(S.gauge_path(), self.L.gauge_path())

    def test_thresholds_agree(self):
        self.assertEqual(S.DEFAULT_ANCHORS, self.L.ANCHORS)
        published = S.parse_anchors(self.L.gauge_record()["thresholds"])
        self.assertEqual(published, tuple(self.L.ANCHORS))
        grid = [0, 1, 99_999, 100_000, 199_999, 200_000, 200_001, 333_333, 500_000,
                600_000, 777_777, 999_999, 1_000_000, 1_000_001, 1_500_000, 2_000_000]
        grid += list(range(100_000, 2_000_001, 12_345))
        for w in grid:
            self.assertEqual(S.thresholds(w), self.L.thresholds(w), w)
            self.assertEqual(S.thresholds(w, published), self.L.thresholds(w), w)

    def test_published_gauge_switches_publisher_mode_on(self):
        self.assertTrue(self.L.publish_gauge())
        self.assertIsNone(S.publisher("s"))           # no state for this session yet
        self.L.save_state("s", {"epoch": 2})
        p = S.publisher("s")
        self.assertEqual(p["anchors"], tuple(self.L.ANCHORS))
        self.assertEqual(p["labels"], self.L.GAUGE_LABELS)
        self.assertEqual(p["epoch"], self.L.epoch(self.L.load_state("s")))

    def show(self, sid, ctx, limits=None):
        payload = {"session_id": sid, "model": {"display_name": "M"}, "context_window": ctx}
        if limits:
            payload["rate_limits"] = limits
        return self.line(payload)

    def test_end_to_end_depth_is_exact(self):
        now = time.time()
        for sid in ("s", "../../evil"):
            with self.subTest(sid=sid):
                self.show(sid, helpers.CTX, {"five_hour": {"used_percentage": 23.5,
                                                              "resets_at": now + 3600}})
                tokens, window, pct, src = self.L.depth("/nonexistent", sid)
                self.assertEqual((tokens, window, pct, src),
                                 (420_000, 1_000_000, 42.0, "exact"))
                rec = self.L.sensor_record(sid)
                self.assertEqual(rec["rate_limits"]["five_hour"],
                                 {"used_percentage": 23.5, "resets_at": now + 3600})
                self.assertEqual(rec["exact"]["at"], rec["rate_limits"]["at"])

    def test_reset_epoch_demotes_an_earlier_record(self):
        self.show("s", helpers.CTX)
        self.L.reset_epoch("s")
        ex = self.L.sensor("s")
        self.assertEqual(ex, {"window": 1_000_000, "at": 0})
        self.assertTrue(self.L.depth("/nonexistent", "s")[3].startswith("inferred"))
        # the reset read the sensor for the ending epoch's fill
        self.assertEqual(self.L.load_state("s")["epoch_end_tokens"], 420_000)
        time.sleep(0.01)
        self.show("s", dict(helpers.CTX, used_percentage=3.0, total_input_tokens=30_000))
        self.assertEqual(self.L.depth("/nonexistent", "s"),
                         (30_000, 1_000_000, 3.0, "exact"))

    def test_render_in_publisher_mode_never_writes_its_state(self):
        self.L.publish_gauge()
        self.L.save_state("s", {"epoch": 1, "checkpoint_epoch": 1})
        before = json.dumps(self.L.load_state("s"), sort_keys=True)
        out = self.show("s", helpers.CTX)
        self.assertIn("580k left  e1", out)
        self.assertEqual(json.dumps(self.L.load_state("s"), sort_keys=True), before)


if __name__ == "__main__":
    unittest.main()
