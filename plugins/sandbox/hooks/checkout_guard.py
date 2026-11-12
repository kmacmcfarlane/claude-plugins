#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit|NotebookEdit): enforce the checkout/
worktree convention from the missing direction.

The harness blocks worktree sessions from editing the main checkout, but
nothing stops a main-checkout session editing tracked files. This guard denies
the edit tools on a file tracked by git when the session's cwd is a MAIN
checkout (git-dir == git-common-dir), pointing at EnterWorktree / Agent
worktree isolation / the sandbox skill's convention section.

Allowed without question: linked-worktree cwds, non-git cwds, untracked files,
paths outside the repo, anything under .claude-sandbox/ or .claude/ (except
the rules file below), and the SANDBOX_ALLOW_CHECKOUT_EDITS=1 env escape hatch
(CLAUDE_KIT_ALLOW_CHECKOUT_EDITS=1 is honoured as a deprecated alias with the
same semantics), which overrides everything else here.

Per-repo path rules: <main checkout>/.claude/allow-checkout-edits lists
`allow <glob>` / `deny <glob>` lines. An implicit first rule `deny *` comes
before them and the LAST matching rule decides; `allow **` allows every
tracked file. The format's owner is the sandbox skill's
references/checkout-guard-rules.md. Agents' Edit/Write on any
.claude/allow-checkout-edits is denied, from any cwd.

Failure directions are split. Anything the guard cannot tell about the file
(bad stdin, git missing or broken) fails OPEN: a guard that breaks edits on
git errors is worse than no guard. The rules file fails CLOSED: an empty,
unreadable, symlinked or unparseable file, or any error while reading or
applying it, allows nothing. Known limitations (documented in the sandbox
skill): Bash writes (sed/heredoc) are out of scope, files inside submodules
are not guarded from the superproject's checkout (ls-files in the
superproject sees only the gitlink, so the target reads as untracked), and a
path spelled in a different case from the index reads as untracked.

The predicate is shared: checkout_state(cwd) says whether the guard is on for
a cwd (the override, then git state), and judge_path(cwd, path) runs the whole
order and returns (allowed, code, message), its codes frozen in CODES. The
order is: override, no path, the rules-file check (before any git call, so the
rules file is denied from every cwd), git state, then the per-path steps.

Block contract: exit 0 with hookSpecificOutput.permissionDecision "deny" on
stdout, per the hooks reference (PreToolUse decision control,
https://code.claude.com/docs/en/hooks).
"""
import collections, json, os, re, stat, subprocess, sys, unicodedata

MARKER_DIR = ".claude"
MARKER_NAME = "allow-checkout-edits"
MARKER_REL = MARKER_DIR + "/" + MARKER_NAME
MARKER_MAX = 64 * 1024

_WORKTREE_HINT = (
    "Enter a worktree first (EnterWorktree) or delegate to an Agent with "
    "worktree isolation; see the sandbox skill's checkout/worktree convention.")

BLOCK_MSG = (
    "This file is tracked in the main checkout. " + _WORKTREE_HINT +
    " Escape hatches, both the operator's to set: "
    "SANDBOX_ALLOW_CHECKOUT_EDITS=1, or allow rules in "
    ".claude/allow-checkout-edits."
)

MARKER_EDIT_MSG = (
    ".claude/allow-checkout-edits holds the checkout guard's rules and is the "
    "operator's to change: Edit and Write on it are denied in every session. "
    "Ask the operator to edit it, and do not write it another way."
)

MARKER_CHECK_MSG = (
    "The checkout guard could not check whether this path is its rules file "
    ".claude/allow-checkout-edits (internal error), so the edit is denied."
)

# Canonical opt-out first; the CLAUDE_KIT_ name is a deprecated alias kept so
# existing env files keep working. Either one set to exactly "1" allows.
ALLOW_ENV_VARS = ("SANDBOX_ALLOW_CHECKOUT_EDITS", "CLAUDE_KIT_ALLOW_CHECKOUT_EDITS")


def rule_msg(path, why):
    return ("This file (`%s`) is tracked in the main checkout and "
            ".claude/allow-checkout-edits denies it: %s. %s The rules are the "
            "operator's to change; SANDBOX_ALLOW_CHECKOUT_EDITS=1 overrides "
            "them." % (path, why, _WORKTREE_HINT))


def broken_msg(cause):
    return ("This file is tracked in the main checkout, and "
            ".claude/allow-checkout-edits cannot be used: %s. A broken rules "
            "file allows nothing, so every tracked file is denied as if it "
            "had no allow rules. Ask the operator to fix it, or enter a "
            "worktree first (EnterWorktree) or delegate to an Agent with "
            "worktree isolation." % cause)


# --- rules: parse, compile, decide (pure; tested in-process) ---------------

class RuleError(Exception):
    """A line of the rules file that does not parse."""

    def __init__(self, line, msg):
        super().__init__("line %d: %s" % (line, msg))
        self.line, self.msg = line, msg


class MarkerBroken(Exception):
    """The rules file cannot be used; the message is the cause."""


class GlobError(ValueError):
    pass


class Rule:
    __slots__ = ("line", "kind", "glob", "regex", "dir_only")

    def __init__(self, line, kind, glob):
        self.line, self.kind, self.glob = line, kind, glob
        self.regex, self.dir_only = compile_glob(glob)

    def describe(self):
        return "line %d: %s %s" % (self.line, self.kind, self.glob)

    def matches(self, path):
        parts = path.split("/")
        parents = ["/".join(parts[:i]) for i in range(1, len(parts))]
        cands = parents if self.dir_only else [path] + parents
        return any(self.regex.fullmatch(c) for c in cands)


def _class(seg, i):
    """Translate the class opening at seg[i] == '['; return (regex, next i)."""
    j = i + 1
    neg = j < len(seg) and seg[j] in "!^"
    if neg:
        j += 1
    start = j
    if j < len(seg) and seg[j] == "]":
        j += 1  # a ']' first in the class is literal
    close = seg.find("]", j)
    if close < 0:
        raise GlobError("unclosed `[`")
    body, items, k = seg[start:close], [], 0
    while k < len(body):
        if k + 2 < len(body) and body[k + 1] == "-":
            lo, hi = body[k], body[k + 2]
            if lo > hi:
                raise GlobError("reversed range `%s-%s`" % (lo, hi))
            items.append(re.escape(lo) + "-" + re.escape(hi))
            k += 3
        else:
            items.append(re.escape(body[k]))
            k += 1
    # (?!/) keeps the class off '/' even when its body or negation admits it.
    return "(?!/)[" + ("^" if neg else "") + "".join(items) + "]", close + 1


def _segment(seg):
    out, i = [], 0
    while i < len(seg):
        c = seg[i]
        if c == "*":
            if i + 1 < len(seg) and seg[i + 1] == "*":
                raise GlobError("`**` must be a whole segment")
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == "\\":
            if i + 1 >= len(seg):
                raise GlobError("trailing `\\`")
            i += 1
            out.append(re.escape(seg[i]))
        elif c == "[":
            rx, i = _class(seg, i)
            out.append(rx)
            continue
        else:
            out.append(re.escape(c))
        i += 1
    return "".join(out)


def compile_glob(pat):
    """Glob -> (compiled regex, dir_only). Anchored at the repo root; every
    wildcard is built from [^/]; consecutive `**` segments act as one."""
    if pat.startswith("!"):
        raise GlobError("a leading `!` is not negation here; write `\\!` "
                        "for a literal `!`")
    if pat.startswith("/"):
        pat = pat[1:]
    dir_only = pat.endswith("/")
    if dir_only:
        pat = pat[:-1]
    if not pat:
        raise GlobError("empty glob")
    segs = pat.split("/")
    for s in segs:
        if s == "":
            raise GlobError("empty path segment")
        if s in (".", ".."):
            raise GlobError("`%s` segment" % s)
    collapsed = []
    for s in segs:
        if not (s == "**" and collapsed and collapsed[-1] == "**"):
            collapsed.append(s)
    segs, n = collapsed, len(collapsed)
    if segs == ["**"]:
        body = "[^/]+(?:/[^/]+)*"
    else:
        body = ""
        for i, s in enumerate(segs):
            if s == "**":
                if i == 0:
                    body += "(?:[^/]+/)*"
                elif i == n - 1:
                    body += "/[^/]+(?:/[^/]+)*"
                else:
                    body += "(?:/[^/]+)*"
                continue
            if i > 0 and not (i == 1 and segs[0] == "**"):
                body += "/"
            body += _segment(s)
    return re.compile(body, re.DOTALL), dir_only


DEFAULT_RULE_LINE = 0


def parse_rules(text):
    """Text -> [Rule], the implicit `deny *` first. Raises RuleError."""
    rules = [Rule(DEFAULT_RULE_LINE, "deny", "*")]
    if text.startswith("﻿"):
        text = text[1:]
    for n, raw in enumerate(text.split("\n"), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        tok = line.split()
        if tok[0] not in ("allow", "deny"):
            raise RuleError(n, "unknown keyword `%s` (expected `allow` or "
                               "`deny`)" % tok[0])
        if len(tok) < 2:
            raise RuleError(n, "missing glob")
        if tok[1].startswith("#"):
            raise RuleError(n, "missing glob (a `#` starts a comment)")
        if len(tok) > 2 and not tok[2].startswith("#"):
            raise RuleError(n, "unexpected text after the glob (a glob holds "
                               "no whitespace; `?` matches a space)")
        try:
            rules.append(Rule(n, tok[0], tok[1]))
        except (GlobError, re.error) as e:
            raise RuleError(n, "bad glob `%s`: %s" % (tok[1], e))
    return rules


def decide(rules, path):
    """Last matching rule wins -> (allowed, rule)."""
    win = None
    for r in rules:
        if r.matches(path):
            win = r
    return win.kind == "allow", win


# --- the rules file on disk --------------------------------------------------

def load_marker(top, st):
    """Read and parse top/.claude/allow-checkout-edits (already lstat'd as
    st). Raises MarkerBroken or RuleError; never blocks (a hook that times out
    fails open)."""
    marker = os.path.join(top, MARKER_DIR, MARKER_NAME)
    if (stat.S_ISLNK(st.st_mode) or os.path.realpath(marker)
            != os.path.join(os.path.realpath(top), MARKER_DIR, MARKER_NAME)):
        raise MarkerBroken("the rules file or its .claude directory is a "
                           "symlink")
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0) \
        | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(marker, flags)
    except PermissionError:
        raise MarkerBroken("permission denied reading it")
    except OSError as e:
        raise MarkerBroken("cannot open it (%s)" % (e.strerror or e))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise MarkerBroken("it is not a regular file")
        chunks, size = [], 0
        while size <= MARKER_MAX:
            b = os.read(fd, MARKER_MAX + 1 - size)
            if not b:
                break
            chunks.append(b)
            size += len(b)
    finally:
        os.close(fd)
    if size > MARKER_MAX:
        raise MarkerBroken("it is larger than 64 KiB")
    try:
        text = b"".join(chunks).decode("utf-8")
    except UnicodeDecodeError:
        raise MarkerBroken("it is not UTF-8")
    return parse_rules(text)


def judge_marker(top, path):
    """(allowed, code, reason) for tracked `path` (index spelling) under the
    rules file; code `rules`, or `broken` when the file cannot be used. Every
    failure past this point is closed: a deny, never an allow."""
    try:
        marker = os.path.join(top, MARKER_DIR, MARKER_NAME)
        try:
            st = os.lstat(marker)
        except FileNotFoundError:
            return False, "rules", BLOCK_MSG
        except NotADirectoryError:
            return False, "broken", broken_msg("`.claude` is not a directory")
        except OSError as e:
            return False, "broken", broken_msg(
                "cannot read it (%s)" % (e.strerror or e))
        try:
            rules = load_marker(top, st)
        except (MarkerBroken, RuleError) as e:
            return False, "broken", broken_msg(str(e))
        allowed, rule = decide(rules, path)
        if allowed:
            return True, "rules", None
        if rule.line != DEFAULT_RULE_LINE:
            why = "`%s` is the last rule that matches" % rule.describe()
        elif len(rules) == 1:
            why = ("the file has no rules, so the default rule `deny *` "
                   "applies; `allow **` allows everything")
        else:
            why = ("no rule in the file matches, so the default rule "
                   "`deny *` applies")
        return False, "rules", rule_msg(path, why)
    except Exception:
        return False, "broken", broken_msg("internal error")


# --- the hook ----------------------------------------------------------------

def is_marker_path(cwd, path):
    """True when the lexical or the resolved target names
    .claude/allow-checkout-edits, compared case-folded."""
    lexical = os.path.normpath(os.path.join(cwd, path))
    for cand in (lexical, os.path.realpath(os.path.join(cwd, path))):
        parts = cand.split(os.sep)
        if (len(parts) >= 2 and parts[-1].casefold() == MARKER_NAME
                and parts[-2].casefold() == MARKER_DIR):
            return True
    return False


def git(cwd, *args):
    try:
        r = subprocess.run(("git", "-C", cwd) + args, capture_output=True,
                           text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def tracked_spelling(top, rel):
    """The index's own spelling of tracked `rel`, or None when untracked or
    git fails. Bytes, decoded with fsdecode, never stripped."""
    try:
        r = subprocess.run(("git", "-C", top, "--literal-pathspecs",
                            "ls-files", "-z", "--full-name", "--error-unmatch",
                            "--", rel), capture_output=True, timeout=5)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    entries = r.stdout.split(b"\0")
    if entries and entries[-1] == b"":
        entries.pop()
    if len(entries) == 1:
        return os.fsdecode(entries[0])
    return rel.replace(os.sep, "/")


def emit(decision=None, reason=None):
    if decision is None:
        print(json.dumps({}))
    else:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
                "permissionDecisionReason": reason,
            }
        }))
    sys.exit(0)


def allow():
    emit()


def deny(reason=BLOCK_MSG):
    emit("deny", reason)


# --- the predicate: one order, shared by the guard and the notice -----------

# Every code judge_path returns, frozen: skills and tests match these words.
CODES = ("override", "no-path", "marker", "not-git", "linked-worktree",
         "outside", "exempt", "untracked", "rules", "broken")

CheckoutState = collections.namedtuple("CheckoutState", "on why top")


def override_set(env=None):
    """True when either override name is exactly "1"."""
    env = os.environ if env is None else env
    return any(env.get(v) == "1" for v in ALLOW_ENV_VARS)


def git_state(cwd):
    """(why, top): `main-checkout` with the realpath'd top, `linked-worktree`,
    or `not-git` (no repo, git absent or broken). Never raises."""
    try:
        lines = (git(cwd, "rev-parse", "--git-dir", "--git-common-dir",
                     "--show-toplevel") or "").splitlines()
        if len(lines) != 3:
            return "not-git", None  # not a git repo, or git unavailable/broken
        git_dir, common_dir, top = lines
        if (os.path.realpath(os.path.join(cwd, git_dir))
                != os.path.realpath(os.path.join(cwd, common_dir))):
            return "linked-worktree", None  # the harness guards this direction
        return "main-checkout", os.path.realpath(top)
    except Exception:
        return "not-git", None


def checkout_state(cwd, env=None):
    """Is the guard on for this cwd? `why` is `override`, `not-git`,
    `linked-worktree` or `main-checkout`; `on` only for the last."""
    if override_set(env):
        return CheckoutState(False, "override", None)
    why, top = git_state(cwd)
    return CheckoutState(why == "main-checkout", why, top)


ESCAPED_CATEGORIES = ("Cc", "Cf", "Zl", "Zp")


def escape_path(s):
    """A path made safe to put in text: `\\` -> `\\\\`, the backtick -> `\\x60`,
    and every control, format, line- or paragraph-separator character as
    `\\xNN`, `\\uNNNN` or `\\UNNNNNNNN`. A directory name can be chosen by
    whoever made the repo, so nothing in it may break a line or a code span."""
    out = []
    for ch in s:
        o = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == "`":
            out.append("\\x60")
        elif unicodedata.category(ch) in ESCAPED_CATEGORIES:
            out.append("\\x%02x" % o if o < 0x100 else
                       "\\u%04x" % o if o <= 0xFFFF else "\\U%08x" % o)
        else:
            out.append(ch)
    return "".join(out)


def judge_path(cwd, path, env=None):
    """(allowed, code, message) for an edit of `path` from `cwd`, in this
    order: (a) override, (b) no path, (c) the rules-file check, before any git
    call, so the rules file is denied from every cwd, (d) git state, (e) the
    per-path steps. `message` is the deny reason, None when allowed."""
    if override_set(env):
        return True, "override", None
    if not path or not isinstance(path, str):
        return True, "no-path", None

    # The rules file is the operator's: no agent edit of it, from any cwd.
    try:
        hit = is_marker_path(cwd, path)
    except Exception:
        return False, "marker", MARKER_CHECK_MSG
    if hit:
        return False, "marker", MARKER_EDIT_MSG

    why, top = git_state(cwd)
    if why != "main-checkout":
        return True, why, None

    target = path if os.path.isabs(path) else os.path.join(cwd, path)
    target = os.path.realpath(target)
    rel = os.path.relpath(target, top)
    if rel == ".." or rel.startswith(".." + os.sep):
        return True, "outside", None
    if rel.split(os.sep, 1)[0] in (".claude-sandbox", ".claude"):
        return True, "exempt", None  # sandbox/config paths are process, not work

    spelled = tracked_spelling(top, rel)
    if spelled is None:
        return True, "untracked", None  # untracked (or git failed): fail open

    return judge_marker(top, spelled)


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        allow()

    tool_input = inp.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    cwd = inp.get("cwd") or os.getcwd()
    allowed, _code, reason = judge_path(cwd, path)
    if allowed:
        allow()
    deny(reason)


def run():
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        # Never crash the tool call: an unexpected error outside the rules
        # file fails open.
        print(json.dumps({}))
        sys.exit(0)


if __name__ == "__main__":
    run()
