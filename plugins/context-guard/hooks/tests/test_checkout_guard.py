"""End-to-end checkout_guard tests: the hook is run as a subprocess with a
PreToolUse JSON payload on stdin against real temp git repos, the way Claude
Code runs it."""
import json, os, subprocess, sys, tempfile, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLOCK = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "This file is tracked in the main checkout. Enter a worktree "
            "first (EnterWorktree) or delegate to an Agent with worktree "
            "isolation; see the sandbox skill's checkout/worktree convention. "
            "Escape hatches: CLAUDE_KIT_ALLOW_CHECKOUT_EDITS=1 or a "
            ".claude/allow-checkout-edits file."),
    }
}


def run_hook(payload, env=None):
    e = dict(os.environ)
    e.pop("CLAUDE_KIT_ALLOW_CHECKOUT_EDITS", None)
    e.pop("GIT_DIR", None)
    if env:
        e.update(env)
    p = subprocess.run([sys.executable, os.path.join(HOOKS, "checkout_guard.py")],
                       input=json.dumps(payload), capture_output=True,
                       text=True, env=e, timeout=30)
    out = {}
    if p.stdout.strip():
        try:
            out = json.loads(p.stdout)
        except Exception:
            out = {"_raw": p.stdout}
    return p.returncode, out, p.stderr


def git(cwd, *args):
    subprocess.run(("git", "-C", cwd, "-c", "user.name=t",
                    "-c", "user.email=t@t") + args,
                   check=True, capture_output=True)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.realpath(os.path.join(self.tmp.name, "repo"))
        os.makedirs(self.repo)
        git(self.repo, "init", "-q")
        self.tracked = os.path.join(self.repo, "src.py")
        with open(self.tracked, "w") as f:
            f.write("x = 1\n")
        git(self.repo, "add", "src.py")
        git(self.repo, "commit", "-q", "-m", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, path, cwd=None, tool="Edit", env=None):
        key = "notebook_path" if tool == "NotebookEdit" else "file_path"
        return run_hook({"session_id": "s", "hook_event_name": "PreToolUse",
                         "tool_name": tool, "cwd": cwd or self.repo,
                         "tool_input": {key: path, "old_string": "a",
                                        "new_string": "b"}}, env)


class TestCheckoutGuard(Base):
    def test_tracked_file_in_main_checkout_blocked(self):
        rc, out, _ = self.edit(self.tracked)
        self.assertEqual((rc, out), (0, BLOCK))

    def test_relative_path_resolved_against_cwd(self):
        rc, out, _ = self.edit("src.py")
        self.assertEqual((rc, out), (0, BLOCK))

    def test_untracked_allowed(self):
        rc, out, _ = self.edit(os.path.join(self.repo, "new.py"))
        self.assertEqual((rc, out), (0, {}))

    def test_claude_sandbox_and_claude_paths_allowed(self):
        for sub in (".claude-sandbox/backlog.yaml", ".claude/settings.json"):
            p = os.path.join(self.repo, sub)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write("{}\n")
            git(self.repo, "add", "-f", sub)
            git(self.repo, "commit", "-q", "-m", "cfg")
            rc, out, _ = self.edit(p)
            self.assertEqual((rc, out), (0, {}), sub)  # even though tracked

    def test_path_outside_repo_allowed(self):
        outside = os.path.join(self.tmp.name, "elsewhere.txt")
        rc, out, _ = self.edit(outside)
        self.assertEqual((rc, out), (0, {}))

    def test_worktree_cwd_allowed_same_file(self):
        # Rule 2: a linked-worktree cwd is exempt — this is also why ralph
        # (which always runs in a worktree) needs no special case.
        wt = os.path.join(self.tmp.name, "wt")
        git(self.repo, "worktree", "add", "-q", wt, "-b", "wt-branch")
        rc, out, _ = self.edit(os.path.join(wt, "src.py"), cwd=wt)
        self.assertEqual((rc, out), (0, {}))
        # ...but the SAME main-checkout file stays blocked from the main cwd.
        rc, out, _ = self.edit(self.tracked)
        self.assertEqual(out, BLOCK)

    def test_non_git_cwd_allowed(self):
        plain = os.path.join(self.tmp.name, "plain")
        os.makedirs(plain)
        rc, out, _ = self.edit(os.path.join(plain, "f.txt"), cwd=plain)
        self.assertEqual((rc, out), (0, {}))

    def test_env_escape_hatch_allows(self):
        rc, out, _ = self.edit(self.tracked,
                               env={"CLAUDE_KIT_ALLOW_CHECKOUT_EDITS": "1"})
        self.assertEqual((rc, out), (0, {}))

    def test_marker_file_allows(self):
        os.makedirs(os.path.join(self.repo, ".claude"))
        open(os.path.join(self.repo, ".claude", "allow-checkout-edits"), "w").close()
        rc, out, _ = self.edit(self.tracked)
        self.assertEqual((rc, out), (0, {}))

    def test_git_absent_fails_open(self):
        rc, out, _ = self.edit(self.tracked,
                               env={"PATH": os.path.join(self.tmp.name, "nobin")})
        self.assertEqual((rc, out), (0, {}))

    def test_git_broken_fails_open(self):
        rc, out, _ = self.edit(self.tracked,
                               env={"GIT_DIR": os.path.join(self.tmp.name, "no.git")})
        self.assertEqual((rc, out), (0, {}))

    def test_multi_edit_payload_blocked(self):
        rc, out, _ = run_hook({"session_id": "s", "hook_event_name": "PreToolUse",
                               "tool_name": "MultiEdit", "cwd": self.repo,
                               "tool_input": {"file_path": self.tracked,
                                              "edits": [{"old_string": "a",
                                                         "new_string": "b"}]}})
        self.assertEqual((rc, out), (0, BLOCK))

    def test_notebook_edit_file_path_spelling_blocked(self):
        # The docs' NotebookEdit payloads use file_path; the guard reads it.
        nb = os.path.join(self.repo, "fp.ipynb")
        with open(nb, "w") as f:
            f.write("{}\n")
        git(self.repo, "add", "fp.ipynb")
        git(self.repo, "commit", "-q", "-m", "fp")
        rc, out, _ = run_hook({"session_id": "s", "hook_event_name": "PreToolUse",
                               "tool_name": "NotebookEdit", "cwd": self.repo,
                               "tool_input": {"file_path": nb,
                                              "new_source": "x"}})
        self.assertEqual((rc, out), (0, BLOCK))

    def test_notebook_edit_payload_shape(self):
        nb = os.path.join(self.repo, "nb.ipynb")
        with open(nb, "w") as f:
            f.write("{}\n")
        git(self.repo, "add", "nb.ipynb")
        git(self.repo, "commit", "-q", "-m", "nb")
        rc, out, _ = self.edit(nb, tool="NotebookEdit")
        self.assertEqual((rc, out), (0, BLOCK))
        rc, out, _ = self.edit(os.path.join(self.repo, "new.ipynb"),
                               tool="NotebookEdit")
        self.assertEqual((rc, out), (0, {}))

    def test_garbage_stdin_fails_open(self):
        p = subprocess.run([sys.executable,
                            os.path.join(HOOKS, "checkout_guard.py")],
                           input="not json", capture_output=True, text=True,
                           timeout=30)
        self.assertEqual((p.returncode, json.loads(p.stdout)), (0, {}))

    def test_missing_path_fails_open(self):
        rc, out, _ = run_hook({"session_id": "s", "tool_name": "Edit",
                               "cwd": self.repo, "tool_input": {}})
        self.assertEqual((rc, out), (0, {}))


if __name__ == "__main__":
    unittest.main()
