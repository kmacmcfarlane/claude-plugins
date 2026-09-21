"""The statusline plugin and the hub together: the statusLine slot changes
hands once, from the statusline plugin (which no longer writes settings) to
the hub, with the footer drawing on both sides of it.

Both plugins' SessionStart hooks run as subprocesses against one temp config
dir, in both orders (Claude Code starts a session's hooks together, so either
may finish first), and each "session" also renders whatever the settings'
statusLine command is, through a shell, as Claude Code does. Scenarios: a
fresh machine, an existing statusline install (the upgrade), a foreign
status line, the hub removed, the statusline plugin disabled later, an older
copy of the footer (context-guard's) in the slot, and an upgrade that left
the hub uninstalled (`/plugin update` does not add a new dependency).

Runs only in the source repo, where plugins/statusline/ sits beside this
plugin; an installed copy skips it."""
import json, os, shutil, subprocess, sys, time, unittest

import helpers
import owner

SL_PLUGIN = os.path.join(os.path.dirname(helpers.PLUGIN), "statusline")
SL_HOOKS = os.path.join(SL_PLUGIN, "hooks")
BESIDE = os.path.isfile(os.path.join(SL_HOOKS, "session_start.py"))
HUB_SS = os.path.join(helpers.HOOKS, "session_start.py")
SL_SS = os.path.join(SL_HOOKS, "session_start.py")
MKT = "kmacmcfarlane"
BOTH_ON = {"enabledPlugins": {f"statusline-hub@{MKT}": True, f"statusline@{MKT}": True}}
FOREIGN = {"type": "command", "command": "echo mine"}
FOOTER = "580k left"   # what the statusline footer shows for helpers.CTX


@unittest.skipUnless(BESIDE, "statusline plugin not beside this one")
class Handover(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        base = os.path.join(self.cfg, "plugins", "data")
        self.hub_data = os.path.join(base, f"statusline-hub-{MKT}")
        self.sl_data = os.path.join(base, f"statusline-{MKT}")
        self.proj = os.path.join(self.cfg, "proj")
        os.makedirs(self.proj)
        self.user = os.path.join(self.cfg, "settings.json")
        self.messages = []

    # -- a session -----------------------------------------------------------

    def _hook(self, script, plugin, data):
        # the symlink command each plugin's hooks.json runs first
        os.makedirs(data, exist_ok=True)
        link = os.path.join(data, "current-hooks")
        if os.path.lexists(link):
            os.remove(link)
        os.symlink(os.path.join(plugin, "hooks"), link)
        env = dict(self.env, CLAUDE_PLUGIN_DATA=data, CLAUDE_PLUGIN_ROOT=plugin,
                   CLAUDE_PROJECT_DIR=self.proj)
        p = subprocess.run([sys.executable, script], cwd=self.proj, env=env,
                           input=json.dumps({"session_id": "s", "cwd": self.proj}),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual((p.returncode, p.stderr), (0, ""), p.stdout)
        out = json.loads(p.stdout)
        if out:
            self.messages.append(out["systemMessage"])
        return out

    def hub_ss(self):
        return self._hook(HUB_SS, helpers.PLUGIN, self.hub_data)

    def sl_ss(self):
        out = self._hook(SL_SS, SL_PLUGIN, self.sl_data)
        # the statusline plugin has nothing to say while the hub is there
        self.assertEqual(out, {})
        return out

    def sl_ss_said(self):
        out = self._hook(SL_SS, SL_PLUGIN, self.sl_data)
        self.assertEqual(list(out), ["systemMessage"])
        return out["systemMessage"]

    def records(self, *keys):
        """Claude Code's install records: each key installed from this repo."""
        where = {"statusline": SL_PLUGIN, "statusline-hub": helpers.PLUGIN}
        self.write_json(os.path.join(self.cfg, "plugins", "installed_plugins.json"),
                        {"version": 2, "plugins": {
                            f"{k}@{MKT}": [{"scope": "user", "installPath": where[k]}]
                            for k in keys}})

    def session(self, hub=True, sl=True, sl_first=True):
        """One session start: the enabled plugins' hooks, in the given order.
        Returns the settings file's bytes afterwards."""
        order = [(sl, self.sl_ss), (hub, self.hub_ss)]
        for on, run in (order if sl_first else order[::-1]):
            if on:
                run()
        return self.raw()

    def render(self):
        """(stdout, stderr) of the settings' statusLine command, as Claude
        Code runs it: through a shell, the payload on stdin."""
        cmd = self.load().get("statusLine", {}).get("command")
        self.assertIsInstance(cmd, str)
        p = subprocess.run(cmd, shell=True, cwd=self.proj, env=self.env,
                           input=json.dumps(helpers.with_defaults({})),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout, p.stderr

    # -- files ---------------------------------------------------------------

    def load(self):
        with open(self.user) as f:
            return json.load(f)

    def raw(self):
        try:
            with open(self.user, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def kind(self):
        return owner.classify(self.load().get("statusLine"))

    def sl_entry(self, data=None):
        return {"type": "command", "command": 'python3 "%s/current-hooks/statusline.py"'
                % (data or self.sl_data)}

    def sl_marker(self, state):
        """The owner.json an earlier statusline version kept, and the
        current-hooks link its entry runs through."""
        os.makedirs(self.sl_data, exist_ok=True)
        link = os.path.join(self.sl_data, "current-hooks")
        if not os.path.lexists(link):
            os.symlink(SL_HOOKS, link)
        self.write_json(os.path.join(self.sl_data, "owner.json"),
                        {"v": 1, "state": state, "settings": self.user,
                         "command": self.sl_entry()["command"], "at": 1})

    def sl_manifest(self):
        return os.path.join(self.cfg, "statusline-hub", "hooks.d", "statusline.json")

    def hub_state(self):
        m = owner.read_marker(self.hub_data)
        return m and m["state"]

    def assertFooterViaHub(self):
        self.assertEqual(self.kind(), "own")
        if os.path.exists(self.sensor_file()):
            os.remove(self.sensor_file())
        out, _ = self.render()
        self.assertIn(FOOTER, out)
        self.assertEqual(len(out.splitlines()), 1)
        # the hub's tee wrote the record, before the footer ran
        self.assertEqual(self.read_sensor()["exact"]["pct"], 42.0)

    # -- scenarios -----------------------------------------------------------

    def test_statusline_writes_its_manifest_and_nothing_else(self):
        self.write_json(self.user, dict(BOTH_ON, statusLine=FOREIGN))
        before = self.raw()
        self.sl_ss()
        self.assertEqual(self.raw(), before)
        with open(self.sl_manifest()) as f:
            m = json.load(f)
        self.assertEqual((m["v"], m["name"], m["kind"]), (1, "statusline", "display"))
        self.assertEqual(m["command"], ["python3", os.path.join(SL_HOOKS, "statusline.py"),
                                        "--segment"])
        for p in (self.sl_manifest(), os.path.dirname(self.sl_manifest())):
            self.assertEqual(os.stat(p).st_mode & 0o077, 0, p)
        self.assertFalse(os.path.exists(os.path.join(self.sl_data, "owner.json")))
        # refreshed each session
        old = time.time() - 3 * 86400
        os.utime(self.sl_manifest(), (old, old))
        self.sl_ss()
        self.assertGreater(os.stat(self.sl_manifest()).st_mtime, old + 86400)

    def test_segment_mode_writes_no_sensor_record(self):
        p = subprocess.run([sys.executable, os.path.join(SL_HOOKS, "statusline.py"),
                            "--segment"], input=json.dumps(helpers.with_defaults({})),
                           capture_output=True, text=True, env=self.env, timeout=30)
        self.assertIn(FOOTER, p.stdout)
        self.assertIsNone(self.read_sensor())
        p = subprocess.run([sys.executable, os.path.join(SL_HOOKS, "statusline.py")],
                           input=json.dumps(helpers.with_defaults({})),
                           capture_output=True, text=True, env=self.env, timeout=30)
        self.assertIn(FOOTER, p.stdout)
        self.assertEqual(self.read_sensor()["exact"]["pct"], 42.0)

    def test_fresh_machine(self):
        for sl_first in (True, False):
            with self.subTest(sl_first=sl_first):
                self.setUp_fresh()
                self.write_json(self.user, BOTH_ON)
                self.session(sl_first=sl_first)
                if not sl_first:   # the hub looked before the footer registered: waits
                    self.assertNotIn("statusLine", self.load())
                    self.assertEqual(self.messages, [])
                    self.session(sl_first=sl_first)
                self.assertEqual(len(self.messages), 1, self.messages)
                self.assertIn("status line slot taken", self.messages[0])
                self.assertIn("statusline footer", self.messages[0])
                self.assertFooterViaHub()
                settled = self.raw()
                for _ in range(3):
                    self.assertEqual(self.session(sl_first=sl_first), settled)
                self.assertEqual(len(self.messages), 1, self.messages)

    def test_fresh_machine_hub_first_does_not_wait_for_a_footer_that_only_registers(self):
        # the install records show a statusline without owner.py: it will
        # never install its own entry, so the hub takes the slot at once
        self.records("statusline", "statusline-hub")
        self.write_json(self.user, BOTH_ON)
        self.session(sl_first=False)
        self.assertEqual(len(self.messages), 1, self.messages)
        self.assertIn("status line slot taken", self.messages[0])
        self.assertEqual(self.kind(), "own")
        self.session(sl_first=False)
        self.assertFooterViaHub()
        self.assertEqual(len(self.messages), 1, self.messages)

    def setUp_fresh(self):
        self.tearDown()
        self.setUp()

    def test_existing_statusline_install_hands_over_once(self):
        for sl_first in (True, False):
            with self.subTest(sl_first=sl_first):
                self.setUp_fresh()
                # an earlier statusline version installed its entry and marker
                self.write_json(self.user, dict(BOTH_ON, statusLine=self.sl_entry()))
                self.sl_marker("installed")
                kinds = []
                for _ in range(5):
                    kinds.append(self.kind())
                    # the footer draws whoever holds the slot: never a blank line
                    out, _ = self.render()
                    self.assertIn(FOOTER, out)
                    self.session(sl_first=sl_first)
                kinds.append(self.kind())
                # exactly one change of hands, statusline -> hub, never back
                changes = [(a, b) for a, b in zip(kinds, kinds[1:]) if a != b]
                self.assertEqual(changes, [("statusline", "own")], kinds)
                self.assertEqual(len(self.messages), 1, self.messages)
                self.assertIn("took over the status line slot", self.messages[0])
                self.assertNotIn("changed by something else", " ".join(self.messages))
                self.assertEqual(self.hub_state(), "installed")
                # the old marker is left as it was; the statusline plugin reads nothing of it
                with open(os.path.join(self.sl_data, "owner.json")) as f:
                    self.assertEqual(json.load(f)["state"], "installed")
                self.assertFooterViaHub()

    def test_upgrade_without_the_hub_is_said_once_then_fixed_by_reinstalling(self):
        # an earlier statusline owned the slot; `/plugin update statusline`
        # brought the new version but not its new dependency
        self.write_json(self.user, {"enabledPlugins": {f"statusline@{MKT}": True},
                                    "statusLine": self.sl_entry()})
        self.sl_marker("installed")
        self.records("statusline")
        before = self.raw()
        msg = self.sl_ss_said()
        self.assertTrue(msg.startswith("statusline: "), msg)
        self.assertIn(f"/plugin install statusline@{MKT}", msg)
        self.assertIn("statusline-hub", msg)
        self.assertEqual(self.raw(), before)             # no settings write
        self.assertIn(FOOTER, self.render()[0])          # the old entry still draws
        for _ in range(2):                               # said once
            self.assertEqual(self.session(hub=False), before)
        # re-running the install brings the hub: it takes over, quietly for statusline
        self.records("statusline", "statusline-hub")
        self.write_json(self.user, dict(BOTH_ON, statusLine=self.sl_entry()))
        self.session()
        self.assertEqual(len(self.messages), 2, self.messages)
        self.assertIn("took over the status line slot", self.messages[1])
        self.assertFalse(os.path.exists(os.path.join(self.sl_data,
                                                     "hub-missing-notice.json")))
        self.assertFooterViaHub()

    def test_foreign_status_line_is_left_alone(self):
        self.write_json(self.user, dict(BOTH_ON, statusLine=FOREIGN))
        before = self.raw()
        for sl_first in (True, False, True):
            self.assertEqual(self.session(sl_first=sl_first), before)
        self.assertEqual(len(self.messages), 1, self.messages)
        self.assertIn("already define a statusLine", self.messages[0])
        self.assertEqual(self.hub_state(), "deferred")

    def test_hub_removed_statusline_never_takes_the_slot_back(self):
        self.write_json(self.user, dict(BOTH_ON, statusLine=self.sl_entry()))
        self.sl_marker("installed")
        self.session()
        self.session()
        self.assertEqual(self.kind(), "own")
        settled = self.raw()
        # uninstall the hub: its data dir goes, and its hook no longer runs
        shutil.rmtree(self.hub_data)   # removes the current-hooks link, not its target
        self.messages.clear()
        for _ in range(3):
            self.assertEqual(self.session(hub=False), settled)   # one owner, no flap
        self.assertEqual(self.messages, [])
        self.assertTrue(os.path.isfile(self.sl_manifest()))
        # reinstalling the hub adopts its own entry quietly
        self.session()
        self.assertEqual(self.raw(), settled)
        self.assertEqual(self.messages, [])
        self.assertEqual(self.hub_state(), "installed")

    def test_statusline_disabled_later(self):
        self.write_json(self.user, BOTH_ON)
        self.session()
        self.assertEqual(self.kind(), "own")
        settled = self.raw()
        self.messages.clear()
        # disabled: its hook stops running, so nothing refreshes its manifest
        for _ in range(2):
            self.assertEqual(self.session(sl=False), settled)
        self.assertIn(FOOTER, self.render()[0])   # still fresh: still drawn
        old = time.time() - 15 * 86400
        os.utime(self.sl_manifest(), (old, old))
        self.assertEqual(self.session(sl=False), settled)   # the hub keeps the slot
        self.assertFalse(os.path.exists(self.sl_manifest()))  # the dead hook is pruned
        self.assertEqual(self.messages, [])
        out, _ = self.render()
        self.assertNotIn(FOOTER, out)
        self.assertEqual(self.read_sensor()["exact"]["pct"], 42.0)   # the tee goes on
        # enabled again: it registers, and draws, without a settings write
        self.assertEqual(self.session(), settled)
        self.assertIn(FOOTER, self.render()[0])

    def test_an_older_copy_of_the_footer_is_taken_over_once_hooked(self):
        cg = os.path.join(self.cfg, "plugins", "data", f"context-guard-{MKT}")
        self.write_json(self.user, dict(BOTH_ON, statusLine=self.sl_entry(cg)))
        self.hub_ss()                      # the footer is not a hook yet: wait
        self.assertEqual(self.load()["statusLine"], self.sl_entry(cg))
        self.assertEqual(self.messages, [])
        self.session()
        self.assertEqual(len(self.messages), 1, self.messages)
        self.assertIn("took over the status line slot", self.messages[0])
        self.assertFooterViaHub()

    def test_a_removed_footer_stays_removed(self):
        self.write_json(self.user, BOTH_ON)
        self.sl_marker("removed")
        before = self.raw()
        for _ in range(3):
            self.assertEqual(self.session(), before)
        self.assertEqual(len(self.messages), 1, self.messages)
        self.assertIn("footer was removed", self.messages[0])
        self.assertEqual(self.hub_state(), "removed")


if __name__ == "__main__":
    unittest.main()
