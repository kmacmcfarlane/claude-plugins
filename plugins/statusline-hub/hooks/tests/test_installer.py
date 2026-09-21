"""The install-statusline-hub skill's script: install, remove, consent to
replace, and the statusline plugin's entry (replaceable without consent only
once that plugin draws as a hub hook). Runs as a subprocess, hermetic."""
import json, os, subprocess, sys

import helpers
import owner

SCRIPT = os.path.join(helpers.PLUGIN, "skills", "install-statusline-hub", "scripts",
                      "install_hub.py")
FOREIGN = {"type": "command", "command": "bash ~/bin/my-prompt.sh"}


class Installer(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        self.data = os.path.join(self.cfg, "plugins", "data", "statusline-hub-kmacmcfarlane")
        self.env["CLAUDE_PLUGIN_DATA"] = self.data
        self.user = os.path.join(self.cfg, "settings.json")
        self.sl = {"type": "command", "command": 'python3 "%s/plugins/data/statusline-'
                   'kmacmcfarlane/current-hooks/statusline.py"' % self.cfg}

    def run_it(self, *args):
        p = subprocess.run([sys.executable, SCRIPT, *args], env=self.env, cwd=self.cfg,
                           capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout + p.stderr

    def entry(self):
        with open(self.user) as f:
            return json.load(f).get("statusLine")

    def own(self):
        return {"type": "command", "command": owner.command_for(self.data)}

    def test_install_and_remove(self):
        self.write_json(self.user, {"model": "opus"})
        rc, out = self.run_it()
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.entry(), self.own())
        rc, out = self.run_it("--remove")
        self.assertEqual(rc, 0, out)
        self.assertIsNone(self.entry())
        with open(os.path.join(self.data, "owner.json")) as f:
            self.assertEqual(json.load(f)["state"], "removed")

    def test_foreign_needs_consent(self):
        self.write_json(self.user, {"statusLine": FOREIGN})
        rc, out = self.run_it()
        self.assertEqual(rc, 3)
        self.assertNotIn("my-prompt", out)
        self.assertEqual(self.entry(), FOREIGN)
        self.assertEqual(self.run_it("--remove")[0], 3)
        self.assertEqual(self.run_it("--replace")[0], 0)
        self.assertEqual(self.entry(), self.own())

    def test_statusline_entry_needs_consent_until_it_is_a_hook(self):
        self.write_json(self.user, {"statusLine": self.sl})
        rc, out = self.run_it()
        self.assertEqual(rc, 3)
        self.assertIn("drops the footer", out)
        self.assertEqual(self.entry(), self.sl)
        self.manifest("statusline", ["python3", "/x/statusline.py"])
        self.assertEqual(self.run_it()[0], 0)
        self.assertEqual(self.entry(), self.own())

    def test_status(self):
        self.manifest("a", ["echo"])
        rc, out = self.run_it("--status")
        self.assertEqual(rc, 0)
        self.assertIn("a: display, active", out)
