#!/usr/bin/env python3
"""PostToolUse(Bash|Write|Edit): free ledger pointers.

A commit or an investigation write is already durable; the ledger records
WHERE, so the checkpoint's inventory is a lookup rather than a recall. Fires
in subagents and forks too (PostToolUse reaches them), so it returns {} when
agent_id/agent_type is present — a subagent's actions are not this session's
reasoning trail.

A commit's pointer names the repo the commit landed in, read from the
command itself: the commit's own `git -C <dir>` (relative to any `cd` or
`pushd` before it, across `&&`, `;`, `||`, `|`, newlines, subshells and brace
groups), else that `cd`, else the payload cwd. A `cd` backgrounded with a lone
`&` is skipped, since it runs in its own subshell. A derived directory is
resolved to its repo's toplevel. Still falling back to the cwd: a path that
does not exist or cannot be expanded here (a `$VAR`, a glob), `cd -`, and a
commit behind a wrapper (`time`, `command`, `env`). Not followed at all:
`GIT_DIR` and `--git-dir` (the `cd`/`-C` repo, else the cwd, is named) and
`popd` (the directory before it stays in force).
"""
import json, os, re, shlex, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger

COMMIT = re.compile(r"\bgit\b[^|;&]*\bcommit\b")
# Match "[main abc1234] msg" (git commit) OR "abc1234 msg" (git log --oneline,
# common right after a -q commit in compound commands).
SHA = re.compile(r"\[[\w./-]+ ([0-9a-f]{7,40})\]|^([0-9a-f]{7,40}) ", re.M)
# Control operators: shlex hands a run of these characters back as one token
# ("&&\n", ";\n\n"), so a token made only of them is an operator.
OPERATOR_CHARS = ";&|\n"
# git's global options that take the next token as their value.
GIT_VALUE_OPTS = {"-c", "--git-dir", "--work-tree", "--namespace",
                  "--exec-path", "--config-env", "--super-prefix"}
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
UNEXPANDABLE = re.compile(r"[$`*?\[]")


def _segments(command):
    """The command's simple commands as (tokens, background) pairs, split at
    its control operators and newlines; `background` is True when the
    command ends in a lone `&`. Subshell and brace-group delimiters are
    stripped from the tokens."""
    lex = shlex.shlex(command.replace("\\\n", " "), posix=True,
                      punctuation_chars=OPERATOR_CHARS)
    lex.whitespace_split = True
    lex.whitespace = " \t\r"
    lex.commenters = ""
    segs, cur = [], []
    for tok in lex:
        if tok and not tok.strip(OPERATOR_CHARS):
            segs.append((cur, tok.replace("\n", "") == "&"))
            cur = []
            continue
        bare = tok.lstrip("({!") if not cur else tok
        bare = bare.rstrip(")}")
        if bare or not tok:  # an empty quoted word ('') stays a word
            cur.append(bare)
    segs.append((cur, False))
    return [(s, bg) for s, bg in segs if s]


def _join(base, path):
    """`path` against `base`, or None when it cannot be resolved here."""
    if not path or UNEXPANDABLE.search(path):
        return None
    path = os.path.expanduser(path)
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(base, path)) if base else None


def _commit_dir(seg, base):
    """(is a git commit, its directory) for one simple command: its -C
    options applied in order to `base`; the directory is None when any of
    them cannot be resolved."""
    i = 0
    while i < len(seg) and ASSIGN.match(seg[i]):
        i += 1
    if i >= len(seg) or os.path.basename(seg[i]) != "git":
        return False, base
    i += 1
    d = base
    while i < len(seg) and seg[i].startswith("-"):
        opt = seg[i]
        if opt == "-C" and i + 1 < len(seg):
            # `git -C ''` is a no-op: it keeps the directory.
            d = _join(d, seg[i + 1]) if seg[i + 1] else d
            i += 2
        elif opt in GIT_VALUE_OPTS:
            i += 2
        else:
            i += 1
    return (i < len(seg) and seg[i] == "commit"), d


def _toplevel(d):
    """`d`'s git toplevel, else `d`; None when `d` is not a directory (git
    never runs on a path that does not resolve)."""
    if not d or not os.path.isdir(d):
        return None
    try:
        r = subprocess.run(("git", "-C", d, "rev-parse", "--show-toplevel"),
                           capture_output=True, text=True, timeout=3)
        top = r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        top = ""
    return top or d


def commit_repo(command, cwd):
    """The repo `command`'s git commit landed in: the commit's `git -C`
    (relative to any `cd` before it), else that `cd`, else `cwd`. A derived
    directory resolves to its toplevel; an unresolvable one falls back to
    `cwd`. Never raises."""
    try:
        base = cwd
        for seg, background in _segments(command):
            if seg[0] in ("cd", "pushd"):
                if background:  # `cd x &` runs in its own subshell
                    continue
                seg = [seg[0]] + [t for t in seg[1:]
                                  if t == "-" or not t.startswith("-")]
                if len(seg) == 1:
                    base = os.path.expanduser("~")
                elif seg[1] == "-":  # the previous directory: not tracked
                    base = None
                else:
                    base = _join(base, seg[1])
                continue
            is_commit, d = _commit_dir(seg, base)
            if is_commit:
                if d == cwd:
                    return cwd
                return _toplevel(d) or cwd
        return cwd
    except Exception:
        return cwd


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return
    if inp.get("agent_id") or inp.get("agent_type"):
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    tool = inp.get("tool_name")
    ti = inp.get("tool_input") or {}

    if tool == "Bash" and COMMIT.search(ti.get("command") or ""):
        resp = inp.get("tool_response") or {}
        out = resp.get("stdout") if isinstance(resp, dict) else str(resp)
        m = SHA.search(out or "")
        sha = (m.group(1) or m.group(2)) if m else "?"
        # Prefer the line that names the commit over whatever the compound
        # command printed first ("lint clean: 7 items" made a poor summary).
        lines = [l for l in (out or "").splitlines() if l.strip()]
        first = next((l for l in lines if sha != "?" and sha in l), lines[0] if lines else "")[:120]
        ledger.append(sid, "P", f"commit {sha}: {first}",
                      ref=commit_repo(ti.get("command") or "", inp.get("cwd")))
    elif tool in ("Write", "Edit"):
        path = ti.get("file_path") or ""
        if "/investigations/" in path or path.endswith(("HANDOFF.md", "INDEX.md")):
            ledger.append(sid, "P", f"wrote {os.path.basename(path)}", ref=path)
    print(json.dumps({}))


main()
