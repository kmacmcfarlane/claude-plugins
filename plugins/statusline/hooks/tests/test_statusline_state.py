"""The sensor record: `exact` and `rate_limits` written to
<cfg>/statusline/sensor/<sid>.json (v1) on each render, merged with what is
there, and a bad numeric field degrading the gauge to "ctx --" instead of
blanking the line.

Each case runs statusline.py as a subprocess, the way Claude Code runs it,
with CLAUDE_CONFIG_DIR and HOME pointed at a temp dir, then reads the record
back."""
import json, os, stat, subprocess, sys, time, unittest

import helpers

CTX = helpers.CTX


class StateRecord(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        self.state = self.sensor_file("s")

    def run_line(self, payload, raw=None):
        rc, out, err = self.render(payload, raw=raw)
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")
        return out

    def read_state(self):
        return self.read_sensor("s")

    def seed(self, st):
        self.write_json(self.state, st)

    # -- shape -----------------------------------------------------------

    def test_rate_limits_written_with_shape(self):
        now = time.time()
        five, seven = now + 3600, now + 3 * 86400
        self.run_line({"rate_limits": {
            "five_hour": {"used_percentage": 23.5, "resets_at": five},
            "seven_day": {"used_percentage": 91, "resets_at": int(seven)}}})
        st = self.read_state()
        rl = st["rate_limits"]
        self.assertEqual(set(rl), {"five_hour", "seven_day", "at"})
        self.assertEqual(rl["five_hour"], {"used_percentage": 23.5, "resets_at": five})
        self.assertEqual(rl["seven_day"], {"used_percentage": 91.0,
                                           "resets_at": float(int(seven))})
        self.assertIsInstance(rl["seven_day"]["used_percentage"], float)
        self.assertAlmostEqual(rl["at"], now, delta=60)
        # exact is written in the same render, same timestamp
        self.assertEqual(st["exact"]["pct"], 42.0)
        self.assertEqual(st["exact"]["at"], rl["at"])

    def test_every_window_kept_under_its_own_name(self):
        now = time.time()
        self.run_line({"rate_limits": {
            "five_hour": {"used_percentage": 1, "resets_at": now + 60},
            "seven_day_opus": {"used_percentage": 99, "resets_at": now + 86400},
            "spend_limit": {"used_percentage": 5, "resets_at": now + 7200}}})
        rl = self.read_state()["rate_limits"]
        self.assertEqual(set(rl), {"five_hour", "seven_day_opus", "spend_limit", "at"})
        self.assertEqual(rl["seven_day_opus"]["used_percentage"], 99.0)

    def test_only_numeric_fields_and_safe_names(self):
        now = time.time()
        self.run_line({"rate_limits": {
            "five_hour": {"used_percentage": 10, "resets_at": now + 60,
                          "label": "free text", "extra": {"x": 1}},
            "Bad Name\n": {"used_percentage": 1, "resets_at": now + 60},
            "x" * 41: {"used_percentage": 1, "resets_at": now + 60},
            "at": {"used_percentage": 1, "resets_at": now + 60},
            "seven_day": {"used_percentage": "abc", "resets_at": now + 60},
            "spend_limit": {"used_percentage": True, "resets_at": "soon"},
            "ms_window": {"used_percentage": 3, "resets_at": (now + 60) * 1000}}})
        rl = self.read_state()["rate_limits"]
        self.assertEqual(set(rl), {"five_hour", "seven_day", "ms_window", "at"})
        self.assertEqual(set(rl["five_hour"]), {"used_percentage", "resets_at"})
        self.assertEqual(rl["seven_day"], {"resets_at": now + 60})
        self.assertEqual(rl["ms_window"], {"used_percentage": 3.0})
        self.assertIsInstance(rl["at"], float)

    def test_past_reset_is_kept(self):
        past = time.time() - 60
        self.run_line({"rate_limits": {"five_hour": {"used_percentage": 100,
                                                     "resets_at": past}}})
        self.assertEqual(self.read_state()["rate_limits"]["five_hour"]["resets_at"], past)

    # -- nothing to write ------------------------------------------------

    def test_missing_or_bad_rate_limits_write_nothing(self):
        bads = [None, [], "x", 5, True, {}, {"five_hour": None},
                {"five_hour": "90%"}, {"five_hour": {}},
                {"five_hour": {"used_percentage": "abc", "resets_at": None}},
                {"five_hour": {"used_percentage": float("nan")}},
                {"seven_day": {"resets_at": "Infinity"}}]
        for bad in bads:
            with self.subTest(bad=bad):
                payload = {"context_window": None}
                if bad is not None:
                    payload["rate_limits"] = bad
                out = self.run_line(payload)
                self.assertIn("ctx --", out)
                self.assertIsNone(self.read_state())

    def test_bad_rate_limits_leave_exact_alone(self):
        self.run_line({"rate_limits": {"five_hour": "x"}})
        st = self.read_state()
        self.assertNotIn("rate_limits", st)
        self.assertEqual(st["exact"]["window"], 1_000_000)

    def test_no_session_id_writes_nothing(self):
        now = time.time()
        for sid in (None, 7, ["s"]):
            with self.subTest(sid=sid):
                self.run_line({"session_id": sid, "rate_limits": {
                    "five_hour": {"used_percentage": 1, "resets_at": now + 60}}})
                self.assertIsNone(self.read_state())

    # -- preserving what is there ----------------------------------------

    def test_existing_exact_preserved_when_only_limits_arrive(self):
        exact = {"pct": 12.0, "tokens": 120_000, "window": 1_000_000, "at": 1.0}
        self.seed({"v": 1, "exact": exact})
        now = time.time()
        self.run_line({"context_window": {}, "rate_limits": {
            "five_hour": {"used_percentage": 50, "resets_at": now + 60}}})
        st = self.read_state()
        self.assertEqual(st["exact"], exact)
        self.assertEqual(st["v"], 1)
        self.assertEqual(st["rate_limits"]["five_hour"]["used_percentage"], 50.0)

    def test_stored_limits_survive_a_render_without_them(self):
        now = time.time()
        self.run_line({"rate_limits": {
            "five_hour": {"used_percentage": 50, "resets_at": now + 60}}})
        first = self.read_state()["rate_limits"]
        self.run_line({})
        st = self.read_state()
        self.assertEqual(st["rate_limits"], first)
        self.assertIn("exact", st)

    # -- bad numeric fields in the gauge ---------------------------------

    def test_bad_pct_gives_ctx_dashes_rest_intact(self):
        now = time.time()
        for bad in ("abc", True, [], {}, "NaN", "inf"):
            with self.subTest(bad=bad):
                ctx = dict(CTX, used_percentage=bad)
                out = self.run_line({
                    "context_window": ctx, "model": {"display_name": "Fable"},
                    "workspace": {"current_dir": "/w/proj"},
                    "session_name": "my session",
                    "rate_limits": {"five_hour": {"used_percentage": 20,
                                                  "resets_at": now + 3600}}})
                self.assertEqual(out.count("\n"), 1)
                self.assertIn("[Fable] proj", out)
                self.assertIn("(my session)", out)
                self.assertIn("ctx --", out)
                self.assertIn("5h ", out)
                st = self.read_state()
                self.assertNotIn("exact", st)
                self.assertIn("rate_limits", st)

    def test_bad_size_or_tokens_give_ctx_dashes(self):
        for field in ("context_window_size", "total_input_tokens"):
            with self.subTest(field=field):
                out = self.run_line({"context_window": dict(CTX, **{field: "lots"})})
                self.assertIn("[Fable]", out)
                self.assertIn("ctx --", out)
                self.assertIsNone(self.read_state())

    def test_numeric_string_pct_still_renders(self):
        out = self.run_line({"context_window": dict(CTX, used_percentage="42")})
        self.assertIn("42%  580k left", out)
        self.assertNotIn("e0", out)

    def test_bad_or_foreign_record_on_disk_is_replaced(self):
        for raw in ("{garbage", "[]", json.dumps({"v": 2, "exact": {"at": 9e99}}),
                    json.dumps({"exact": {"pct": 1}})):
            with self.subTest(raw=raw):
                os.makedirs(os.path.dirname(self.state), exist_ok=True)
                with open(self.state, "w") as f:
                    f.write(raw)
                out = self.run_line({})
                self.assertIn("[Fable]", out)
                self.assertIn("42%  580k left", out)
                st = self.read_state()
                self.assertEqual(st["v"], 1)
                self.assertEqual(st["exact"]["window"], 1_000_000)

    # -- bounds ----------------------------------------------------------

    def test_window_cap_keeps_first_sixteen_valid_in_payload_order(self):
        now = time.time()
        limits = {}
        for i in range(100):
            # every tenth is invalid, so the cap counts stored windows only
            v = "bad" if i % 10 == 0 else i
            limits[f"w{i:03d}"] = {"used_percentage": v, "resets_at": "x" if v == "bad" else now + 60}
        expected = [f"w{i:03d}" for i in range(100) if i % 10][:16]
        for _ in range(2):
            self.run_line({"rate_limits": limits})
            rl = self.read_state()["rate_limits"]
            self.assertEqual([k for k in rl if k != "at"], expected)
        self.assertEqual(expected[0], "w001")
        self.assertEqual(expected[-1], "w017")

    def test_huge_integer_does_not_blank_the_line(self):
        now = float(int(time.time()))
        huge = "9" * 400  # a JSON integer too large for a float: OverflowError
        raw = ('{"session_id": "s", "model": {"display_name": "Fable"},'
               ' "context_window": {"used_percentage": %s, "context_window_size": 1000000,'
               ' "total_input_tokens": 1},'
               ' "rate_limits": {"five_hour": {"used_percentage": %s, "resets_at": %f},'
               ' "seven_day": {"used_percentage": 50, "resets_at": %s},'
               ' "spend_limit": {"used_percentage": 5, "resets_at": %f}}}'
               % (huge, huge, now + 3600, huge, now + 7200))
        out = self.run_line({}, raw=raw)
        self.assertEqual(out.count("\n"), 1)
        self.assertIn("[Fable]", out)
        self.assertIn("ctx --", out)
        self.assertNotIn("5h ", out)
        self.assertNotIn("7d ", out)
        self.assertIn("$ ", out)
        rl = self.read_state()["rate_limits"]
        self.assertEqual(rl["five_hour"], {"resets_at": now + 3600})
        self.assertEqual(rl["seven_day"], {"used_percentage": 50.0})

    def test_pct_clamped_to_0_100(self):
        for raw_pct, shown, stored in ((1e300, "100%", 100.0), (-5, "0%", 0.0)):
            with self.subTest(pct=raw_pct):
                out = self.run_line({"context_window": dict(CTX, used_percentage=raw_pct)})
                self.assertIn(f" {shown}  580k left", out)
                self.assertLess(len(out), 400)
                self.assertEqual(self.read_state()["exact"]["pct"], stored)

    def test_nonpositive_or_fractional_size_is_unknown(self):
        # A size in (0, 1) passed the old `<= 0` check and int() made it 0.
        for size in (0, -5, -1e9, 0.5, 0.999):
            with self.subTest(size=size):
                out = self.run_line({"context_window": dict(CTX, context_window_size=size)})
                self.assertIn("[Fable]", out)
                self.assertIn("ctx --", out)
                self.assertIsNone(self.read_state())

    def test_unparsable_stdin_still_one_line(self):
        out = self.run_line({}, raw="{not json")
        self.assertEqual(out, "\n")
        self.assertIsNone(self.read_state())


    # -- the file itself ---------------------------------------------------

    def test_record_is_v1_private_and_nothing_else_is_written(self):
        self.run_line({"rate_limits": {"five_hour": {"used_percentage": 1,
                                                     "resets_at": time.time() + 60}}})
        st = self.read_state()
        self.assertEqual(set(st), {"v", "exact", "rate_limits"})
        self.assertIs(type(st["v"]), int)
        self.assertEqual(stat.S_IMODE(os.stat(self.state).st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(self.state)).st_mode), 0o700)
        self.assertEqual(self.all_files(), [self.state])
        self.assertFalse(os.path.exists(os.path.join(self.cfg, "claude-kit")))

    def test_at_is_stamped_when_the_payload_is_read(self):
        before = time.time()
        self.run_line({})
        at = self.read_state()["exact"]["at"]
        self.assertGreaterEqual(at, before)
        self.assertLessEqual(at, time.time())

    def test_a_newer_record_on_disk_is_not_regressed(self):
        future = time.time() + 30  # a render that read its payload after ours
        newer = {"pct": 1.0, "tokens": 10_000, "window": 1_000_000, "at": future}
        self.seed({"v": 1, "exact": newer})
        self.run_line({})
        self.assertEqual(self.read_state()["exact"], newer)

    def test_a_far_future_record_does_not_block_writes(self):
        self.seed({"v": 1, "exact": {"pct": 1.0, "tokens": 1, "window": 1_000_000,
                                     "at": time.time() + 86400}})
        self.run_line({})
        self.assertEqual(self.read_state()["exact"]["tokens"], 420_000)

    def test_unknown_keys_are_not_carried(self):
        self.seed({"v": 1, "junk": "x" * 100})
        self.run_line({})
        self.assertNotIn("junk", self.read_state())

    def test_traversal_session_id_writes_inside(self):
        import sensor
        sid = "../../evil"
        self.run_line({"session_id": sid})
        self.assertFalse(os.path.exists(os.path.join(self.cfg, "..", "evil.json")))
        for f in self.all_files():
            self.assertTrue(os.path.relpath(f, self.cfg).startswith(
                os.path.join("statusline", "sensor")), f)
        self.assertEqual(self.read_sensor(sensor.safe_sid(sid))["exact"]["window"], 1_000_000)

    def test_no_temp_files_left_behind(self):
        for _ in range(3):
            self.run_line({})
        names = os.listdir(os.path.dirname(self.state))
        self.assertEqual(names, ["s.json"])

    def test_unwritable_dir_still_renders(self):
        os.makedirs(os.path.join(self.cfg, "statusline"))
        with open(os.path.join(self.cfg, "statusline", "sensor"), "w") as f:
            f.write("not a dir")
        out = self.run_line({})
        self.assertIn("42%  580k left", out)


if __name__ == "__main__":
    unittest.main()
