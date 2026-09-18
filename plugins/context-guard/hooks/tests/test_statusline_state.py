"""The status line's state record: `rate_limits` is written next to `exact` for
librarian-mode's fable-unavailable fallback, and a bad numeric field degrades
the gauge to "ctx --" instead of blanking the line.

Each case runs statusline.py as a subprocess, the way Claude Code runs it, with
CLAUDE_CONFIG_DIR pointed at a temp dir, then reads the state file back."""
import json, os, subprocess, sys, tempfile, time, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTX = {"used_percentage": 42.0, "context_window_size": 1_000_000,
       "total_input_tokens": 420_000}


class StateRecord(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = os.path.join(self.tmp.name, "claude-kit", "context-gate", "s.json")

    def tearDown(self):
        self.tmp.cleanup()

    def run_line(self, payload, raw=None):
        payload.setdefault("session_id", "s")
        payload.setdefault("model", {"display_name": "Fable"})
        payload.setdefault("context_window", dict(CTX))
        env = dict(os.environ, CLAUDE_CONFIG_DIR=self.tmp.name)
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "statusline.py")],
                           input=raw if raw is not None else json.dumps(payload),
                           capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stderr, "")
        return p.stdout

    def read_state(self):
        if not os.path.exists(self.state):
            return None
        with open(self.state) as f:
            return json.load(f)

    def seed(self, st):
        os.makedirs(os.path.dirname(self.state), exist_ok=True)
        with open(self.state, "w") as f:
            json.dump(st, f)

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
        self.seed({"exact": exact, "epoch": 3})
        now = time.time()
        self.run_line({"context_window": {}, "rate_limits": {
            "five_hour": {"used_percentage": 50, "resets_at": now + 60}}})
        st = self.read_state()
        self.assertEqual(st["exact"], exact)
        self.assertEqual(st["epoch"], 3)
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
        self.assertIn("42%  580k left  e0", out)

    def test_bad_epoch_in_state_does_not_blank_line(self):
        self.seed({"epoch": "two"})
        out = self.run_line({})
        self.assertIn("[Fable]", out)
        self.assertIn("ctx --", out)

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


if __name__ == "__main__":
    unittest.main()
