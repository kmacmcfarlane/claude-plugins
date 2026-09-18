"""Nothing of the optional gauge publisher leaks into what a user of this
plugin alone sees: no rendered line, installer message or SKILL.md names it or
its vocabulary, and a standalone render never creates its directory. In code,
the publisher's names appear exactly twice - the two constant blocks."""
import glob, json, os, re, subprocess, sys, time, unittest

import helpers

LEAKS = ("claude-kit", "context-guard", "librarian", "checkpoint", "HARD", "CLAUDE_KIT_")
NAMES = re.compile(r"claude-kit|context-guard")


class Standalone(helpers.Hermetic):
    def assertClean(self, text, what):
        for w in LEAKS:
            self.assertNotIn(w, text, f"{what}: {w!r} in {text!r}")

    def test_renders_never_leak_or_touch_the_publisher_dir(self):
        now = time.time()
        payloads = [{}, {"context_window": None}, {"session_id": None},
                    {"session_name": "x"},
                    {"rate_limits": {"five_hour": {"used_percentage": 95,
                                                   "resets_at": now + 60}}}]
        for left in (900_000, 150_000, 100_000, 60_000, 1000, 0):
            payloads.append({"context_window": {
                "used_percentage": 100 * (1 - left / 1e6), "context_window_size": 1_000_000,
                "total_input_tokens": 1_000_000 - left}})
        for p in payloads:
            out = self.line(p)
            self.assertClean(out, p)
        self.assertFalse(os.path.exists(os.path.join(self.cfg, "claude-kit")))
        for f in self.all_files():
            self.assertTrue(os.path.relpath(f, self.cfg).startswith("statusline"), f)

    def test_installer_messages_never_leak(self):
        data = os.path.join(self.cfg, "plugins", "data", "statusline-kmacmcfarlane")
        env = dict(self.env, CLAUDE_PLUGIN_DATA=data)
        settings = os.path.join(self.cfg, "settings.json")
        proj = os.path.join(self.cfg, "proj")
        os.makedirs(proj)
        pred = os.path.join(self.cfg, "plugins", "data", "context-guard-kmacmcfarlane")
        self.write_json(os.path.join(pred, "statusline-installed.json"),
                        {"settings": settings, "command": "x"})

        def run(*args, e=env, script=helpers.INSTALLER):
            p = subprocess.run([sys.executable, script, *args], cwd=proj,
                               capture_output=True, text=True, env=e, timeout=30)
            self.assertClean(p.stdout + p.stderr, args)
            return p.returncode

        run("--help")
        self.write_json(settings, {"statusLine": {"type": "command", "command":
                        f'python3 "{pred}/current-hooks/statusline.py"'}})
        self.assertEqual(run(), 0)                       # predecessor takeover
        self.assertEqual(run(), 0)                       # own, again
        self.assertEqual(run("--project"), 0)
        self.assertEqual(run("--remove"), 0)
        self.assertEqual(run("--remove"), 0)             # nothing there
        self.write_json(settings, {"statusLine": {"type": "command", "command": "x"}})
        self.assertEqual(run(), 3)
        self.assertEqual(run("--remove"), 3)
        self.write_json(settings, raw="{bad")
        self.assertEqual(run(), 1)
        bare = {k: v for k, v in env.items() if k != "CLAUDE_PLUGIN_DATA"}
        self.write_json(settings, {})
        os.rename(os.path.join(self.cfg, "plugins"), os.path.join(self.cfg, "gone"))
        self.assertEqual(run(e=bare, script=self.plain_copy()), 1)   # no data dir

    def test_skill_md_never_leaks(self):
        with open(os.path.join(helpers.SKILL, "SKILL.md"), encoding="utf-8") as f:
            self.assertClean(f.read(), "SKILL.md")

    def test_hooks_json_description_is_neutral(self):
        with open(os.path.join(helpers.HOOKS, "hooks.json")) as f:
            self.assertClean(json.load(f)["description"], "hooks.json")

    def test_publisher_names_only_in_the_two_constants(self):
        hits = []
        for path in glob.glob(os.path.join(helpers.PLUGIN, "**", "*.py"), recursive=True):
            if os.sep + "tests" + os.sep in path:
                continue
            with open(path, encoding="utf-8") as f:
                for n, ln in enumerate(f, 1):
                    if NAMES.search(ln):
                        hits.append((os.path.relpath(path, helpers.PLUGIN), ln.strip()))
        self.assertEqual(sorted(hits), [
            (os.path.join("hooks", "owner.py"),
             'PREDECESSORS = ("claude-kit", "context-guard")'),
            (os.path.join("hooks", "sensor.py"),
             'CG_DIR = ("claude-kit", "context-gate")')])


if __name__ == "__main__":
    unittest.main()
