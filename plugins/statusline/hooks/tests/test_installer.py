"""The install-statusline script and owner.py: explicit install and remove,
fingerprints, predecessor-marker retirement, and the atomic settings write."""
import collections, json, os, stat, subprocess, sys, unittest
from unittest import mock

import helpers
import owner

PRED_CMD = 'python3 "{cfg}/plugins/data/context-guard-kmacmcfarlane/current-hooks/statusline.py"'
LEGACY_CMD = "python3 {cfg}/plugins/data/claude-kit-kmacmcfarlane/current-hooks/statusline.py"
FOREIGN = {"type": "command", "command": "bash ~/bin/my-prompt.sh", "padding": 1}


class Base(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        self.data = os.path.join(self.cfg, "plugins", "data", "statusline-test")
        self.env["CLAUDE_PLUGIN_DATA"] = self.data
        self.proj = os.path.join(self.cfg, "proj")
        os.makedirs(self.proj)
        self.settings = os.path.join(self.cfg, "settings.json")

    def install(self, *args, env=None, script=helpers.INSTALLER):
        e = dict(self.env, **(env or {}))
        p = subprocess.run([sys.executable, script, *args], cwd=self.proj,
                           capture_output=True, text=True, env=e, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def load(self, path=None):
        with open(path or self.settings) as f:
            return json.load(f)

    def seed(self, obj, path=None):
        return self.write_json(path or self.settings, obj)

    def pred_marker(self, plugin, settings=None):
        d = os.path.join(self.cfg, "plugins", "data", plugin + "-kmacmcfarlane")
        return self.write_json(os.path.join(d, "statusline-installed.json"),
                               {"settings": settings or self.settings, "command": "x"})

    def own_cmd(self):
        return "python3 " + json.dumps(os.path.join(self.data, "current-hooks", "statusline.py"))

    def marker(self):
        with open(os.path.join(self.data, "owner.json")) as f:
            return json.load(f)


class Install(Base):
    def test_fresh_user_install(self):
        rc, out, err = self.install()
        self.assertEqual((rc, err), (0, ""))
        self.assertIn(f"installed statusLine in {self.settings}", out)
        self.assertIn("It shows from the next session.", out)
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

    def test_installed_command_renders(self):
        self.install()
        cmd = self.load()["statusLine"]["command"]
        p = subprocess.run(cmd, shell=True, input=json.dumps(
            {"session_id": "s", "context_window": helpers.CTX,
             "model": {"display_name": "M"}}),
            capture_output=True, text=True, env=self.env, timeout=30)
        self.assertIn("580k left", p.stdout)

    def test_predecessor_is_repointed_and_markers_retired(self):
        for cmd in (PRED_CMD, LEGACY_CMD):
            with self.subTest(cmd=cmd):
                self.seed({"statusLine": {"type": "command", "command": cmd.format(cfg=self.cfg)},
                           "model": "opus"})
                a = self.pred_marker("context-guard")
                b = self.pred_marker("claude-kit", settings="/somewhere/else.json")
                rc, out, _ = self.install()
                self.assertEqual(rc, 0)
                self.assertIn("replaced statusLine", out)
                self.assertEqual(self.load()["statusLine"]["command"], self.own_cmd())
                self.assertEqual(self.load()["model"], "opus")
                self.assertFalse(os.path.exists(a))
                self.assertFalse(os.path.exists(b))

    def test_foreign_needs_replace(self):
        self.seed({"statusLine": FOREIGN, "x": 1})
        with open(self.settings, "rb") as f:
            raw = f.read()
        rc, out, _ = self.install()
        self.assertEqual(rc, 3)
        self.assertIn("already has a different statusLine; left unchanged", out)
        with open(self.settings, "rb") as f:
            self.assertEqual(f.read(), raw)
        self.assertFalse(os.path.exists(os.path.join(self.data, "owner.json")))
        rc, out, _ = self.install("--write-read-only")   # the other consent is not this one
        self.assertEqual(rc, 3)
        rc, out, _ = self.install("--replace")
        self.assertEqual(rc, 0)
        self.assertEqual(self.load(), {"statusLine": {"type": "command",
                                                      "command": self.own_cmd()}, "x": 1})

    def test_unrelated_keys_survive(self):
        other = {"model": "opus", "env": {"A": "é", "B": [1, 2.5, None, True]},
                 "hooks": {"Stop": [{"matcher": "", "hooks": []}]},
                 "enabledPlugins": {"statusline@kmacmcfarlane": True}}
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
        found = os.path.join(self.cfg, "plugins", "data", "statusline-mkt")
        os.makedirs(found)
        e = dict(self.env)
        e.pop("CLAUDE_PLUGIN_DATA")
        p = subprocess.run([sys.executable, self.plain_copy()], cwd=self.proj,
                           capture_output=True, text=True, env=e, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("statusline-mkt/current-hooks/statusline.py",
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

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes anything")
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
    ENTRY = {"type": "command", "command": "python3 /x/plugins/data/statusline-m/current-hooks/statusline.py"}

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
            owner.write_settings(self.p, self.ENTRY, expect={"absent", "own", "predecessor"})
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
        data = os.path.join(cfg, "plugins", "data", "statusline-m")
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
                self.assertIn("580k left", p.stdout, p.stderr)

    def test_shell_specials_in_the_path_are_quoted(self):
        cmd = owner.command_for('/h/a$b`c"d\\e')
        self.assertEqual(cmd, 'python3 "/h/a\\$b\\`c\\"d\\\\e/current-hooks/statusline.py"')
        out = subprocess.run("printf %s " + cmd[len("python3 "):], shell=True,
                             capture_output=True, text=True).stdout
        self.assertEqual(out, '/h/a$b`c"d\\e/current-hooks/statusline.py')


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
        self.assertIn("was not installed by this plugin", out)
        self.assertEqual(self.load()["statusLine"], FOREIGN)
        rc, _, _ = self.install("--remove", "--replace")
        self.assertEqual((rc, self.load()), (0, {}))

    def test_remove_predecessor_retires_only_its_markers(self):
        self.seed({"statusLine": {"type": "command",
                                  "command": PRED_CMD.format(cfg=self.cfg)}})
        mine = self.pred_marker("context-guard")
        other = self.pred_marker("claude-kit", settings="/somewhere/else.json")
        rc, _, _ = self.install("--remove")
        self.assertEqual((rc, self.load()), (0, {}))
        self.assertFalse(os.path.exists(mine))
        self.assertTrue(os.path.exists(other))

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
        own = ['python3 "/h/.claude/plugins/data/statusline-kmacmcfarlane/current-hooks/statusline.py"',
               "python3 /h/.claude/plugins/data/statusline-x/current-hooks/statusline.py",
               '  python3  "/a b/plugins/data/statusline-m/current-hooks/statusline.py"  ']
        pred = ['python3 "/h/plugins/data/context-guard-kmacmcfarlane/current-hooks/statusline.py"',
                "python3 /h/plugins/data/claude-kit-kmacmcfarlane/current-hooks/statusline.py"]
        foreign = ["bash ~/x.sh",
                   'python3 "/h/plugins/data/statusline-x/current-hooks/statusline.py" && rm -rf ~',
                   "python3 /h/plugins/data/other-x/current-hooks/statusline.py",
                   "python3 /h/plugins/data/statusline-x/current-hooks/other.py",
                   "python3 /h/plugins/data/statusline-x/y/current-hooks/statusline.py"]
        for c in own:
            self.assertEqual(owner.classify({"command": c}), "own", c)
        for c in pred:
            self.assertEqual(owner.classify({"command": c}), "predecessor", c)
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

    def test_data_dir_from_cache_path(self):
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        got = owner.data_dir("/x/.claude/plugins/cache/mkt/statusline/1.2.0/skills/"
                             "install-statusline/scripts/install_statusline.py")
        self.assertEqual(got, os.path.join(self.cfg, "plugins", "data", "statusline-mkt"))

    def record(self, key, install_path):
        p = os.path.join(self.cfg, "plugins", "installed_plugins.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        self.write_json(p, {"version": 2, "plugins": {
            "other@mkt": [{"scope": "user", "installPath": "/elsewhere"}],
            key: [{"scope": "project", "installPath": "/not/this/one"},
                  {"scope": "user", "installPath": install_path}]}})

    def test_data_dir_from_the_install_record_beats_the_scan(self):
        # two data dirs; the sorted-first scan would take statusline-aaa
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        for n in ("statusline-aaa", "statusline-my-mkt"):
            os.makedirs(os.path.join(self.cfg, "plugins", "data", n))
        root = os.path.join(self.cfg, "src", "statusline")
        script = os.path.join(root, "skills", "install-statusline", "scripts", "x.py")
        self.record("statusline@my.mkt", root)       # "." -> "-", Claude Code's id rule
        self.assertEqual(owner.data_dir(script),
                         os.path.join(self.cfg, "plugins", "data", "statusline-my-mkt"))

    def test_install_record_for_another_path_is_not_used(self):
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        self.record("statusline@my-mkt", os.path.join(self.cfg, "src", "statusline"))
        self.assertIsNone(owner.installed_by_record(
            os.path.join(self.cfg, "src", "statusline-2", "x.py")))
        got = owner.data_dir("/x/.claude/plugins/cache/mkt/statusline/1.2.0/x.py")
        self.assertEqual(got, os.path.join(self.cfg, "plugins", "data", "statusline-mkt"))

    def test_cache_path_beats_the_scan(self):
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        os.makedirs(os.path.join(self.cfg, "plugins", "data", "statusline-aaa"))
        got = owner.data_dir("/x/.claude/plugins/cache/mkt/statusline/1.2.0/x.py")
        self.assertEqual(got, os.path.join(self.cfg, "plugins", "data", "statusline-mkt"))

    def test_scan_never_takes_the_hubs_data_dir(self):
        # statusline-hub-<mkt> sorts before statusline-<mkt>; its current-hooks
        # link leads to the hub's hooks, which have no statusline.py
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        data = os.path.join(self.cfg, "plugins", "data")
        hub_hooks = os.path.join(self.cfg, "hub-src", "hooks")
        os.makedirs(hub_hooks)
        open(os.path.join(hub_hooks, "hub.py"), "w").close()
        os.makedirs(os.path.join(data, "statusline-hub-mkt"))
        os.symlink(hub_hooks, os.path.join(data, "statusline-hub-mkt", "current-hooks"))
        os.makedirs(os.path.join(data, "statusline-mkt"))
        self.assertEqual(owner.data_dir("/elsewhere/x.py"),
                         os.path.join(data, "statusline-mkt"))
        # a statusline dir with its own link still counts
        os.symlink(os.path.dirname(os.path.abspath(owner.__file__)),
                   os.path.join(data, "statusline-mkt", "current-hooks"))
        self.assertEqual(owner.data_dir("/elsewhere/x.py"),
                         os.path.join(data, "statusline-mkt"))

    def test_unreadable_install_record_falls_back(self):
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        p = os.path.join(self.cfg, "plugins", "installed_plugins.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        for bad in ("{not json", "[]", '{"plugins": {"statusline@m": "x"}}',
                    '{"plugins": {"statusline@m": [7, {"installPath": 7}]}}'):
            with open(p, "w") as f:
                f.write(bad)
            self.assertIsNone(owner.installed_by_record("/m/x.py"))
        os.remove(p)
        os.mkfifo(p)                                  # never opened: no hang
        self.assertIsNone(owner.installed_by_record("/m/x.py"))


if __name__ == "__main__":
    unittest.main()
