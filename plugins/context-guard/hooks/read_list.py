"""The manifest's "Read in full" list, followed through (5039 H6).

Three hooks share this state key, `read_list` = {paths: [{path, real}],
read: [real, ...], at}; the record exists only while a reminder is pending:

  rehydrate.py  on a full injection of a manifest this session owns, records
                the list (paths_from_manifest) - replacing any earlier record,
                so each injection gets its own reminder.
  lineage.py    PostToolUse(Read): a whole-file Read (no offset, no limit) of
                a listed path, matched by realpath, marks it read (mark_read).
                Not inside a subagent. A partial Read, `cat` or `grep` does
                not count: the list asks for the whole file.
  context_warn  the next UserPromptSubmit that is not /checkpoint, /compact or
                /clear and is not hard-stopped takes the record (take) and,
                when any path is unread, adds ONE line to that prompt's
                context (reminder). The record is dropped either way: once
                per injection, never a block, never a turn of its own.

Paths come from repo text, so only existing regular files are kept, echoed
as absolute paths with no control characters, at most MAX_PATHS of them.
Every writer goes through L.update_state. Never raises.
"""
import os, re, time

KEY = "read_list"
MAX_PATHS = 10
MAX_LEN = 300
_SECTION = re.compile(r"^##[ \t]+Read in full[ \t]*$", re.M | re.I)
_BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_TICKED = re.compile(r"`([^`\n]+)`")
_SUFFIX = re.compile(r"(?::\d+(?:-\d+)?|#L\d+(?:-L?\d+)?)$")


def section_lines(text):
    """The non-blank lines of the manifest body's `## Read in full` section."""
    if not isinstance(text, str):
        return []
    m = _SECTION.search(text)
    if not m:
        return []
    j = text.find("\n## ", m.end())
    body = text[m.end():j if j >= 0 else len(text)]
    return [ln for ln in body.splitlines() if ln.strip()]


def _candidate(line):
    s = _BULLET.sub("", line, count=1).strip()
    t = _TICKED.match(s)
    tok = t.group(1).strip() if t else (s.split() or [""])[0]
    return _SUFFIX.sub("", tok.rstrip(",;:.")) if tok else ""


def paths_from_manifest(text, top, cwd=None):
    """[{path, real}]: each Read-in-full line's path (the first backticked
    span, else the first word, a `:12` or `#L12` suffix dropped), resolved
    against the repo top, then cwd; only existing regular files, deduplicated
    by realpath."""
    out, seen = [], set()
    try:
        for ln in section_lines(text):
            c = _candidate(ln)
            if not c or len(c) > MAX_LEN or any(ord(ch) < 32 or ord(ch) == 127 for ch in c):
                continue
            c = os.path.expanduser(c)
            bases = [""] if os.path.isabs(c) else [b for b in (top, cwd) if b]
            for b in bases:
                p = os.path.abspath(os.path.join(b, c))
                if os.path.isfile(p):
                    real = os.path.realpath(p)
                    if real not in seen:
                        seen.add(real)
                        out.append({"path": p, "real": real})
                    break
            if len(out) >= MAX_PATHS:
                break
    except Exception:
        return []
    return out


def record(st, paths, now=None):
    """Set (or, with no paths, drop) this injection's record in state `st`."""
    if paths:
        st[KEY] = {"paths": paths, "read": [],
                   "at": time.time() if now is None else now}
    else:
        st.pop(KEY, None)


def unread(rec):
    """The display paths of `rec` not yet read, in manifest order."""
    if not isinstance(rec, dict) or not isinstance(rec.get("paths"), list):
        return []
    done = set(x for x in rec.get("read") or [] if isinstance(x, str))
    return [p["path"] for p in rec["paths"]
            if isinstance(p, dict) and isinstance(p.get("path"), str)
            and p.get("real") not in done]


def mark_read(L, inp):
    """PostToolUse(Read): mark a whole-file Read of a listed path. Cheap when
    nothing is pending: one state-file read, no lock."""
    if inp.get("agent_id") or inp.get("tool_name") not in (None, "Read"):
        return
    ti = inp.get("tool_input")
    if not isinstance(ti, dict):
        return
    fp = ti.get("file_path")
    if not isinstance(fp, str) or not fp:
        return
    if ti.get("offset") is not None or ti.get("limit") is not None:
        return
    sid = inp.get("session_id")
    if not isinstance(sid, str) or not sid:
        return
    if not unread(L.load_state(sid).get(KEY)):
        return
    cwd = inp.get("cwd") or os.getcwd()
    real = os.path.realpath(fp if os.path.isabs(fp) else os.path.join(cwd, fp))

    def apply(st):
        rec = st.get(KEY)
        if not isinstance(rec, dict) or not isinstance(rec.get("paths"), list):
            return
        if real not in [p.get("real") for p in rec["paths"] if isinstance(p, dict)]:
            return
        read = [x for x in rec.get("read") or [] if isinstance(x, str)]
        if real not in read:
            rec["read"] = read + [real]
        if not unread(rec):
            st.pop(KEY, None)          # all read: nothing left to remind

    L.update_state(sid, apply)


def take(st):
    """Pop the pending record from `st` (under the caller's lock) and return
    its unread paths: the reminder fires at most once per injection."""
    rec = st.pop(KEY, None)
    return unread(rec)


def reminder(paths):
    return ("[context-guard rehydration] Read in full, not yet read this "
            "session: " + ", ".join(paths) + ". The manifest lists these to "
            "be read before anything else - with the Read tool, the whole "
            "file (a partial Read, cat or grep does not count).")
