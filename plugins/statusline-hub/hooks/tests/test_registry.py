"""registry.py in-process: manifest validation and trust, config, health files,
and display-text hygiene. The render that uses them is test_render.py's."""
import json, os, tempfile, time, unittest

import helpers
import registry as R

ROOT_SKIP = unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                            "root owns everything")


class Manifests(helpers.Hermetic):
    def names(self, **kw):
        return [h["name"] for h in R.scan(**kw)[0]]

    def problem(self, name):
        return dict(R.scan()[1]).get(name)

    def test_array_and_string_commands(self):
        self.manifest("a", ["/bin/echo", "x y"])
        self.manifest("b", "echo 'x y'; rm -rf /")
        hooks = {h["name"]: h for h in R.scan()[0]}
        self.assertEqual(hooks["a"]["argv"], ["/bin/echo", "x y"])
        # a string is split into words and exec'd: no shell sees the ; or rm
        self.assertEqual(hooks["b"]["argv"], ["echo", "x y;", "rm", "-rf", "/"])

    def test_shell_only_when_asked(self):
        self.manifest("a", "echo hi | tr a-z A-Z", shell=True)
        self.assertEqual(R.scan()[0][0]["argv"], ["/bin/sh", "-c", "echo hi | tr a-z A-Z"])
        self.manifest("a", ["echo", "hi"], shell=True)  # shell needs a string
        self.assertEqual(self.names(), [])
        self.manifest("a", "echo", shell="yes")
        self.assertEqual(self.problem("a"), "shell is not true or false")

    def test_invalid_manifests_are_skipped(self):
        cases = {
            "relative program": ("bin/tool",),
            "empty": ([],),
            "not a string": ([1],),
            "nul": (["echo", "a\0b"],),
            "object": ({"x": 1},),
            "unbalanced quote": ("echo 'x",),
        }
        for why, (cmd,) in cases.items():
            with self.subTest(why):
                self.manifest("a", cmd)
                self.assertEqual(self.names(), [])
        self.manifest("a", ["echo"], kind="both")
        self.assertEqual(self.problem("a"), "kind is not display or record")
        self.manifest("a", ["echo"], v=2)
        self.assertEqual(self.problem("a"), "unknown version")
        p = self.manifest("a", ["echo"])
        with open(p, "w") as f:
            json.dump({"name": "b", "kind": "display", "command": ["echo"]}, f)
        self.assertEqual(self.problem("a"), "name does not match the file name")
        with open(p, "w") as f:
            f.write("{nope")
        self.assertEqual(self.problem("a"), "not JSON")
        os.rename(p, os.path.join(self.hooks_d(), "Bad_Name.json"))
        self.assertEqual(self.problem("Bad_Name.json"), "file name is not a hook name")

    def test_timeouts_clamped_per_kind(self):
        self.manifest("a", ["echo"])
        self.manifest("b", ["echo"], timeout_ms=99999)
        self.manifest("c", ["echo"], kind="record", timeout_ms=99999)
        self.manifest("d", ["echo"], kind="record", timeout_ms=1)
        self.manifest("e", ["echo"], timeout_ms=True)
        t = {h["name"]: h["timeout_ms"] for h in R.scan()[0]}
        self.assertEqual(t, {"a": 150, "b": 250, "c": 10000, "d": R.TIMEOUT_MIN_MS, "e": 150})

    def test_unknown_keys_ignored(self):
        self.manifest("a", ["echo"], future={"x": 1}, v=1)
        self.assertEqual(self.names(), ["a"])

    @ROOT_SKIP
    def test_writable_by_others_never_counts(self):
        self.manifest("a", ["echo"], mode=0o664)
        self.manifest("b", ["echo"], mode=0o644)
        self.assertEqual(self.names(), ["b"])
        self.assertEqual(self.problem("a"), "group- or other-writable")
        os.chmod(self.hooks_d(), 0o770)
        self.assertEqual(self.names(), [])
        os.chmod(self.hooks_d(), 0o700)
        os.chmod(os.path.dirname(self.hooks_d()), 0o707)
        self.assertEqual(self.names(), [])

    def test_symlinks_never_count(self):
        real = self.manifest("real", ["echo"])
        os.symlink(real, os.path.join(self.hooks_d(), "link.json"))
        self.assertEqual(self.names(), ["real"])
        self.assertEqual(self.problem("link"), "a symlink")
        # a symlinked hooks.d is refused whole
        d = self.hooks_d()
        os.rename(d, d + ".real")
        os.symlink(d + ".real", d)
        self.assertEqual(self.names(), [])

    def test_oversized_and_stale(self):
        big = self.manifest("big", ["echo"], pad="x" * R.MANIFEST_MAX)
        self.manifest("old", ["echo"])
        self.manifest("new", ["echo"])
        old = time.time() - (R.STALE_DAYS * 86400 + 60)
        os.utime(os.path.join(self.hooks_d(), "old.json"), (old, old))
        self.assertEqual(self.names(), ["new"])
        self.assertTrue(os.path.exists(big))

    def test_never_from_a_project_tree(self):
        self.manifest("a", ["echo"])
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        os.environ["HOME"] = home.name
        # a config dir inside the session's project: no hooks
        self.assertEqual(self.names(project_dirs=[self.cfg]), [])
        self.assertEqual(self.names(project_dirs=[None, os.path.join(self.cfg, ".")]), [])
        self.assertIn("inside the project tree", dict(R.scan(project_dirs=[self.cfg])[1])
                      .values())
        # a project elsewhere: hooks
        self.assertEqual(self.names(project_dirs=[home.name]), ["a"])
        # a home directory, or a dir above it, is not a project tree
        os.environ["HOME"] = os.path.join(self.cfg, "home")
        self.assertEqual(self.names(project_dirs=[self.cfg]), ["a"])

    def use_config(self, path):
        """Point CLAUDE_CONFIG_DIR at `path` (HOME at a dir of its own)."""
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        os.environ["HOME"] = home.name
        os.environ["CLAUDE_CONFIG_DIR"] = path
        return home.name

    def test_never_from_a_git_work_tree(self):
        # Claude Code started in a subdirectory of a cloned repo whose settings
        # relocate the config dir into the repo: the payload names only the
        # subdirectory, which does not contain the config dir.
        repo = os.path.join(self.cfg, "repo")
        os.makedirs(os.path.join(repo, ".git"))
        os.makedirs(os.path.join(repo, "sub"))
        self.use_config(os.path.join(repo, "cfg"))
        self.cfg = os.path.join(repo, "cfg")
        self.manifest("a", ["echo"])
        self.assertEqual(self.names(project_dirs=[os.path.join(repo, "sub")]), [])
        self.assertEqual(self.names(), [])  # no dirs in the payload: still refused
        self.assertIn("inside a git work tree", dict(R.scan()[1]).values())
        os.rmdir(os.path.join(repo, ".git"))
        self.assertEqual(self.names(project_dirs=[os.path.join(repo, "sub")]), ["a"])

    def test_git_above_home_or_in_the_default_config_dir_does_not_count(self):
        home = self.use_config(self.cfg)
        # the default ~/.claude, kept in a dotfiles repo
        default = os.path.join(home, ".claude")
        os.makedirs(os.path.join(default, ".git"))
        os.environ["CLAUDE_CONFIG_DIR"] = default
        self.cfg = default
        self.manifest("a", ["echo"])
        self.assertEqual(self.names(), ["a"])
        # a relocated config dir under a home that is itself a git work tree
        os.makedirs(os.path.join(home, ".git"))
        other = os.path.join(home, "cfg2")
        os.environ["CLAUDE_CONFIG_DIR"] = self.cfg = other
        self.manifest("a", ["echo"])
        self.assertEqual(self.names(), ["a"])

    def test_pinned_manifests_do_not_go_stale(self):
        p = self.manifest("mine", ["echo"], pinned=True)
        old = time.time() - (R.STALE_DAYS * 86400 + 60)
        os.utime(p, (old, old))
        self.assertEqual(self.names(), ["mine"])
        self.manifest("bad", ["echo"], pinned="yes")
        self.assertEqual(self.problem("bad"), "pinned is not true or false")

    def test_health_path_stays_inside_the_config_dir(self):
        self.manifest("a", ["echo"], kind="record",
                      health_path=os.path.join(self.cfg, "x", "health.json"))
        self.manifest("b", ["echo"], kind="record", health_path="/etc/passwd")
        self.manifest("c", ["echo"], kind="record", health_path="rel/health.json")
        self.manifest("d", ["echo"], kind="record",
                      health_path=os.path.join(self.cfg, "..", "escape.json"))
        hp = {h["name"]: h["health_path"] for h in R.scan()[0]}
        self.assertEqual(hp["a"], os.path.realpath(os.path.join(self.cfg, "x", "health.json")))
        self.assertEqual((hp["b"], hp["c"], hp["d"]), (None, None, None))

    def test_config_orders_and_disables(self):
        for n in ("a", "b", "c"):
            self.manifest(n, ["echo"], order={"a": 5, "b": 1, "c": 3}[n])
        self.assertEqual([h["name"] for h in R.load()], ["b", "c", "a"])
        self.write_json(R.config_path(), {"order": ["a"], "disabled": ["c"],
                                          "separator": " |\x1b[2J| ", "health_stale_min": 5})
        cfg = R.config()
        self.assertEqual(cfg["separator"], " || ")
        self.assertEqual(cfg["health_stale_min"], 5)
        self.assertEqual([h["name"] for h in R.load(cfg=cfg)], ["a", "b"])
        self.write_json(R.config_path(), raw="[1,2]")
        self.assertEqual(R.config()["order"], [])


class Health(helpers.Hermetic):
    def put(self, obj=None, raw=None, age=0):
        p = self.write_json(os.path.join(self.cfg, "h", "health.json"), obj, raw=raw)
        t = time.time() - age
        os.utime(p, (t, t))
        return p

    def test_cases(self):
        now = time.time()
        cases = [
            ("never ran", {"runs": 0, "errors": 0}, None),
            ("nothing known", {}, None),
            ("ok", {"last_ok": now - 5, "runs": 3}, None),
            ("last run errored", {"last_ok": now - 60, "last_error": now - 5}, "warn"),
            ("only errors", {"last_error": now - 5, "error": "boom"}, "warn"),
            ("recovered", {"last_ok": now - 1, "last_error": now - 60}, None),
            ("no ok within N", {"last_ok": now - 3600, "runs": 9}, "warn"),
            ("iso strings", {"last_ok": "2020-01-01T00:00:00Z",
                             "last_error": "2020-01-01T00:00:01+00:00"}, "warn"),
            ("junk stamps", {"last_ok": True, "last_error": "yesterday"}, None),
            ("not an object", [1], None),
        ]
        for why, obj, want in cases:
            with self.subTest(why):
                self.assertEqual(R.health(self.put(obj), now), want)

    def test_a_quiet_hook_is_not_a_failing_one(self):
        # idle for an hour: the last write is the last success, so no glyph
        p = self.put({"last_ok": time.time() - 3600}, age=3600)
        self.assertIsNone(R.health(p))

    def test_unusable_files_show_nothing(self):
        now = time.time()
        self.assertIsNone(R.health(os.path.join(self.cfg, "missing.json"), now))
        self.assertIsNone(R.health(self.put({"last_error": now}, age=R.HEALTH_IGNORE_S + 60)))
        self.assertIsNone(R.health(self.put(raw='{"last_error": %d, "pad": "%s"}'
                                            % (now, "x" * R.HEALTH_MAX))))
        self.assertIsNone(R.health(self.put(raw="{broken")))
        fifo = os.path.join(self.cfg, "fifo")
        os.mkfifo(fifo)
        self.assertIsNone(R.health(fifo, now))  # never blocks on a FIFO
        self.assertIsNone(R.health(None, now))

    def test_stale_window_from_config(self):
        p = self.put({"last_ok": time.time() - 120})
        self.assertIsNone(R.health(p, stale_min=5))
        self.assertEqual(R.health(p, stale_min=1), "warn")


class Sanitise(unittest.TestCase):
    def test_keeps_colour_drops_every_other_escape(self):
        s = R.sanitise("\x1b]0;evil title\x07a \x1b[31mred\x1b[0m \x1b[2J\x1b[Hb"
                       "\x1b]8;;http://x\x1b\\link\x1b]8;;\x1b\\")
        self.assertEqual(s, "a \x1b[31mred\x1b[0m blink" + R.RESET)

    def test_controls_format_chars_and_lines(self):
        self.assertEqual(R.sanitise("a‮b​c\x07d\x9be\tf\nsecond line"),
                         "abcde f")
        self.assertEqual(R.sanitise("न्‍ष"), "न्‍ष")
        self.assertEqual(R.sanitise("\x1b[31m  \x1b[0m"), "")
        self.assertEqual(R.sanitise("a\u2028b\u2029c"), "abc")
        self.assertEqual(R.sanitise(None), "")
        self.assertEqual(len(R.sanitise("x" * 5000)), R.VISIBLE_MAX)


if __name__ == "__main__":
    unittest.main()
