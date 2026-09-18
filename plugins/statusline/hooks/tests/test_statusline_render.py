"""The rendered line, standalone (no gauge publisher): usage bars, clamping,
countdowns, the session-name chain and its sanitising. Ported from the
earlier in-repo copy's suite; standalone lines carry no epoch and no band
word, so "42%  580k left" ends the gauge."""
import json, os, subprocess, sys, time, unittest

import helpers

HOOKS = helpers.HOOKS


class Render(helpers.Hermetic):
    CTX = {"used_percentage": 42.0, "context_window_size": 1_000_000,
           "total_input_tokens": 420_000}

    def line(self, payload):
        return self.render(payload)

    def test_plan_usage_bars_both_windows(self):
        now = time.time()
        rc, line, _ = self.line({"rate_limits": {
            "five_hour": {"used_percentage": 23.5, "resets_at": now + 2 * 3600 + 600},
            "seven_day": {"used_percentage": 91.2, "resets_at": now + 3 * 86400}}})
        self.assertEqual(rc, 0)
        self.assertEqual(line.count("\n"), 1)
        self.assertIn("[Fable]", line)
        self.assertIn("42%  580k left", line)
        self.assertIn("5h \033[32m██░░░░░░░░\033[0m 23% resets 2h10m", line)
        self.assertIn("7d \033[31m█████████░\033[0m 91% resets 3d", line)
        self.assertLess(line.index("580k left"), line.index("5h "))
        self.assertLess(line.index("5h "), line.index("7d "))

    def test_no_bars_without_rate_limits(self):
        rc, line, _ = self.line({})
        self.assertEqual(rc, 0)
        self.assertNotIn("resets", line)
        self.assertIn("42%  580k left", line)
        rc, line, _ = self.line({"rate_limits": {}})
        self.assertEqual((rc, "resets" in line), (0, False))

    def test_window_with_past_reset_is_absent(self):
        now = time.time()
        rc, line, _ = self.line({"rate_limits": {
            "five_hour": {"used_percentage": 99.0, "resets_at": now - 60},
            "seven_day": {"used_percentage": 75.0, "resets_at": now + 86400}}})
        self.assertEqual(rc, 0)
        self.assertNotIn("5h ", line)
        self.assertIn("7d \033[33m███████░░░\033[0m 75% resets 1d", line)

    def test_malformed_rate_limits_do_not_crash(self):
        for bad in ("garbage", 7, ["five_hour"],
                    {"five_hour": "x", "seven_day": {"used_percentage": "no",
                                                     "resets_at": None}},
                    {"five_hour": {"used_percentage": 12.0}}):
            rc, line, err = self.line({"rate_limits": bad})
            self.assertEqual((rc, err), (0, ""), bad)
            self.assertNotIn("resets", line)
            self.assertIn("42%  580k left", line)

    def test_non_finite_and_bool_fields_are_skipped(self):
        now = time.time()
        for bad in ({"used_percentage": 5.0, "resets_at": float("nan")},
                    {"used_percentage": 5.0, "resets_at": float("inf")},
                    {"used_percentage": float("nan"), "resets_at": now + 100},
                    {"used_percentage": float("inf"), "resets_at": now + 100},
                    {"used_percentage": True, "resets_at": now + 100},
                    {"used_percentage": 5.0, "resets_at": True}):
            rc, line, err = self.line({"rate_limits": {
                "five_hour": bad,
                "seven_day": {"used_percentage": 1.0, "resets_at": now + 100}}})
            self.assertEqual((rc, err), (0, ""), bad)
            self.assertNotIn("5h ", line)
            self.assertIn("7d ", line)

    def test_reset_too_far_out_is_dropped(self):
        now = time.time()
        rc, line, err = self.line({"rate_limits": {
            "five_hour": {"used_percentage": 5.0, "resets_at": (now + 7200) * 1000},
            "seven_day": {"used_percentage": 5.0, "resets_at": now + 367 * 86400},
            "spend_limit": {"used_percentage": 5.0, "resets_at": now + 365 * 86400}}})
        self.assertEqual((rc, err), (0, ""))
        self.assertNotIn("5h ", line)
        self.assertNotIn("7d ", line)
        self.assertIn("$ \033[32m░░░░░░░░░░\033[0m 5% resets 365d", line)

    def test_spend_limit_is_third(self):
        now = time.time()
        rc, line, _ = self.line({"rate_limits": {
            "spend_limit": {"used_percentage": 10.0, "resets_at": now + 86400},
            "seven_day": {"used_percentage": 20.0, "resets_at": now + 86400},
            "five_hour": {"used_percentage": 30.0, "resets_at": now + 86400}}})
        self.assertEqual(rc, 0)
        self.assertIn("$ \033[32m█░░░░░░░░░\033[0m 10% resets 1d", line)
        self.assertLess(line.index("5h "), line.index("7d "))
        self.assertLess(line.index("7d "), line.index("$ "))
        self.assertEqual(line.count("resets"), 3)

    def test_clamping_and_threshold_boundaries(self):
        now = time.time()
        for used, want in ((150.0, "\033[31m██████████\033[0m 100%"),
                           (-5.0, "\033[32m░░░░░░░░░░\033[0m 0%"),
                           (69.9, "\033[32m██████░░░░\033[0m 69%"),
                           (70.0, "\033[33m███████░░░\033[0m 70%"),
                           (89.9, "\033[33m████████░░\033[0m 89%"),
                           (90.0, "\033[31m█████████░\033[0m 90%")):
            rc, line, _ = self.line({"rate_limits": {
                "five_hour": {"used_percentage": used, "resets_at": now + 100}}})
            self.assertEqual(rc, 0)
            self.assertIn("5h " + want, line, used)

    def test_countdown_rounds_up_to_the_minute(self):
        now = time.time()
        for ahead, want in ((59, "1m"), (60, "1m"), (90, "2m"),
                            (3600 + 5 * 60, "1h05m"), (3600, "1h"),
                            (86400 + 3600, "1d1h"), (2 * 86400, "2d")):
            rc, line, _ = self.line({"rate_limits": {
                "five_hour": {"used_percentage": 1.0, "resets_at": now + ahead}}})
            self.assertEqual(rc, 0)
            self.assertIn(f"1% resets {want}", line, ahead)

    def test_exact_sensor_record_still_written(self):
        rc, _, _ = self.line({"rate_limits": {
            "five_hour": {"used_percentage": 5.0, "resets_at": time.time() + 100}}})
        self.assertEqual(rc, 0)
        ex = self.read_sensor()["exact"]
        self.assertEqual((ex["pct"], ex["tokens"], ex["window"]),
                         (42.0, 420_000, 1_000_000))

    # The statusline is our direct child, so its parent pid is this process:
    # a registry entry at sessions/<our pid>.json is what it finds first. Our
    # own parent is its grandparent, one /proc hop up the ancestor walk.
    def registry(self, body, sid="s", pid=None):
        pid = os.getpid() if pid is None else pid
        d = os.path.join(self.tmp.name, "sessions")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, f"{pid}.json")
        if isinstance(body, str):
            with open(p, "w") as f:
                f.write(body)
        else:
            entry = {"pid": pid, "sessionId": sid, "name": "beta",
                     "nameSource": "peer"}
            entry.update(body)
            with open(p, "w") as f:
                json.dump(entry, f)

    def grandparent(self):
        if not os.path.isdir("/proc") or os.getppid() <= 1:
            self.skipTest("ancestor walk needs /proc and a real parent")
        return os.getppid()

    def line_via_shell(self, payload):
        """Run the hook through `sh -c` so the real chain has depth 2."""
        payload.setdefault("session_id", "s")
        payload.setdefault("context_window", dict(self.CTX))
        payload.setdefault("model", {"display_name": "Fable"})
        e = dict(self.env)
        p = subprocess.run(["sh", "-c", f'"$0" "$1"', sys.executable,
                            os.path.join(HOOKS, "statusline.py")],
                           input=json.dumps(payload), capture_output=True,
                           text=True, env=e, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def test_payload_session_name_shown(self):
        rc, line, err = self.line({"session_name": "alpha"})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (alpha)  ", line)

    def test_registry_name_when_payload_has_none(self):
        self.registry({})
        for payload in ({}, {"session_name": ""}, {"session_name": "   "},
                        {"session_name": None}, {"session_name": 7}):
            rc, line, err = self.line(dict(payload))
            self.assertEqual((rc, err), (0, ""), payload)
            self.assertIn("  (beta)  ", line, payload)

    def test_no_name_segment_without_any_source(self):
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertNotIn("(", line)
        self.assertTrue(line.startswith("[Fable]   "), line)

    def test_malformed_registry_does_not_crash(self):
        for bad in ("{not json", "", "[]", '"beta"', json.dumps({"name": "beta"}),
                    json.dumps({"sessionId": "s", "name": 7}),
                    json.dumps({"sessionId": "s", "name": "  "}),
                    json.dumps({"sessionId": "s"}), "x" * 70000):
            self.registry(bad)
            rc, line, err = self.line({})
            self.assertEqual((rc, err), (0, ""), bad[:40])
            self.assertNotIn("(", line, bad[:40])
            self.assertIn("42%  580k left", line)

    def test_registry_explicit_name_wins_over_payload_title(self):
        # /rename and an agent naming itself land in the registry first; the
        # payload lags (next render) or carries only the AI title.
        for src in ("user", "peer", "hook", "collision"):
            self.registry({"name": "set-by-" + src, "nameSource": src})
            rc, line, err = self.line({"session_name": "AI title"})
            self.assertEqual((rc, err), (0, ""), src)
            self.assertIn(f"  (set-by-{src})  ", line, src)
            self.assertNotIn("AI title", line, src)

    def test_registry_auto_name_is_skipped_for_payload_title(self):
        self.registry({"name": "hooks-3f", "nameSource": "auto"})
        rc, line, err = self.line({"session_name": "AI title"})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (AI title)  ", line)
        self.assertNotIn("hooks-3f", line)

    def test_registry_entry_for_another_session_is_ignored(self):
        self.registry({}, sid="someone-else")
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertNotIn("(", line)

    def test_derived_and_auto_default_names_are_never_shown(self):
        for src in ("derived", "auto", None, "bogus"):
            self.registry({"name": "hooks-3f", "nameSource": src})
            rc, line, err = self.line({})
            self.assertEqual((rc, err), (0, ""), src)
            self.assertNotIn("(", line, src)

    # -- names are sanitised to one printable line, whatever the source --

    HOSTILE = "ev\x1b[31mil\nsecond\x07 line\x7f\x85end"

    def test_registry_name_with_control_chars_stays_one_line(self):
        self.registry({"name": self.HOSTILE, "nameSource": "user"})
        rc, line, err = self.line({"session_name": "AI title"})
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(line.count("\n"), 1, repr(line))  # only the trailing one
        self.assertIn("  (ev [31mil second line end)  ", line)
        self.assertNotIn("AI title", line)

    def test_payload_name_with_control_chars_stays_one_line(self):
        rc, line, err = self.line({"session_name": self.HOSTILE})
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(line.count("\n"), 1, repr(line))
        self.assertIn("  (ev [31mil second line end)  ", line)

    def test_each_control_char_collapses_to_one_space(self):
        for raw, shown in (("a\x1bb", "a b"), ("a\nb", "a b"), ("a\x07b", "a b"),
                           ("a\x1b[0m\r\n\tb", "a [0m b"), ("a\x7f\x9fb", "a b"),
                           ("  a   b  ", "a b"), ("\x1b\x07\n", "")):
            self.registry({"name": raw, "nameSource": "user"})
            rc, line, err = self.line({})
            self.assertEqual((rc, err), (0, ""), repr(raw))
            if shown:
                self.assertIn(f"  ({shown})  ", line, repr(raw))
            else:
                self.assertNotIn("(", line, repr(raw))
            rc, line, err = self.line({"session_name": raw})
            self.assertEqual((rc, err), (0, ""), repr(raw))
            if shown:
                self.assertIn(f"  ({shown})  ", line, repr(raw))
            else:
                self.assertNotIn("(", line, repr(raw))

    def test_long_names_are_capped_with_an_ellipsis(self):
        long = "n" * 100
        for src in ("registry", "payload"):
            if src == "registry":
                self.registry({"name": long, "nameSource": "user"})
                rc, line, err = self.line({})
            else:
                rc, line, err = self.line({"session_name": long})
            self.assertEqual((rc, err), (0, ""), src)
            self.assertIn("  (" + "n" * 59 + "\u2026)  ", line, src)
            self.assertNotIn("n" * 60, line, src)
        self.registry({"name": "n" * 60, "nameSource": "user"})
        rc, line, _ = self.line({})
        self.assertIn("  (" + "n" * 60 + ")  ", line)  # exactly NAME_MAX is untouched

    # -- the ancestor walk: nearest entry for this session wins --

    def test_registry_match_at_the_grandparent(self):
        self.registry({}, pid=self.grandparent())
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (beta)  ", line)

    def test_walk_continues_past_a_parent_entry_for_another_session(self):
        self.registry({"name": "not-ours", "nameSource": "user"}, sid="someone-else")
        self.registry({}, pid=self.grandparent())
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (beta)  ", line)
        self.assertNotIn("not-ours", line)

    def test_nearest_matching_entry_wins(self):
        self.registry({"name": "near", "nameSource": "user"})
        self.registry({"name": "far", "nameSource": "user"}, pid=self.grandparent())
        rc, line, err = self.line({})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (near)  ", line)
        self.assertNotIn("far", line)

    def test_nearer_auto_entry_stops_the_walk_for_the_payload_title(self):
        self.registry({"name": "hooks-3f", "nameSource": "auto"})
        self.registry({"name": "far", "nameSource": "user"}, pid=self.grandparent())
        rc, line, err = self.line({"session_name": "AI title"})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (AI title)  ", line)
        self.assertNotIn("far", line)
        self.assertNotIn("hooks-3f", line)

    def test_walk_reaches_the_session_through_an_intermediate_shell(self):
        # sh -c between us and the hook: our entry is now at its grandparent.
        if not os.path.isdir("/proc"):
            self.skipTest("ancestor walk needs /proc")
        self.registry({})
        rc, line, err = self.line_via_shell({"session_name": "AI title"})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (beta)  ", line)
        self.assertNotIn("AI title", line)


if __name__ == "__main__":
    unittest.main()
