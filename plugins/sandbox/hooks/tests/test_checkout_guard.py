"""End-to-end checkout_guard tests: the hook is run as a subprocess with a
PreToolUse JSON payload on stdin against real temp git repos, the way Claude
Code runs it."""
import contextlib, io, json, os, subprocess, sys, tempfile, unittest
from unittest import mock

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)
import checkout_guard as cg  # noqa: E402

BLOCK = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "This file is tracked in the main checkout. Enter a worktree "
            "first (EnterWorktree) or delegate to an Agent with worktree "
            "isolation; see the sandbox skill's checkout/worktree convention. "
            "Escape hatches, both the operator's to set: "
            "SANDBOX_ALLOW_CHECKOUT_EDITS=1, or allow rules in "
            ".claude/allow-checkout-edits."),
    }
}


def run_hook(payload, env=None):
    e = dict(os.environ)
    e.pop("SANDBOX_ALLOW_CHECKOUT_EDITS", None)
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
                               env={"SANDBOX_ALLOW_CHECKOUT_EDITS": "1"})
        self.assertEqual((rc, out), (0, {}))

    def test_deprecated_alias_escape_hatch_allows(self):
        rc, out, _ = self.edit(self.tracked,
                               env={"CLAUDE_KIT_ALLOW_CHECKOUT_EDITS": "1"})
        self.assertEqual((rc, out), (0, {}))

    def test_both_env_names_set_allows(self):
        rc, out, _ = self.edit(self.tracked,
                               env={"SANDBOX_ALLOW_CHECKOUT_EDITS": "1",
                                    "CLAUDE_KIT_ALLOW_CHECKOUT_EDITS": "1"})
        self.assertEqual((rc, out), (0, {}))

    def test_neither_env_name_set_blocks(self):
        # run_hook strips both names, so this is the unset baseline.
        rc, out, _ = self.edit(self.tracked)
        self.assertEqual((rc, out), (0, BLOCK))

    def test_env_values_other_than_1_do_not_allow(self):
        # Same accepted values under both names: exactly "1", nothing else.
        for name in ("SANDBOX_ALLOW_CHECKOUT_EDITS",
                     "CLAUDE_KIT_ALLOW_CHECKOUT_EDITS"):
            for val in ("", "0", "true", "yes", " 1"):
                rc, out, _ = self.edit(self.tracked, env={name: val})
                self.assertEqual((rc, out), (0, BLOCK), (name, val))

    def test_either_name_at_1_allows_whatever_the_other_holds(self):
        for env in ({"SANDBOX_ALLOW_CHECKOUT_EDITS": "1",
                     "CLAUDE_KIT_ALLOW_CHECKOUT_EDITS": "0"},
                    {"SANDBOX_ALLOW_CHECKOUT_EDITS": "0",
                     "CLAUDE_KIT_ALLOW_CHECKOUT_EDITS": "1"}):
            rc, out, _ = self.edit(self.tracked, env=env)
            self.assertEqual((rc, out), (0, {}), env)

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


# --- path rules in .claude/allow-checkout-edits ------------------------------

MARKER_EDIT = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            ".claude/allow-checkout-edits holds the checkout guard's rules "
            "and is the operator's to change: Edit and Write on it are denied "
            "in every session. Ask the operator to edit it, and do not write "
            "it another way."),
    }
}

MARKER_CHECK = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "The checkout guard could not check whether this path is its "
            "rules file .claude/allow-checkout-edits (internal error), so the "
            "edit is denied."),
    }
}

FIXTURES = ("README.md", "issues/x.md", "issues/a/b.md", "issues/a/b/x.md",
            "bin/tool", "docs/x.md", "notes", ".github/w.yml", "Issues/x.md",
            "issues/n.ipynb", "bin/n.ipynb")


def reason(out):
    return out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")


def decision(out):
    return out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")


class RulesBase(Base):
    def setUp(self):
        super().setUp()
        for rel in FIXTURES:
            p = os.path.join(self.repo, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write("x\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "fixtures")
        self.marker = os.path.join(self.repo, ".claude", "allow-checkout-edits")

    def rules(self, text, mode="w"):
        os.makedirs(os.path.dirname(self.marker), exist_ok=True)
        with open(self.marker, mode) as f:
            f.write(text)

    def p(self, rel):
        return os.path.join(self.repo, rel)

    def check(self, rel, want, **kw):
        rc, out, _ = self.edit(self.p(rel), **kw)
        self.assertEqual(rc, 0)
        self.assertEqual(decision(out), want, (rel, out))
        return reason(out)


class TestRules(RulesBase):
    def test_t1_allow_rule_and_named_deny(self):
        self.rules("deny *\nallow issues/**\n")
        self.check("issues/x.md", "allow")
        r = self.check("bin/tool", "deny")
        self.assertIn("`line 1: deny *` is the last rule that matches", r)
        self.assertIn("(`bin/tool`)", r)

    def test_t2_last_match_wins(self):
        self.rules("allow **\ndeny bin/**\n")
        self.assertIn("`line 2: deny bin/**`", self.check("bin/tool", "deny"))
        self.rules("deny bin/**\nallow **\n")
        self.check("bin/tool", "allow")

    def test_t3_implicit_default_deny(self):
        self.rules("allow issues/**\n")
        r = self.check("src.py", "deny")
        self.assertIn("no rule in the file matches, so the default rule "
                      "`deny *` applies", r)

    def test_t4_empty_or_comment_only_allows_nothing(self):
        for text in ("", "# only a comment\n\n"):
            self.rules(text)
            r = self.check("src.py", "deny")
            self.assertIn("has no rules", r)
            self.assertIn("`allow **`", r)

    def test_t5_broken_line_fails_closed(self):
        for line, err in (("alow x", "unknown keyword"),
                          ("allow", "missing glob"),
                          ("allow a b", "unexpected text"),
                          ("allow a**b", "whole segment"),
                          ("allow a/../b", "`..` segment"),
                          ("allow a//b", "empty path segment"),
                          ("allow [z-a]", "reversed range"),
                          ("allow !x", "leading `!`"),
                          ("Allow x", "unknown keyword"),
                          ("allow [abc", "unclosed `[`"),
                          ("allow a\\", "trailing `\\`"),
                          ("allow # note", "missing glob (a `#` starts")):
            self.rules("allow **\n" + line + "\n")
            r = self.check("src.py", "deny")
            self.assertIn("cannot be used: line 2: ", r, line)
            self.assertIn(err, r, line)
            self.assertIn("A broken rules file allows nothing", r)

    def test_t6_bad_line_voids_whole_file(self):
        self.rules("allow **\ndney bin/**\n")
        r = self.check("issues/x.md", "deny")
        self.assertIn("line 2: unknown keyword `dney`", r)

    def test_t7_trailing_comment(self):
        self.rules("allow issues/** # records\n")
        self.check("issues/x.md", "allow")

    def test_t8_slashless_is_top_level_only(self):
        self.rules("allow *.md\n")
        self.check("README.md", "allow")
        self.check("docs/x.md", "deny")
        self.rules("allow **/*.md\n")
        self.check("docs/x.md", "allow")

    def test_t9_star_stays_in_segment(self):
        self.rules("allow issues/*.md\n")
        self.check("issues/x.md", "allow")
        self.check("issues/a/b.md", "deny")

    def test_t10_parent_matching_and_dir_only(self):
        for text in ("allow issues\n", "allow issues/\n"):
            self.rules(text)
            self.check("issues/a/b.md", "allow")
        self.rules("allow notes/\n")
        self.check("notes", "deny")

    def test_t11_double_star_zero_segments(self):
        self.rules("allow issues/**/x.md\n")
        self.check("issues/x.md", "allow")
        self.check("issues/a/b/x.md", "allow")

    def test_t12_leading_slash(self):
        self.rules("allow /issues/**\n")
        self.check("issues/x.md", "allow")

    def test_t13_case_sensitive(self):
        self.rules("allow issues/**\n")
        self.check("Issues/x.md", "deny")

    def test_t14_star_matches_dotfiles(self):
        self.rules("deny *\nallow *\n")
        self.check(".github/w.yml", "allow")

    def test_t15_tracked_file_symlink_judged_by_target(self):
        os.symlink("../bin/tool", self.p("issues/link.md"))
        git(self.repo, "add", "issues/link.md")
        git(self.repo, "commit", "-q", "-m", "link")
        self.rules("allow issues/**\n")
        self.assertIn("(`bin/tool`)", self.check("issues/link.md", "deny"))

    def test_t15b_directory_symlink_judged_by_target(self):
        os.symlink("../bin", self.p("issues/tools"))
        self.rules("allow issues/**\n")
        self.assertIn("(`bin/tool`)", self.check("issues/tools/tool", "deny"))

    def test_t16_paths_relative_to_cwd_and_normalised(self):
        self.rules("allow issues/**\n")
        sub = self.p("issues")
        for path, want in (("x.md", "allow"), ("../bin/tool", "deny"),
                           (self.p("issues/../bin/tool"), "deny")):
            rc, out, _ = self.edit(path, cwd=sub)
            self.assertEqual(decision(out), want, path)

    def test_t17_env_override_beats_everything(self):
        for name in ("SANDBOX_ALLOW_CHECKOUT_EDITS",
                     "CLAUDE_KIT_ALLOW_CHECKOUT_EDITS"):
            env = {name: "1"}
            self.rules("deny *\n")
            self.check("src.py", "allow", env=env)
            self.rules("dney *\n")
            self.check("src.py", "allow", env=env)
            rc, out, _ = self.edit(self.marker, env=env)
            self.assertEqual(out, {}, name)

    def test_t18_marker_edits_denied_everywhere(self):
        # absent, then present untracked, then present tracked
        for tool in ("Edit", "Write"):
            rc, out, _ = self.edit(self.marker, tool=tool)
            self.assertEqual(out, MARKER_EDIT, tool)
        self.rules("allow **\n")
        self.assertEqual(self.edit(self.marker)[1], MARKER_EDIT)
        git(self.repo, "add", "-f", ".claude/allow-checkout-edits")
        git(self.repo, "commit", "-q", "-m", "rules")
        self.assertEqual(self.edit(self.marker)[1], MARKER_EDIT)
        # from a linked worktree: the main checkout's file and its own copy
        wt = os.path.join(self.tmp.name, "wt")
        git(self.repo, "worktree", "add", "-q", wt, "-b", "wt-branch")
        self.assertEqual(self.edit(self.marker, cwd=wt)[1], MARKER_EDIT)
        own = os.path.join(wt, ".claude", "allow-checkout-edits")
        self.assertEqual(self.edit(own, cwd=wt)[1], MARKER_EDIT)
        # from a non-git cwd, by absolute path
        plain = os.path.join(self.tmp.name, "plain")
        os.makedirs(plain)
        self.assertEqual(self.edit(self.marker, cwd=plain)[1], MARKER_EDIT)
        # a symlink alias pointing at it
        os.symlink(".claude/allow-checkout-edits", self.p("notes2"))
        self.assertEqual(self.edit(self.p("notes2"))[1], MARKER_EDIT)
        # case variants
        for v in (".claude/Allow-Checkout-Edits", ".CLAUDE/allow-checkout-edits"):
            self.assertEqual(self.edit(self.p(v))[1], MARKER_EDIT, v)

    def test_t18_symlinked_claude_dir_marker_edit_denied(self):
        os.makedirs(self.p("claude-cfg"))
        os.symlink("claude-cfg", self.p(".claude"))
        self.assertEqual(self.edit(self.marker)[1], MARKER_EDIT)

    def test_t19_process_paths_stay_exempt(self):
        for sub in (".claude/settings.json", ".claude-sandbox/x"):
            p = self.p(sub)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write("{}\n")
            git(self.repo, "add", "-f", sub)
        git(self.repo, "commit", "-q", "-m", "cfg")
        self.rules("deny *\n")
        for sub in (".claude/settings.json", ".claude-sandbox/x"):
            self.check(sub, "allow")

    def test_t20_unusable_marker_is_broken(self):
        os.makedirs(self.p(".claude"))
        real = self.p("rules.txt")
        with open(real, "w") as f:
            f.write("allow **\n")
        os.symlink(real, self.marker)
        self.assertIn("is a symlink", self.check("src.py", "deny"))
        os.unlink(self.marker)
        os.mkdir(self.marker)
        self.assertIn("not a regular file", self.check("src.py", "deny"))
        os.rmdir(self.marker)
        os.mkfifo(self.marker)
        self.assertIn("not a regular file", self.check("src.py", "deny"))
        os.unlink(self.marker)
        self.rules(b"allow \xff\n", mode="wb")
        self.assertIn("not UTF-8", self.check("src.py", "deny"))
        self.rules(b"#" * (64 * 1024) + b"\n", mode="wb")
        self.assertIn("larger than 64 KiB", self.check("src.py", "deny"))
        if os.geteuid() != 0:
            self.rules("allow **\n")
            os.chmod(self.marker, 0)
            try:
                self.assertIn("permission denied", self.check("src.py", "deny"))
            finally:
                os.chmod(self.marker, 0o644)

    def test_t20_claude_is_a_regular_file(self):
        with open(self.p(".claude"), "w") as f:
            f.write("x\n")
        self.assertIn("`.claude` is not a directory",
                      self.check("src.py", "deny"))

    def test_t20_symlinked_claude_dir_is_broken(self):
        cfg = os.path.join(self.tmp.name, "claude-cfg")
        os.makedirs(cfg)
        with open(os.path.join(cfg, "allow-checkout-edits"), "w") as f:
            f.write("allow **\n")
        os.symlink("../claude-cfg", self.p(".claude"))
        self.assertIn("the rules file or its .claude directory is a symlink",
                      self.check("src.py", "deny"))

    def test_t21_untracked_files_not_ruled(self):
        self.rules("deny *\n")
        self.check("bin/new", "allow")

    def test_t23_literal_pathspec(self):
        rc, out, _ = self.edit(self.p("s*"))
        self.assertEqual(out, {})

    def test_t24_bom_and_crlf(self):
        self.rules("﻿allow issues/**\r\n")
        self.check("issues/x.md", "allow")

    def test_t25_every_edit_tool_ruled(self):
        self.rules("deny *\nallow issues/**\n")
        for rel, want in (("issues/n.ipynb", "allow"), ("bin/n.ipynb", "deny")):
            for payload in ({"tool_name": "MultiEdit",
                             "tool_input": {"file_path": self.p(rel)}},
                            {"tool_name": "NotebookEdit",
                             "tool_input": {"notebook_path": self.p(rel)}},
                            {"tool_name": "NotebookEdit",
                             "tool_input": {"file_path": self.p(rel)}}):
                payload.update(cwd=self.repo, hook_event_name="PreToolUse")
                rc, out, _ = run_hook(payload)
                self.assertEqual(decision(out), want, (rel, payload))

    def test_t26_worktree_cwd_ignores_rules(self):
        self.rules("deny *\n")
        wt = os.path.join(self.tmp.name, "wt")
        git(self.repo, "worktree", "add", "-q", wt, "-b", "wt-branch")
        rc, out, _ = self.edit(os.path.join(wt, "bin/tool"), cwd=wt)
        self.assertEqual(out, {})

    def test_t28_index_spelling_bytes_safe(self):
        name = os.fsdecode(b"bin/\xff")
        with open(self.p(name), "w") as f:
            f.write("x\n")
        with open(self.p(" lead.md"), "w") as f:
            f.write("x\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "odd names")
        self.rules("allow **\ndeny bin/**\n")
        self.check(name, "deny")
        self.rules("allow **\ndeny ?lead.md\n")
        self.check(" lead.md", "deny")


class TestGlob(unittest.TestCase):
    """T27: compile_glob, every dialect line."""

    def m(self, pat, path):
        return cg.Rule(1, "allow", pat).matches(path)

    def test_table(self):
        for pat, path, want in (
                ("*", "a", True), ("*", "a/b", True), ("*", ".x", True),
                ("*.md", "a.md", True), ("*.md", "d/a.md", False),
                ("?", "a", True), ("?", "ab", False),
                ("a?c", "a/c", False),
                ("[abc]", "b", True), ("[!abc]", "b", False),
                ("[^abc]", "d", True), ("[a-c]x", "bx", True),
                ("a[!x]b", "a/b", False), ("a[.-0]b", "a/b", False),
                ("[]]", "]", True), ("[\\]", "\\", True),
                ("\\*", "*", True), ("\\*", "a", False),
                ("\\#x", "#x", True), ("\\!x", "!x", True),
                ("**", "a/b/c", True),
                ("a/**", "a", False), ("a/**", "a/b/c", True),
                ("**/x", "x", True), ("**/x", "a/b/x", True),
                ("a/**/b", "a/b", True), ("a/**/b", "a/x/y/b", True),
                ("**/**", "a/b", True), ("a/**/**/b", "a/x/b", True),
                ("bin/**", "bin/a\nb", True),
                ("/a", "a", True),
                ("a/", "a", False), ("a/", "a/b", True),
                ("a", "a/b/c", True), ("a/b", "a", False)):
            self.assertEqual(self.m(pat, path), want, (pat, path))

    def test_parse_errors(self):
        for pat in ("a**b", "a//b", "a/./b", "../a", "[z-a]", "[abc", "a\\",
                    "!x", "", "/"):
            with self.assertRaises((cg.GlobError, ValueError), msg=pat):
                cg.compile_glob(pat)

    def test_no_dot_in_regex(self):
        for pat in ("*", "?", "**", "a/**", "**/x", "a/**/b", "[^a]"):
            rx = cg.compile_glob(pat)[0].pattern
            self.assertNotIn(".", rx.replace("\\.", ""), pat)


@contextlib.contextmanager
def _clean_env():
    with mock.patch.dict(os.environ):
        for k in ("SANDBOX_ALLOW_CHECKOUT_EDITS",
                  "CLAUDE_KIT_ALLOW_CHECKOUT_EDITS", "GIT_DIR"):
            os.environ.pop(k, None)
        yield


class TestInProcess(RulesBase):
    """T22, T22b, T22c: an exception inside the rules code fails closed."""

    def run_main(self, path):
        payload = json.dumps({"tool_name": "Edit", "cwd": self.repo,
                              "tool_input": {"file_path": path}})
        buf = io.StringIO()
        with _clean_env(), mock.patch.object(sys, "stdin", io.StringIO(payload)), \
                contextlib.redirect_stdout(buf):
            with self.assertRaises(SystemExit):
                cg.run()
        return json.loads(buf.getvalue())

    def boom(self, *a, **k):
        raise RuntimeError("boom")

    def test_baseline(self):
        self.rules("allow **\n")
        self.assertEqual(self.run_main(self.tracked), {})

    def test_t22_parse_raises(self):
        self.rules("allow **\n")
        with mock.patch.object(cg, "parse_rules", self.boom):
            out = self.run_main(self.tracked)
        self.assertEqual(decision(out), "deny")
        self.assertIn("cannot be used: internal error", reason(out))

    def test_t22b_decide_raises(self):
        self.rules("allow **\n")
        with mock.patch.object(cg, "decide", self.boom):
            out = self.run_main(self.tracked)
        self.assertIn("cannot be used: internal error", reason(out))

    def test_t22c_marker_protection_raises(self):
        with mock.patch.object(cg, "is_marker_path", self.boom):
            self.assertEqual(self.run_main(self.tracked), MARKER_CHECK)

    def test_outer_handler_still_fails_open(self):
        with mock.patch.object(cg, "tracked_spelling", self.boom):
            self.assertEqual(self.run_main(self.tracked), {})


if __name__ == "__main__":
    unittest.main()
