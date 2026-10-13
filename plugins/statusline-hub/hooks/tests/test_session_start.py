"""session_start.py: owner states, first-run install, the takeover from the
statusline plugin (only once it draws as a hub hook), self-heal, blocked
files, and the prune pass. Hermetic; the hook runs as a subprocess with
CLAUDE_PLUGIN_ROOT and CLAUDE_PLUGIN_DATA set, as Claude Code runs it."""
import json, os, stat, subprocess, sys, time, unittest

import helpers
import owner

HOOK = os.path.join(helpers.HOOKS, "session_start.py")
FOREIGN = {"type": "command", "command": "bash ~/bin/my-prompt.sh"}
HUB_ON = {"enabledPlugins": {"statusline-hub@kmacmcfarlane": True}}
BOTH_ON = {"enabledPlugins": {"statusline-hub@kmacmcfarlane": True,
                              "statusline@kmacmcfarlane": True}}
ROOT_SKIP = unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes anything")


class Base(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        self.data = os.path.join(self.cfg, "plugins", "data", "statusline-hub-kmacmcfarlane")
        self.sl_data = os.path.join(self.cfg, "plugins", "data", "statusline-kmacmcfarlane")
        self.env["CLAUDE_PLUGIN_DATA"] = self.data
        self.env["CLAUDE_PLUGIN_ROOT"] = helpers.PLUGIN
        self.proj = os.path.join(self.cfg, "proj")
        os.makedirs(self.proj)
        self.env["CLAUDE_PROJECT_DIR"] = self.proj
        for k in [k for k in self.env if k.startswith("GIT_")]:
            self.env.pop(k)   # an outer repo's GIT_DIR would answer for the temp repos
        self.user = os.path.join(self.cfg, "settings.json")

    def hook(self, sid="s1"):
        p = subprocess.run([sys.executable, HOOK], cwd=self.proj, env=self.env,
                           input=json.dumps({"session_id": sid, "cwd": self.proj}),
                           capture_output=True, text=True, timeout=30)
        lines = p.stdout.splitlines()
        self.assertEqual((p.returncode, p.stderr, len(lines)), (0, "", 1), p.stdout)
        out = json.loads(lines[0])
        self.assertIsInstance(out, dict)
        return out

    def quiet(self):
        self.assertEqual(self.hook(), {})

    def said(self):
        out = self.hook()
        self.assertEqual(list(out), ["systemMessage"])
        msg = out["systemMessage"]
        self.assertTrue(msg.startswith("statusline-hub: "), msg)
        self.assertNotIn("\n", msg)
        return msg

    def own(self):
        return {"type": "command", "command": owner.command_for(self.data)}

    def sl_entry(self):
        return {"type": "command", "command": 'python3 "%s/current-hooks/statusline.py"'
                % self.sl_data}

    def sl_marker(self, state, settings=None):
        os.makedirs(self.sl_data, exist_ok=True)
        self.write_json(os.path.join(self.sl_data, "owner.json"),
                        {"v": 1, "state": state, "settings": settings or self.user,
                         "command": self.sl_entry()["command"], "at": 1})

    def sl_hooked(self):
        self.manifest("statusline", ["python3", "/x/statusline.py", "--segment"])

    def load(self, path=None):
        with open(path or self.user) as f:
            return json.load(f)

    def raw(self, path=None):
        with open(path or self.user, "rb") as f:
            return f.read()

    def marker(self):
        p = os.path.join(self.data, "owner.json")
        if not os.path.exists(p):
            return None
        with open(p) as f:
            return json.load(f)


class FirstRun(Base):
    def test_takes_a_free_slot_where_enabled(self):
        self.write_json(self.user, raw='{\n    "model": "opus",\n    "enabledPlugins": '
                        '{"statusline-hub@kmacmcfarlane": true}\n}\n')
        msg = self.said()
        self.assertIn("status line slot taken in", msg)
        d = self.load()
        self.assertEqual(d["statusLine"], self.own())
        self.assertEqual(d["model"], "opus")
        self.assertTrue(self.raw().startswith(b'{\n    "model": "opus",\n'))
        self.assertEqual(self.marker()["state"], "installed")
        self.assertTrue(os.path.isfile(os.path.join(self.data, "current-hooks", "hub.py")))
        self.quiet()  # installed: nothing more to say

    def test_not_enabled_anywhere_does_nothing(self):
        self.write_json(self.user, {"model": "opus"})
        self.quiet()
        self.assertNotIn("statusLine", self.load())
        self.assertIsNone(self.marker())

    def test_foreign_statusline_is_deferred_once(self):
        self.write_json(self.user, dict(HUB_ON, statusLine=FOREIGN))
        before = self.raw()
        msg = self.said()
        self.assertIn("/statusline-hub", msg)
        self.assertIn("/install-statusline-hub", msg)
        self.assertNotIn("my-prompt", msg)  # a path is named, never a value
        self.assertEqual(self.raw(), before)
        self.assertEqual(self.marker()["state"], "deferred")
        self.quiet()

    def test_statusline_entry_waits_until_it_draws_as_a_hook(self):
        self.write_json(self.user, dict(BOTH_ON, statusLine=self.sl_entry()))
        self.sl_marker("installed")
        before = self.raw()
        for _ in range(2):
            self.quiet()
            self.assertEqual(self.raw(), before)
            self.assertIsNone(self.marker())
        self.sl_hooked()
        msg = self.said()
        self.assertIn("took over the status line slot", msg)
        self.assertEqual(self.load()["statusLine"], self.own())
        self.assertEqual(self.marker()["state"], "installed")

    def test_takeover_follows_statuslines_marker_to_another_file(self):
        other = os.path.join(self.cfg, "elsewhere.json")
        self.write_json(other, {"statusLine": self.sl_entry(), "keep": 1})
        self.write_json(self.user, {"model": "opus"})
        self.sl_marker("installed", settings=other)
        self.sl_hooked()
        self.said()
        self.assertEqual(self.load(other), {"statusLine": self.own(), "keep": 1})

    def test_does_not_race_statusline_for_an_empty_slot(self):
        self.write_json(self.user, BOTH_ON)
        self.quiet()  # statusline has not run yet: its turn
        self.assertNotIn("statusLine", self.load())
        self.sl_marker("installed")
        self.quiet()
        self.sl_marker("removed")  # the user removed statusline's line: kept empty
        msg = self.said()
        self.assertIn("footer was removed from", msg)
        self.assertNotIn("statusLine", self.load())
        self.assertEqual(self.marker()["state"], "removed")
        self.quiet()
        self.assertNotIn("statusLine", self.load())

    def records(self, *roots):
        """installed_plugins.json recording a statusline install at each root."""
        self.write_json(os.path.join(self.cfg, "plugins", "installed_plugins.json"),
                        {"version": 2, "plugins": {"statusline@kmacmcfarlane": [
                            {"scope": "user", "installPath": r} for r in roots]}})

    def fake_statusline(self, name, owner_py):
        root = os.path.join(self.cfg, "plugins", "cache", "kmacmcfarlane", "statusline", name)
        os.makedirs(os.path.join(root, "hooks"))
        if owner_py:
            self.write_json(os.path.join(root, "hooks", "owner.py"), raw="")
        return root

    def test_no_wait_when_no_installed_statusline_can_install_itself(self):
        # a fresh machine, the hub's hook first: the installed footer only
        # registers as a hook, so there is nothing to wait for
        self.write_json(self.user, BOTH_ON)
        self.records(self.fake_statusline("2.0.0", owner_py=False))
        msg = self.said()
        self.assertIn("status line slot taken", msg)
        self.assertIn("draws the statusline footer", msg)   # it registers this session
        self.assertNotIn("blank line", msg)
        self.assertEqual(self.load()["statusLine"], self.own())

    def test_a_disabled_statusline_gets_no_footer_wording(self):
        self.write_json(self.user, HUB_ON)
        self.records(self.fake_statusline("2.0.0", owner_py=False))
        msg = self.said()
        self.assertIn("status line slot taken", msg)
        self.assertIn("blank line until one registers", msg)
        self.assertIn("enable the statusline plugin", msg)

    def test_a_hub_only_install_names_the_statusline_plugin_once(self):
        self.write_json(self.user, HUB_ON)
        self.write_json(os.path.join(self.cfg, "plugins", "installed_plugins.json"),
                        {"version": 2, "plugins": {"statusline-hub@other-mkt": [
                            {"scope": "user", "installPath": "/x/hub"}]}})
        msg = self.said()
        self.assertIn("blank line until one registers", msg)
        self.assertIn("/plugin install statusline@other-mkt", msg)   # its marketplace
        self.quiet()

    def test_waits_while_an_installed_statusline_can_install_itself(self):
        self.write_json(self.user, BOTH_ON)
        self.records(self.fake_statusline("2.0.0", owner_py=False),
                     self.fake_statusline("1.0.0", owner_py=True))
        self.quiet()
        self.assertNotIn("statusLine", self.load())

    def test_empty_slot_taken_when_statusline_is_hooked(self):
        self.write_json(self.user, BOTH_ON)
        self.sl_hooked()
        self.said()
        self.assertEqual(self.load()["statusLine"], self.own())

    def test_adopts_its_own_entry_when_the_marker_is_lost(self):
        self.write_json(self.user, dict(HUB_ON, statusLine=self.own()))
        self.quiet()
        self.assertEqual(self.marker()["state"], "installed")

    def test_project_local_install_only_when_git_ignored(self):
        self.write_json(self.user, {})
        shared = os.path.join(self.proj, ".claude", "settings.json")
        local = os.path.join(self.proj, ".claude", "settings.local.json")
        self.write_json(shared, HUB_ON)
        self.said()
        self.assertEqual(self.load(local)["statusLine"], self.own())
        self.assertNotIn("statusLine", self.load(shared))

    def test_project_local_not_ignored_by_git_is_blocked(self):
        subprocess.run(["git", "init", "-q", self.proj], check=True, env=self.env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.write_json(self.user, {})
        self.write_json(os.path.join(self.proj, ".claude", "settings.json"), HUB_ON)
        self.assertIn("is not git-ignored", self.said())
        self.assertFalse(os.path.exists(os.path.join(self.proj, ".claude",
                                                     "settings.local.json")))
        self.assertEqual(self.marker()["state"], "blocked")

    def test_invalid_settings_blocked_once(self):
        self.write_json(self.user, raw="{not json")
        msg = self.said()
        self.assertIn("is not valid JSON", msg)
        self.assertEqual(self.marker()["state"], "blocked")
        self.quiet()
        self.write_json(self.user, HUB_ON)  # fixed: the retry installs
        self.hook()
        self.assertEqual(self.load()["statusLine"], self.own())

    @ROOT_SKIP
    def test_read_only_settings_blocked(self):
        self.write_json(self.user, HUB_ON)
        os.chmod(self.user, 0o444)
        self.assertIn("is read-only", self.said())
        self.assertNotIn("statusLine", self.load())


class TrackedProjectSettings(Base):
    """A footer entry in a project's .claude/settings.json (the old
    installer's --project): when git tracks that file the hub refuses to put
    its machine-specific absolute path there and leaves the file as it is;
    an untracked one, and the user settings file even when tracked, are
    taken as before."""
    HUB_ONLY_RECORDS = {"version": 2, "plugins": {"statusline-hub@kmacmcfarlane": [
        {"scope": "user", "installPath": "/x/statusline-hub"}]}}

    def setUp(self):
        super().setUp()
        self.shared = os.path.join(self.proj, ".claude", "settings.json")
        self.write_json(self.user, {})
        self.write_json(os.path.join(self.cfg, "plugins", "installed_plugins.json"),
                        self.HUB_ONLY_RECORDS)

    def dead_copy(self):
        """context-guard's older footer copy, its plugin gone (no data dir)."""
        cg = os.path.join(self.cfg, "plugins", "data", "context-guard-kmacmcfarlane")
        return {"type": "command",
                "command": 'python3 "%s/current-hooks/statusline.py"' % cg}

    def git(self, *args, repo=None):
        subprocess.run(["git", "-C", repo or self.proj] + list(args), check=True,
                       env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def taken_then_tracked(self):
        """The hub's entry in the project's shared file (taken over while it
        was untracked), and then the file committed."""
        self.write_json(self.shared, dict(HUB_ON, statusLine=self.dead_copy()))
        self.git("init", "-q")
        self.assertIn("took over the status line slot", self.said())
        self.git("add", ".claude/settings.json")

    def test_a_dead_copy_in_a_tracked_project_file_is_refused(self):
        self.write_json(self.shared, dict(HUB_ON, statusLine=self.dead_copy()))
        self.git("init", "-q")
        self.git("add", ".claude/settings.json")
        before = self.raw(self.shared)
        msg = self.said()
        self.assertIn("is tracked by git", msg)
        self.assertIn(self.shared, msg)
        self.assertEqual(self.raw(self.shared), before)
        self.assertEqual(self.marker()["state"], "blocked")
        self.assertEqual(self.marker()["reason"], "tracked")
        self.quiet()  # said once; retried quietly
        self.assertEqual(self.raw(self.shared), before)

    def test_a_footer_entry_in_a_tracked_project_file_is_not_taken_over(self):
        self.write_json(self.shared, dict(HUB_ON, statusLine=self.sl_entry()))
        self.sl_marker("installed", settings=self.shared)
        self.sl_hooked()
        self.git("init", "-q")
        self.git("add", ".claude/settings.json")
        before = self.raw(self.shared)
        msg = self.said()
        self.assertIn("is tracked by git", msg)
        self.assertIn("/install-statusline-hub --local", msg)
        self.assertEqual(self.raw(self.shared), before)
        self.assertEqual(self.marker()["reason"], "tracked")
        self.quiet()
        self.assertEqual(self.raw(self.shared), before)

    def test_a_force_added_local_file_is_named_as_tracked(self):
        local = os.path.join(self.proj, ".claude", "settings.local.json")
        self.write_json(self.shared, HUB_ON)
        self.write_json(local, {})
        self.git("init", "-q")
        self.write_json(os.path.join(self.proj, ".gitignore"),
                        raw=".claude/settings.local.json\n")
        self.git("add", "-f", ".claude/settings.local.json")
        before = self.raw(local)
        self.assertIn("is tracked by git", self.said())
        self.assertEqual(self.raw(local), before)
        self.assertEqual(self.marker()["reason"], "tracked")

    def test_heal_does_not_replace_a_committed_footer_entry_git_brings_back(self):
        self.taken_then_tracked()
        self.sl_hooked()
        # e.g. a checkout of the team's commit puts the footer's entry back
        self.write_json(self.shared, dict(HUB_ON, statusLine=self.sl_entry()))
        before = self.raw(self.shared)
        msg = self.said()
        self.assertIn("is tracked by git", msg)
        self.assertIn("not restored", msg)
        self.assertEqual(self.raw(self.shared), before)
        self.assertEqual(self.marker()["reason"], "tracked")
        self.quiet()
        self.assertEqual(self.raw(self.shared), before)

    def test_heal_does_not_fight_a_git_revert_that_drops_the_entry(self):
        self.taken_then_tracked()
        self.write_json(self.shared, HUB_ON)   # the revert: no statusLine
        before = self.raw(self.shared)
        self.assertIn("is tracked by git", self.said())
        for _ in range(2):
            self.assertEqual(self.raw(self.shared), before)
            self.quiet()
        self.assertNotIn("statusLine", self.load(self.shared))

    def test_heal_of_an_explicit_project_install_names_project(self):
        self.write_json(self.shared, HUB_ON)
        self.git("init", "-q")
        self.git("add", ".claude/settings.json")
        owner.write_marker(self.data, "installed", self.shared,
                           owner.command_for(self.data), scope="project")
        before = self.raw(self.shared)
        msg = self.said()
        self.assertIn("is tracked by git", msg)
        self.assertIn("/install-statusline-hub --project again", msg)
        self.assertEqual(self.raw(self.shared), before)

    def test_an_explicit_project_install_keeps_its_scope_through_a_heal(self):
        self.write_json(self.shared, dict(HUB_ON, statusLine=self.own()))
        self.git("init", "-q")   # a repo, the file not yet added
        owner.write_marker(self.data, "installed", self.shared,
                           owner.command_for(self.data), scope="project")
        self.write_json(self.shared, HUB_ON)   # a stale write drops the entry
        self.assertIn("restored the status line", self.said())
        self.assertEqual(self.load(self.shared)["statusLine"], self.own())
        self.assertEqual(self.marker()["scope"], "project")
        self.git("add", ".claude/settings.json")
        self.write_json(self.shared, HUB_ON)   # dropped again, the file now tracked
        before = self.raw(self.shared)
        msg = self.said()
        self.assertIn("is tracked by git", msg)
        self.assertIn("/install-statusline-hub --project again", msg)
        self.assertEqual(self.raw(self.shared), before)
        self.assertEqual(self.marker()["state"], "blocked")
        self.assertEqual(self.marker()["scope"], "project")
        self.quiet()

    def test_a_git_timeout_waits_for_the_next_session(self):
        fake = os.path.join(self.cfg, "bin")
        os.makedirs(fake)
        with open(os.path.join(fake, "git"), "w") as f:
            f.write("#!/bin/sh\nsleep 10\n")
        os.chmod(os.path.join(fake, "git"), 0o755)
        self.write_json(self.shared, dict(HUB_ON, statusLine=self.dead_copy()))
        before = self.raw(self.shared)
        self.env["PATH"] = fake + os.pathsep + self.env.get("PATH", "")
        self.quiet()
        self.assertEqual(self.raw(self.shared), before)
        self.assertIsNone(self.marker())

    def test_a_dead_copy_in_an_untracked_project_file_is_taken(self):
        self.write_json(self.shared, dict(HUB_ON, statusLine=self.dead_copy()))
        self.git("init", "-q")  # a repo, the file not added
        msg = self.said()
        self.assertIn("took over the status line slot", msg)
        self.assertEqual(self.load(self.shared)["statusLine"], self.own())
        self.assertEqual(self.marker()["state"], "installed")

    def test_a_dead_copy_in_a_tracked_user_settings_file_is_taken(self):
        self.write_json(self.user, dict(HUB_ON, statusLine=self.dead_copy()))
        self.git("init", "-q", repo=self.cfg)
        self.git("add", "settings.json", repo=self.cfg)
        msg = self.said()
        self.assertIn("took over the status line slot", msg)
        self.assertEqual(self.load()["statusLine"], self.own())


class Heal(Base):
    def install(self, extra=None):
        self.write_json(self.user, dict(HUB_ON, **(extra or {})))
        self.said()

    def test_restores_a_dropped_entry(self):
        self.install()
        d = self.load()
        del d["statusLine"]
        self.write_json(self.user, d)
        self.assertIn("restored the status line", self.said())
        self.assertEqual(self.load()["statusLine"], self.own())

    def test_yields_to_a_foreign_entry(self):
        self.install()
        self.write_json(self.user, dict(HUB_ON, statusLine=FOREIGN))
        before = self.raw()
        self.assertIn("changed by something else", self.said())
        self.assertEqual(self.raw(), before)
        self.assertEqual(self.marker()["state"], "yielded")
        self.quiet()

    def test_a_stale_write_back_of_the_footers_entry_is_repointed(self):
        # an older session read settings before the takeover and wrote them back
        self.install()
        self.sl_hooked()
        self.write_json(self.user, dict(BOTH_ON, statusLine=self.sl_entry(), model="opus"))
        msg = self.said()
        self.assertIn("restored the status line", msg)
        self.assertNotIn("changed by something else", msg)
        self.assertEqual(self.load(), dict(BOTH_ON, statusLine=self.own(), model="opus"))
        self.assertEqual(self.marker()["state"], "installed")
        self.quiet()

    def test_the_footers_entry_waits_while_the_footer_is_not_a_hook(self):
        self.install()
        self.write_json(self.user, dict(BOTH_ON, statusLine=self.sl_entry()))
        before = self.raw()
        for _ in range(2):
            self.quiet()          # it still draws the footer: never yielded
            self.assertEqual(self.raw(), before)
            self.assertEqual(self.marker()["state"], "installed")
        self.sl_hooked()
        self.assertIn("restored the status line", self.said())
        self.assertEqual(self.load()["statusLine"], self.own())

    HUB_REC = {"statusline-hub@kmacmcfarlane": [{"scope": "user", "installPath": "/x/hub"}]}

    def plugin_records(self, plugins):
        """installed_plugins.json with this `plugins` object."""
        self.write_json(os.path.join(self.cfg, "plugins", "installed_plugins.json"),
                        {"version": 2, "plugins": plugins})

    def footer_entry_back(self, plugins):
        self.install()
        self.plugin_records(plugins)
        self.write_json(self.user, dict(HUB_ON, statusLine=self.sl_entry()))
        return self.raw()

    def test_the_footers_entry_is_taken_back_once_statusline_is_gone(self):
        # a stale footer entry, the records name the hub and no statusline, and
        # its data dir is gone: nothing will ever register and the entry draws
        # nothing, so the hub takes the slot back rather than wait or yield
        self.footer_entry_back(dict(self.HUB_REC))
        msg = self.said()
        self.assertIn("took back the status line slot", msg)
        self.assertIn("footer's entry", msg)
        self.assertIn("no longer installed", msg)
        self.assertIn("/plugin install statusline@kmacmcfarlane", msg)
        self.assertIn(self.user, msg)
        self.assertNotIn(self.sl_entry()["command"], msg)   # a path, never the value
        self.assertEqual(self.load()["statusLine"], self.own())
        self.assertEqual(self.marker()["state"], "installed")
        self.quiet()

    def cg_entry(self):
        """context-guard's old footer entry, its current-hooks resolving to a
        version that no longer ships statusline.py (a95a removed the copy)."""
        cg = os.path.join(self.cfg, "plugins", "data", "context-guard-kmacmcfarlane")
        hooks = os.path.join(self.cfg, "cg-new", "hooks")
        os.makedirs(hooks)
        os.makedirs(cg, exist_ok=True)
        os.symlink(hooks, os.path.join(cg, "current-hooks"))
        return {"type": "command",
                "command": 'python3 "%s/current-hooks/statusline.py"' % cg}

    def test_a_context_guard_entry_without_its_copy_is_taken_back(self):
        # the footer is not registered: heal takes the slot back
        self.install()
        self.plugin_records(dict(self.HUB_REC, **{
            "context-guard@kmacmcfarlane": [{"scope": "user", "installPath": "/x/cg"}]}))
        self.write_json(self.user, dict(HUB_ON, statusLine=self.cg_entry()))
        msg = self.said()
        self.assertIn("took back the status line slot", msg)
        self.assertIn("no longer ships it", msg)
        self.assertEqual(self.load()["statusLine"], self.own())
        self.quiet()

    def test_a_context_guard_entry_is_repointed_once_the_footer_is_hooked(self):
        # the footer is registered: heal restores the hub's entry
        self.install()
        self.sl_hooked()
        self.write_json(self.user, dict(BOTH_ON, statusLine=self.cg_entry()))
        self.assertIn("restored the status line", self.said())
        self.assertEqual(self.load()["statusLine"], self.own())

    def project_scoped(self):
        """The scope the installer records for a project's shared file, here
        on the user file: heal carries the field whatever the path."""
        owner.write_marker(self.data, "installed", self.user,
                           owner.command_for(self.data), scope="project")

    def test_repointing_the_footers_entry_keeps_the_project_scope(self):
        self.install()
        self.project_scoped()
        self.sl_hooked()
        self.write_json(self.user, dict(BOTH_ON, statusLine=self.sl_entry()))
        self.assertIn("restored the status line", self.said())
        self.assertEqual(self.load()["statusLine"], self.own())
        self.assertEqual(self.marker()["state"], "installed")
        self.assertEqual(self.marker()["scope"], "project")

    def test_taking_back_an_older_copy_keeps_the_project_scope(self):
        self.footer_entry_back(dict(self.HUB_REC))
        self.project_scoped()
        self.assertIn("took back the status line slot", self.said())
        self.assertEqual(self.load()["statusLine"], self.own())
        self.assertEqual(self.marker()["state"], "installed")
        self.assertEqual(self.marker()["scope"], "project")

    def test_the_footers_entry_still_drawing_is_said_once_never_yielded(self):
        # statusline uninstalled with its data kept: the entry still draws
        os.makedirs(os.path.join(self.sl_data, "current-hooks"))
        self.write_json(os.path.join(self.sl_data, "current-hooks", "statusline.py"), raw="")
        before = self.footer_entry_back(dict(self.HUB_REC))
        msg = self.said()
        self.assertIn("left alone while it draws", msg)
        self.assertIn("/plugin install statusline@kmacmcfarlane", msg)
        self.assertNotIn(self.sl_entry()["command"], msg)
        for _ in range(2):
            self.assertEqual(self.raw(), before)
            self.assertEqual(self.marker()["state"], "installed")
            self.quiet()
        self.sl_hooked()                     # statusline installed again: taken back
        self.assertIn("restored the status line", self.said())
        self.assertEqual(self.load()["statusLine"], self.own())

    def waits(self, plugins):
        """Unsure whether statusline is uninstalled: the footer's entry waits."""
        before = self.footer_entry_back(plugins)
        self.quiet()
        self.assertEqual(self.raw(), before)
        self.assertEqual(self.marker()["state"], "installed")

    SL = "statusline@kmacmcfarlane"

    def test_the_footers_entry_waits_while_statusline_is_installed(self):
        self.waits(dict(self.HUB_REC, **{self.SL: [{"scope": "user", "installPath": "/x/sl"}]}))

    def test_the_footers_entry_waits_on_a_v1_shaped_statusline_record(self):
        self.waits(dict(self.HUB_REC, **{self.SL: {"installPath": "/x/sl"}}))

    def test_the_footers_entry_waits_on_an_empty_statusline_record(self):
        self.waits(dict(self.HUB_REC, **{self.SL: []}))

    def test_the_footers_entry_waits_on_empty_records(self):
        self.waits({})

    def test_the_footers_entry_waits_when_the_records_do_not_name_the_hub(self):
        self.waits({"other@kmacmcfarlane": [{"scope": "user", "installPath": "/x/o"}]})

    def test_removed_stays_removed(self):
        self.install()
        owner.write_marker(self.data, "removed", self.user, owner.command_for(self.data))
        self.write_json(self.user, HUB_ON)
        self.quiet()
        self.assertNotIn("statusLine", self.load())


class Prune(Base):
    def test_prunes_dead_manifests_sensor_records_cache_and_logs(self):
        old = time.time() - 40 * 86400
        dead = self.manifest("dead", ["true"])
        live = self.manifest("live", ["true"])
        pinned = self.manifest("pinned", ["true"], pinned=True)
        rec = self.write_json(self.sensor_file("gone"), {"v": 1})
        mine = self.write_json(self.sensor_file("s1"), {"v": 1})
        cache = self.write_json(os.path.join(self.cfg, "statusline-hub", "cache", "dead",
                                             "x.json"), {"at": 1, "text": "t"})
        log = self.write_json(os.path.join(self.cfg, "statusline-hub", "log", "dead.log"),
                              raw="x")
        for p in (dead, rec, mine, cache, log, pinned):
            os.utime(p, (old, old))
        self.quiet()
        for p in (dead, rec, cache, log):
            self.assertFalse(os.path.exists(p), p)
        self.assertFalse(os.path.exists(os.path.dirname(cache)))
        self.assertTrue(os.path.exists(live))
        self.assertTrue(os.path.exists(pinned))  # hand-written and pinned: kept
        self.assertTrue(os.path.exists(mine))  # the current session's record stays

    def test_creates_a_private_hooks_dir(self):
        self.quiet()
        d = os.path.join(self.cfg, "statusline-hub", "hooks.d")
        self.assertEqual(stat.S_IMODE(os.stat(d).st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(d)).st_mode), 0o700)

    def test_never_follows_a_symlinked_hub_dir(self):
        victim = os.path.join(self.cfg, "victim")
        os.makedirs(os.path.join(victim, "hooks.d"))
        f = self.write_json(os.path.join(victim, "hooks.d", "x.json"), {})
        old = time.time() - 40 * 86400
        os.utime(f, (old, old))
        os.symlink(victim, os.path.join(self.cfg, "statusline-hub"))
        msg = self.said()   # its hooks are refused: said once
        self.assertIn("is a symlink", msg)
        self.quiet()
        self.assertTrue(os.path.exists(f))
        self.assertEqual(sorted(os.listdir(victim)), ["hooks.d"])


class RefusalNotice(Base):
    """A config dir inside a git work tree refuses every hook: said once, at
    session start, rather than only by --status."""

    def setUp(self):
        super().setUp()
        # HOME above the config dir, which sits in a cloned repository
        self.home = os.path.join(self.cfg, "home")
        self.repo = os.path.join(self.home, "src", "repo")
        os.makedirs(os.path.join(self.repo, ".git"))
        cfg = os.path.join(self.repo, "cfg")
        os.makedirs(cfg)
        self.env.update(HOME=self.home, CLAUDE_CONFIG_DIR=cfg,
                        CLAUDE_PLUGIN_DATA=os.path.join(cfg, "plugins", "data",
                                                        "statusline-hub-kmacmcfarlane"))
        self.cfg_in_repo = cfg

    def plant(self):
        d = os.path.join(self.cfg_in_repo, "statusline-hub", "hooks.d")
        os.makedirs(d, mode=0o700, exist_ok=True)
        os.chmod(os.path.dirname(d), 0o700)
        path = os.path.join(d, "x.json")
        with open(path, "w") as f:
            json.dump({"name": "x", "kind": "display", "command": ["echo", "hi"]}, f)
        os.chmod(path, 0o600)
        return path

    def test_said_once_only_when_a_hook_is_refused(self):
        self.quiet()                      # nothing registered: nothing refused
        self.plant()
        msg = self.said()
        self.assertIn("are not run", msg)
        self.assertIn("inside a git work tree", msg)
        self.assertIn(self.cfg_in_repo, msg)
        self.assertIn("--status", msg)
        for _ in range(2):
            self.quiet()
        # the refusal clears (the repository goes), then comes back: said again
        os.rmdir(os.path.join(self.repo, ".git"))
        self.quiet()
        os.makedirs(os.path.join(self.repo, ".git"))
        self.assertIn("inside a git work tree", self.said())

    def test_a_directory_reason_names_the_fix_and_an_unknown_one_is_quoted(self):
        import session_start
        d = os.path.join(self.cfg, "statusline-hub", "hooks.d")
        cases = [("a symlink", "is a symlink; it must be a real directory of yours"),
                 ("something new", "is refused (something new)")]
        for why, want in cases:
            with self.subTest(why=why):
                stamp = os.path.join(self.data, session_start.NOTICE)
                if os.path.exists(stamp):
                    os.remove(stamp)
                os.makedirs(self.data, exist_ok=True)
                saved = session_start.refusal
                session_start.refusal = lambda: (d, why)
                try:
                    msg = session_start.refusal_notice(self.data)
                finally:
                    session_start.refusal = saved
                self.assertIn(d + " " + want, msg)

    def test_rides_along_with_the_slot_message(self):
        self.plant()
        self.write_json(os.path.join(self.cfg_in_repo, "settings.json"), HUB_ON)
        msg = self.said()
        self.assertIn("status line slot taken", msg)
        self.assertIn("inside a git work tree", msg)
        self.assertEqual(msg.count("statusline-hub: "), 1)


class NeverRaises(Base):
    def test_garbage_stdin(self):
        for stdin in ("", "not json", "[]", "null"):
            p = subprocess.run([sys.executable, HOOK], env=self.env, input=stdin,
                               capture_output=True, text=True, timeout=30)
            self.assertEqual((p.returncode, p.stdout, p.stderr), (0, "{}\n", ""))


if __name__ == "__main__":
    unittest.main()
