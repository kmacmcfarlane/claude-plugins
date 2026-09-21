"""hub.py end to end, as Claude Code runs it: payload on stdin, one line out.
The tee always writes the sensor record; display hooks run in parallel under
timeouts with a last-good cache; record hooks get the raw payload byte for
byte, detached; health files add one glyph; nothing a hook does reaches the
terminal except its sanitised first line."""
import json, os, sys, time, unittest

import helpers
import registry as R

PY = sys.executable
GLYPH = "⚠".encode()


def py(code):
    """A hook command running `code` in Python."""
    return [PY, "-c", code]


def wait_for(path, seconds=10):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if os.path.exists(path):
            return True
        time.sleep(0.02)
    return False


class Render(helpers.Hermetic):
    def line(self, payload=None, raw=None):
        rc, out, err, secs = self.hub(payload, raw=raw)
        self.assertEqual((rc, err), (0, b""))
        self.assertTrue(out.endswith(b"\n") and out.count(b"\n") == 1, out)
        return out[:-1], secs

    def test_no_hooks_empty_line_and_the_tee_still_runs(self):
        out, _ = self.line()
        self.assertEqual(out, b"")
        self.assertEqual(self.read_sensor()["exact"]["pct"], 42.0)

    def test_display_hooks_in_order_with_separator(self):
        self.manifest("b", ["echo", "bee"], order=1)
        self.manifest("a", ["echo", "ay"], order=2)
        self.assertEqual(self.line()[0], b"bee  ay")
        self.write_json(R.config_path(), {"order": ["a"], "separator": " | "})
        self.assertEqual(self.line()[0], b"ay | bee")
        self.write_json(R.config_path(), {"disabled": ["b"]})
        self.assertEqual(self.line()[0], b"ay")

    def test_hooks_get_the_payload_and_env(self):
        self.manifest("a", py("import json,os,sys; d=json.load(sys.stdin); "
                              "print(d['session_id'], os.environ['STATUSLINE_HUB'], "
                              "os.environ['STATUSLINE_HUB_KIND'], os.getcwd())"))
        out, _ = self.line({"session_id": "abc"})
        self.assertEqual(out.decode(), f"abc 1 display {os.path.realpath(R.hub_dir())}")

    def test_display_hooks_run_in_parallel(self):
        for n in ("a", "b", "c"):
            self.manifest(n, py(f"import time; time.sleep(0.15); print('{n}')"), timeout_ms=250)
        out, secs = self.line()
        # in series these would take 0.45 s, past the 250 ms budget
        self.assertEqual(out, b"a  b  c")
        self.assertLess(secs, 1.5)

    def test_timeout_shows_last_good_then_drops(self):
        self.manifest("slow", ["echo", "fresh"])
        self.manifest("z", ["echo", "other"])
        self.assertEqual(self.line()[0], b"fresh  other")
        self.manifest("slow", py("import time; print('late', flush=True); time.sleep(5)"),
                      timeout_ms=100)
        out, secs = self.line()
        self.assertEqual(out, b"fresh  other")
        self.assertLess(secs, 2)
        # a last-good entry older than LAST_GOOD_S is not shown
        cache = os.path.join(R.cache_dir(), "slow", "s.json")
        self.write_json(cache, {"at": time.time() - 61, "text": "fresh"})
        self.assertEqual(self.line()[0], b"other")

    def test_failing_hook_never_blanks_the_line(self):
        self.manifest("a", ["echo", "good"])
        self.manifest("b", py("import sys; print('partial'); sys.exit(3)"))
        self.manifest("c", ["/nonexistent/program"])
        self.manifest("d", py("raise SystemExit('boom to stderr')"))
        self.assertEqual(self.line()[0], b"good")
        with open(os.path.join(R.log_dir(), "d.log")) as f:
            self.assertIn("boom to stderr", f.read())

    def test_empty_output_is_nothing_to_show(self):
        self.manifest("a", ["echo", "x"])
        self.assertEqual(self.line()[0], b"x")
        self.manifest("a", ["true"])
        self.assertEqual(self.line()[0], b"")

    def test_output_is_sanitised(self):
        self.manifest("a", py(r"print('\x1b]0;pwned\x07ok \x1b[32mgreen\x1b[0m\x1b[2J"
                              r"‮txt\nline two')"))
        self.assertEqual(self.line()[0].decode(),
                         "ok \x1b[32mgreen\x1b[0mtxt" + R.RESET)

    def test_no_shell_unless_the_manifest_asks(self):
        marker = os.path.join(self.cfg, "pwned")
        self.manifest("a", f"echo a; touch {marker}")
        self.assertEqual(self.line()[0].decode(), f"a; touch {marker}")
        self.assertFalse(os.path.exists(marker))
        self.manifest("a", "echo a | tr a A", shell=True)
        self.assertEqual(self.line()[0], b"A")

    def test_untrusted_manifests_never_run(self):
        marker = os.path.join(self.cfg, "ran")
        if os.geteuid() != 0:
            self.manifest("a", ["touch", marker], mode=0o666)
            self.line()
            self.assertFalse(os.path.exists(marker))
        other = self.manifest("b", ["touch", marker])
        os.rename(other, other + ".real")
        os.symlink(other + ".real", other)
        self.line()
        self.assertFalse(os.path.exists(marker))

    def test_oversized_payload_runs_nothing(self):
        marker = os.path.join(self.cfg, "ran")
        self.manifest("a", ["touch", marker])
        self.manifest("r", ["touch", marker], kind="record")
        out, _ = self.line(raw=b" " * (R.tee.READ_MAX + 1))
        self.assertEqual(out, b"")
        time.sleep(0.3)
        self.assertFalse(os.path.exists(marker))


class Records(helpers.Hermetic):
    def test_raw_payload_byte_for_byte(self):
        got = os.path.join(self.cfg, "got")
        self.manifest("r", py(f"import sys; open({got!r}, 'wb').write(sys.stdin.buffer.read())"),
                      kind="record")
        raw = ('{ "session_id" : "s",\n\t"context_window": {"used_percentage": 1, '
               '"context_window_size": 200000, "total_input_tokens": 2000},'
               ' "x": "café ☃", "z": [1,2 , 3] }  \n').encode()
        rc, out, err, _ = self.hub(raw=raw)
        self.assertEqual((rc, out, err), (0, b"\n", b""))
        self.assertTrue(wait_for(got))
        time.sleep(0.1)
        with open(got, "rb") as f:
            self.assertEqual(f.read(), raw)
        self.assertEqual(self.read_sensor()["exact"]["tokens"], 2000)

    def test_slow_record_hook_never_blocks_the_render(self):
        self.manifest("a", ["echo", "gauge"])
        self.manifest("r", py("import time; time.sleep(8)"), kind="record", timeout_ms=10000)
        rc, out, err, secs = self.hub()
        self.assertEqual((rc, out, err), (0, b"gauge\n", b""))
        self.assertLess(secs, 2)
        self.assertIsNotNone(self.read_sensor())

    def test_crashing_record_hook_leaves_line_and_sensor(self):
        self.manifest("a", ["echo", "gauge"])
        self.manifest("r", py("import os; os.abort()"), kind="record")
        self.manifest("q", ["/nonexistent/program"], kind="record")
        rc, out, err, _ = self.hub()
        self.assertEqual((rc, out, err), (0, b"gauge\n", b""))
        self.assertEqual(self.read_sensor()["exact"]["pct"], 42.0)

    def test_record_hook_killed_at_its_timeout(self):
        pidfile = os.path.join(self.cfg, "pid")
        self.manifest("r", py(f"import os,time; open({pidfile!r},'w').write(str(os.getpid()));"
                              "time.sleep(30)"), kind="record", timeout_ms=200)
        self.hub()
        self.assertTrue(wait_for(pidfile))
        time.sleep(0.1)
        with open(pidfile) as f:
            pid = int(f.read())
        end = time.monotonic() + 5
        while time.monotonic() < end:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            os.kill(pid, 9)
            self.fail("record hook outlived its timeout")


class HealthGlyph(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        self.health = os.path.join(self.cfg, "analytics", "health.json")
        self.manifest("a", ["echo", "gauge"])
        self.manifest("r", ["true"], kind="record", health_path=self.health)

    def test_glyph_only_when_the_hook_says_it_failed(self):
        out = self.hub()[1]
        self.assertEqual(out, b"gauge\n")  # never ran: no health file, no glyph
        now = time.time()
        self.write_json(self.health, {"last_ok": now - 10, "runs": 2})
        self.assertEqual(self.hub()[1], b"gauge\n")
        self.write_json(self.health, {"last_ok": now - 10, "last_error": now, "errors": 1})
        self.assertEqual(self.hub()[1], b"gauge " + GLYPH + b"\n")
        self.write_json(self.health, raw="{garbage")
        self.assertEqual(self.hub()[1], b"gauge\n")

    def test_glyph_alone_when_nothing_else_shows(self):
        self.manifest("a", ["true"])
        self.write_json(self.health, {"last_error": time.time()})
        self.assertEqual(self.hub()[1], GLYPH + b"\n")


class Status(helpers.Hermetic):
    def test_lists_hooks_and_why_any_is_skipped(self):
        self.manifest("a", ["echo"])
        self.manifest("b", ["echo"], kind="nope")
        rc, out, err, _ = self.hub(raw=b"", args=("--status",))
        text = out.decode()
        self.assertEqual((rc, err), (0, b""))
        self.assertIn("a: display, active", text)
        self.assertIn("b: skipped (kind is not display or record)", text)


if __name__ == "__main__":
    unittest.main()
