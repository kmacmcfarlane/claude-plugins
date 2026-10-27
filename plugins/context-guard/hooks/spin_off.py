#!/usr/bin/env python3
"""Write a spin-off: a new session's own rehydration manifest, written by this
session before the new one starts, plus the line that starts it.

    python3 spin_off.py --from <draft> --topic <topic> [--name <name>]
        [--launch-dir <dir>] [--librarian <name>] [--prompt-file <file>]
        [--no-session-id]

A spin-off is a new session, in a new claude-sandbox (or a plain `claude`),
that starts from a compacted, topic-scoped handoff of this one while this
session goes on. This is a CLI the spin-off skill runs, beside
mark_checkpoint.py and handoff_path.py, not a registered hook.

What it does, in order; any refusal exits 2 with nothing written:

  - takes this session's id (the parent) from $CLAUDE_CODE_SESSION_ID,
    refused when unset or not a plain id;
  - checks the topic, raw and before any stripping, against TOPIC_RE (a
    letter or digit, then letters, digits, space, `.`, `_`, `-`; at most 40);
  - generates a fresh UUID v4, the child id, and installs the draft at the
    child's own store path, claude-kit/handoff/<child>/HANDOFF.md, through
    mark_checkpoint.install_draft with fresh=True: the draft's refusals (missing,
    unreadable, over 256 KB, last written over 30 minutes ago), the link
    checks and the atomic 0700/0600 install are that function's, and an
    existing <child>/ in any form is refused;
  - adds the three role HOLD lines after the holds it carries and stamps the
    frontmatter with mark_checkpoint.restamp: `session:` the child,
    `spun_from:` the parent, `mode: handoff`, `by: spin-off`, and `written`,
    `head`, `branch`, `top` from the LAUNCH directory (the one the line cds
    into, where the new session works), never from this session's cwd; a
    draft with no frontmatter, or with a `mode_skill:` (a spin-off has no
    standing mode), is refused and the install removed;
  - writes the spin-off record, claude-kit/spin-off/<child>.json (0700/0600,
    temp file and os.replace), and prunes records over 14 days old: regular
    `*.json` files only, judged by lstat, never through a link;
  - appends one pointer line to this session's ledger,
    `P spin-off <name> (<child>) -> <manifest path>`;
  - prints `installed <path>`, `spin-off <child>`, then the launch line, last
    and alone on its line.

It never touches this session's own manifest or its gate state (no
checkpoint is recorded), and the new session has no gate state until its own
first turn. It never prints `--dangerous`: the launch line takes the
project's configured permission mode, and the skill's close explains the
trade.

The launch line (every value single-quoted, a `'` written `'\\''`):

    cd '<launch dir>' && claude-sandbox --new -- --session-id '<child>' --name '<name>' '<opener>'

when $CLAUDE_SANDBOX_PROJECT_DIR is set (the session runs in a claude-sandbox,
so the operator has the launcher on the host), else the plain form

    cd '<launch dir>' && claude --session-id '<child>' --name '<name>' '<opener>'

`--session-id` (documented, https://code.claude.com/docs/en/cli-reference)
makes the installed file the new session's own manifest by path. Whether it
passes through claude-sandbox and sets the new session's id is unverified
until the spike runs; PRINT_SESSION_ID is the one switch for its default, and
`--no-session-id` omits it for one run. Without it the same file still works:
the opener tells the new session to Read it in full, and a whole-file Read of
a `mode: handoff` manifest adopts it (lineage.post_read). That is also why
this session must never Read the file itself: it would adopt it.

The name, the librarian, the parent's name and the prompt lose control
characters, Unicode format characters (bidi controls included) and line
breaks before they reach the opener or the line; the name and the librarian
must then match NAME_RE and the repo name REPO_RE, since they sit inside the
opener, itself one quoted shell word. The stamped frontmatter is read back
as the rehydrate hook reads it and refused unless it reads as stamped.
"""
import argparse, json, os, re, stat, sys, tempfile, time, unicodedata, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L
import mark_checkpoint as M

# The spike decides this default: True prints `--session-id <child>` in the
# launch line; False leaves it out and the opener's Read is the only path.
PRINT_SESSION_ID = True

TOPIC_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ._-]{0,39}")
# A session name (the spin-off's, the librarian's), after clean(): it is set
# inside the opener, which is itself one quoted shell word, so no quote, `$`,
# backtick or other shell character may reach it.
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}")
REPO_RE = re.compile(r"[A-Za-z0-9._-]+")
PROMPT_MAX = 16 * 1024
RECORD_DIR = ("claude-kit", "spin-off")
RECORD_TTL_S = 14 * 24 * 3600
RECORD_V = 1

OPENER = ("You are a spin-off of {parent} in {repo}, on: {topic}. "
          "Read (the Read tool) {manifest} in full first. "
          "You are not this repo's librarian: do not run librarian-mode and keep "
          "your session name. "
          "Use wi for your own items (claim with --as {name_q}); never merge to "
          "main or push: {hand_in} "
          "Then: {prompt}")
HAND_IN = ("hand finished branches to the librarian {librarian} with "
           "SendMessage, first line `hand-in from spin-off {name}: <branch> @ "
           "<full sha>`; wait for `filed <id>`.")
NO_LIBRARIAN = "no librarian is live: when a branch is ready, tell the operator."
NO_PROMPT = "continue with the manifest's Goal."

# Short, and after the carried holds: the startup header carries at most
# rehydrate.HOLDS_MAX lines in rehydrate.HOLDS_BUDGET characters, and the
# holds this session hands over must not be the ones crowded out.
ROLE_HOLDS = (
    "HOLD librarian mode and the bare name {repo} — {writer} — until the "
    "operator says otherwise",
    "HOLD merging to main and pushing — {hand} — until the operator says "
    "otherwise",
    "HOLD writing items another session holds — until it releases them",
)


class Refused(Exception):
    """A spin-off not written; the message says why."""


def new_child_id():
    """A fresh UUID v4: the new session's id. A test seam."""
    return str(uuid.uuid4())


def clean(s):
    """`s` on one line: line breaks and tabs become spaces, every other
    control, format (bidi controls, zero-width joiners), surrogate or
    private-use character is dropped, and runs of spaces collapse."""
    out = []
    for ch in s or "":
        cat = unicodedata.category(ch)
        if ch in "\t\n\r\x0b\x0c" or cat in ("Zl", "Zp"):
            out.append(" ")
        elif cat in ("Cc", "Cf", "Cs", "Co"):
            continue
        else:
            out.append(ch)
    return " ".join("".join(out).split())


def sq(s):
    """POSIX single quotes: the shell reads the value byte for byte."""
    return "'" + s.replace("'", "'\\''") + "'"


def main_checkout(cwd):
    """The main checkout of the repo at `cwd` (a worktree's included), else
    its toplevel, else None."""
    import rehydrate as R
    common = R.git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if common and os.path.basename(common.rstrip(os.sep)) == ".git":
        return os.path.dirname(common.rstrip(os.sep))
    return R.git(cwd, "rev-parse", "--show-toplevel")


def launch_dir(given, environ, cwd):
    d = given or environ.get("CLAUDE_SANDBOX_PROJECT_DIR") or main_checkout(cwd)
    if not d:
        raise Refused("no launch directory: pass --launch-dir, or run inside "
                      "a git checkout")
    d = os.path.abspath(d)
    if not os.path.isdir(d):
        raise Refused(f"the launch directory {d} is not a directory")
    return d


def stamp_fields(top_dir, child, parent, now):
    """The frontmatter this writer stamps, `head`, `branch` and `top` from the
    launch directory."""
    import rehydrate as R
    top = R.git(top_dir, "rev-parse", "--show-toplevel") or top_dir
    fields = {"written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
              "top": top, "session": child}
    head = R.git(top, "rev-parse", "--short", "HEAD")
    if head:
        fields["head"] = head
        branch = R.git(top, "rev-parse", "--abbrev-ref", "HEAD")
        if branch:
            fields["branch"] = branch
    fields.update({"spun_from": parent, "mode": "handoff", "by": "spin-off"})
    return fields


def role_holds(repo, librarian):
    if librarian:
        writer = f"{librarian} is the single writer"
        hand = f"hand branches to {librarian}"
    else:
        writer = "the librarian is the single writer (none live: the operator decides)"
        hand = "hand branches to the librarian (none live: tell the operator)"
    return [h.format(repo=repo, writer=writer, hand=hand) for h in ROLE_HOLDS]


_HEADING = re.compile(r"##[ \t]+([^\n]*?)[ \t]*(?:\(.*\))?[ \t]*:?[ \t]*$")


def _heading(line):
    m = _HEADING.fullmatch(line.rstrip("\r\n"))
    return m.group(1).strip().lower() if m else None


def with_role_holds(text, holds):
    """`text` with `holds` as the last lines of its `## Holds` section, after
    the holds it carries (a lone `None` there is replaced); a Holds section is added before
    `## In flight`, else at the end, when there is none. Frontmatter
    untouched."""
    lines = text.splitlines(keepends=True)
    eol = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"
    new = [f"- {h}{eol}" for h in holds]
    start = 0
    if lines and lines[0].strip() == "---":
        start = next((i + 1 for i in range(1, len(lines))
                      if lines[i].strip() == "---"), len(lines))
    at = next((i for i in range(start, len(lines))
               if _heading(lines[i]) == "holds"), None)
    if at is None:
        at = next((i for i in range(start, len(lines))
                   if _heading(lines[i]) == "in flight"), None)
        block = [f"## Holds{eol}"] + new + [eol]
        if at is None:
            tail = "" if not lines or lines[-1].endswith("\n") else eol
            return "".join(lines) + tail + eol + "".join(block)
        return "".join(lines[:at] + block + lines[at:])
    end = next((i for i in range(at + 1, len(lines))
                if lines[i].startswith("## ")), len(lines))
    body = lines[at + 1:end]
    content = [ln for ln in body if ln.strip()]
    if len(content) == 1 and \
            content[0].strip().lstrip("-* ").rstrip(".").lower() == "none":
        body = []                             # the lone `None` goes
    last = max((i for i, ln in enumerate(body) if ln.strip()), default=-1)
    body = body[:last + 1] + new + (body[last + 1:] or [eol])
    return "".join(lines[:at + 1] + body + lines[end:])


def opener(parent, repo, topic, manifest, name, librarian, prompt):
    hand_in = HAND_IN.format(librarian=librarian, name=name) if librarian \
        else NO_LIBRARIAN
    return OPENER.format(parent=parent, repo=repo, topic=topic,
                         manifest=manifest, name_q=sq(name), hand_in=hand_in,
                         prompt=prompt or NO_PROMPT)


def launch_line(where, child, name, open_text, sandbox, session_id):
    parts = ["cd", sq(where), "&&"]
    parts += ["claude-sandbox", "--new", "--"] if sandbox else ["claude"]
    if session_id:
        parts += ["--session-id", sq(child)]
    parts += ["--name", sq(name), sq(open_text)]
    return " ".join(parts)


def parent_name(parent, environ):
    """This session's own name from its registry entry,
    <config dir>/sessions/<CLAUDE_PID>.json, read only when its `sessionId`
    is this session's; else None. No other entry is ever opened. The entry's
    `sessionId` and `name` fields are not documented (fields observed on this
    session's own entry file, Claude Code 2.1.292; not documented), so a
    missing or changed field reads as no name."""
    pid = environ.get("CLAUDE_PID") or ""
    if not pid.isdigit():
        return None
    try:
        with open(os.path.join(L._base_dir(), "sessions", f"{pid}.json")) as fh:
            d = json.load(fh)
    except Exception:
        return None
    if not isinstance(d, dict) or d.get("sessionId") != parent:
        return None
    n = clean(d.get("name")) if isinstance(d.get("name"), str) else ""
    return n or None


def record_dir():
    return os.path.join(L._base_dir(), *RECORD_DIR)


def write_record(rec, now):
    """Install `rec` as <record dir>/<session_id>.json, 0600, atomically, then
    prune. Returns a warning line or None; never raises."""
    try:
        d = record_dir()
        os.makedirs(d, mode=0o700, exist_ok=True)
        if os.path.islink(d) or not os.path.isdir(d):
            return f"spin_off.py: warning: {d} is not a directory; no record written"
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".rec.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as fh:
                json.dump(rec, fh, indent=1)
                fh.write("\n")
            os.chmod(tmp, 0o600)
            os.replace(tmp, os.path.join(d, rec["session_id"] + ".json"))
            tmp = None
        finally:
            if tmp:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
        prune(d, now)
        return None
    except Exception as e:
        return f"spin_off.py: warning: no spin-off record written ({type(e).__name__})"


def prune(d, now):
    """Remove records older than RECORD_TTL_S: regular `*.json` files only,
    judged by lstat, so a link (to anything) and any other file are left."""
    for e in os.scandir(d):
        if not e.name.endswith(".json"):
            continue
        try:
            st = os.lstat(e.path)
            if stat.S_ISREG(st.st_mode) and now - st.st_mtime > RECORD_TTL_S:
                os.unlink(e.path)
        except OSError:
            pass


def _remove_install(target):
    for f in (os.unlink, os.rmdir):
        try:
            f(target if f is os.unlink else os.path.dirname(target))
        except OSError:
            pass


def _value(s):
    if s.startswith("-"):
        raise argparse.ArgumentTypeError(f"{s!r} looks like a flag, not a value")
    return s


def parser():
    p = argparse.ArgumentParser(
        prog="spin_off.py", allow_abbrev=False,
        description="Install a spin-off's own manifest and print its launch line.")
    p.add_argument("--from", dest="draft", required=True, type=_value,
                   help="the drafted manifest (in the session scratchpad)")
    p.add_argument("--topic", required=True, type=_value,
                   help="the topic: a letter or digit, then letters, digits, "
                        "space . _ -, at most 40")
    p.add_argument("--name", type=_value,
                   help="the new session's name (default '<repo> - <topic>')")
    p.add_argument("--launch-dir", type=_value,
                   help="the directory the line cds into (default "
                        "$CLAUDE_SANDBOX_PROJECT_DIR, else the main checkout)")
    p.add_argument("--librarian", type=_value,
                   help="the live librarian's session name, if any")
    p.add_argument("--prompt-file", type=_value,
                   help="the operator's prompt for the new session")
    p.add_argument("--no-session-id", action="store_true",
                   help="leave --session-id out of the launch line")
    return p


def run(args, environ, cwd, now, child=None):
    """(stdout lines, warning lines); raises Refused with nothing written."""
    parent = environ.get("CLAUDE_CODE_SESSION_ID") or ""
    if not L._SAFE_SID.fullmatch(parent):
        raise Refused("$CLAUDE_CODE_SESSION_ID is unset or not a plain id")
    if not TOPIC_RE.fullmatch(args.topic):
        raise Refused(f"the topic must match ^{TOPIC_RE.pattern}$ (a letter or "
                      f"digit, then letters, digits, space . _ -, at most 40)")
    where = launch_dir(args.launch_dir, environ, cwd)
    import rehydrate as R
    top = R.git(where, "rev-parse", "--show-toplevel") or where
    repo = os.path.basename(top)
    for what, v in (("launch directory", where), ("repo toplevel", top),
                    ("repo name", repo)):
        if any(unicodedata.category(ch)[0] == "C"
               or unicodedata.category(ch) in ("Zl", "Zp") for ch in v):
            raise Refused(f"the {what} holds a control, format or line-break "
                          f"character")
    if not REPO_RE.fullmatch(repo):
        raise Refused("the repo name may hold only letters, digits, . _ -")
    name = clean(args.name) if args.name is not None else f"{repo} - {args.topic}"
    librarian = clean(args.librarian) if args.librarian is not None else ""
    if not NAME_RE.fullmatch(name) or \
            (args.librarian is not None and not NAME_RE.fullmatch(librarian)):
        raise Refused(f"a session name must match ^{NAME_RE.pattern}$ (a letter "
                      f"or digit, then letters, digits, space . _ -, at most 80)")
    if name == repo:
        raise Refused(f"the name must not be the bare {repo!r}, which marks "
                      f"this repo's librarian")
    prompt = ""
    if args.prompt_file is not None:
        try:
            with open(args.prompt_file, encoding="utf-8", errors="replace") as fh:
                raw = fh.read(PROMPT_MAX + 1)
        except OSError as e:
            raise Refused(f"the prompt file {args.prompt_file} could not be read "
                          f"({type(e).__name__})")
        if len(raw) > PROMPT_MAX:
            raise Refused(f"the prompt file is over {PROMPT_MAX:,} characters")
        prompt = clean(raw)
    child = child or new_child_id()
    try:
        target = M.install_draft(args.draft, child, environ={}, now=now, fresh=True)
    except M.InstallRefused as e:
        raise Refused(str(e))
    try:
        with open(target, "rb") as fh:
            raw = fh.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise Refused("the draft is not UTF-8")
        fm = R.front_matter(text)
        if not fm:
            raise Refused("the draft has no frontmatter (see "
                          "references/handoff-format.md)")
        if "mode_skill" in fm:
            raise Refused("the draft sets mode_skill:, and a spin-off has no "
                          "standing mode; remove it")
        body = with_role_holds(text, role_holds(repo, librarian))
        stamps = stamp_fields(where, child, parent, now)
        new = M.restamp(body.encode("utf-8"), stamps)
        if new is None:
            raise Refused("the installed manifest could not be stamped")
        # Read the stamped file back the way the rehydrate hook will: a line
        # restamp's parser and the reader's split differently (a vertical tab
        # inside a value) must not leave the reader a different `session:`,
        # `mode:` or standing mode than the one stamped.
        fm2 = R.front_matter(new.decode("utf-8"))
        if any(fm2.get(k) != str(v) for k, v in stamps.items()) \
                or "mode_skill" in fm2:
            raise Refused("the stamped frontmatter does not read back as "
                          "stamped (a line the reader splits differently)")
        if not M._write_atomic(target, raw, new, 0o600):
            raise Refused("the installed manifest could not be stamped")
    except Refused:
        _remove_install(target)
        raise
    except Exception as e:
        _remove_install(target)
        raise Refused(f"the installed manifest could not be stamped "
                      f"({type(e).__name__})")
    warn = []
    pname = parent_name(parent, environ)
    rec = {"v": RECORD_V, "session_id": child, "name": name, "topic": args.topic,
           "spun_from": parent, "parent_name": pname,
           "librarian": librarian or None,
           "top": R.git(where, "rev-parse", "--show-toplevel") or where,
           "repo": repo,
           "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
           "manifest": target}
    w = write_record(rec, now)
    if w:
        warn.append(w)
    try:
        import ledger
        ledger.append(parent, "P", f"spin-off {name} ({child})", ref=target)
    except Exception:
        pass
    text_open = opener(pname or f"session {parent}", repo, args.topic, target,
                       name, librarian, prompt)
    sandbox = bool(environ.get("CLAUDE_SANDBOX_PROJECT_DIR"))
    show_id = PRINT_SESSION_ID and not args.no_session_id
    line = launch_line(where, child, name, text_open, sandbox, show_id)
    return [f"installed {target}", f"spin-off {child}", line], warn


def main(argv, environ=None, cwd=None, now=None, child=None):
    env = os.environ if environ is None else environ
    args = parser().parse_args(argv[1:])
    try:
        out, warn = run(args, env, cwd or os.getcwd(),
                        time.time() if now is None else now, child)
    except Refused as e:
        print(f"spin_off.py: refused: {e}; nothing written.", file=sys.stderr)
        return 2
    for w in warn:
        print(w, file=sys.stderr)
    for ln in out:
        print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
