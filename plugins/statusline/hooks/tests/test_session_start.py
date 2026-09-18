"""session_start.py: first-run install, takeover, self-heal, owner.json states,
prune, and never raising. Hermetic (helpers.Hermetic); the hook runs as a
subprocess with CLAUDE_PLUGIN_ROOT and CLAUDE_PLUGIN_DATA set, as Claude Code
runs it."""
import json, os, shutil, subprocess, sys, time, unittest

import helpers
import owner
import sensor

HOOK = os.path.join(helpers.HOOKS, "session_start.py")
LEGACY_CMD = "python3 {cfg}/plugins/data/claude-kit-kmacmcfarlane/current-hooks/statusline.py"
PRED_CMD = 'python3 "{cfg}/plugins/data/context-guard-kmacmcfarlane/current-hooks/statusline.py"'
FOREIGN = {"type": "command", "command": "bash ~/bin/my-prompt.sh"}
ENABLED = {"enabledPlugins": {"statusline@kmacmcfarlane": True}}
LEAKS = ("claude-kit", "context-guard", "librarian", "checkpoint", "HARD", "CLAUDE_KIT_")
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
        self.shared = os.path.join(self.proj, ".claude", "settings.json")
        self.local = os.path.join(self.proj, ".claude", "settings.local.json")

    def hook(self, env=None, stdin=None, script=HOOK, sid="s1"):
        """(returncode, the one JSON object printed, stderr)."""
        e = dict(self.env, **(env or {}))
        e = {k: v for k, v in e.items() if v is not None}
        p = subprocess.run([sys.executable, script], cwd=self.proj, env=e,
                           input=stdin if stdin is not None else json.dumps(
                               {"session_id": sid, "cwd": self.proj, "source": "startup"}),
                           capture_output=True, text=True, timeout=30)
        lines = p.stdout.splitlines()
        self.assertEqual(len(lines), 1, p.stdout)
        out = json.loads(lines[0])
        self.assertIsInstance(out, dict)
        for w in LEAKS:
            self.assertNotIn(w, p.stdout)
        return p.returncode, out, p.stderr

    def quiet(self, **kw):
        rc, out, err = self.hook(**kw)
        self.assertEqual((rc, out, err), (0, {}, ""))

    def said(self, **kw):
        rc, out, err = self.hook(**kw)
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(list(out), ["systemMessage"])
        msg = out["systemMessage"]
        self.assertTrue(msg.startswith("statusline: "), msg)
        self.assertNotIn("\n", msg)
        return msg

    def own(self):
        return {"type": "command", "command": owner.command_for(self.data)}

    def load(self, path=None):
        with open(path or self.user) as f:
            return json.load(f)

    def raw(self, path=None):
        with open(path or self.user, "rb") as f:
            return f.read()

    def marker(self):
        with open(os.path.join(self.data, "owner.json")) as f:
            return json.load(f)

    def set_marker(self, state, settings=None):
        os.makedirs(self.data, exist_ok=True)
        owner.write_marker(self.data, state, settings or self.user,
                           owner.command_for(self.data))

    def pred_marker(self, plugin, settings=None):
        d = os.path.join(self.cfg, "plugins", "data", plugin + "-kmacmcfarlane")
        return self.write_json(os.path.join(d, "statusline-installed.json"),
                               {"settings": settings or self.user, "command": "x"})


class FirstRun(Base):
    def test_install_into_user_scope_where_enabled(self):
        self.write_json(self.user, dict(ENABLED, model="opus"))
        msg = self.said()
        self.assertIn(f"status line installed in {self.user}", msg)
        self.assertIn("next session", msg)
        self.assertIn("/install-statusline --remove", msg)
        self.assertEqual(self.load(), dict(ENABLED, model="opus", statusLine=self.own()))
        self.assertEqual((self.marker()["state"], self.marker()["settings"]),
                         ("installed", self.user))
        self.assertTrue(os.path.isfile(os.path.join(self.data, "current-hooks", "statusline.py")))
        self.quiet()                                    # second session: nothing to do
        self.assertEqual(self.load()["statusLine"], self.own())

    def test_empty_config_enabled_nowhere_does_nothing(self):
        self.quiet()
        self.assertFalse(os.path.exists(self.user))
        self.assertFalse(os.path.exists(os.path.join(self.data, "owner.json")))

    def test_enabled_only_in_project_installs_into_local(self):
        for where in (self.shared, self.local):
            with self.subTest(where=where):
                shutil.rmtree(os.path.join(self.proj, ".claude"), ignore_errors=True)
                shutil.rmtree(self.data, ignore_errors=True)
                self.write_json(self.user, {"model": "opus"})
                self.write_json(where, ENABLED)
                shared_before = self.raw(where) if where == self.shared else None
                msg = self.said()
                self.assertIn(f"installed in {self.local}", msg)
                self.assertIn("/install-statusline --local --remove", msg)
                self.assertEqual(self.load(self.local)["statusLine"], self.own())
                self.assertEqual(self.load(), {"model": "opus"})
                if shared_before is not None:
                    self.assertEqual(self.raw(self.shared), shared_before)
                self.assertEqual(self.marker()["settings"], self.local)

    def test_user_scope_wins_over_project(self):
        self.write_json(self.user, ENABLED)
        self.write_json(self.shared, ENABLED)
        self.said()
        self.assertIn("statusLine", self.load())
        self.assertFalse(os.path.exists(self.local))

    def test_disabled_is_not_enabled(self):
        self.write_json(self.user, {"enabledPlugins": {"statusline@kmacmcfarlane": False,
                                                       "other@x": True}})
        self.quiet()
        self.assertNotIn("statusLine", self.load())

    def test_home_as_project_is_user_scope(self):
        # cwd = the config dir's parent: its .claude/settings.json IS the user
        # settings file, so a .claude/settings.local.json there is no project
        home = os.path.join(self.cfg, "home")
        cfg = os.path.join(home, ".claude")
        self.write_json(os.path.join(cfg, "settings.json"), {"model": "opus"})
        self.write_json(os.path.join(cfg, "settings.local.json"), ENABLED)
        self.quiet(env={"CLAUDE_CONFIG_DIR": cfg, "HOME": home, "CLAUDE_PROJECT_DIR": home,
                        "CLAUDE_PLUGIN_DATA": os.path.join(cfg, "plugins", "data", "statusline-k")})
        self.assertEqual(self.load(os.path.join(cfg, "settings.local.json")), ENABLED)
        self.assertEqual(self.load(os.path.join(cfg, "settings.json")), {"model": "opus"})

    def test_never_over_a_foreign_entry(self):
        for where, st in ((self.user, dict(ENABLED, statusLine=FOREIGN)),
                          (self.shared, dict(ENABLED, statusLine=FOREIGN))):
            with self.subTest(where=where):
                shutil.rmtree(os.path.join(self.proj, ".claude"), ignore_errors=True)
                shutil.rmtree(self.data, ignore_errors=True)
                self.write_json(self.user, {} if where != self.user else st)
                if where != self.user:
                    self.write_json(where, st)
                before = self.raw(where)
                msg = self.said()
                self.assertIn("already define a statusLine", msg)
                self.assertIn("and answer yes to replace it", msg)
                self.assertNotIn("--replace", msg)
                self.assertEqual(self.raw(where), before)
                self.assertEqual(self.marker()["state"], "deferred")
                self.assertFalse(os.path.exists(self.local))
                self.quiet()                             # said once
                self.assertEqual(self.raw(where), before)

    def test_foreign_in_user_blocks_a_project_install(self):
        self.write_json(self.user, {"statusLine": FOREIGN})
        self.write_json(self.shared, ENABLED)
        self.assertIn("already define", self.said())
        self.assertFalse(os.path.exists(self.local))

    def test_own_entry_without_marker_is_adopted_silently(self):
        os.makedirs(self.data)
        self.write_json(self.user, dict(ENABLED, statusLine=self.own()))
        before = self.raw()
        self.quiet()
        self.assertEqual(self.raw(), before)
        self.assertEqual(self.marker()["state"], "installed")

    def test_no_install_until_the_script_resolves(self):
        self.write_json(self.user, ENABLED)
        os.makedirs(self.data)
        # a current-hooks name that is a plain file: the link cannot be made
        with open(os.path.join(self.data, "current-hooks"), "w") as f:
            f.write("x")
        os.chmod(self.data, 0o555)
        try:
            self.quiet()
        finally:
            os.chmod(self.data, 0o755)
        self.assertEqual(self.load(), ENABLED)


class Takeover(Base):
    def test_claude_kit_path_without_any_marker(self):
        cmd = LEGACY_CMD.format(cfg=self.cfg)
        self.write_json(self.user, {"model": "opus", "statusLine": {"type": "command",
                                                                     "command": cmd}})
        msg = self.said()
        self.assertEqual(msg, f"statusline: took over an existing status line setting "
                              f"in {self.user}.")
        self.assertEqual(self.load(), {"model": "opus", "statusLine": self.own()})
        self.assertEqual(self.marker()["state"], "installed")
        self.quiet()

    def test_takeover_needs_no_enabledPlugins_entry(self):
        self.write_json(self.user, {"statusLine": {"type": "command",
                                                   "command": PRED_CMD.format(cfg=self.cfg)}})
        self.assertIn("took over", self.said())

    def test_marker_named_file_first_and_markers_retired(self):
        other = os.path.join(self.cfg, "elsewhere", "settings.json")
        self.write_json(other, {"statusLine": {"type": "command",
                                               "command": PRED_CMD.format(cfg=self.cfg)}})
        self.write_json(self.user, {"statusLine": {"type": "command",
                                                   "command": LEGACY_CMD.format(cfg=self.cfg)}})
        a = self.pred_marker("context-guard", settings=other)
        b = self.pred_marker("claude-kit", settings=os.path.join(self.cfg, "gone.json"))
        self.assertIn(f"in {other}", self.said())
        self.assertEqual(self.load(other)["statusLine"], self.own())
        self.assertFalse(os.path.exists(a) or os.path.exists(b))
        self.assertEqual(self.marker()["settings"], other)

    def test_predecessor_in_project_local_is_taken_over(self):
        self.write_json(self.user, {})
        self.write_json(self.shared, ENABLED)
        self.write_json(self.local, {"statusLine": {"type": "command",
                                                    "command": PRED_CMD.format(cfg=self.cfg)}})
        self.assertIn(f"took over an existing status line setting in {self.local}", self.said())
        self.assertEqual(self.load(self.local)["statusLine"], self.own())


class States(Base):
    def test_removed_is_never_re_added(self):
        self.write_json(self.user, ENABLED)
        self.said()
        p = subprocess.run([sys.executable, helpers.INSTALLER, "--remove"], cwd=self.proj,
                           env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.marker()["state"], "removed")
        for _ in range(2):
            self.quiet()
        self.assertEqual(self.load(), ENABLED)

    def test_yielded_and_deferred_are_hands_off(self):
        for state in ("removed", "yielded", "deferred"):
            for st in ({}, dict(ENABLED),
                       {"statusLine": {"type": "command",
                                       "command": LEGACY_CMD.format(cfg=self.cfg)}}):
                with self.subTest(state=state, st=st):
                    self.write_json(self.user, st)
                    self.set_marker(state)
                    before = self.raw()
                    self.quiet()
                    self.assertEqual(self.raw(), before)
                    self.assertEqual(self.marker()["state"], state)

    def test_unreadable_marker_is_hands_off(self):
        self.write_json(self.user, ENABLED)
        os.makedirs(self.data)
        for raw in ("{bad", '{"v": 2, "state": "installed"}', "[]"):
            with self.subTest(raw=raw):
                self.write_json(os.path.join(self.data, "owner.json"), raw=raw)
                self.quiet()
                self.assertEqual(self.load(), ENABLED)


class Heal(Base):
    def setUp(self):
        super().setUp()
        self.write_json(self.user, dict(ENABLED, model="opus"))
        self.said()

    def test_restores_a_dropped_entry(self):
        self.write_json(self.user, dict(ENABLED, model="opus"))   # a stale session's write
        msg = self.said()
        self.assertIn(f"restored the status line in {self.user}", msg)
        self.assertEqual(self.load()["statusLine"], self.own())
        self.quiet()

    def test_repoints_a_predecessor_put_back_by_an_older_heal(self):
        self.write_json(self.user, {"statusLine": {"type": "command",
                                                   "command": PRED_CMD.format(cfg=self.cfg)}})
        self.assertIn("took over", self.said())
        self.assertEqual(self.load()["statusLine"], self.own())

    def test_foreign_yields_once(self):
        self.write_json(self.user, {"statusLine": FOREIGN})
        msg = self.said()
        self.assertIn("changed by something else; left alone", msg)
        self.assertIn("run /install-statusline and answer yes to replace it", msg)
        self.assertNotIn("--replace", msg)
        self.assertEqual(self.marker()["state"], "yielded")
        self.quiet()
        self.write_json(self.user, {})               # even when it goes away later
        self.quiet()
        self.assertEqual(self.load(), {})

    def test_missing_settings_file_is_not_recreated(self):
        os.remove(self.user)
        self.quiet()
        self.assertFalse(os.path.exists(self.user))

    def test_restore_keeps_a_hand_formatted_file(self):
        text = ('{\n    "model": "opus",\n  "permissions": {"allow": ["Bash(ls)"]},\n'
                '\t"enabledPlugins": {"statusline@kmacmcfarlane": true}\n}\n')
        self.write_json(self.user, raw=text)
        self.said()
        with open(self.user) as f:
            new = f.read()
        self.assertTrue(new.startswith(text[:-3]), new)   # every original byte kept
        self.assertEqual(self.load()["statusLine"], self.own())

    @ROOT_SKIP
    def test_read_only_settings_block_the_restore_once(self):
        self.write_json(self.user, ENABLED)
        os.chmod(self.user, 0o444)
        try:
            before = self.raw()
            msg = self.said()
            self.assertIn(f"{self.user} is read-only; status line not restored", msg)
            self.assertIn("Make it writable", msg)
            self.assertEqual((self.marker()["state"], self.marker()["resume"]),
                             ("blocked", "installed"))
            self.quiet()
            self.assertEqual(self.raw(), before)
        finally:
            os.chmod(self.user, 0o644)
        self.assertIn("restored the status line", self.said())
        self.assertEqual(self.marker()["state"], "installed")


class Blocked(Base):
    @ROOT_SKIP
    def test_read_only_user_settings_said_once_then_retried(self):
        self.write_json(self.user, ENABLED)
        os.chmod(self.user, 0o444)
        try:
            msg = self.said()
            self.assertEqual(msg, f"statusline: {self.user} is read-only; status line not "
                                  f"installed. Make it writable, then start a new session, "
                                  f"or run /install-statusline.")
            m = self.marker()
            self.assertEqual((m["state"], m["reason"], m["resume"], m["settings"]),
                             ("blocked", "read-only", "new", self.user))
            self.quiet()
            self.quiet()
            self.assertEqual(self.load(), ENABLED)
        finally:
            os.chmod(self.user, 0o644)
        self.assertIn("status line installed", self.said())
        self.assertEqual(self.load()["statusLine"], self.own())

    def test_invalid_user_settings_said_once_then_retried(self):
        self.write_json(self.user, raw='{"enabledPlugins": {')
        msg = self.said()
        self.assertIn("is not valid JSON; status line not installed. Fix it", msg)
        self.assertEqual(self.marker()["reason"], "invalid")
        self.quiet()
        self.write_json(self.user, ENABLED)
        self.assertIn("status line installed", self.said())

    def test_empty_settings_file_is_an_empty_object(self):
        self.write_json(self.user, raw="")
        self.quiet()                                    # nothing enables it
        self.assertFalse(os.path.exists(os.path.join(self.data, "owner.json")))

    def test_removed_while_blocked_stays_removed(self):
        self.write_json(self.user, raw="{bad")
        self.said()
        self.write_json(self.user, ENABLED)
        p = subprocess.run([sys.executable, helpers.INSTALLER, "--remove"], cwd=self.proj,
                           env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.quiet()
        self.assertEqual(self.load(), ENABLED)


@unittest.skipUnless(shutil.which("git"), "git not installed")
class GitIgnore(Base):
    def git(self, *args):
        subprocess.run(["git", "-C", self.proj, *args], env=self.env, check=True,
                       capture_output=True, timeout=30)

    def setUp(self):
        super().setUp()
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        self.git("init", "-q")
        self.write_json(self.user, {})
        self.write_json(self.shared, ENABLED)

    def test_not_ignored_local_file_is_never_created(self):
        msg = self.said()
        self.assertIn(f"{self.local} is not git-ignored", msg)
        self.assertIn("Add .claude/settings.local.json to .gitignore", msg)
        self.assertIn("run /install-statusline to install it in your user settings", msg)
        self.assertFalse(os.path.exists(self.local))
        self.assertEqual(self.marker()["reason"], "not-ignored")
        self.quiet()
        self.assertFalse(os.path.exists(self.local))
        with open(os.path.join(self.proj, ".gitignore"), "w") as f:
            f.write(".claude/settings.local.json\n")
        self.assertIn(f"status line installed in {self.local}", self.said())
        self.assertEqual(self.load(self.local)["statusLine"], self.own())

    def test_ignored_local_file_is_installed(self):
        with open(os.path.join(self.proj, ".gitignore"), "w") as f:
            f.write("settings.local.json\n")
        self.assertIn("installed", self.said())

    def test_a_tracked_local_file_is_not_written(self):
        self.write_json(self.local, {"model": "opus"})
        self.git("add", "-f", ".claude/settings.local.json")
        self.git("commit", "-qm", "x")
        before = self.raw(self.local)
        self.assertIn("is not git-ignored", self.said())
        self.assertEqual(self.raw(self.local), before)

    def test_outside_a_repo_installs(self):
        shutil.rmtree(os.path.join(self.proj, ".git"))
        self.assertIn("installed", self.said())


class NeverRaises(Base):
    def test_malformed_settings(self):
        for raw in ("{bad", "[1]", "", "null", '{"enabledPlugins": [1]}',
                    '{"enabledPlugins": {"statusline@x": true}, "statusLine": 7}'):
            with self.subTest(raw=raw):
                shutil.rmtree(self.data, ignore_errors=True)
                self.write_json(self.user, raw=raw)
                rc, out, err = self.hook()
                self.assertEqual((rc, err), (0, ""))
                if raw.startswith('{"enabledPlugins": {"statusline@x"'):
                    self.assertIn("already define", out.get("systemMessage", ""))
                elif raw in ("{bad", "[1]", "null"):
                    self.assertIn(f"{self.user} is not valid JSON; status line not "
                                  f"installed", out.get("systemMessage", ""))
                    with open(self.user) as f:
                        self.assertEqual(f.read(), raw)
                else:
                    self.assertEqual(out, {})
                    with open(self.user) as f:
                        self.assertEqual(f.read(), raw)

    def test_malformed_stdin(self):
        for stdin in ("", "not json", "[]", '{"session_id": ["x"], "cwd": 5}'):
            with self.subTest(stdin=stdin):
                rc, out, err = self.hook(stdin=stdin)
                self.assertEqual((rc, err), (0, ""))

    @ROOT_SKIP
    def test_read_only_config_dir(self):
        self.write_json(self.user, ENABLED)
        os.makedirs(self.data)
        os.chmod(self.cfg, 0o555)
        try:
            self.assertIn("could not be written; status line not installed", self.said())
            self.quiet()
        finally:
            os.chmod(self.cfg, 0o755)
        self.assertEqual(self.load(), ENABLED)
        self.assertEqual(self.marker()["reason"], "unwritable")

    @ROOT_SKIP
    def test_data_dir_cannot_be_created(self):
        self.write_json(self.user, ENABLED)
        ro = os.path.join(self.cfg, "ro")
        os.makedirs(ro)
        os.chmod(ro, 0o555)
        try:
            self.quiet(env={"CLAUDE_PLUGIN_DATA": os.path.join(ro, "statusline-x")})
        finally:
            os.chmod(ro, 0o755)
        self.assertEqual(self.load(), ENABLED)

    def test_no_data_dir_at_all(self):
        self.write_json(self.user, ENABLED)
        e = {"CLAUDE_PLUGIN_DATA": None, "CLAUDE_PLUGIN_ROOT": None}
        src = os.path.dirname(os.path.dirname(self.plain_copy()))
        script = os.path.join(os.path.dirname(os.path.dirname(src)), "hooks",
                              "session_start.py")
        self.assertTrue(os.path.isfile(script), script)
        self.quiet(env=e, script=script)
        self.assertEqual(self.load(), ENABLED)

    def test_data_dir_derived_from_an_installed_cache_path(self):
        cache = os.path.join(self.cfg, "plugins", "cache", "mkt", "statusline", "1.0.0")
        shutil.copytree(helpers.PLUGIN, cache,
                        ignore=shutil.ignore_patterns("__pycache__", "tests"))
        self.write_json(self.user, ENABLED)
        rc, out, _ = self.hook(env={"CLAUDE_PLUGIN_DATA": None},
                               script=os.path.join(cache, "hooks", "session_start.py"))
        self.assertEqual(rc, 0)
        self.assertIn("installed", out["systemMessage"])
        self.assertIn("statusline-mkt/current-hooks/statusline.py",
                      self.load()["statusLine"]["command"])


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
    def test_a_quiet_session_start_is_fast(self):
        self.write_json(self.user, ENABLED)
        self.said()
        t = time.monotonic()
        self.quiet()
        self.assertLess(time.monotonic() - t, 2.0)


if __name__ == "__main__":
    unittest.main()
