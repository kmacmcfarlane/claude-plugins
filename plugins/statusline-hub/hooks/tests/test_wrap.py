"""Wrap mode: the hub runs the user's previous statusLine command inside itself,
only on their consent (the installer's --wrap; a first run only asks), and
--unwrap puts the entry back byte for byte. Covers the render (output shown,
sensor record still written, a failing or hanging command costing only its
own output), the wrap record's trust rules, and the interplay with heal,
yield, remove and a stale session's settings write-back. Hermetic;
everything runs as a subprocess, the way Claude Code runs it."""
import json, os, stat, subprocess, sys, time, unittest

import helpers
import owner
import registry

SCRIPT = os.path.join(helpers.PLUGIN, "skills", "install-statusline-hub", "scripts",
                      "install_hub.py")
HOOK = os.path.join(helpers.HOOKS, "session_start.py")
TOKEN = "SECRETISH"  # in every foreign command: no message may print it
ROOT_SKIP = unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes anything")

# A hand-formatted user settings file: one-line nested object, odd spacing,
# escapes in the command. Unwrap must give these exact bytes back.
ODD = ('{\n  "model": "opus",\n  "statusLine":   {"type":"command", "command": '
       '"bash ~/bin/my\\tprompt.sh --tag \\"%s\\" \\u00e9", "padding": 0},\n'
       '    "enabledPlugins": {"statusline-hub@kmacmcfarlane": true},\n  "z": [1, 2]\n}\n'
       % TOKEN)


class Base(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        self.data = os.path.join(self.cfg, "plugins", "data", "statusline-hub-kmacmcfarlane")
        self.env["CLAUDE_PLUGIN_DATA"] = self.data
        self.env["CLAUDE_PLUGIN_ROOT"] = helpers.PLUGIN
        self.proj = os.path.join(self.cfg, "proj")
        os.makedirs(self.proj)
        self.env["CLAUDE_PROJECT_DIR"] = self.proj
        self.user = os.path.join(self.cfg, "settings.json")
        self.outputs = []

    def tearDown(self):
        for out in self.outputs:
            self.assertNotIn(TOKEN, out)  # paths and keys only, never values
        super().tearDown()

    def run_it(self, *args, cwd=None):
        p = subprocess.run([sys.executable, SCRIPT, *args], env=self.env, cwd=cwd or self.proj,
                           capture_output=True, text=True, timeout=30)
        self.outputs.append(p.stdout + p.stderr)
        return p.returncode, p.stdout + p.stderr

    def hook(self):
        p = subprocess.run([sys.executable, HOOK], cwd=self.proj, env=self.env,
                           input=json.dumps({"session_id": "s1", "cwd": self.proj}),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual((p.returncode, p.stderr), (0, ""))
        self.outputs.append(p.stdout)
        return json.loads(p.stdout).get("systemMessage")

    def raw(self, path=None):
        with open(path or self.user, "rb") as f:
            return f.read()

    def entry(self, path=None):
        with open(path or self.user) as f:
            return json.load(f).get("statusLine")

    def own(self):
        return owner.command_for(self.data)

    def marker(self):
        return owner.read_marker(self.data)

    def wrap_rec(self):
        return registry.read_wrap()[0]

    def wrapped(self, text=ODD, path=None):
        """Write `text` as the settings file and wrap it; returns the bytes."""
        path = path or self.user
        self.write_json(path, raw=text)
        args = () if path == self.user else ("--settings", path)
        rc, out = self.run_it("--wrap", *args)
        self.assertEqual(rc, 0, out)
        return text.encode()


class Consent(Base):
    def test_first_run_asks_once_and_never_wraps(self):
        self.write_json(self.user, raw=ODD)
        msg = self.hook()
        self.assertIn("--wrap", msg)
        self.assertIn("To accept", msg)
        self.assertIn("--unwrap", msg)
        self.assertEqual(self.raw(), ODD.encode())
        self.assertIsNone(self.wrap_rec())
        self.assertEqual(self.marker()["state"], "deferred")
        self.assertIsNone(self.hook())  # asked once
        self.assertEqual(self.raw(), ODD.encode())

    def test_plain_install_does_not_wrap(self):
        self.write_json(self.user, raw=ODD)
        self.assertEqual(self.run_it()[0], 3)
        self.assertEqual(self.raw(), ODD.encode())
        self.assertIsNone(self.wrap_rec())

    def test_nothing_to_wrap(self):
        self.write_json(self.user, {"model": "opus"})
        self.assertEqual(self.run_it("--wrap")[0], 1)
        self.assertNotIn("statusLine", json.loads(self.raw()))
        self.write_json(self.user, {"statusLine": {"type": "command"}})
        self.assertEqual(self.run_it("--wrap")[0], 1)
        self.assertIsNone(self.wrap_rec())

    def test_wrap_takes_no_replace(self):
        self.write_json(self.user, raw=ODD)
        self.assertEqual(self.run_it("--wrap", "--replace")[0], 2)
        self.assertEqual(self.raw(), ODD.encode())

    @ROOT_SKIP
    def test_read_only_file_leaves_nothing_behind(self):
        self.write_json(self.user, raw=ODD)
        os.chmod(self.user, 0o444)
        rc, out = self.run_it("--wrap")
        self.assertEqual(rc, 4, out)
        self.assertEqual(self.raw(), ODD.encode())
        self.assertIsNone(self.wrap_rec())
        self.assertIsNone(self.marker())


class WrapUnwrap(Base):
    def test_wrap_swaps_only_the_command(self):
        self.wrapped()
        e = self.entry()
        self.assertEqual(e, {"type": "command", "command": self.own(), "padding": 0})
        self.assertEqual(self.marker()["state"], "wrapping")
        self.assertNotIn(TOKEN, json.dumps(self.marker()))
        rec = self.wrap_rec()
        self.assertTrue(rec["running"])
        self.assertIn(TOKEN, rec["command"])
        mode = stat.S_IMODE(os.stat(registry.wrap_path()).st_mode)
        self.assertEqual(mode, 0o600)
        d = json.loads(self.raw())
        self.assertEqual((d["model"], d["z"]), ("opus", [1, 2]))

    def test_unwrap_is_byte_exact(self):
        before = self.wrapped()
        rc, out = self.run_it("--unwrap")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.raw(), before)
        self.assertEqual(self.marker()["state"], "unwrapped")
        self.assertFalse(self.wrap_rec()["running"])

    def test_unwrap_is_byte_exact_with_crlf(self):
        text = ODD.replace("\n", "\r\n")
        before = self.wrapped(text)
        self.assertIn(b"\r\n", self.raw())
        self.assertEqual(self.run_it("--unwrap")[0], 0)
        self.assertEqual(self.raw(), before)

    def test_uninstall_then_reinstall_and_unwrap_recovers(self):
        before = self.wrapped()
        import shutil
        shutil.rmtree(self.data)          # the uninstall takes the plugin data dir
        self.assertTrue(os.path.exists(registry.wrap_path()))
        self.assertIsNone(self.hook())    # reinstalled: its first session adopts the wrap
        self.assertEqual(self.marker()["state"], "wrapping")
        self.assertEqual(self.run_it("--unwrap")[0], 0)
        self.assertEqual(self.raw(), before)

    def test_unwrap_works_with_no_plugin_data_at_all(self):
        before = self.wrapped()
        import shutil
        shutil.rmtree(self.data)
        self.assertEqual(self.run_it("--unwrap")[0], 0)
        self.assertEqual(self.raw(), before)

    def test_success_message_says_unwrap_before_uninstalling(self):
        self.write_json(self.user, raw=ODD)
        rc, out = self.run_it("--wrap")
        self.assertEqual(rc, 0)
        self.assertIn("--unwrap before uninstalling", out)

    def test_unwrap_keeps_the_command_exact_when_the_file_changed(self):
        self.wrapped()
        d = json.loads(self.raw())
        d["model"] = "fable"
        self.write_json(self.user, d)
        self.assertEqual(self.run_it("--unwrap")[0], 0)
        self.assertEqual(self.entry(), json.loads(ODD)["statusLine"])
        self.assertEqual(json.loads(self.raw())["model"], "fable")

    def test_remove_on_a_wrapped_file_unwraps(self):
        before = self.wrapped()
        self.assertEqual(self.run_it("--remove")[0], 0)
        self.assertEqual(self.raw(), before)

    def test_one_wrap_at_a_time_and_install_elsewhere_refused(self):
        self.wrapped()
        other = os.path.join(self.cfg, "other.json")
        self.write_json(other, {"statusLine": {"type": "command", "command": "x"}})
        self.assertEqual(self.run_it("--wrap", "--settings", other)[0], 1)
        self.write_json(other, {})
        self.assertEqual(self.run_it("--settings", other)[0], 1)
        self.assertEqual(json.loads(self.raw(other)), {})
        self.assertEqual(self.run_it()[0], 0)       # same file: already the hub
        self.assertEqual(self.run_it("--wrap")[0], 0)
        self.assertTrue(self.wrap_rec()["running"])

    def test_unwrap_over_something_else_needs_replace(self):
        before = self.wrapped()
        self.write_json(self.user, {"statusLine": {"type": "command", "command": "new"}})
        rc, out = self.run_it("--unwrap")
        self.assertEqual(rc, 3, out)
        self.assertEqual(self.entry()["command"], "new")
        self.assertEqual(self.run_it("--unwrap", "--replace")[0], 0)
        self.assertEqual(self.entry(), json.loads(before)["statusLine"])

    def test_status_names_the_file_not_the_command(self):
        self.wrapped()
        rc, out = self.run_it("--status")
        self.assertEqual(rc, 0)
        self.assertIn("wrap: running", out)
        self.assertIn(self.user, out)


class Scope(Base):
    """Wrap mode is user scope only: a project's command would otherwise run
    in every other project's sessions."""

    def local(self, proj):
        p = os.path.join(proj, ".claude", "settings.local.json")
        self.write_json(p, {"statusLine": {"type": "command", "command": "sh ./%s.sh" % TOKEN}})
        return p

    def test_project_scopes_are_refused(self):
        a = os.path.join(self.cfg, "a")
        p = self.local(a)
        before = self.raw(p)
        for args in (("--local", "--wrap"), ("--settings", p, "--wrap")):
            rc, out = self.run_it(*args, cwd=a)
            self.assertEqual(rc, 1, out)
            self.assertIn("user settings", out)
        self.assertEqual(self.raw(p), before)
        self.assertIsNone(self.wrap_rec())

    def test_a_project_record_never_runs_in_another_project(self):
        a, b = os.path.join(self.cfg, "a"), os.path.join(self.cfg, "b")
        ran = os.path.join(self.cfg, "ran")
        for proj in (a, b):
            os.makedirs(proj, exist_ok=True)
            with open(os.path.join(proj, "sl.sh"), "w") as f:
                f.write('echo %s >> "%s"; echo X\n' % (os.path.basename(proj), ran))
        owner.write_wrap(os.path.join(a, ".claude", "settings.local.json"),
                         {"type": "command", "command": "sh ./sl.sh"}, None, True)
        self.manifest("foot", ["/bin/echo", "FOOT"])
        for proj in (a, b):
            p = subprocess.run([sys.executable, helpers.HUB], cwd=proj, env=self.env,
                               input=json.dumps(helpers.with_defaults(
                                   {"workspace": {"project_dir": proj}})).encode(),
                               capture_output=True, timeout=30)
            self.assertEqual(p.stdout, b"FOOT\n")
        time.sleep(0.3)
        self.assertFalse(os.path.exists(ran))

    def test_first_run_never_offers_to_wrap_a_project_file(self):
        self.write_json(self.user, {"model": "opus"})
        shared = os.path.join(self.proj, ".claude", "settings.json")
        self.write_json(shared, {"enabledPlugins": {"statusline-hub@kmacmcfarlane": True},
                                 "statusLine": {"type": "command", "command": TOKEN}})
        msg = self.hook()
        self.assertNotIn("--wrap", msg)
        self.assertIn("repository's command", msg)
        self.assertIsNone(self.wrap_rec())

    def test_wrap_refused_while_the_hub_entry_lives_elsewhere(self):
        local = os.path.join(self.proj, ".claude", "settings.local.json")
        self.write_json(local, {})
        self.assertEqual(self.run_it("--local")[0], 0)
        self.write_json(self.user, raw=ODD)
        rc, out = self.run_it("--wrap")
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.raw(), ODD.encode())
        self.assertEqual(self.marker()["state"], "installed")


class Heal(Base):
    def test_stale_write_back_of_the_wrapped_entry_is_rewrapped(self):
        before = self.wrapped()
        self.write_json(self.user, raw=before.decode())  # a session from before the wrap
        msg = self.hook()
        self.assertIn("restored the wrapped status line", msg)
        self.assertEqual(self.entry()["command"], self.own())
        self.assertIsNone(self.hook())
        self.assertEqual(self.run_it("--unwrap")[0], 0)
        self.assertEqual(self.raw(), before)

    def test_dropped_entry_is_restored(self):
        self.wrapped()
        d = json.loads(self.raw())
        del d["statusLine"]
        self.write_json(self.user, d)
        self.assertIn("dropped it", self.hook())
        self.assertEqual(self.entry()["command"], self.own())

    def test_something_else_is_yielded_to(self):
        self.wrapped()
        self.write_json(self.user, {"statusLine": {"type": "command", "command": "new"}})
        msg = self.hook()
        self.assertIn("changed by something else", msg)
        self.assertEqual(self.marker()["state"], "yielded")
        self.assertFalse(self.wrap_rec()["running"])
        self.assertIsNone(self.hook())
        self.assertEqual(self.entry()["command"], "new")

    def test_stale_write_back_after_unwrap_is_undone(self):
        before = self.wrapped()
        wrapped_text = self.raw()
        self.assertEqual(self.run_it("--unwrap")[0], 0)
        self.write_json(self.user, raw=wrapped_text.decode())  # a session from the wrap
        self.assertIn("put your own status line back", self.hook())
        self.assertEqual(self.raw(), before)
        self.assertIsNone(self.hook())

    def test_lost_marker_after_unwrap_never_rewraps(self):
        before = self.wrapped()
        wrapped_text = self.raw()
        self.assertEqual(self.run_it("--unwrap")[0], 0)
        self.write_json(self.user, raw=wrapped_text.decode())  # stale write-back
        os.unlink(os.path.join(self.data, "owner.json"))
        self.assertIn("put your own status line back", self.hook())
        self.assertEqual(self.raw(), before)
        self.assertEqual(self.marker()["state"], "unwrapped")
        self.assertFalse(self.wrap_rec()["running"])

    def test_lost_marker_is_adopted_as_wrapping(self):
        self.wrapped()
        os.unlink(os.path.join(self.data, "owner.json"))
        self.assertIsNone(self.hook())
        self.assertEqual(self.marker()["state"], "wrapping")

    def test_lost_wrap_record_ends_the_wrap_once(self):
        self.wrapped()
        os.unlink(registry.wrap_path())
        self.assertIn("no longer on record", self.hook())
        self.assertEqual(self.marker()["state"], "installed")
        self.assertIsNone(self.hook())


class Render(Base):
    """The hub render with a wrapped command (written straight to the wrap
    record) and one display hook, "foot"."""

    def setUp(self):
        super().setUp()
        self.manifest("foot", ["/bin/echo", "FOOT"])

    def inner(self, body):
        """Wrap a shell script with `body`; returns its path."""
        path = os.path.join(self.cfg, "inner.sh")
        with open(path, "w") as f:
            f.write("#!/bin/sh\n" + body + "\n")
        os.chmod(path, 0o700)
        owner.write_wrap(self.user, {"type": "command", "command": "sh '%s'" % path},
                         None, True)
        return path

    def render(self, sid="s"):
        rc, out, err, secs = self.hub({"session_id": sid})
        self.assertEqual((rc, err), (0, b""))
        return out.decode().rstrip("\n"), secs

    def test_output_first_then_hooks_and_the_record_is_written(self):
        got = os.path.join(self.cfg, "got")
        self.inner('cat > "%s"; pwd >> "%s"; printf "L1\\nL2\\n"' % (got, got))
        payload = json.dumps(helpers.with_defaults({"session_id": "s"})).encode()
        rc, out, _, _ = self.hub(raw=payload)
        self.assertEqual(out.decode(), "L1\nL2  FOOT\n")
        self.assertIsNotNone(self.read_sensor("s"))
        with open(got, "rb") as f:
            self.assertEqual(f.read(), payload + self.cfg.encode() + b"\n")

    def test_colour_is_reset_before_the_segments(self):
        self.inner(r"printf '\033[31mRED'")
        self.render()
        deadline = time.time() + 5
        while time.time() < deadline:
            line, _ = self.render()
            if "RED" in line:
                break
            time.sleep(0.2)
        self.assertEqual(line, "\x1b[31mRED" + registry.RESET + "  FOOT")

    def test_failing_command_costs_only_its_output(self):
        ran = os.path.join(self.cfg, "ran")
        self.inner('echo x >> "%s"; echo half; echo broken >&2; exit 3' % ran)
        self.assertEqual(self.render()[0], "FOOT")
        self.assertIsNotNone(self.read_sensor("s"))
        self.assertTrue(os.path.exists(ran))
        with open(os.path.join(self.cfg, "statusline-hub", "log", "_wrapped.log")) as f:
            self.assertIn("broken", f.read())

    def test_hanging_command_does_not_hold_the_line(self):
        ran = os.path.join(self.cfg, "ran")
        self.inner('echo x >> "%s"; exec sleep 30' % ran)
        line, secs = self.render()
        self.assertEqual(line, "FOOT")
        self.assertLess(secs, 2)
        self.assertIsNotNone(self.read_sensor("s"))
        line, secs = self.render()
        self.assertEqual(line, "FOOT")
        self.assertLess(secs, 2)
        with open(ran) as f:  # one live instance: the second render started none
            self.assertEqual(f.read(), "x\n")

    def test_slow_command_shows_its_last_output(self):
        self.inner("sleep 0.6; echo SLOW")
        self.assertEqual(self.render()[0], "FOOT")
        deadline = time.time() + 10
        while time.time() < deadline:
            time.sleep(0.3)
            line, _ = self.render()
            if line.startswith("SLOW"):
                break
        self.assertEqual(line, "SLOW  FOOT")

    def test_not_running_or_untrusted_record_is_not_run(self):
        got = os.path.join(self.cfg, "ran")
        self.inner('touch "%s"; echo X' % got)
        rec = self.wrap_rec()
        owner.set_running(rec, False)
        self.assertEqual(self.render()[0], "FOOT")
        owner.set_running(rec, True)
        os.chmod(registry.wrap_path(), 0o666)
        self.assertEqual(self.render()[0], "FOOT")
        time.sleep(0.3)
        self.assertFalse(os.path.exists(got))


if __name__ == "__main__":
    unittest.main()
