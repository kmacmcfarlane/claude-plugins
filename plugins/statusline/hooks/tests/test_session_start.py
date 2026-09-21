"""session_start.py: the hub hook manifest (written, refreshed, private,
atomic), no settings writes and no messages in any state an earlier version
left behind, prune, and never raising. Hermetic (helpers.Hermetic); the hook
runs as a subprocess with CLAUDE_PLUGIN_ROOT and CLAUDE_PLUGIN_DATA set, as
Claude Code runs it."""
import json, os, stat, subprocess, sys, time, unittest

import helpers
import sensor

HOOK = os.path.join(helpers.HOOKS, "session_start.py")
FOREIGN = {"type": "command", "command": "bash ~/bin/my-prompt.sh"}
ENABLED = {"enabledPlugins": {"statusline@kmacmcfarlane": True}}
ROOT_SKIP = unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes anything")


class Base(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        self.data = os.path.join(self.cfg, "plugins", "data", "statusline-kmacmcfarlane")
        self.env["CLAUDE_PLUGIN_DATA"] = self.data
        self.env["CLAUDE_PLUGIN_ROOT"] = helpers.PLUGIN
        self.proj = os.path.join(self.cfg, "proj")
        os.makedirs(self.proj)
        self.env["CLAUDE_PROJECT_DIR"] = self.proj
        self.user = os.path.join(self.cfg, "settings.json")
        self.hub = os.path.join(self.cfg, "statusline-hub")
        self.manifest = os.path.join(self.hub, "hooks.d", "statusline.json")

    def hook(self, env=None, stdin=None, script=HOOK, sid="s1"):
        """(returncode, stdout, stderr)."""
        e = dict(self.env, **(env or {}))
        e = {k: v for k, v in e.items() if v is not None}
        p = subprocess.run([sys.executable, script], cwd=self.proj, env=e,
                           input=stdin if stdin is not None else json.dumps(
                               {"session_id": sid, "cwd": self.proj, "source": "startup"}),
                           capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def quiet(self, **kw):
        self.assertEqual(self.hook(**kw), (0, "{}\n", ""))

    def raw(self, path=None):
        with open(path or self.user, "rb") as f:
            return f.read()

    def load_manifest(self):
        with open(self.manifest) as f:
            return json.load(f)


class Manifest(Base):
    def test_written_as_the_hook_contract_asks(self):
        self.quiet()
        m = self.load_manifest()
        self.assertEqual(m, {"v": 1, "name": "statusline", "kind": "display",
                             "command": ["python3", os.path.join(helpers.HOOKS, "statusline.py"),
                                         "--segment"],
                             "timeout_ms": 250, "order": 0})
        for d in (self.hub, os.path.dirname(self.manifest)):
            self.assertEqual(stat.S_IMODE(os.stat(d).st_mode), 0o700, d)
        self.assertEqual(stat.S_IMODE(os.stat(self.manifest).st_mode), 0o600)
        self.assertEqual(sorted(os.listdir(os.path.dirname(self.manifest))),
                         ["statusline.json"])        # no temp file left behind

    def test_the_command_it_names_draws_the_footer_and_writes_no_record(self):
        self.quiet()
        p = subprocess.run(self.load_manifest()["command"], capture_output=True, text=True,
                           input=json.dumps({"session_id": "s", "context_window": helpers.CTX,
                                             "model": {"display_name": "M"}}),
                           env=self.env, timeout=30)
        self.assertIn("580k left", p.stdout)
        self.assertEqual(p.stderr, "")
        self.assertIsNone(self.read_sensor())

    def test_refreshed_every_session(self):
        self.quiet()
        stale = self.write_json(self.manifest, {"name": "statusline", "kind": "display",
                                                "command": ["python3", "/old/statusline.py"]})
        old = time.time() - 10 * 86400
        os.utime(stale, (old, old))
        self.quiet()
        self.assertIn(os.path.join(helpers.HOOKS, "statusline.py"),
                      self.load_manifest()["command"])
        self.assertGreater(os.stat(self.manifest).st_mtime, old + 86400)

    def test_a_symlink_in_its_place_is_replaced_not_followed(self):
        self.quiet()
        victim = self.write_json(os.path.join(self.cfg, "victim.json"), {"keep": 1})
        os.remove(self.manifest)
        os.symlink(victim, self.manifest)
        self.quiet()
        self.assertFalse(os.path.islink(self.manifest))
        with open(victim) as f:
            self.assertEqual(json.load(f), {"keep": 1})

    def test_never_writes_through_a_symlinked_hub_dir(self):
        victim = os.path.join(self.cfg, "victim")
        os.makedirs(victim)
        os.symlink(victim, self.hub)
        self.quiet()
        self.assertEqual(os.listdir(victim), [])

    @ROOT_SKIP
    def test_an_unwritable_hub_dir_is_quiet(self):
        os.makedirs(self.hub, mode=0o500)
        try:
            self.quiet()
        finally:
            os.chmod(self.hub, 0o700)
        self.assertFalse(os.path.exists(self.manifest))


class NoSettings(Base):
    """It never writes settings or says anything, whatever an earlier version
    left behind: the hub owns the slot, and takes it over itself."""

    def entry(self, plugin="statusline"):
        d = os.path.join(self.cfg, "plugins", "data", plugin + "-kmacmcfarlane")
        return {"type": "command", "command": f'python3 "{d}/current-hooks/'
                + ("hub.py" if plugin == "statusline-hub" else "statusline.py") + '"'}

    def marker(self, state, **extra):
        self.write_json(os.path.join(self.data, "owner.json"),
                        dict({"v": 1, "state": state, "settings": self.user,
                              "command": self.entry()["command"], "at": 1}, **extra))

    def test_every_state_and_entry(self):
        entries = [None, self.entry(), self.entry("statusline-hub"), FOREIGN,
                   self.entry("context-guard")]
        states = [None, "installed", "removed", "yielded", "deferred", "blocked"]
        for entry in entries:
            for state in states:
                with self.subTest(entry=entry, state=state):
                    settings = dict(ENABLED, **({"statusLine": entry} if entry else {}))
                    self.write_json(self.user, settings)
                    m = os.path.join(self.data, "owner.json")
                    if state:
                        self.marker(state, **({"reason": "invalid", "resume": "new"}
                                              if state == "blocked" else {}))
                    elif os.path.exists(m):
                        os.remove(m)
                    before, mark = self.raw(), (self.raw(m) if state else None)
                    self.quiet()
                    self.assertEqual(self.raw(), before)
                    if state:
                        self.assertEqual(self.raw(m), mark)   # the hub reads it; left as is
                    else:
                        self.assertFalse(os.path.exists(m))

    def test_a_dropped_entry_is_not_restored(self):
        self.write_json(self.user, ENABLED)
        self.marker("installed")
        before = self.raw()
        self.quiet()
        self.assertEqual(self.raw(), before)

    def test_no_settings_file_is_not_created(self):
        self.quiet()
        self.assertFalse(os.path.exists(self.user))
        self.assertFalse(os.path.exists(os.path.join(self.proj, ".claude")))


class NeverRaises(Base):
    def test_malformed_settings_are_not_even_read(self):
        for raw in ("{bad", "[1]", "", "null"):
            with self.subTest(raw=raw):
                self.write_json(self.user, raw=raw)
                self.quiet()
                with open(self.user) as f:
                    self.assertEqual(f.read(), raw)

    def test_malformed_stdin(self):
        for stdin in ("", "not json", "[]", "null", '{"session_id": ["x"], "cwd": 5}'):
            with self.subTest(stdin=stdin):
                self.quiet(stdin=stdin)

    @ROOT_SKIP
    def test_read_only_config_dir(self):
        os.chmod(self.cfg, 0o555)
        try:
            self.quiet()
        finally:
            os.chmod(self.cfg, 0o755)
        self.assertFalse(os.path.exists(self.hub))

    def test_no_data_dir_at_all(self):
        self.quiet(env={"CLAUDE_PLUGIN_DATA": None, "CLAUDE_PLUGIN_ROOT": None})
        self.assertTrue(os.path.isfile(self.manifest))


class Prune(Base):
    def age(self, path, days):
        t = time.time() - days * 86400
        os.utime(path, (t, t))

    def seed(self):
        d = os.path.join(self.cfg, "statusline", "sensor")
        os.makedirs(d)
        files = {n: self.write_json(os.path.join(d, n), {"v": 1})
                 for n in ("old.json", "fresh.json", "s1.json", "notes.txt")}
        files["tmp"] = self.write_json(os.path.join(d, ".old.123.0123456789ab.tmp"), raw="x")
        files["newtmp"] = self.write_json(os.path.join(d, ".new.123.0123456789ab.tmp"), raw="x")
        for n in ("old.json", "s1.json", "notes.txt"):
            self.age(files[n], 45)
        self.age(files["fresh.json"], 10)
        self.age(files["tmp"], 1 / 12)                    # two hours
        return d, files

    def test_old_records_and_stale_temps_go_current_session_stays(self):
        d, f = self.seed()
        self.quiet(sid="s1")
        self.assertFalse(os.path.exists(f["old.json"]))
        self.assertFalse(os.path.exists(f["tmp"]))
        for k in ("fresh.json", "s1.json", "notes.txt", "newtmp"):
            self.assertTrue(os.path.exists(f[k]), k)
        self.assertTrue(os.path.isfile(os.path.join(d, ".pruned")))

    def test_once_a_day(self):
        d, f = self.seed()
        open(os.path.join(d, ".pruned"), "w").close()
        self.quiet(sid="x")
        self.assertTrue(os.path.exists(f["old.json"]))
        self.age(os.path.join(d, ".pruned"), 2)
        self.quiet(sid="x")
        self.assertFalse(os.path.exists(f["old.json"]))

    def test_a_planted_stamp_symlink_is_replaced_not_followed(self):
        d, f = self.seed()
        target = os.path.join(self.cfg, "victim")
        with open(target, "w") as fh:
            fh.write("keep")
        self.age(target, 0)
        os.symlink(target, os.path.join(d, ".pruned"))
        self.quiet(sid="x")
        self.assertFalse(os.path.exists(f["old.json"]))
        self.assertFalse(os.path.islink(os.path.join(d, ".pruned")))
        with open(target) as fh:
            self.assertEqual(fh.read(), "keep")

    def test_no_sensor_dir_is_fine_and_not_created(self):
        self.quiet()
        self.assertFalse(os.path.exists(os.path.join(self.cfg, "statusline")))

    def test_stale_temp_files_in_the_data_dir(self):
        os.makedirs(self.data)
        t = self.write_json(os.path.join(self.data, ".owner.json.9.0123456789ab.tmp"), raw="x")
        keep = self.write_json(os.path.join(self.data, "keep.tmp"), raw="x")
        self.age(t, 1)
        self.age(keep, 1)
        self.quiet()
        self.assertFalse(os.path.exists(t))
        self.assertTrue(os.path.exists(keep))

    def test_prune_api(self):
        d, f = self.seed()
        self.assertEqual(sensor.prune(keep="s1"), 2)
        self.assertIsNone(sensor.prune(keep="s1"))


class Timing(Base):
    def test_a_session_start_is_fast(self):
        self.quiet()
        t = time.monotonic()
        self.quiet()
        self.assertLess(time.monotonic() - t, 2.0)


if __name__ == "__main__":
    unittest.main()
