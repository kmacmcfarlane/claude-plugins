#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit|NotebookEdit): enforce the checkout/
worktree convention from the missing direction.

The harness blocks worktree sessions from editing the main checkout, but
nothing stops a main-checkout session editing tracked files. This guard denies
the edit tools on a file tracked by git when the session's cwd is a MAIN
checkout (git-dir == git-common-dir), pointing at EnterWorktree / Agent
worktree isolation / the sandbox skill's convention section.

Allowed without question: linked-worktree cwds, non-git cwds, untracked files,
paths outside the repo, anything under .claude-sandbox/ or .claude/, the
SANDBOX_ALLOW_CHECKOUT_EDITS=1 env escape hatch (CLAUDE_KIT_ALLOW_CHECKOUT_EDITS=1
is honoured as a deprecated alias with the same semantics), and a per-repo
.claude/allow-checkout-edits marker file.

Every failure path fails OPEN (allow, exit 0): a guard that breaks edits on
git errors is worse than no guard. Known limitations (documented in the
sandbox skill): Bash writes (sed/heredoc) are out of scope, and files inside
submodules are not guarded from the superproject's checkout — ls-files in the
superproject sees only the gitlink, so the target reads as untracked.

Block contract: exit 0 with hookSpecificOutput.permissionDecision "deny" on
stdout, per the hooks reference (PreToolUse decision control).
"""
import json, os, subprocess, sys

BLOCK_MSG = (
    "This file is tracked in the main checkout. Enter a worktree first "
    "(EnterWorktree) or delegate to an Agent with worktree isolation; see the "
    "sandbox skill's checkout/worktree convention. Escape hatches: "
    "SANDBOX_ALLOW_CHECKOUT_EDITS=1 or a .claude/allow-checkout-edits file."
)

# Canonical opt-out first; the CLAUDE_KIT_ name is a deprecated alias kept so
# existing env files keep working. Either one set to exactly "1" allows.
ALLOW_ENV_VARS = ("SANDBOX_ALLOW_CHECKOUT_EDITS", "CLAUDE_KIT_ALLOW_CHECKOUT_EDITS")


def git(cwd, *args):
    try:
        r = subprocess.run(("git", "-C", cwd) + args, capture_output=True,
                           text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def allow():
    print(json.dumps({}))
    sys.exit(0)


def deny():
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": BLOCK_MSG,
        }
    }))
    sys.exit(0)


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        allow()

    if any(os.environ.get(v) == "1" for v in ALLOW_ENV_VARS):
        allow()

    tool_input = inp.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path or not isinstance(path, str):
        allow()

    cwd = inp.get("cwd") or os.getcwd()

    lines = (git(cwd, "rev-parse", "--git-dir", "--git-common-dir",
                 "--show-toplevel") or "").splitlines()
    if len(lines) != 3:
        allow()  # not a git repo, or git unavailable/broken
    git_dir, common_dir, top = lines
    if (os.path.realpath(os.path.join(cwd, git_dir))
            != os.path.realpath(os.path.join(cwd, common_dir))):
        allow()  # linked worktree: the harness already guards that direction
    top = os.path.realpath(top)

    target = path if os.path.isabs(path) else os.path.join(cwd, path)
    target = os.path.realpath(target)
    rel = os.path.relpath(target, top)
    if rel == ".." or rel.startswith(".." + os.sep):
        allow()  # outside the repo
    if rel.split(os.sep, 1)[0] in (".claude-sandbox", ".claude"):
        allow()  # sandbox/config paths are process, not work

    if os.path.exists(os.path.join(top, ".claude", "allow-checkout-edits")):
        allow()  # per-repo marker escape hatch

    if git(top, "ls-files", "--error-unmatch", "--", rel) is None:
        allow()  # untracked (or git failed): fail open

    deny()


try:
    main()
except SystemExit:
    raise
except Exception:
    # Never crash the tool call: any unexpected error fails open.
    print(json.dumps({}))
    sys.exit(0)
