#!/usr/bin/env python3
"""SessionStart and SubagentStart: tell the model, before its first edit, that
the checkout guard is on for its working directory.

The guard (checkout_guard.py) denies the edit tools on tracked files from a
main checkout only when an edit is attempted, and it does not check Bash
writes. This hook puts one short, factual paragraph into the context of every
session (SessionStart, every source, so it comes back after compact and clear)
and every sub-agent (SubagentStart, every agent type: a sub-agent does not see
the session's SessionStart context) whose cwd is a main checkout the guard is
on for. It shares the guard's predicate (checkout_guard.checkout_state), so
the two cannot disagree.

Output: when the notice applies, one JSON object whose
hookSpecificOutput.additionalContext is the paragraph, hookEventName the
input's event (https://code.claude.com/docs/en/hooks § SessionStart,
§ SubagentStart). Otherwise it prints NOTHING and exits 0: the guard off
(override, not a git repo, git absent or broken, a linked worktree), bad
stdin, any error, or a rules file whose last rule allows every file. Plain
stdout on SessionStart is added to the model's context
(https://code.claude.com/docs/en/hooks § Exit code output), so no stray output
is harmless. No notice is the safe failure: the guard still enforces.

The paragraph ends with the guard's status command, naming the real absolute
path of checkout_guard.py, shell-quoted, so a session can ask the guard about
its cwd, or one file, with no lookup. A path that needs escaping, or is over the
cap, leaves the sentence out.

The text is deterministic for a given repo state (no timestamps or ids): on a
repeat SubagentStart for the same sub-agent the copy already in its context is
not injected again (https://code.claude.com/docs/en/hooks § SubagentStart).
Stateless: no marker, no file written.
"""
import json, os, shlex, sys

try:
    import checkout_guard as cg  # this script's own directory, never the cwd's
except Exception:  # pragma: no cover - a broken install prints nothing
    cg = None

EVENTS = ("SessionStart", "SubagentStart")

# Each inserted path, after escaping, is at most this long; over it the path is
# replaced by FALLBACK_TOP.
PATH_CAP = 256
FALLBACK_TOP = "this repository's main checkout"

ALLOW_CLAUSE = " except paths .claude/allow-checkout-edits allows"

# The status sentence names the guard script's real absolute path,
# shell-quoted; it is left out when the path needs escaping or is over
# PATH_CAP quoted (either way the command would not run as printed).
STATUS_CLAUSE = (" python3 {cmd} --status prints whether the guard is on for "
                 "the current directory.")

TEXT = (
    "sandbox checkout guard: {top} is a main git checkout, and the sandbox "
    "plugin's checkout guard is on for it. Edit, Write, MultiEdit and "
    "NotebookEdit on git-tracked files under it are denied{allow}. The "
    "sandbox convention is that changes to tracked files are made from a "
    "linked worktree: EnterWorktree, an Agent with isolation \"worktree\", or "
    "git worktree add .claude/worktrees/<name>. The guard does not check Bash "
    "writes; a tracked file changed through Bash from this checkout breaks the "
    "same convention. Untracked files and paths under .claude/ and "
    ".claude-sandbox/ are exempt, except the rules file "
    ".claude/allow-checkout-edits, which is the operator's to change: Edit "
    "and Write on it are denied from every working directory, and a Bash "
    "write to it is not checked but breaks the same rule. A working directory "
    "that is a linked worktree is not affected. The guard catches accidental "
    "edits through the edit tools; it is not a security boundary. The "
    "overrides (SANDBOX_ALLOW_CHECKOUT_EDITS=1, rules in "
    ".claude/allow-checkout-edits) are the operator's to set.{status}"
)


def allows_everything(glob):
    """True for `*`, `**` and their `/`-led and repeated-`**` spellings: each
    matches every path, since a glob also matches any parent directory. A
    sufficient test, not a complete one: a miss only over-warns."""
    g = glob[1:] if glob.startswith("/") else glob
    if g == "*":
        return True
    return g != "" and all(s == "**" for s in g.split("/"))


def rules_view(top):
    """(allow_all, has_allow) for top's rules file. A missing, broken or
    unreadable file is (False, False): it allows nothing."""
    try:
        marker = os.path.join(top, cg.MARKER_DIR, cg.MARKER_NAME)
        rules = cg.load_marker(top, os.lstat(marker))
    except Exception:
        return False, False
    last = rules[-1]
    allow_all = last.kind == "allow" and allows_everything(last.glob)
    return allow_all, any(r.kind == "allow" for r in rules)


def guard_script():
    """The absolute, symlink-resolved path of the checkout_guard.py this hook
    shares its predicate with."""
    return os.path.realpath(cg.__file__)


def notice_text(top, has_allow, script=None):
    """The paragraph for main checkout `top`; `script` is the guard's path
    for the status sentence (default: guard_script())."""
    esc = cg.escape_path(top)
    shown = "`%s`" % esc if len(esc) <= PATH_CAP else FALLBACK_TOP
    script = guard_script() if script is None else script
    cmd = shlex.quote(script)
    # An escaped path would not run as printed, so it is left out, as is one
    # over the cap.
    ok = cg.escape_path(script) == script and len(cmd) <= PATH_CAP
    status = STATUS_CLAUSE.format(cmd=cmd) if ok else ""
    return TEXT.format(top=shown, allow=ALLOW_CLAUSE if has_allow else "",
                       status=status)


def notice(inp, env=None):
    """The hook's JSON output for input `inp`, or None for silence."""
    if cg is None or not isinstance(inp, dict):
        return None
    event = inp.get("hook_event_name")
    if event not in EVENTS:
        return None
    cwd = inp.get("cwd") or os.getcwd()
    if not isinstance(cwd, str):
        return None
    state = cg.checkout_state(cwd, env)
    if not state.on:
        return None
    allow_all, has_allow = rules_view(state.top)
    if allow_all:
        return None
    return json.dumps({"hookSpecificOutput": {
        "hookEventName": event,
        "additionalContext": notice_text(state.top, has_allow),
    }})


def run():
    try:
        out = notice(json.load(sys.stdin))
    except Exception:
        out = None
    if out is not None:
        sys.stdout.write(out + "\n")
    sys.exit(0)


if __name__ == "__main__":
    run()
