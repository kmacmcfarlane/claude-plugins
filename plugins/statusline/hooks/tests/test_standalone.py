"""Nothing of the optional gauge publisher leaks into what a user of this
plugin alone sees: no rendered line, SessionStart output, hook manifest or
SKILL.md names it or its vocabulary, and a standalone render never creates its
directory. In code, the publisher's names appear exactly once - the constant
block."""
import glob, json, os, re, subprocess, sys, time, unittest

import helpers

LEAKS = ("claude-kit", "context-guard", "librarian", "checkpoint", "HARD", "CLAUDE_KIT_")
NAMES = re.compile(r"claude-kit|context-guard")

# The repo/worktree root this checkout lives under - e.g. a worktree named
# after a context-guard work item embeds "context-guard" in its own path.
# That's a property of where this tree happens to be checked out, not a
# leak the plugin wrote, so it's scrubbed out before the leak check runs.
CHECKOUT_ROOT = os.path.dirname(os.path.dirname(helpers.PLUGIN))


class Standalone(helpers.Hermetic):
    def assertClean(self, text, what):
        for w in LEAKS:
            self.assertNotIn(w, text, f"{what}: {w!r} in {text!r}")

    def _scrub_checkout_path(self, text):
        """Strip occurrences of the checkout root (and its realpath, in
        case of a symlinked tmp/worktree) so an incidental 'context-guard'
        in *where the repo lives* doesn't false-fail a check that's about
        what the plugin *wrote*."""
        for root in {CHECKOUT_ROOT, os.path.realpath(CHECKOUT_ROOT)}:
            text = text.replace(root, "")
        return text

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

    def test_session_start_never_leaks(self):
        env = dict(self.env, CLAUDE_PLUGIN_DATA=os.path.join(
            self.cfg, "plugins", "data", "statusline-kmacmcfarlane"))
        p = subprocess.run([sys.executable, os.path.join(helpers.HOOKS, "session_start.py")],
                           input="{}", capture_output=True, text=True, env=env, timeout=30)
        self.assertClean(self._scrub_checkout_path(p.stdout + p.stderr), "session_start")
        with open(os.path.join(self.cfg, "statusline-hub", "hooks.d", "statusline.json")) as f:
            self.assertClean(self._scrub_checkout_path(f.read()), "manifest")

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
            (os.path.join("hooks", "sensor.py"),
             'CG_DIR = ("claude-kit", "context-gate")')])


if __name__ == "__main__":
    unittest.main()
