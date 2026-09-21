"""owner.py, and the install-statusline-hub script over it: the atomic,
formatting-preserving settings write, fingerprints, the data-dir lookup.

These moved here with the code: owner.py was a vendored copy of the
statusline plugin's, whose own tests held it, until that plugin handed the
slot to the hub and dropped its copy. Hermetic; the script runs as a
subprocess."""
import collections, json, os, shutil, stat, subprocess, sys, unittest
from unittest import mock

import helpers
import owner

SCRIPT = os.path.join(helpers.PLUGIN, "skills", "install-statusline-hub", "scripts",
                      "install_hub.py")
FOREIGN = {"type": "command", "command": "bash ~/bin/my-prompt.sh", "padding": 1}
ROOT_SKIP = unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes anything")


class Base(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        self.data = os.path.join(self.cfg, "plugins", "data", "statusline-hub-test")
        self.env["CLAUDE_PLUGIN_DATA"] = self.data
        self.proj = os.path.join(self.cfg, "proj")
        os.makedirs(self.proj)
        self.settings = os.path.join(self.cfg, "settings.json")

    def install(self, *args, env=None, script=SCRIPT):
        e = dict(self.env, **(env or {}))
        p = subprocess.run([sys.executable, script, *args], cwd=self.proj,
                           capture_output=True, text=True, env=e, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def plain_copy(self):
        """The installer of a copy of this plugin at a temp path that is not
        under plugins/cache/, so owner.data_dir() cannot derive a data dir
        from the script's own path."""
        dst = os.path.join(self.cfg, "src", "statusline-hub")
        if not os.path.isdir(dst):
            shutil.copytree(helpers.PLUGIN, dst, ignore=shutil.ignore_patterns(
                "__pycache__", "tests"))
        return os.path.join(dst, os.path.relpath(SCRIPT, helpers.PLUGIN))

    def load(self, path=None):
        with open(path or self.settings) as f:
            return json.load(f)

    def seed(self, obj, path=None):
        return self.write_json(path or self.settings, obj)

    def own_cmd(self):
        return "python3 " + json.dumps(os.path.join(self.data, "current-hooks", "hub.py"))

    def marker(self):
        with open(os.path.join(self.data, "owner.json")) as f:
            return json.load(f)


class Install(Base):
    def test_fresh_user_install(self):
        rc, out, err = self.install()
        self.assertEqual((rc, err), (0, ""))
        self.assertIn(f"installed statusLine in {self.settings}", out)
        self.assertEqual(self.load(), {"statusLine": {"type": "command",
                                                      "command": self.own_cmd()}})
        link = os.path.join(self.data, "current-hooks")
        self.assertTrue(os.path.islink(link))
        self.assertEqual(os.path.realpath(link), os.path.realpath(helpers.HOOKS))
        m = self.marker()
        self.assertEqual((m["v"], m["state"], m["settings"], m["command"]),
                         (1, "installed", self.settings, self.own_cmd()))
        self.assertEqual(stat.S_IMODE(os.stat(os.path.join(self.data, "owner.json")).st_mode),
                         0o600)

    def test_idempotent(self):
        self.install()
        before = self.load()
        rc, out, _ = self.install("--user")
        self.assertEqual(rc, 0)
        self.assertIn("updated statusLine", out)
        self.assertEqual(self.load(), before)

    def test_unrelated_keys_survive(self):
        other = {"model": "opus", "env": {"A": "é", "B": [1, 2.5, None, True]},
                 "hooks": {"Stop": [{"matcher": "", "hooks": []}]},
                 "enabledPlugins": {"statusline-hub@kmacmcfarlane": True}}
        self.seed(other)
        self.install()
        got = self.load()
        got.pop("statusLine")
        self.assertEqual(got, other)
        self.assertEqual(list(got), list(other))

    def test_symlinked_settings_stays_a_symlink(self):
        target = os.path.join(self.cfg, "dotfiles", "settings.json")
        self.seed({"a": 1}, target)
        os.symlink(target, self.settings)
        self.install()
        self.assertTrue(os.path.islink(self.settings))
        self.assertEqual(self.load(target)["statusLine"]["command"], self.own_cmd())

    def test_mode_is_kept(self):
        self.seed({"a": 1})
        os.chmod(self.settings, 0o600)
        self.install()
        self.assertEqual(stat.S_IMODE(os.stat(self.settings).st_mode), 0o600)
        self.assertEqual([n for n in os.listdir(self.cfg) if n.endswith(".tmp")], [])

    def test_unparsable_settings_are_left_alone(self):
        for raw in ("{broken", "[1, 2]"):
            with self.subTest(raw=raw):
                self.write_json(self.settings, raw=raw)
                rc, out, err = self.install()
                self.assertEqual(rc, 1)
                self.assertIn("left unchanged", err)
                with open(self.settings) as f:
                    self.assertEqual(f.read(), raw)

    def test_project_and_local_scopes(self):
        rc, out, _ = self.install("--project")
        self.assertEqual(rc, 0)
        self.assertIn("WARNING", out)
        self.assertIn("absolute path on this machine", out)
        p = os.path.join(self.proj, ".claude", "settings.json")
        self.assertEqual(self.load(p)["statusLine"]["command"], self.own_cmd())
        rc, out, _ = self.install("--local")
        self.assertNotIn("WARNING:", out)
        self.assertIn("statusLine", self.load(os.path.join(self.proj, ".claude",
                                                             "settings.local.json")))
        self.assertFalse(os.path.exists(self.settings))

    def test_explicit_settings_path(self):
        p = os.path.join(self.cfg, "x", "custom.json")
        rc, _, _ = self.install("--settings", p)
        self.assertEqual(rc, 0)
        self.assertIn("statusLine", self.load(p))

    def test_no_data_dir_is_an_error_and_writes_nothing(self):
        e = dict(self.env)
        e.pop("CLAUDE_PLUGIN_DATA")
        p = subprocess.run([sys.executable, self.plain_copy()], cwd=self.proj,
                           capture_output=True, text=True, env=e, timeout=30)
        self.assertEqual(p.returncode, 1)
        self.assertIn("data dir was not found", p.stderr)
        self.assertFalse(os.path.exists(self.settings))

    def test_existing_data_dir_is_found_without_env(self):
        found = os.path.join(self.cfg, "plugins", "data", "statusline-hub-mkt")
        os.makedirs(found)
        e = dict(self.env)
        e.pop("CLAUDE_PLUGIN_DATA")
        p = subprocess.run([sys.executable, self.plain_copy()], cwd=self.proj,
                           capture_output=True, text=True, env=e, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("statusline-hub-mkt/current-hooks/hub.py",
                      self.load()["statusLine"]["command"])


class Layout(Base):
    def test_install_remove_round_trip_is_byte_identical(self):
        for text in ('{\n    "model": "opus",\n    "env": {\n        "A": "\u00e9"\n    },\n'
                     '    "empty": {},\n    "list": []\n}',
                     '{\n\t"a": [\n\t\t1,\n\t\t2\n\t]\n}\n',
                     '{"a": 1, "b": [1, 2]}\n', '{"a":1}',
                     '{\n  "a": "\\u00e9"\n}\n'):
            with self.subTest(text=text):
                self.write_json(self.settings, raw=text)
                self.assertEqual(self.install()[0], 0)
                self.assertEqual(self.install("--remove")[0], 0)
                with open(self.settings, encoding="utf-8") as f:
                    self.assertEqual(f.read(), text)

    def test_only_the_status_line_lines_change(self):
        # Claude Code writes settings as JSON.stringify(v, null, 2): the diff
        # is the new key's lines plus the comma on the line before them.
        old = {"model": "opus", "env": {"A": "1"}, "permissions": {"allow": ["Bash(ls)"]}}
        text = json.dumps(old, indent=2) + "\n"
        self.write_json(self.settings, raw=text)
        self.install()
        with open(self.settings) as f:
            new = f.read()
        want = dict(old, statusLine={"type": "command", "command": self.own_cmd()})
        self.assertEqual(new, json.dumps(want, indent=2, ensure_ascii=False) + "\n")
        old_lines, new_lines = (collections.Counter(t.splitlines()) for t in (text, new))
        self.assertEqual(old_lines - new_lines, collections.Counter())  # nothing lost
        self.assertEqual(sorted((new_lines - old_lines).elements()), sorted([
            "  },", '  "statusLine": {', '    "type": "command",',
            "    " + json.dumps("command") + ": " + json.dumps(self.own_cmd())]))

    def test_unchanged_settings_are_not_rewritten(self):
        self.install()
        ino = os.stat(self.settings).st_ino
        rc, out, _ = self.install()
        self.assertEqual(rc, 0)
        self.assertEqual(os.stat(self.settings).st_ino, ino)

    @ROOT_SKIP
    def test_read_only_settings_are_refused_without_consent(self):
        for args, st in (((), {"a": 1}),
                         (("--remove",), {"a": 1, "statusLine": {
                             "type": "command", "command": self.own_cmd()}})):
            if os.path.exists(self.settings):
                os.chmod(self.settings, 0o644)
            self.seed(st)
            os.chmod(self.settings, 0o444)
            with open(self.settings, "rb") as f:
                raw = f.read()
            for extra in ((), ("--replace",)):  # --replace is not consent to this
                rc, out, err = self.install(*args, *extra)
                self.assertEqual(rc, 4, args + extra)
                self.assertIn("is read-only; left unchanged", err)
                self.assertIn("--write-read-only", err)
                with open(self.settings, "rb") as f:
                    self.assertEqual(f.read(), raw)
        os.chmod(self.settings, 0o644)
        self.seed({"a": 1, "statusLine": {"type": "command", "command": "x"}})
        os.chmod(self.settings, 0o444)
        rc, _, _ = self.install("--write-read-only")     # foreign: still needs --replace
        self.assertEqual(rc, 3)
        rc, _, _ = self.install("--write-read-only", "--replace")
        self.assertEqual(rc, 0)
        self.assertEqual(self.load()["statusLine"]["command"], self.own_cmd())
        self.assertEqual(stat.S_IMODE(os.stat(self.settings).st_mode), 0o444)

    def test_mixed_hand_formatted_layout_keeps_every_other_byte(self):
        # a hand-edited file: mixed indents, one-line nested objects, odd
        # spacing, braces and quotes inside strings. Only the statusLine
        # member's text is added, and --remove takes exactly it away again.
        text = ('{\n    "model": "opus",\n  "permissions": {"allow": ["Bash(ls)", "x}{\\"]"]},\n'
                '\t"env":{"A":"1"},\n    "hooks":   {\n        "Stop": []\n    }\n}\n')
        self.write_json(self.settings, raw=text)
        self.assertEqual(self.install()[0], 0)
        with open(self.settings, encoding="utf-8") as f:
            new = f.read()
        head = text[:text.rindex("}", 0, len(text) - 2) + 1]
        self.assertTrue(new.startswith(head), new)
        self.assertEqual(self.load()["statusLine"]["command"], self.own_cmd())
        self.assertEqual(self.install("--remove")[0], 0)
        with open(self.settings, encoding="utf-8") as f:
            self.assertEqual(f.read(), text)

    def test_replacing_an_entry_keeps_its_place_and_neighbours(self):
        text = ('{\n  "a": 1,\n  "statusLine": {"type": "command", "command": "x"},\n'
                '  "b":   [1,2]\n}\n')
        self.write_json(self.settings, raw=text)
        self.assertEqual(self.install("--replace")[0], 0)
        with open(self.settings) as f:
            new = f.read()
        self.assertTrue(new.startswith('{\n  "a": 1,\n  "statusLine": {\n    "type"'), new)
        self.assertTrue(new.endswith('\n  },\n  "b":   [1,2]\n}\n'), new)
        self.assertEqual(list(self.load()), ["a", "statusLine", "b"])


class FreshWrite(helpers.Hermetic):
    ENTRY = {"type": "command",
             "command": "python3 /x/plugins/data/statusline-hub-m/current-hooks/hub.py"}

    def setUp(self):
        super().setUp()
        self.p = self.write_json(os.path.join(self.cfg, "settings.json"),
                                 {"model": "opus", "permissions": {"allow": []}})

    def test_a_concurrent_change_between_read_and_write_is_kept(self):
        seen = owner.read_settings(self.p)              # the caller's (stale) read
        self.assertEqual(owner.classify(seen.get("statusLine")), "absent")
        # another process changes two keys meanwhile
        self.write_json(self.p, {"model": "sonnet", "permissions": {"allow": ["Bash(ls)"]},
                                 "env": {"A": "1"}})
        self.assertTrue(owner.write_settings(self.p, self.ENTRY, expect={"absent"}))
        with open(self.p) as f:
            got = json.load(f)
        self.assertEqual(got, {"model": "sonnet", "permissions": {"allow": ["Bash(ls)"]},
                               "env": {"A": "1"}, "statusLine": self.ENTRY})
        self.assertTrue(owner.write_settings(self.p, None))
        with open(self.p) as f:
            self.assertNotIn("statusLine", json.load(f))

    def test_a_fresh_file_that_does_not_parse_aborts(self):
        self.write_json(self.p, raw='{"model": ')
        with self.assertRaises(owner.SettingsError):
            owner.write_settings(self.p, self.ENTRY)
        with open(self.p) as f:
            self.assertEqual(f.read(), '{"model": ')

    def test_an_entry_that_turned_foreign_meanwhile_is_not_replaced(self):
        self.write_json(self.p, {"statusLine": FOREIGN})
        with open(self.p, "rb") as f:
            raw = f.read()
        with self.assertRaises(owner.Changed):
            owner.write_settings(self.p, self.ENTRY, expect={"absent", "own", "statusline"})
        with open(self.p, "rb") as f:
            self.assertEqual(f.read(), raw)

    def test_empty_file_is_an_empty_object(self):
        self.write_json(self.p, raw="")
        self.assertTrue(owner.write_settings(self.p, self.ENTRY))
        with open(self.p) as f:
            self.assertEqual(json.load(f), {"statusLine": self.ENTRY})

    def test_crlf_line_endings_are_kept(self):
        text = '{\r\n  "a": 1,\r\n  "b": {"c": [1, 2]}\r\n}\r\n'
        with open(self.p, "w", newline="") as f:
            f.write(text)
        owner.write_settings(self.p, self.ENTRY)
        with open(self.p, newline="") as f:
            new = f.read()
        self.assertEqual(new.count("\n"), new.count("\r\n"))
        self.assertEqual(json.loads(new)["statusLine"], self.ENTRY)
        owner.write_settings(self.p, None)
        with open(self.p, newline="") as f:
            self.assertEqual(f.read(), text)


class NonAscii(Base):
    def test_non_ascii_home_gives_a_working_command(self):
        cfg = os.path.join(self.cfg, "jos\u00e9", ".claude")
        data = os.path.join(cfg, "plugins", "data", "statusline-hub-m")
        env = {"CLAUDE_CONFIG_DIR": cfg, "HOME": os.path.dirname(cfg),
               "CLAUDE_PLUGIN_DATA": data}
        for text in (None, '{\n  "a": "\\u00e9"\n}\n'):       # plain, and an ASCII-escaped file
            with self.subTest(text=text):
                st = os.path.join(cfg, "settings.json")
                if text:
                    self.write_json(st, raw=text)
                rc, out, err = self.install(env=env)
                self.assertEqual(rc, 0, err)
                with open(st, encoding="utf-8") as f:
                    cmd = json.load(f)["statusLine"]["command"]
                self.assertIn("jos\u00e9", cmd)
                self.assertNotIn("\\u", cmd)
                self.assertEqual(owner.classify({"command": cmd}), "own")
                p = subprocess.run(cmd, shell=True, input=json.dumps(
                    {"session_id": "s", "context_window": helpers.CTX,
                     "model": {"display_name": "M"}}),
                    capture_output=True, text=True, env=dict(self.env, **env), timeout=30)
                self.assertEqual((p.returncode, p.stderr), (0, ""))
                with open(os.path.join(cfg, "statusline", "sensor", "s.json")) as f:
                    self.assertEqual(json.load(f)["exact"]["pct"], 42.0)

    def test_shell_specials_in_the_path_are_quoted(self):
        cmd = owner.command_for('/h/a$b`c"d\\e')
        self.assertEqual(cmd, 'python3 "/h/a\\$b\\`c\\"d\\\\e/current-hooks/hub.py"')
        out = subprocess.run("printf %s " + cmd[len("python3 "):], shell=True,
                             capture_output=True, text=True).stdout
        self.assertEqual(out, '/h/a$b`c"d\\e/current-hooks/hub.py')


class Splice(unittest.TestCase):
    V = {"type": "command", "command": 'python3 "/p"'}

    def test_falls_back_when_not_provably_right(self):
        self.assertIsNone(owner.splice_key("{}", "statusLine", self.V))
        self.assertIsNone(owner.splice_key('{"statusLine": 1}', "statusLine"))
        self.assertIsNone(owner.splice_key('{"statusLine": 1, "statusLine": 2}',
                                           "statusLine", self.V))
        for bad in ("{bad", "[1]", '{"a" 1}', '{"a": 1', ""):
            self.assertIsNone(owner.splice_key(bad, "statusLine", self.V), bad)

    def test_only_a_single_key_change_splices(self):
        self.assertIsNone(owner._splice_settings('{"a": 1}', {"a": 2, "b": 3}))
        self.assertIsNone(owner._splice_settings('{"a": 1, "b": 2}', {"b": 2, "a": 1, "c": 3}))
        self.assertEqual(owner._splice_settings('{"a": 1}', {"a": 1, "statusLine": 2}),
                         '{"a": 1, "statusLine": 2}')

    def test_delete_first_middle_last(self):
        for text, want in (('{"statusLine": 1, "a": 2}', '{"a": 2}'),
                           ('{"a": 1, "statusLine": 1, "b": 2}', '{"a": 1, "b": 2}'),
                           ('{\n  "a": 1,\n  "statusLine": 1\n}', '{\n  "a": 1\n}')):
            self.assertEqual(owner.splice_key(text, "statusLine"), want)


class Remove(Base):
    def test_remove_own(self):
        self.seed({"keep": [1]})
        self.install()
        rc, out, _ = self.install("--remove")
        self.assertEqual(rc, 0)
        self.assertIn(f"removed statusLine from {self.settings}", out)
        self.assertEqual(self.load(), {"keep": [1]})
        self.assertEqual(self.marker()["state"], "removed")

    def test_remove_absent(self):
        rc, out, _ = self.install("--remove")
        self.assertEqual(rc, 0)
        self.assertIn("no statusLine in", out)

    def test_remove_foreign_needs_replace(self):
        self.seed({"statusLine": FOREIGN})
        rc, out, _ = self.install("--remove")
        self.assertEqual(rc, 3)
        self.assertIn("was not installed by the hub", out)
        self.assertEqual(self.load()["statusLine"], FOREIGN)
        rc, _, _ = self.install("--remove", "--replace")
        self.assertEqual((rc, self.load()), (0, {}))

    def test_remove_from_another_scope_keeps_the_install_marker(self):
        self.install()
        self.install("--local", "--remove")
        self.assertEqual(self.marker()["state"], "installed")


class Usage(Base):
    def test_unknown_or_abbreviated_flags_are_usage_errors(self):
        for args in (("--force",), ("--rep",), ("--write",), ("--bogus",),
                     ("--user", "--local"), ("extra",)):
            with self.subTest(args=args):
                rc, out, err = self.install(*args)
                self.assertEqual(rc, 2)
                self.assertIn("usage:", err)
                self.assertFalse(os.path.exists(self.settings))
                self.assertFalse(os.path.exists(self.data))


class Classify(unittest.TestCase):
    def test_fingerprints(self):
        own = ['python3 "/h/.claude/plugins/data/statusline-hub-kmacmcfarlane/current-hooks/hub.py"',
               "python3 /h/.claude/plugins/data/statusline-hub-x/current-hooks/hub.py",
               '  python3  "/a b/plugins/data/statusline-hub-m/current-hooks/hub.py"  ']
        footer = ['python3 "/h/plugins/data/statusline-kmacmcfarlane/current-hooks/statusline.py"',
                  'python3 "/h/plugins/data/context-guard-kmacmcfarlane/current-hooks/statusline.py"',
                  "python3 /h/plugins/data/claude-kit-kmacmcfarlane/current-hooks/statusline.py"]
        foreign = ["bash ~/x.sh",
                   'python3 "/h/plugins/data/statusline-hub-x/current-hooks/hub.py" && rm -rf ~',
                   "python3 /h/plugins/data/other-x/current-hooks/hub.py",
                   "python3 /h/plugins/data/other-x/current-hooks/statusline.py",
                   "python3 /h/plugins/data/statusline-hub-x/current-hooks/other.py",
                   "python3 /h/plugins/data/statusline-hub-x/y/current-hooks/hub.py"]
        for c in own:
            self.assertEqual(owner.classify({"command": c}), "own", c)
        for c in footer:
            self.assertEqual(owner.classify({"command": c}), "statusline", c)
        for c in foreign:
            self.assertEqual(owner.classify({"command": c}), "foreign", c)
        self.assertEqual(owner.classify(None), "absent")
        for v in ("x", [], {}, {"command": 7}):
            self.assertEqual(owner.classify(v), "foreign", v)


class AtomicWrite(helpers.Hermetic):
    def test_failed_replace_keeps_original(self):
        p = self.write_json(os.path.join(self.cfg, "settings.json"), {"a": 1})
        with open(p, "rb") as f:
            raw = f.read()
        with mock.patch.object(owner.os, "replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                owner.atomic_write_json(p, {"a": 2})
        with open(p, "rb") as f:
            self.assertEqual(f.read(), raw)
        self.assertEqual(os.listdir(self.cfg), ["settings.json"])


class DataDir(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        self.base = os.path.join(self.cfg, "plugins", "data")

    def record(self, key, install_path):
        p = os.path.join(self.cfg, "plugins", "installed_plugins.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        self.write_json(p, {"version": 2, "plugins": {
            "other@mkt": [{"scope": "user", "installPath": "/elsewhere"}],
            key: [{"scope": "project", "installPath": "/not/this/one"},
                  {"scope": "user", "installPath": install_path}]}})

    def test_from_cache_path(self):
        got = owner.data_dir("/x/.claude/plugins/cache/mkt/statusline-hub/1.2.0/skills/"
                             "install-statusline-hub/scripts/install_hub.py")
        self.assertEqual(got, os.path.join(self.base, "statusline-hub-mkt"))

    def test_the_install_record_beats_the_scan(self):
        for n in ("statusline-hub-aaa", "statusline-hub-my-mkt"):
            os.makedirs(os.path.join(self.base, n))
        root = os.path.join(self.cfg, "src", "statusline-hub")
        self.record("statusline-hub@my.mkt", root)   # "." -> "-", Claude Code's id rule
        self.assertEqual(owner.data_dir(os.path.join(root, "hooks", "x.py")),
                         os.path.join(self.base, "statusline-hub-my-mkt"))

    def test_install_record_for_another_path_is_not_used(self):
        self.record("statusline-hub@my-mkt", os.path.join(self.cfg, "src", "statusline-hub"))
        self.assertIsNone(owner.installed_by_record(
            os.path.join(self.cfg, "src", "statusline-hub-2", "x.py")))

    def test_scan_never_takes_the_statusline_plugins_dir(self):
        # statusline-<mkt> does not start with statusline-hub-, whatever sorts first
        os.makedirs(os.path.join(self.base, "statusline-mkt"))
        self.assertIsNone(owner.data_dir("/elsewhere/x.py"))
        os.makedirs(os.path.join(self.base, "statusline-hub-mkt"))
        self.assertEqual(owner.data_dir("/elsewhere/x.py"),
                         os.path.join(self.base, "statusline-hub-mkt"))

    def test_unreadable_install_record_falls_back(self):
        p = os.path.join(self.cfg, "plugins", "installed_plugins.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        for bad in ("{not json", "[]", '{"plugins": {"statusline-hub@m": "x"}}',
                    '{"plugins": {"statusline-hub@m": [7, {"installPath": 7}]}}'):
            with open(p, "w") as f:
                f.write(bad)
            self.assertIsNone(owner.installed_by_record("/m/x.py"))
        os.remove(p)
        os.mkfifo(p)                                  # never opened: no hang
        self.assertIsNone(owner.installed_by_record("/m/x.py"))


if __name__ == "__main__":
    unittest.main()
