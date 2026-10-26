#!/usr/bin/env python3
"""wi — work-item CLI over one-markdown-file-per-item in a git repo.

Constraints this file lives under:

- stdlib only. Front matter is a strict YAML *subset* (scalars, one-line flow
  lists, block lists of scalars, one level of map for x_backlog) parsed here;
  the one command that needs a real YAML parser (`import --format
  backlog-yaml`) tries ruamel.yaml then yaml and exits 3 without them.
- `status:` is the only authority on state; files never move on done.
  `archive` moves closed items to archive/YYYY/ only when invoked.
- Mutations take flock(<root>/.lock) and write tmp+rename, so same-machine
  claims are atomic; cross-machine atomicity is git's job.
- A decision's card record is one immutable JSON file under cards/, written
  once by `raise --record` before the indented `card:` line that names it;
  nothing rewrites or moves it (format.md § Card records).
- Exit codes: 0 ok, 1 usage/validation, 2 not found/empty, 3 file/parser
  error, 4 lock or claim conflict.
"""
import argparse
import base64
import contextlib
import errno
import fcntl
import fnmatch
import getpass
import glob
import hashlib
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import typing
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

FIELD_ORDER = ["id", "title", "short_display_name", "type", "status", "stage",
               "priority", "tags",
               "deps", "parent", "owner", "claimed", "blocked", "parked",
               "grooming", "feedback",
               "mode", "complexity", "alias", "created", "updated", "closed",
               "refs", "x_backlog"]
FLOW_LIST_FIELDS = {"tags"}
BLOCK_LIST_FIELDS = {"deps", "refs"}
LIST_FIELDS = FLOW_LIST_FIELDS | BLOCK_LIST_FIELDS
MAP_FIELDS = {"x_backlog"}
INT_FIELDS = {"priority"}
TYPES = {"task", "bug", "feature", "refactor", "workflow", "chore", "epic", "spike"}
STATUSES = {"todo", "doing", "blocked", "parked", "grooming", "done", "dropped"}
STAGES = {"implement", "review", "testing", "uat", "uat_feedback"}
MODES = {"autonomous", "interactive", "mixed"}
COMPLEXITIES = {"low", "medium", "high"}
# short_display_name: the optional name agents give an item to the operator
# (format.md § Short display name and tag); wi checks its shape only
SHORT_NAME_MAX = 40
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}-[0-9a-f]{4}$")
ALIAS_RE = re.compile(r"^[SBRWM]-\d{1,3}$")
HANDOFF_KEYS = ("doing", "next", "blocked", "learned")
TYPE_PREFIX = {"feature": "S", "task": "S", "bug": "B", "refactor": "R",
               "spike": "R", "workflow": "W", "chore": "M"}
PRIO_TO_BACKLOG = {0: 90, 1: 70, 2: 50, 3: 30, 4: 10}
STATE_TO_BACKLOG = {("todo", None): "todo", ("doing", None): "in_progress",
                    ("doing", "implement"): "in_progress",
                    ("doing", "review"): "review", ("doing", "testing"): "testing",
                    ("doing", "uat"): "uat", ("doing", "uat_feedback"): "uat_feedback",
                    ("blocked", None): "blocked", ("parked", None): "blocked",
                    ("grooming", None): "blocked",
                    ("done", None): "done", ("dropped", None): "closed"}
BACKLOG_TO_STATE = {"todo": ("todo", None), "in_progress": ("doing", "implement"),
                    "review": ("doing", "review"), "testing": ("doing", "testing"),
                    "uat": ("doing", "uat"), "uat_feedback": ("doing", "uat_feedback"),
                    "blocked": ("blocked", None), "done": ("done", None),
                    "closed": ("dropped", None)}
# backlog.yaml has no deferred state: a parked item exports as `blocked` with
# its reason prefixed `PARKED: `, and a blocked story whose reason starts
# with PARKED imports as parked (the same rule `wi migrate-parked` applies).
# An optional parenthesised group right after PARKED ("PARKED (operator
# 2026-09-19): ...") is provenance, not reason: it is stripped from the reason;
# migrate-parked keeps the original text in the Notes line it writes.
PARKED_PREFIX_RE = re.compile(r"^\s*PARKED\b\s*(\([^)\n]*\))?[\s:;,.\u2014-]*")


def parked_reason(blocked):
    """The parked reason carried by a blocked reason that starts with PARKED,
    else None; a bare `PARKED` keeps the whole text as its reason."""
    if not blocked:
        return None
    m = PARKED_PREFIX_RE.match(blocked)
    if not m:
        return None
    return blocked[m.end():].strip() or blocked.strip()


# A grooming item has no backlog.yaml state either: it exports as `blocked`
# with its questions prefixed `GROOMING: `, and imports back by that prefix.
GROOMING_PREFIX_RE = re.compile(r"^\s*GROOMING\b[\s:;,.\u2014-]*")


def grooming_questions(blocked):
    """The grooming questions carried by a blocked reason that starts with
    GROOMING, else None; a bare `GROOMING` keeps the whole text."""
    if not blocked:
        return None
    m = GROOMING_PREFIX_RE.match(blocked)
    if not m:
        return None
    return blocked[m.end():].strip() or blocked.strip()


# The lenient readings above eat any punctuation after the prefix, so a park
# or grooming whose own text starts with it ("-", "— reason", "- [ ] x")
# would drift on the first export -> import. Export writes such a text
# quoted — `PARKED: "- x"` — and import unwraps the quotes only where export
# itself would have written them: when the inner text's plain form would not
# read back as that text. Anything else (`PARKED: "x"`, `PARKED: ""`,
# `PARKED: "a" and "b"`) gets the lenient reading, as before. migrate-parked
# reads hand-written text, so it keeps the lenient reading alone.
def _bridge_decode(tag, lenient, blocked):
    """Import's reading of a `PARKED`/`GROOMING` blocked reason: export's
    quoted form unwrapped, else `lenient` (parked_reason/grooming_questions)."""
    head = tag + ': "'
    if (blocked and blocked.startswith(head) and blocked.endswith('"')
            and len(blocked) > len(head) + 1):
        inner = blocked[len(head):-1]
        if _bridge_decode(tag, lenient, f"{tag}: {inner}") != inner:
            return inner
    return lenient(blocked)


def _bridge_encode(tag, lenient, text):
    """Export's `PARKED: <text>` (or GROOMING), quoted exactly when import's
    reading of the plain form would not give `text` back."""
    plain = f"{tag}: {text}"
    if not text or _bridge_decode(tag, lenient, plain) == text:
        return plain
    return f'{tag}: "{text}"'


# The librarian-mode Report convention: an operator question is a body line
# `decision N: <text>`, its reply a body line `answer N: <reply>`.
DECISION_RE = re.compile(r"^decision (\d+):\s*(.*)$")
ANSWER_RE = re.compile(r"^answer (\d+):")


def unanswered_decisions(item):
    """[(N, text)] for each `decision N:` body line with no `answer N:` line
    anywhere in the same body, in order of each N's first line, one per N.
    A repeated N is a revised question: its text is the last line's. Lines
    inside a fenced code block are text, not markers."""
    lines = item.body.replace("\r\n", "\n").split("\n")
    fenced = set()
    for i, j in _fence_spans(lines):
        fenced.update(range(i, j + 1))
    asked, answered = {}, set()
    for i, line in enumerate(lines):
        if i in fenced:
            continue
        m = DECISION_RE.match(line)
        if m:
            asked[int(m.group(1))] = m.group(2).strip()
            continue
        m = ANSWER_RE.match(line)
        if m:
            answered.add(int(m.group(1)))
    return [(n, text) for n, text in asked.items() if n not in answered]


# A stored decision card (librarian-mode's references/decisions.md) indents
# its fields under the `decision N:` headline; `raised:` is when it was asked.
RAISED_RE = re.compile(r"^[ \t]+raised:\s*(\S+)")


def decision_raised(item):
    """{N: raised} from the indented `raised:` line of each `decision N:`
    card, the first one per N (a revision keeps the original ask time).
    Same fence rule as unanswered_decisions; a card ends at the first line
    that is not indented."""
    lines = item.body.replace("\r\n", "\n").split("\n")
    fenced = set()
    for i, j in _fence_spans(lines):
        fenced.update(range(i, j + 1))
    raised, current = {}, None
    for i, line in enumerate(lines):
        if i in fenced:
            current = None
            continue
        m = DECISION_RE.match(line)
        if m:
            current = int(m.group(1))
            continue
        if current is None:
            continue
        if not line[:1].isspace():
            current = None
            continue
        m = RAISED_RE.match(line)
        if m:
            raised.setdefault(current, m.group(1))
    return raised


# A decision's card record (format.md § Card records): one immutable JSON
# file per revision under cards/, named by an indented `card:` line under
# its `decision N:` headline. Indented, the line matches neither marker,
# and decision_raised reads past it. Applied with fullmatch only.
CARD_RE = re.compile(
    r"[ \t]+card: (cards/[a-z0-9][a-z0-9-]*/[0-9]+/[0-9]{4}-[0-9]{2}-[0-9]{2}"
    r"T[0-9]{2}-[0-9]{2}-[0-9]{2}Z\.card[1-9][0-9]{0,3}\.json) rev ([0-9]{4}-"
    r"[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z) · (decision-card/"
    r"[1-9][0-9]{0,3})(?: — .*)?")


def _card_scan(item):
    """[(N, line index, (path, rev, format))] for every `card:` line in
    the block of a `decision N:` headline, in file order. Same fence and
    block rules as decision_raised: a block ends at the first line that is
    not indented; a fenced line is text."""
    lines = item.body.replace("\r\n", "\n").split("\n")
    fenced = set()
    for i, j in _fence_spans(lines):
        fenced.update(range(i, j + 1))
    out, current = [], None
    for i, line in enumerate(lines):
        if i in fenced:
            current = None
            continue
        m = DECISION_RE.match(line)
        if m:
            current = int(m.group(1))
            continue
        if current is None:
            continue
        if not line[:1].isspace():
            current = None
            continue
        m = CARD_RE.fullmatch(line)
        if m:
            out.append((current, i, m.groups()))
    return out


def card_lines(item):
    """{N: [(path, rev, format)]} from the item's `card:` lines, in file
    order; the last one per N names the current record."""
    out = {}
    for n, _, groups in _card_scan(item):
        out.setdefault(n, []).append(groups)
    return out


# A showing of decision N and the operator's turn that saw it (the format
# reference's § Shown and seen): column-0 lines appended by the session that
# displays the decision. Only a line whose first token is a UTC time reads.
_UTC = r"(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z)\b"
SHOWN_RE = re.compile(r"^shown (\d+):\s*" + _UTC)
SEEN_RE = re.compile(r"^seen (\d+):\s*" + _UTC)


def decision_showings(item):
    """{N: {"first_shown", "last_shown", "last_seen", "unseen"}} from the
    `shown N:` and `seen N:` lines, times kept as written. First and last
    are by position; `unseen` is None with no `shown N:` line, True when no
    `seen N:` line follows the last `shown N:` line in file order (never by
    comparing times), else False. Same fence rule as unanswered_decisions."""
    lines = item.body.replace("\r\n", "\n").split("\n")
    fenced = set()
    for i, j in _fence_spans(lines):
        fenced.update(range(i, j + 1))
    out = {}
    for i, line in enumerate(lines):
        if i in fenced:
            continue
        m = SHOWN_RE.match(line)
        if m:
            rec = out.setdefault(int(m.group(1)), _no_showing())
            if rec["first_shown"] is None:
                rec["first_shown"] = m.group(2)
            rec["last_shown"] = m.group(2)
            rec["unseen"] = True
            continue
        m = SEEN_RE.match(line)
        if m:
            rec = out.setdefault(int(m.group(1)), _no_showing())
            rec["last_seen"] = m.group(2)
            if rec["unseen"] is not None:
                rec["unseen"] = False
    return out


def _no_showing():
    return {"first_shown": None, "last_shown": None, "last_seen": None,
            "unseen": None}


class WiError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


class AmbiguousId(WiError):
    """A prefix matching more than one item: never read as "no match"."""


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now_minute():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def tokens(text):
    return (len(text) + 3) // 4


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:40].rstrip("-") or "item"


ID_TRIES = 1024


def _id_suffix(title, created):
    """One random 4-hex id suffix; make_id redraws it on a repeat."""
    return hashlib.sha1((title + created).encode() + os.urandom(8)).hexdigest()[:4]


def make_id(title, created, taken, slug=None):
    """A new `<slug>-<4hex>` id that is not in `taken` — every id and file
    stem already in the store plus every id handed out earlier in the same
    batch (see taken_ids). The id is added to `taken` before it is returned,
    so a batch caller cannot be handed it twice. A 4-hex suffix can repeat,
    so a repeat is retried; when ID_TRIES draws all land on taken ids the
    call fails loudly rather than widening the id format (ID_RE)."""
    base = slugify(slug) if slug else slugify(title)
    for _ in range(ID_TRIES):
        iid = f"{base}-{_id_suffix(title, created)}"
        if iid not in taken:
            taken.add(iid)
            return iid
    raise WiError(3, f"no free id for '{base}-XXXX' after {ID_TRIES} tries; "
                     "nothing written")


def parse_duration(text):
    m = re.match(r"^(\d+)([smhd])$", text)
    if not m:
        raise WiError(1, f"bad duration: {text}")
    return int(m.group(1)) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(2)]


def age_str(claimed):
    try:
        dt = datetime.strptime(claimed, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return "?"
    secs = (datetime.now(timezone.utc) - dt).total_seconds()
    for unit, div in (("d", 86400), ("h", 3600), ("m", 60)):
        if secs >= div:
            return f"{int(secs // div)}{unit}"
    return f"{int(secs)}s"


# ── Front matter (strict subset) ────────────────────────────────────────────

# Scalars are emitted bare when that reads back unchanged, else as a YAML
# double-quoted scalar. The escapes below are the whole contract, and
# _dq_decode is the exact inverse of _dq_escape: parse(emit(v)) == v for
# every one-line string, so a rewrite never changes a value's bytes.
_DQ_SIMPLE = {"\\": "\\", '"': '"', "/": "/", "t": "\t", "0": "\0",
              "a": "\a", "b": "\b", "e": "\x1b", "v": "\v", "f": "\f",
              " ": " ", "_": "\xa0", "N": "\x85", "L": "\u2028",
              "P": "\u2029"}
_DQ_HEX = {"x": 2, "u": 4, "U": 8}
# Tab, C0/C1 controls, DEL, the characters YAML or str.splitlines treat as
# line or byte-order marks, U+FFFE/U+FFFF and lone surrogates (which a YAML
# reader rejects raw) are written as escapes, never raw — and never bare
_DQ_ESCAPE_RE = re.compile("[\x00-\x08\x09\x0b-\x1f\x7f-\x9f\u2028\u2029"
                           "\ufeff\ufffe\uffff\ud800-\udfff]")
# what `wi lint` flags in a decoded value: any control character, tab
# included (wi never writes one raw), most often a hand-written backslash
# path ("C:\\temp" holds a tab, "C:\\bin" a \b)
_CONTROL_RE = re.compile("[\x00-\x08\x09\x0b-\x1f\x7f-\x9f]")
# what the front-matter writer refuses (and lint flags, and import folds to
# a space): a control character, or U+2028/U+2029, which a YAML 1.1 loader
# and str.splitlines read as a line break
_FRONT_REFUSE_RE = re.compile("[\x00-\x08\x09\x0b-\x1f\x7f-\x9f"
                              "\u2028\u2029]")


def _dq_escape_char(m):
    c = ord(m.group())
    if c == 0x09:
        return "\\t"
    return f"\\x{c:02x}" if c < 0x100 else f"\\u{c:04x}"


def _dq_escape(v):
    v = v.replace("\\", "\\\\").replace('"', '\\"')
    return _DQ_ESCAPE_RE.sub(_dq_escape_char, v)


def _dq_decode(v):
    """Decode a whole double-quoted scalar `"..."`; None when `v` is not
    exactly one well-formed one (legacy input is then read leniently). An
    unknown escape, or one that would decode to a line break, is kept as
    written: a hand-edited file loads, and stays one line."""
    out, i, n = [], 1, len(v)
    while i < n:
        c = v[i]
        if c == '"':
            return "".join(out) if i == n - 1 else None
        if c != "\\" or i + 1 >= n:
            out.append(c)
            i += 1
            continue
        e = v[i + 1]
        if e in _DQ_SIMPLE:
            out.append(_DQ_SIMPLE[e])
            i += 2
            continue
        width = _DQ_HEX.get(e)
        digits = v[i + 2:i + 2 + width] if width else ""
        if (width and len(digits) == width
                and re.fullmatch(r"[0-9A-Fa-f]+", digits)):
            ch = int(digits, 16)
            if ch <= 0x10FFFF and chr(ch) not in "\n\r":
                out.append(chr(ch))
                i += 2 + width
                continue
        out.append(c)  # unknown or unsafe escape: keep the backslash
        i += 1
    return None


def _parse_scalar(text):
    """(value, quoted) for one scalar token."""
    v = text.strip()
    if len(v) >= 2 and v[0] == v[-1] == '"':
        dec = _dq_decode(v)
        return (v[1:-1] if dec is None else dec), True
    if len(v) >= 2 and v[0] == v[-1] == "'":
        inner = v[1:-1]
        if re.fullmatch(r"(?:[^']|'')*", inner):
            inner = inner.replace("''", "'")
        return inner, True
    return v, False


def _unquote(v):
    return _parse_scalar(v)[0]


def _split_flow(inner):
    """Split a flow list's inside on the commas outside quoted scalars."""
    parts, cur, quote, i = [], [], None, 0
    while i < len(inner):
        c = inner[i]
        cur.append(c)
        if quote == '"' and c == "\\" and i + 1 < len(inner):
            cur.append(inner[i + 1])
            i += 1
        elif quote and c == quote:
            quote = None
        elif not quote and c in "\"'" and not "".join(cur[:-1]).strip():
            quote = c
        elif not quote and c == ",":
            cur.pop()
            parts.append("".join(cur))
            cur = []
        i += 1
    if quote:  # an unterminated quote: read it the old way, comma by comma
        return [x for x in inner.split(",") if x.strip()]
    parts.append("".join(cur))
    return [x for x in parts if x.strip()]


def _looks_amplified(v):
    """True when every backslash in `v` is half of a `\\\\` or `\\"` pair —
    the trace an older wi left: its reader never unescaped, so each rewrite of
    a quoted value doubled its backslashes and escaped its quotes again."""
    return "\\" in v and re.fullmatch(r'(?:[^\\]|\\[\\"])*', v) is not None


def _deamplify(v):
    while _looks_amplified(v):
        v = re.sub(r'\\([\\"])', r"\1", v)
    return v


def parse_front(lines):
    """Return (meta, extra_keys, errors). Scalars stay strings; a bare `—` or
    an empty value → None."""
    meta, extra, errors = {}, [], []

    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):(.*)$", line)
        if not m:
            errors.append(f"unparseable front-matter line: {line!r}")
            continue
        key, rest = m.group(1), m.group(2).strip()
        if rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            val = [_parse_scalar(x)[0] for x in _split_flow(inner)] \
                if inner else []
        elif rest:
            val, quoted = _parse_scalar(rest)
            if val == "" or (val == "—" and not quoted):
                val = None
        else:
            block, submap = [], {}
            while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                if not lines[i].startswith("  ") or lines[i].startswith("    "):
                    errors.append(f"nested structure under {key}: {lines[i]!r}")
                sub = lines[i].strip()
                i += 1
                if sub.startswith("- "):
                    item, quoted = _parse_scalar(sub[2:])
                    if item.endswith(":") and not quoted:
                        errors.append(f"nested structure under {key}: {sub!r}")
                    block.append(item)
                elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", sub):
                    sk, sv = sub.split(":", 1)
                    submap[sk.strip()] = _unquote(sv)
                else:
                    errors.append(f"unparseable block line under {key}: {sub!r}")
            if block and submap:
                errors.append(f"mixed list and map under {key}")
            val = submap if (submap and not block) else block
        if key in INT_FIELDS and val is not None:
            try:
                val = int(val)
            except (ValueError, TypeError):
                errors.append(f"{key} must be an integer, got {val!r}")
                val = None
        if key in LIST_FIELDS and isinstance(val, str):
            val = [val]
        if key not in FIELD_ORDER:
            extra.append(key)
        meta[key] = val
    return meta, extra, errors


_BARE_UNSAFE_START = tuple("-?:,[]{}#&*!|>'\"%@`")


def _emit_scalar(v, flow=False):
    """Bare when wi reads a bare scalar back unchanged and a YAML loader
    parses it, else double-quoted with _dq_escape: mapping or comment
    indicators, structure chars, surrounding whitespace, a leading YAML
    indicator, the `—` that reads as empty, a lone `=` or `<<` (YAML's
    value and merge keys), a tab or other control character, or (in a flow
    list) a comma. YAML's implicit typing (numbers, booleans, null, dates)
    is left alone: `priority: 2` and `created: 2026-09-21` stay bare, so a
    YAML loader may type a bare value that wi reads as a string."""
    v = str(v)
    if (v in ("", "—", "=", "<<") or v != v.strip() or v.endswith(":")
            or re.search(r":[ \t]|[ \t]#|[\[\]{}]", v)
            or v.startswith(_BARE_UNSAFE_START) or _DQ_ESCAPE_RE.search(v)
            or (flow and "," in v)):
        return '"' + _dq_escape(v) + '"'
    return v


def _front_one_line(key, val, plain=True):
    """Every front-matter value is one line: a line break would forge keys
    (`status: done`) or leave a file no later command can parse. A tab or
    other control character (or U+2028/U+2029) is refused too, so nothing
    wi writes is what `wi lint` reports (there, most often a hand-written
    backslash path).
    This is the backstop behind the per-command checks; render() runs before
    any write, so a rejected value writes nothing. `plain=False` (display
    only: `show`) lets a hand-written control character through."""
    vals = val.values() if isinstance(val, dict) else \
        val if isinstance(val, list) else [val]
    for v in vals:
        if isinstance(v, str) and ("\n" in v or "\r" in v):
            raise WiError(1, f"front-matter '{key}' must be one line; "
                             "it contains a line break")
        if plain and isinstance(v, str) and _FRONT_REFUSE_RE.search(v):
            c = ord(_FRONT_REFUSE_RE.search(v).group())
            raise WiError(1, f"front-matter '{key}' holds a control character "
                             f"(U+{c:04X}{', a tab' if c == 9 else ''}"
                             f"{', a line separator' if c > 0xff else ''}); "
                             "front-matter values are plain text")


def emit_front(meta, extra=(), plain=True):
    out = []
    for key in list(FIELD_ORDER) + [k for k in extra if k not in FIELD_ORDER]:
        if key not in meta:
            continue
        val = meta[key]
        if val is None or val == [] or val == {}:
            continue
        _front_one_line(key, val, plain)
        if isinstance(val, dict):
            out.append(f"{key}:")
            out.extend(f"  {k}: {_emit_scalar(v)}" for k, v in val.items())
        elif isinstance(val, list):
            if key in FLOW_LIST_FIELDS:
                out.append(f"{key}: [" + ", ".join(_emit_scalar(v, flow=True)
                                                   for v in val) + "]")
            else:
                out.append(f"{key}:")
                out.extend(f"  - {_emit_scalar(v)}" for v in val)
        else:
            out.append(f"{key}: {_emit_scalar(val)}")
    return "\n".join(out)


# ── Body sections ───────────────────────────────────────────────────────────

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def _fence_open(content):
    """The opening run (``` / ~~~ ...) when `content` opens a fence, else None.
    A backtick run with a backtick later on the line is inline code."""
    m = FENCE_RE.match(content)
    if m and not (m.group(1)[0] == "`" and "`" in content[m.end():]):
        return m.group(1)
    return None


def _fence_closes(content, run):
    """True when `content` closes a fence opened by `run`: a run of the same
    character at least as long, with nothing but whitespace after it."""
    m = FENCE_RE.match(content)
    return bool(m and m.group(1)[0] == run[0] and len(m.group(1)) >= len(run)
                and not content[m.end():].strip())


def _fence_spans(lines):
    """(opener index, closer index) of every fenced code block (``` or ~~~).
    An opener with no matching closer is not a fence — it must not hide
    every later heading (a real `## Handoff` after a pasted, unclosed block
    stays the section)."""
    contents = [line.rstrip("\r\n") for line in lines]
    spans, i, n = [], 0, len(contents)
    # per fence char, the shortest run already known to have no closer
    # anywhere after an earlier opener: a later opener at least that long
    # has none either, so each such lookahead is skipped (linear, not n²)
    no_closer = {}
    while i < n:
        run = _fence_open(contents[i])
        if run and len(run) < no_closer.get(run[0], len(run) + 1):
            j = i + 1
            while j < n and not _fence_closes(contents[j], run):
                j += 1
            if j < n:
                spans.append((i, j))  # opener..closer inclusive are code
                i = j + 1
                continue
            no_closer[run[0]] = len(run)
        i += 1
    return spans


def _heading_flags(lines):
    """For each line, True when it is a `## ` section heading: it starts with
    `## ` and is not inside a fenced code block (see _fence_spans)."""
    flags = [line.startswith("## ") for line in lines]
    for i, j in _fence_spans(lines):
        flags[i:j + 1] = [False] * (j + 1 - i)
    return flags


def parse_body(text):
    """Split into (description, [(name, text), ...]); section text is stripped.
    A `## ` line inside a fenced code block is text, not a heading."""
    desc, sections, name, buf = None, [], None, []
    lines = text.split("\n")
    for line, heading in zip(lines, _heading_flags(lines)):
        if heading:
            if name is None:
                desc = "\n".join(buf).strip()
            else:
                sections.append((name, "\n".join(buf).strip()))
            name, buf = line[3:].strip(), []
        else:
            buf.append(line)
    if name is None:
        desc = "\n".join(buf).strip()
    else:
        sections.append((name, "\n".join(buf).strip()))
    return desc or "", sections


def emit_body(desc, sections):
    parts = [desc] if desc else []
    for name, text in sections:
        parts.append(f"## {name}\n{text}" if text else f"## {name}")
    return "\n\n".join(parts)


HANDOFF_LINE_RE = re.compile(r"^- (doing|next|blocked|learned):\s*(.*)$")


def parse_handoff(text):
    """First `- key:` line of each key wins — the same line set_handoff rewrites."""
    h, seen = {k: "" for k in HANDOFF_KEYS}, set()
    for line in text.split("\n"):
        m = HANDOFF_LINE_RE.match(line)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            v = m.group(2).strip()
            h[m.group(1)] = "" if v == "—" else v
    return h


def _handoff_line(h, key):
    return f"- {key}: {h.get(key) or '—'}"


def emit_handoff(h):
    return "\n".join(_handoff_line(h, k) for k in HANDOFF_KEYS)


# The raw body is the custody record: rewrites edit it in place, line by line,
# so every byte outside the lines a command owns (the four Handoff bullets,
# one appended Notes line, a section appended at the end) survives untouched —
# unheaded trailing text, spacing between sections, section order, CRLF.

def _raw_lines(text):
    """Lines with their endings kept; ''.join() gives `text` back exactly."""
    return re.findall(r"[^\n]*\n|[^\n]+\Z", text)


def _content(line):
    return line.rstrip("\r\n")


def _fence_hides_section(lines, name):
    """True when a fence looks like it swallowed the real `## name` section:
    a column-0 `## name` line inside it is followed, in the same fence, by
    another column-0 `## ` line. That is the sign of an unclosed opener
    pairing with a later block's fence across sections; appending a second
    section then would split the record, so the caller refuses. A closed
    example holding only `## name` (and no later heading) is left alone and
    a real section is appended as usual."""
    for i, j in _fence_spans(lines):
        hits = [k for k in range(i + 1, j) if lines[k].startswith("## ")]
        for pos, k in enumerate(hits):
            if _content(lines[k])[3:].strip() == name and pos + 1 < len(hits):
                return True
    return False


def _section_span(lines, name):
    """(heading index, end index) of the first `## name` section; the section
    runs to the next `## ` heading or the end of the body. Headings inside
    fenced code blocks do not count (see _heading_flags)."""
    start = None
    for i, (line, heading) in enumerate(zip(lines, _heading_flags(lines))):
        if heading:
            if start is not None:
                return start, i
            if _content(line)[3:].strip() == name:
                start = i
    return None if start is None else (start, len(lines))


# ── Item model ──────────────────────────────────────────────────────────────

class Item:
    def __init__(self, meta, extra, desc, sections, path=None, body=None, eol="\n"):
        """New items pass desc/sections; parsed items pass the raw `body`
        (everything after the closing `---` line), which is kept verbatim."""
        self.meta, self.extra, self.path, self.eol = meta, extra, path, eol
        if body is None:
            body = "\n" + emit_body(desc, sections) + "\n"
            body = body.replace("\n", eol)
        self.body = body
        self._parsed = None

    @classmethod
    def parse(cls, text, path=None):
        if text.startswith("---\r\n"):
            eol = "\r\n"
        elif text.startswith("---\n"):
            eol = "\n"
        else:
            raise WiError(3, f"{path}: missing front matter")
        start = i = len("---" + eol)
        while True:
            j = text.find("\n", i)
            if j == -1:
                raise WiError(3, f"{path}: unterminated front matter")
            if text[i:j].rstrip("\r") == "---":
                front, body = text[start:i], text[j + 1:]
                break
            i = j + 1
        front = front.replace("\r\n", "\n")
        meta, extra, errors = parse_front(front.rstrip("\n").split("\n"))
        if errors:
            raise WiError(3, f"{path}: " + "; ".join(errors))
        return cls(meta, extra, None, None, path, body=body, eol=eol)

    def render(self, plain=True):
        eol = self.eol
        front = emit_front(self.meta, self.extra, plain).replace("\n", eol)
        return "---" + eol + front + eol + "---" + eol + self.body

    def _parse(self):
        if self._parsed is None or self._parsed[0] is not self.body:
            self._parsed = (self.body, parse_body(self.body.replace("\r\n", "\n")))
        return self._parsed[1]

    @property
    def desc(self):
        return self._parse()[0]

    @property
    def sections(self):
        return list(self._parse()[1])

    def section(self, name):
        for n, text in self.sections:
            if n == name:
                return text
        return None

    def _append_section(self, name, text):
        """Add `## name` at the end of the body; existing bytes are a prefix
        of the result (at most a line ending and a blank line are added).
        The heading always starts a line, even after a whitespace-only body."""
        eol, body = self.eol, self.body
        if body and not body.endswith("\n"):
            body += eol
        if body.strip() and not re.search(r"\n\r?\n\Z", body):
            body += eol
        self.body = body + f"## {name}" + eol + text.replace("\n", eol) + eol

    def _refuse_fenced(self, lines, name):
        if _fence_hides_section(lines, name):
            raise WiError(3, f"{self.path or self.id}: '## {name}' is inside a "
                             "fenced code block that runs across sections; add "
                             f"a real '## {name}' heading outside the fence, or "
                             "close an unclosed ``` or ~~~ above it, then retry")

    def set_handoff(self, h):
        """Rewrite only the four `- key:` bullets of `## Handoff` (the first
        of each key); a missing bullet is inserted after its predecessor.
        Nothing else in the section, or after it, is touched."""
        lines = _raw_lines(self.body)
        span = _section_span(lines, "Handoff")
        if span is None:
            self._refuse_fenced(lines, "Handoff")
            self._append_section("Handoff", emit_handoff(h))
            return
        start, end = span
        found = {}
        for i in range(start + 1, end):
            m = HANDOFF_LINE_RE.match(_content(lines[i]))
            if m and m.group(1) not in found:
                found[m.group(1)] = i
        anchor = start
        for key in HANDOFF_KEYS:
            if key in found:
                i = found[key]
                lines[i] = _handoff_line(h, key) + lines[i][len(_content(lines[i])):]
                anchor = i
                continue
            if not lines[anchor].endswith("\n"):
                lines[anchor] += self.eol
            anchor += 1
            lines.insert(anchor, _handoff_line(h, key) + self.eol)
            found = {k: (v + 1 if v >= anchor else v) for k, v in found.items()}
        self.body = "".join(lines)

    def handoff(self):
        return parse_handoff(self.section("Handoff") or "")

    def append_note(self, line):
        """Insert `line` after the last non-blank line of `## Notes` (or add
        the section at the end); every existing byte stays in place."""
        lines = _raw_lines(self.body)
        span = _section_span(lines, "Notes")
        if span is None:
            self._refuse_fenced(lines, "Notes")
            self._append_section("Notes", line)
            return
        start, end = span
        last = start
        for i in range(start + 1, end):
            if lines[i].strip():
                last = i
        if not lines[last].endswith("\n"):
            lines[last] += self.eol
        lines.insert(last + 1, line + self.eol)
        self.body = "".join(lines)

    def summary(self):
        return self.desc.split("\n\n")[0].replace("\n", " ").strip()

    @property
    def id(self):
        return self.meta.get("id", "")

    def get(self, key, default=None):
        v = self.meta.get(key, default)
        return default if v is None else v

    def touch(self):
        self.meta["updated"] = today()

    def validate(self):
        errs = []
        m = self.meta
        for req in ("id", "title", "status", "created", "updated"):
            if not m.get(req):
                errs.append(f"missing required field '{req}'")
        if m.get("id") and not ID_RE.match(m["id"]):
            errs.append(f"invalid id '{m['id']}'")
        for field, valid in (("type", TYPES), ("status", STATUSES), ("stage", STAGES),
                             ("mode", MODES), ("complexity", COMPLEXITIES)):
            if m.get(field) is not None and m[field] not in valid:
                errs.append(f"invalid {field} '{m[field]}'")
        if m.get("priority") is not None and not 0 <= m["priority"] <= 4:
            errs.append(f"priority out of range: {m['priority']}")
        if m.get("alias") and not ALIAS_RE.match(m["alias"]):
            errs.append(f"invalid alias '{m['alias']}'")
        # add and set strip the value and check its length first (exit 1),
        # so this catches a hand-written one: blank, padded or too long
        name = m.get("short_display_name")
        if name is not None and not (
                isinstance(name, str) and name == name.strip()
                and 1 <= len(name) <= SHORT_NAME_MAX):
            errs.append(f"short_display_name must be 1-{SHORT_NAME_MAX} "
                        "chars, no surrounding spaces")
        if m.get("status") == "blocked" and not m.get("blocked"):
            errs.append("blocked without a reason")
        if m.get("status") == "parked" and not m.get("parked"):
            errs.append("parked without a reason")
        if m.get("parked") and m.get("status") in ("todo", "doing", "blocked",
                                                   "grooming"):
            errs.append(f"parked reason on a {m['status']} item (clear it: "
                        f"wi set {m.get('id')} parked \"\")")
        if m.get("status") == "grooming" and not m.get("grooming"):
            errs.append("grooming without questions")
        if m.get("grooming") and m.get("status") in ("todo", "doing", "blocked",
                                                     "parked"):
            errs.append(f"grooming questions on a {m['status']} item (clear "
                        f"them: wi set {m.get('id')} grooming \"\")")
        if m.get("status") in ("done", "dropped") and not m.get("closed"):
            errs.append(f"{m['status']} without closed date")
        return errs


# ── Store: root, lock, load/save ────────────────────────────────────────────

# 5f46: the environment names. WORK_ITEMS_* are current; the WI_* names
# are deprecated fallbacks that still work. The new name wins when both are
# set; an empty value counts as unset.
ENV_NAMES = (("WORK_ITEMS_ROOT", "WI_ROOT"),
             ("WORK_ITEMS_OWNER", "WI_OWNER"))


def _env(new, old):
    """(value, notice) for one variable under its new and deprecated names:
    the new name's value when set, else the old one's, else None. notice is
    a one-line deprecation notice when the old name is used, or is set to a
    different value from the new name; None when both are set alike (the
    transition export) or the old name is unset."""
    new_v, old_v = os.environ.get(new) or "", os.environ.get(old) or ""
    if new_v:
        if old_v and old_v != new_v:
            return new_v, f"wi: deprecated: {old} and {new} differ; {new} wins"
        return new_v, None
    if old_v:
        return old_v, f"wi: deprecated: {old} is set; use {new}"
    return None, None


_ENV_NOTICED = set()


def env_notices():
    """The deprecation notices for the environment names, each at most once
    per process. Printed only where health is read: prime, lint and init."""
    out = []
    for new, old in ENV_NAMES:
        notice = _env(new, old)[1]
        if notice and notice not in _ENV_NOTICED:
            _ENV_NOTICED.add(notice)
            out.append(notice)
    return out


# 5f46: the store locations under a directory, in lookup order. .work-items/
# is the default; the other two are old locations, deprecated, still found.
STORE_LOCATIONS = (".work-items", ".claude-sandbox/work", ".work")
DEFAULT_STORE = STORE_LOCATIONS[0]
MOVING_A_STORE = ("the work-items skill's references/format.md § Moving a "
                  "store")


def _auto_root(base=Path(".")):
    """The first location under base that holds items/, else None."""
    for rel in STORE_LOCATIONS:
        if (base / rel / "items").is_dir():
            return Path(rel) if base == Path(".") else base / rel
    return None


def _root_and_source(explicit=None):
    """(root, auto): the root from --root, then WORK_ITEMS_ROOT (WI_ROOT),
    then the first store location under the cwd that holds items/, else the
    default .work-items. auto is False for a flag or env root."""
    root = explicit or _env("WORK_ITEMS_ROOT", "WI_ROOT")[0]
    if root:
        return Path(root), False
    return (_auto_root() or Path(DEFAULT_STORE)), True


# A linked worktree whose main checkout's path git does not give: its common
# dir is not named .git (a worktree of a bare repo, or of a
# --separate-git-dir clone).
MAIN_UNKNOWN = object()


def linked_worktree_main():
    """The main checkout's path when the cwd is in a linked git worktree,
    MAIN_UNKNOWN when it is one but the main checkout's path is not known,
    else None (the main checkout, outside git, git missing, slow or too old
    for --path-format). One git call; run only on the no-store path."""
    r = _git(".", "rev-parse", "--path-format=absolute", "--git-dir",
             "--git-common-dir")
    if r is None or r.returncode != 0:
        return None
    lines = r.stdout.splitlines()
    if len(lines) != 2 or not all(lines):
        return None
    git_dir, common = (os.path.realpath(ln) for ln in lines)
    if git_dir == common:
        return None
    common = Path(common)
    return common.parent if common.name == ".git" else MAIN_UNKNOWN


def _worktree_store(main):
    """The main checkout's store to name: the first location there that
    holds items/, else the default; a placeholder path when the main
    checkout is not known."""
    if main is MAIN_UNKNOWN:
        return f"<main checkout>/{DEFAULT_STORE}"
    found = _auto_root(main)
    return found if found is not None else main / DEFAULT_STORE


def worktree_init_refusal():
    """init's refusal when no root is named, no store is found and the cwd
    is a linked worktree, else None (D11 of the 5f46 series)."""
    root, auto = _root_and_source(None)
    if not auto or (root / "items").is_dir():
        return None
    main = linked_worktree_main()
    if main is None:
        return None
    where = "" if main is MAIN_UNKNOWN else f" {main}"
    return ("wi init: refusing to create a store in a linked worktree (it "
            f"would be a stray copy); run it in the main checkout{where}, or "
            "name the root with --root or WORK_ITEMS_ROOT")


def old_location(root):
    """True when the store's real path is at an old location: named .work,
    or work inside .claude-sandbox. Flag, env and auto roots alike."""
    real = Path(os.path.realpath(root))
    return (real.name == ".work"
            or (real.name == "work" and real.parent.name == ".claude-sandbox"))


_LOCATION_NOTICED = set()


def location_notices(root):
    """The old-location deprecation notice, at most once per process.
    Printed only where health is read: prime, lint and init."""
    if not old_location(root):
        return []
    notice = (f"wi: deprecated: store {root} is at an old location; the "
              f"default is {DEFAULT_STORE}/ ({MOVING_A_STORE})")
    if notice in _LOCATION_NOTICED:
        return []
    _LOCATION_NOTICED.add(notice)
    return [notice]


def _store_parent(real):
    """D when a real path is D/.work-items, D/.work or D/.claude-sandbox/work;
    else None."""
    if real.name in (".work-items", ".work"):
        return real.parent
    if real.name == "work" and real.parent.name == ".claude-sandbox":
        return real.parent.parent
    return None


def two_store_warning(root):
    """One line when the store is a known location under a directory D and
    another known location under D also holds items/, else None. Stores are
    compared by real path: a symlink alias of the same store is not a
    second one."""
    real = Path(os.path.realpath(root))
    base = _store_parent(real)
    if base is None:
        return None
    seen, others = {real}, []
    for rel in STORE_LOCATIONS:
        cand = base / rel
        if not (cand / "items").is_dir():
            continue
        cand_real = Path(os.path.realpath(cand))
        if cand_real in seen:
            continue
        seen.add(cand_real)
        others.append(str(cand))
    if not others:
        return None
    return (f"wi: WARNING more than one work-item store under {base}: using "
            f"{real}, also {', '.join(others)} (move or remove the extra "
            f"one: {MOVING_A_STORE})")


def resolve_root(explicit=None, must_exist=True, warn_stores=True):
    """The store root. With auto-resolution, a second store under the same
    dir is warned of on stderr (warn_stores; prime and lint report it
    themselves, whatever the root's source). With no store found and no
    root named, a linked worktree is pointed at its main checkout's
    store."""
    root, auto = _root_and_source(explicit)
    if must_exist and not (root / "items").is_dir():
        main = linked_worktree_main() if auto else None
        if main is not None:
            raise WiError(1, "no work-item store in this linked worktree; the "
                             "store lives in the main checkout: export "
                             f"WORK_ITEMS_ROOT={_worktree_store(main)}")
        raise WiError(1, f"no work-item root at {root} (run `wi init`)")
    if auto and warn_stores:
        warning = two_store_warning(root)
        if warning:
            print(warning, file=sys.stderr)
    return root


# Custody check: is the store silently untracked by the git repo that holds
# it? (7f00/7772: a whole-dir /.claude-sandbox/ ignore, written by the
# claude-sandbox launcher when trackInHost is false, hid new items.) At most
# two bounded git calls, run from the store dir so git judges the repo that
# contains it — a sidecar store's own nested repo included.
GIT_TIMEOUT = 2.0
# Below this many items, "none tracked" is a store not yet committed, which
# `git status` already shows; at or above it, a store has grown without ever
# being added.
UNTRACKED_MIN_ITEMS = 10
PROBE_ITEM = "items/wi-custody-probe-0000.md"   # a new item's would-be path
# a new card record's would-be path: an ignore rule that catches only
# cards/ (or *.json) hides every record a raise writes
PROBE_CARD = "cards/wi-custody-probe-0000/1/2026-01-01T00-00-00Z.card5.json"


def _git(cwd, *args, stdin=None, timeout=GIT_TIMEOUT, extra_env=None,
         scrub=()) -> "subprocess.CompletedProcess[str] | None":
    """Run git; None when it is missing, the cwd is gone, or it times out.
    Output is decoded here, not by subprocess: -z output is raw bytes (no
    quotePath), and a non-UTF-8 path must neither crash nor depend on the
    locale; backslashreplace shows such a byte readably, as \\xe9.
    timeout, extra_env and scrub (more names to drop from the env) serve
    `wi commit` in a store its host or sidecar repo tracks, whose hooks get
    longer than a read (d1e9 D5)."""
    drop = {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", *scrub}
    env = {k: v for k, v in os.environ.items() if k not in drop}
    env.update(extra_env or {})
    try:
        r = subprocess.run(["git"] + list(args), cwd=cwd, env=env,
                           input=None if stdin is None else stdin.encode(),
                           capture_output=True, timeout=timeout)
        r.stdout = r.stdout.decode("utf-8", "backslashreplace")
        r.stderr = r.stderr.decode("utf-8", "backslashreplace")
        return typing.cast("subprocess.CompletedProcess[str]", r)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _dir_level(pattern, root):
    """True when an ignore pattern excludes a directory on the store's path
    (a trailing '/', or its last segment matches a parent dir of the probe
    item or probe card). git cannot re-include a path under an excluded
    directory, so a negation is dead advice for such a rule. Heuristic: the
    parents checked are every component of the store's absolute path, plus
    items/ and cards/."""
    p = pattern.strip()
    if p.endswith("/"):
        return True
    last = p.rsplit("/", 1)[-1]
    parents = list(root.absolute().parts[1:]) + ["items", "cards"]
    return any(fnmatch.fnmatchcase(d, last) for d in parents)


# The store's recorded tracking choice (39a2): `wi init` writes it, prime and
# lint read it. A store without the file (or without a valid `tracking:`
# line) has no recorded choice.
STORE_FILE = "store.yaml"
TRACKING_CHOICES = ("tracked", "ignored")
# d1e9: `repo: own` says the store is its own git repo and wi commits there
REPO_OWN = "own"


def read_tracking(root):
    """'tracked' | 'ignored' | None (no file, or no valid tracking: line)."""
    raw = _store_tracking_raw(root)
    return raw if raw in TRACKING_CHOICES else None


def _store_key_values(root, key):
    """Every `key:` value in store.yaml as written, in order, or None when
    there is no readable store file. The file has two top-level keys,
    `tracking:` and `repo:` (d1e9), and one block, `counters:` (03ab F8),
    read by _store_counters; lines with other keys are skipped."""
    try:
        text = (root / STORE_FILE).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    values = []
    for line in text.splitlines():
        m = re.match(rf"^{key}:\s*(.*?)\s*$", line)
        if m:
            values.append(m.group(1).strip("\"'"))
    return values


def _store_tracking_values(root):
    """Every tracking: value as written, in order, or None when there is no
    readable store file."""
    return _store_key_values(root, "tracking")


def read_repo_own(root):
    """True when store.yaml records `repo: own` (its first `repo:` line):
    the store is its own git repo, set up by `wi init` (d1e9)."""
    return (_store_key_values(root, "repo") or [""])[0] == REPO_OWN


def _store_tracking_raw(root):
    """The first tracking: value as written ('' for a file without one), or
    None when there is no readable store file."""
    values = _store_tracking_values(root)
    if values is None:
        return None
    return values[0] if values else ""


def write_tracking(root, choice, repo=None):
    """Rewrite store.yaml with this tracking choice (and `repo:`), carrying
    its `counters:` block over unchanged, so a re-run `wi init` never drops
    the decision counter (03ab F8)."""
    try:
        old = (root / STORE_FILE).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        old = ""
    span = _counters_span(old.splitlines(keepends=True))
    block = ""
    if span is not None:
        lines = old.splitlines(keepends=True)[span[0]:span[1]]
        block = "".join(ln if ln.endswith("\n") else ln + "\n"
                        for ln in lines)
    atomic_write(root / STORE_FILE,
                 "# wi store settings; format: the work-items skill's "
                 "references/format.md\n"
                 f"tracking: {choice}\n"
                 + (f"repo: {repo}\n" if repo else "") + block)


# 03ab F8: decision numbers come from a counter in store.yaml, the last N
# given out, which `wi raise` advances under the store's lock:
#
#   counters:
#     decision: 309
#
# Its value never stands alone: every reader takes the larger of it and the
# highest N on a `decision N:` line in items/ and archive/*/ (format.md
# § Allocating a decision number).
COUNTERS_RE = re.compile(r"^counters:\s*$")
COUNTER_LINE_RE = re.compile(r"^\s+([a-z-]+):\s*(.*?)\s*$")
# [0-9], not \d: \d also takes other scripts' digits, which int() accepts
COUNTER_VALUE_RE = re.compile(r"^[0-9]+$")
CONFLICT_RE = re.compile(r"^(<{7}|={7}|>{7})", re.M)


def _counters_span(lines):
    """(start, end) of the first `counters:` block in store.yaml's lines:
    its header line and the indented lines under it, blank lines between
    them included, up to the first line that is neither indented nor blank
    (trailing blank lines are left outside); None when there is no
    block."""
    for i, line in enumerate(lines):
        if COUNTERS_RE.match(line.rstrip("\r\n")):
            end = j = i + 1
            while j < len(lines):
                if lines[j][:1] in (" ", "\t"):
                    end = j + 1
                elif lines[j].strip():
                    break
                j += 1
            return i, end
    return None


def _counter_entries(text):
    """[(key, raw value)] for every indented key line of text's `counters:`
    block, in order, repeats included."""
    lines = text.splitlines(keepends=True)
    span = _counters_span(lines)
    out = []
    if span is not None:
        for line in lines[span[0] + 1:span[1]]:
            m = COUNTER_LINE_RE.match(line.rstrip("\r\n"))
            if m:
                out.append((m.group(1), m.group(2)))
    return out


def _store_counters(root):
    """(text, {key: raw value}) for store.yaml's `counters:` block: text is
    the file as read, None when there is no readable store file; the map is
    empty without a block. The first line per key counts."""
    try:
        text = (root / STORE_FILE).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None, {}
    values = {}
    for key, raw in _counter_entries(text):
        values.setdefault(key, raw)
    return text, values


def counter_duplicates(root):
    """The lint problems for a key written more than once in store.yaml's
    `counters:` block (the first line counts; the next write keeps one)."""
    try:
        text = (root / STORE_FILE).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    keys = [k for k, _ in _counter_entries(text)]
    return [f"{root / STORE_FILE}: counters: {k} appears more than once; "
            "keep one line, the last number given out"
            for k in dict.fromkeys(keys) if keys.count(k) > 1]


def counter_problem(root, key="decision"):
    """Why store.yaml's counter cannot be read or written, or None: the file
    holds merge conflict markers, or the counter's value is not a whole
    number. Either way `raise` writes nothing and lint never reseeds."""
    text, values = _store_counters(root)
    if text is None:
        return None
    if CONFLICT_RE.search(text):
        return (f"{root / STORE_FILE}: unresolved merge conflict markers; "
                "resolve them (keep the larger counter) and re-run")
    raw = values.get(key)
    if raw is not None and not COUNTER_VALUE_RE.match(raw):
        return (f"{root / STORE_FILE}: counters: {key} must be a whole "
                f"number (got '{raw}'); set it to the last {key} N given out")
    return None


def read_counter(root, key="decision"):
    """The counter's value; 0 for a missing file, block or key. The caller
    checks counter_problem first: a value that is not a whole number
    reads as 0 here."""
    raw = _store_counters(root)[1].get(key)
    return int(raw) if raw is not None and COUNTER_VALUE_RE.match(raw) else 0


def write_counter(root, n, key="decision"):
    """Set the counter to n in store.yaml, keeping every other line (the
    `tracking:` and `repo:` lines, comments, other counters) as it is. A
    store with no store.yaml gets none: a file without `tracking:` would be
    a lint problem, and every reader takes the items' highest N anyway.
    Returns whether it wrote."""
    text, _ = _store_counters(root)
    if text is None:
        return False
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    entry = f"  {key}: {n}\n"
    span = _counters_span(lines)
    if span is None:
        lines += ["counters:\n", entry]
    else:
        start, end = span
        block = [ln for ln in lines[start + 1:end]
                 if not ((m := COUNTER_LINE_RE.match(ln.rstrip("\r\n")))
                         and m.group(1) == key)]
        lines[start + 1:end] = [entry] + block
    atomic_write(root / STORE_FILE, "".join(lines))
    return True


def items_decision_max(root):
    """The highest N on a column-0 `decision N:` line outside a fenced code
    block, over items/ and archive/*/ (the same marker and fence rule as
    unanswered_decisions); 0 when there is none. A file that cannot be
    read is skipped."""
    best = 0
    for path in item_paths(root, archived=True):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.replace("\r\n", "\n").split("\n")
        fenced = set()
        for i, j in _fence_spans(lines):
            fenced.update(range(i, j + 1))
        for i, line in enumerate(lines):
            m = DECISION_RE.match(line) if i not in fenced else None
            if m:
                best = max(best, int(m.group(1)))
    return best


def last_decision(root):
    """The last decision number given out: the larger of the counter and
    the items' highest N, so a counter behind the items (a hand-written
    line, an older wi, a dropped block) never hands a number out again."""
    return max(read_counter(root), items_decision_max(root))


def _custody_git(root):
    """The git runner custody uses for this store: the hardened store runner
    (with custody's 2 s bound) when the store has a .git of its own, so its
    config's fsmonitor and hooks never run (d1e9 D6'); else _git, which reads
    the host or sidecar repo the user's own git runs anyway."""
    if os.path.lexists(Path(root) / ".git"):
        return lambda cwd, *args, stdin=None: _store_git(
            cwd, *args, stdin=stdin, timeout=GIT_TIMEOUT)
    return _git


def custody_warning(root, repo_state=None):
    """One-line warning when the store is silently untracked, else None.
    Silent outside git, when git is missing or slow, or on any git error,
    and for a store whose recorded choice is `ignored` (39a2), except a
    sidecar store, which lands in no repo when ignored (3c06). Silent too for
    a store whose own .git is broken: the store-repo check reports it."""
    if os.path.lexists(Path(root) / ".git"):
        if repo_state is None:
            repo_state = store_repo_state(root)
        if repo_state.state in ("broken", "unknown"):
            return None
    tracking = read_tracking(root)
    sidecar = sandbox_shape(root)[0] == "sidecar"
    if tracking == "ignored":
        # 3c06: a sidecar's host ignores .claude-sandbox/ as a whole, so a
        # store its own repo ignores too lands in no repo at all
        return _sidecar_ignored_warning(root) if sidecar else None
    if tracking == "tracked":
        head = (f"wi: WARNING store {root} is silently untracked, against "
                f"its recorded choice (tracking: tracked in {STORE_FILE}): ")
        tail = ("" if sidecar or read_repo_own(root) else
                "; or, if it is meant to stay local, run `wi init --no-track`")
    else:
        head = f"wi: WARNING store {root} is silently untracked: "
        tail = ("; then record the choice: `wi init --track`" if sidecar else
                "; then record the choice: `wi init --track`, or "
                "`wi init --no-track` if it is meant to stay local")
    body = _custody_body(root)
    return None if body is None else head + body + tail


SIDECAR_NO_REPO = ("a sidecar store (.claude-sandbox/ is its own git repo, "
                   "which the host does not track)")


def _sidecar_ignored_warning(root):
    """The warning for a sidecar store recorded `ignored` (3c06). Raised on
    the record alone; when git names the sidecar repo's rule, the fix names
    it too, since `wi init --track` never edits a .gitignore."""
    msg = (f"wi: WARNING {root} is {SIDECAR_NO_REPO}, recorded git-ignored "
           f"(tracking: ignored in {STORE_FILE}), so new items land in no "
           "repo; fix: `wi init --track`")
    rule = _ignore_rule(root)
    if rule:
        src, lineno, pattern = rule
        where = f"{src}:{lineno} '{pattern}'"
        if not os.path.isabs(src):
            where += " in the sidecar repo .claude-sandbox/"
        msg += f", then remove the ignore line {where}"
    return msg


def _ignore_rule(root, *extra, where=None):
    """The (source, line, pattern) of the rule that ignores a new item's
    path in the store (or, in the store's own form, a new card record's),
    None when nothing does, False when git cannot say. _ignore_hits has
    every ignored probe path."""
    hits = _ignore_hits(root, *extra, where=where)
    if hits is False:
        return False
    return hits[0][:3] if hits else None


def _ignore_hits(root, *extra, where=None):
    """Each (source, line, pattern, path) by which git ignores one of the
    probe paths, in git's order; [] when none is ignored, False when git
    cannot say.
    where=(repo, rel) asks from that repo's top on the store's paths there
    (rel/items, rel/<probe>), so a store that is its own repo is judged by
    the repo around it, not by its own (d1e9 D3 step 4); the source git
    names is relative to the repo's top either way. There a rule from a
    file inside the store (its own .gitignore holding `items/` or `*`)
    never counts: the repo around the store must ignore it itself, or its
    `add -A` stages the store (a gitlink, for a store with its own repo)."""
    if where is None:
        r = _custody_git(root)(root, "check-ignore", "-v", "-z", *extra,
                               "--stdin",
                               stdin=f"items\0{PROBE_ITEM}\0{PROBE_CARD}\0")
    else:
        repo, rel = where
        # item probes only, never PROBE_CARD: this form asks whether the
        # repo around the store ignores the store as a whole (init's ignore
        # line, an own store's host check), and a rule that ignores only
        # card records (`cards/`, `*.json`) does not; counting it would skip
        # the store's ignore line and let the host commit it (3b51 W1)
        r = _git(repo, "check-ignore", "-v", "-z", *extra, "--stdin",
                 stdin=f"{rel}/items\0{rel}/{PROBE_ITEM}\0")
    if r is None or r.returncode not in (0, 1):
        return False
    fields = r.stdout.split("\0")
    inside = None if where is None else where[1].rstrip("/") + "/"
    hits = []
    for i in range(0, len(fields) - 3, 4):   # source, linenum, pattern, path
        src, lineno, pattern, path = fields[i:i + 4]
        if inside and src.startswith(inside):
            continue                                  # the store's own rule
        if pattern and not pattern.startswith("!"):   # a negation un-ignores
            hits.append((src, lineno, pattern, path))
    return hits


def _custody_body(root):
    """The cause and fix of a silently untracked store, or None."""
    # the probe path, not only `items`, catches a store whose tracked files
    # mask the ignore rule: check-ignore skips tracked paths, but a new
    # item's path is still matched against the rule. -v names the rule; -z
    # (which git allows only with --stdin) gives NUL-separated fields with
    # paths unquoted, so a source path holding ':N:', a tab or a non-ASCII
    # byte parses; _git decodes the raw bytes without failing.
    hits = _ignore_hits(root)
    if hits is False:
        return None
    if hits:
        src, lineno, pattern, _ = hits[0]
        # a rule that ignores only card records leaves new items tracked
        what = ("new card records" if all(h[3] == PROBE_CARD for h in hits)
                else "new items")
        shape, _ = sandbox_shape(root)
        where = f"{src}:{lineno} '{pattern}'"
        # sidecar: the nested repo owns the store, so host advice
        # (trackInHost, the host .gitignore) does not apply. A relative
        # source is that repo's own .gitignore or info/exclude; an absolute
        # one (an excludesFile) is named as is.
        there = ""
        if shape == "sidecar" and not os.path.isabs(src):
            where += " in the sidecar repo .claude-sandbox/"
            there = " there"
        whole_dir = shape != "sidecar" and pattern.strip() in SANDBOX_IGNORES
        if whole_dir:
            # git cannot re-include a path under an excluded parent, so a
            # negation after a whole-dir ignore is dead
            remedy = ("remove it, or rewrite it as `/.claude-sandbox/*` plus "
                      "`!/.claude-sandbox/work/`")
        elif _dir_level(pattern, root):
            remedy = (f"remove it or narrow it{there} (a negation cannot "
                      "re-include files under an ignored directory)")
        else:
            remedy = f"remove or negate that rule{there}"
        if shape == "sidecar":
            return f"{what} are git-ignored by {where}; fix: {remedy}"
        fix = [f"{what} are git-ignored by {where}; fix: {remedy}"]
        if shape is not None:
            fix.append(" and set trackInHost: true in the sandbox config (a "
                       "claude-sandbox launcher at 490d8ca or later warns "
                       "about this)")
            if whole_dir:
                # agents 0002: a public-shaped repo keeps the whole-dir
                # ignore; removing it would publish private items
                fix.append(", or, for a public repo, give .claude-sandbox/ "
                           "its own sidecar git")
        return "".join(fix)
    n = len(item_paths(root))
    if n < UNTRACKED_MIN_ITEMS:
        return None
    r = _custody_git(root)(root, "ls-files", "--", ".")
    if r is None or r.returncode != 0 or r.stdout.strip():
        return None
    return f"it holds {n} items and git tracks none; fix: `git add` the store"


class Lock:
    """flock on <root>/.lock; 10s wait then exit 4.

    d1e9 F5: a write command's lock also commits what the command wrote.
    With `commit` (the default), a store recording `repo: own` has its repo
    validated before the flock is taken; every file written under the lock
    is journalled (_journal_write), and __exit__ commits the journal's own
    paths into the store's repo before it releases the flock, also when the
    block raised after some writes. The commit never raises: a failure is
    one stderr warning and the write stands. A store without `repo: own`
    costs one read of store.yaml and runs no git. `commit=False` is for a
    lock that writes nothing (lint's check, `wi commit`) or commits by
    itself (`init`), and for a dry run, which writes nothing."""

    def __init__(self, root, timeout=10.0, *, commit=True):
        self.root, self.commit = root, commit
        self.path, self.timeout, self.fh = root / ".lock", timeout, None
        self.repo = None

    def __enter__(self):
        # validation before the lock (d1e9 D4''): no git runs while it is held
        self.repo = _per_change_state(self.root) if self.commit else None
        self.fh = open(self.path, "a")
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    self.fh.close()
                    raise WiError(4, "lock timeout on " + str(self.path))
                time.sleep(0.05)
        _JOURNAL.clear()
        return self

    def __exit__(self, *exc):
        try:
            if self.repo is not None:
                _commit_journal(self.root, self.repo)
        finally:
            _JOURNAL.clear()
            fcntl.flock(self.fh, fcntl.LOCK_UN)
            self.fh.close()


# d1e9 F5: what a write command wrote, for its lock to commit. Paths as
# written (absolute or relative to the cwd); only those under the locked
# store, among its own paths, are committed. A process holds one lock at a
# time, and each lock starts the journal empty.
_JOURNAL = []
# the subcommand being run (main sets it): the <verb> of a commit message
_COMMAND = ["write"]


def _journal_write(path):
    _JOURNAL.append(Path(path))


# d1e9: a store that is its own git repo (.work-items/.git), recorded
# `repo: own` in store.yaml. Every git call that acts in such a store goes
# through one hardened runner, so the store's config, the user's global
# config, a host hook's environment and a damaged .git can neither run
# commands nor send git into another repo. format.md § The store's own repo.
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
STORE_GIT_PINS = (
    "-c", "core.hooksPath=/dev/null",      # no hook, wherever it sits
    "-c", "core.fsmonitor=false",
    "-c", "commit.gpgSign=false",
    "-c", "core.autocrlf=false", "-c", "core.safecrlf=false",
    "-c", "gc.auto=0", "-c", "maintenance.auto=false",
    "-c", "core.attributesFile=/dev/null",  # no global attributes file
    # a git that reads attr.tree takes attributes from that tree: pinned to
    # the empty tree, a value in any config file selects nothing
    "-c", f"attr.tree={EMPTY_TREE}",
)
# a host hook that calls wi has these set to the host's
STORE_GIT_SCRUB = frozenset((
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE",
    "GIT_PREFIX", "GIT_ATTR_SOURCE",
    # the runner picks its own pathspec magic: literal, or none
    "GIT_ICASE_PATHSPECS", "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS"))
STORE_GIT_TIMEOUT = 10.0
# the store's own paths: what wi writes, and all a store repo commits
OWN_PATHS = ("items", "archive", "cards", "README.md", STORE_FILE,
             ".gitignore")
STALE_INDEX_LOCK = 600   # seconds


def _store_git(root, *args, timeout=STORE_GIT_TIMEOUT, stdin=None,
               pins=True):
    """Run git in a store with its own repo, hardened (d1e9 D2): the pins
    above, cwd the store, GIT_CEILING_DIRECTORIES its real parent (a broken
    .git never falls through to the host), the host's GIT_* scrubbed,
    GIT_ATTR_NOSYSTEM, optional locks off, no prompt, LC_ALL=C, and literal
    pathspecs for every call but check-ignore, which refuses them. Args are
    a list, never a shell. None when git is missing or times out, or when
    the store's parent holds os.pathsep, which would split the ceiling into
    two paths; output decoded as _git does. pins=False drops the -c pins,
    and the caller's command-scope config (GIT_CONFIG_PARAMETERS,
    GIT_CONFIG_COUNT and its KEY_n/VALUE_n), which would win over the repo's
    and blame it: only for reading the config a hand-run git resolves."""
    real = os.path.realpath(root)
    if os.pathsep in os.path.dirname(real):
        return None
    env = {k: v for k, v in os.environ.items() if k not in STORE_GIT_SCRUB}
    if not pins:
        env = {k: v for k, v in env.items()
               if k not in ("GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT")
               and not k.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    # GIT_NO_LAZY_FETCH: a missing object never fetches from a promisor
    # remote, whose uploadpack or ssh command the store's config could name
    env.update(GIT_CEILING_DIRECTORIES=os.path.dirname(real),
               GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0",
               GIT_ATTR_NOSYSTEM="1", GIT_NO_LAZY_FETCH="1", LC_ALL="C")
    if args[:1] == ("check-ignore",):
        env.pop("GIT_LITERAL_PATHSPECS", None)
    else:
        env["GIT_LITERAL_PATHSPECS"] = "1"
    try:
        r = subprocess.run(["git", *(STORE_GIT_PINS if pins else ()), *args],
                           cwd=real, env=env,
                           input=None if stdin is None else stdin.encode(),
                           capture_output=True, timeout=timeout)
        r.stdout = r.stdout.decode("utf-8", "backslashreplace")
        r.stderr = r.stderr.decode("utf-8", "backslashreplace")
        return r
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


class StoreRepo:
    """What a store's own .git is (d1e9 D1). state:
    plain       no .git, no `repo: own`
    own         a valid .git, `repo: own` recorded: wi commits there
    unrecorded  a valid .git, no `repo: own`, a host repo around the store
    dedicated   a valid .git, no `repo: own`, no host: a store at the top of
                its own repo, tracked by it (`--track`); not wi's to commit
    missing     `repo: own` recorded, no .git
    broken      a .git that is not a valid store repo (reason says why)
    old         a .git in an old-location store: never own
    unknown     git missing or slow: every check stays silent"""

    def __init__(self, state, reason=None, git_dir=None, common_dir=None,
                 host=None):
        self.state, self.reason = state, reason
        self.git_dir, self.common_dir, self.host = git_dir, common_dir, host


def _inside(path, base):
    return path == base or path.startswith(base.rstrip(os.sep) + os.sep)


def _validate_store_git(root):
    """(git_dir, common_dir, reason): one hardened rev-parse with the 2 s
    bound. reason is None when the .git is a valid repo of the store's own;
    all three are None when git did not answer."""
    r = _store_git(root, "rev-parse", "--path-format=absolute",
                   "--is-bare-repository", "--git-dir", "--git-common-dir",
                   "--show-toplevel", timeout=GIT_TIMEOUT)
    if r is None:
        return None, None, None
    lines = r.stdout.splitlines()
    if lines[:1] == ["true"]:
        return None, None, ".git is a bare repository"
    if r.returncode != 0 or len(lines) != 4:
        first = (r.stderr.strip().splitlines() or ["git rev-parse failed"])[0]
        return None, None, f".git is not a usable repository: {first[:200]}"
    real = os.path.realpath(root)
    git_dir, common, top = (os.path.realpath(ln) for ln in lines[1:])
    for d in (git_dir, common):
        if not _inside(d, real):
            return None, None, f".git points outside the store ({d})"
        # a git dir among the store's own paths would be committed with them
        own = next((p for p in OWN_PATHS
                    if _inside(d, os.path.join(real, p))), None)
        if own is not None:
            return None, None, (f".git points into the store's own path "
                                f"{own} ({d})")
    if top != real:
        return None, None, (f".git makes {top} the top of its repo, not the "
                            "store")
    return git_dir, common, None


ATTR_REASON = ("{} selects git attributes (a filter there can run "
               "commands); remove it")
NESTED_REASON = "{} is a nested git repo or gitlink; remove it"
PROMISOR_KEYS = r"^(extensions\.partialclone|remote\..*\.promisor)$"
PROMISOR_REASON = ("the store's git config sets {} (a lazy fetch from a "
                   "promisor remote can run commands); remove it")


def _unsafe_walk(root):
    """The part of _unsafe_path a walk of the store's files decides, with no
    git: a .gitattributes anywhere in the store, or a .git below its root.
    Run alone on a store `init` is about to give a repo (d1e9 F3)."""
    real = os.path.realpath(root)
    for dirpath, dirs, files in os.walk(real):
        names = sorted(dirs + files)
        if dirpath != real:
            for name in names:
                if name.lower() == ".git":
                    return NESTED_REASON.format(os.path.relpath(
                        os.path.join(dirpath, name), real))
        for name in names:
            if name.lower() == ".gitattributes":
                return ATTR_REASON.format(os.path.relpath(
                    os.path.join(dirpath, name), real))
        dirs[:] = sorted(d for d in dirs if d.lower() != ".git")
    return None


def _unsafe_path(root, git_dir, common_dir):
    """Why the store's repo could run a command it did not choose, else
    None (d1e9 D1''): an attribute file (a .gitattributes anywhere in the
    store, <git-dir>/info/attributes, or a .gitattributes only the index
    holds), or a nested repo (a .git below the store's root, or a gitlink,
    mode 160000, in the index), whose own config and attributes git can
    reach by recursing into it. Names are compared case-blind, as a
    case-insensitive file system matches them."""
    unsafe = _unsafe_walk(root)
    if unsafe:
        return unsafe
    real = os.path.realpath(root)
    for d in dict.fromkeys((git_dir, common_dir)):
        p = os.path.join(d, "info", "attributes")
        if os.path.lexists(p):
            return ATTR_REASON.format(os.path.relpath(p, real))
    # a promisor remote fetches a missing object lazily, running whatever
    # uploadpack or ssh command the config names; the runner sets
    # GIT_NO_LAZY_FETCH, and this refuses the shape for a git that may not
    # read it. Key names print lowercased; a remote's name keeps its case.
    r = _store_git(root, "config", "--get-regexp", PROMISOR_KEYS,
                   timeout=GIT_TIMEOUT)
    if r is not None and r.returncode == 0 and r.stdout.strip():
        return PROMISOR_REASON.format(r.stdout.split()[0])
    r = _store_git(root, "ls-files", "-s", "-z", timeout=GIT_TIMEOUT)
    if r is not None and r.returncode == 0:
        for rec in r.stdout.split("\0"):
            meta, _, path = rec.partition("\t")
            if not path:
                continue
            if meta.split(" ", 1)[0] == "160000":
                return NESTED_REASON.format(path)
            if path.rsplit("/", 1)[-1].lower() == ".gitattributes":
                return ATTR_REASON.format(path)
    return None


HOST_UNKNOWN = object()   # git did not say whether a repo is around


def _host_repo(root):
    """The top of the git repo around the store, asked from the store's real
    parent, so a store that is its own repo still finds its host; None
    outside git (git says "not a git repository"); HOST_UNKNOWN when git
    did not answer or failed otherwise, so a store is never taken for one
    with no host on a timeout. A host read: plain _git, in the C locale."""
    parent = os.path.dirname(os.path.realpath(root))
    # a store `init` has yet to create: ask from its nearest existing parent
    while not os.path.isdir(parent) and os.path.dirname(parent) != parent:
        parent = os.path.dirname(parent)
    r = _git(parent, "rev-parse", "--show-toplevel",
             extra_env={"LC_ALL": "C"})
    if r is None:
        return HOST_UNKNOWN
    if r.returncode != 0:
        return None if "not a git repository" in r.stderr else HOST_UNKNOWN
    if not r.stdout.strip():
        return HOST_UNKNOWN
    return Path(r.stdout.strip())


def store_repo_state(root):
    """The store's StoreRepo (d1e9 D1). No git call for a store without
    .git: one lstat and a read of store.yaml."""
    has_git = os.path.lexists(Path(root) / ".git")
    own = read_repo_own(root)
    if has_git and old_location(root):
        return StoreRepo("old")
    if not has_git:
        return StoreRepo("missing" if own else "plain")
    git_dir, common, reason = _validate_store_git(root)
    if reason:
        return StoreRepo("broken", reason)
    if git_dir is None:
        return StoreRepo("unknown")
    host = _host_repo(root)
    if host is HOST_UNKNOWN:
        return StoreRepo("unknown")
    if not own and host is None:
        # a dedicated repo keeps its attributes: its rules are the user's
        return StoreRepo("dedicated", git_dir=git_dir, common_dir=common)
    unsafe = _unsafe_path(root, git_dir, common)
    if unsafe:
        return StoreRepo("broken", unsafe)
    return StoreRepo("own" if own else "unrecorded", git_dir=git_dir,
                     common_dir=common, host=host)


def _kept_by_listing(candidates, listed):
    """The candidates a git listing holds: a printed path equal to one, or
    under it as a directory. `archive` is kept by archive/2026/x.md;
    items/x.md is not kept by items/x.md.tmp1."""
    return [c for c in candidates
            if any(p == c or p.startswith(c + "/") for p in listed)]


def existing_paths(root, candidates, git=None):
    """The candidates git can match, in order (d1e9 D4'): one the index
    holds something under (a removal to stage included), or one with an
    untracked file under it that is not ignored. A pathspec matching
    neither makes `add` and `commit` fail, and an empty directory (an
    `items/` whose items were all archived) matches nothing. One
    `ls-files -c -o --exclude-standard` call, through `git(*args)`: the
    store runner by default; `wi commit` passes its own (a deadline, or the
    host's git). When git cannot list, the candidates on disk."""
    if git is None:
        def git(*args):
            return _store_git(root, *args, timeout=GIT_TIMEOUT)
    r = git("ls-files", "-z", "-c", "-o", "--exclude-standard", "--",
            *candidates)
    if r is None or r.returncode != 0:
        return [c for c in candidates if os.path.lexists(Path(root) / c)]
    return _kept_by_listing(candidates, r.stdout.split("\0"))


def _age(seconds):
    seconds = int(seconds)
    if seconds >= 3600:
        return f"{seconds // 3600}h{seconds % 3600 // 60:02d}m"
    return f"{seconds // 60}m"


def _uncommitted(root):
    """How many own paths `git status` lists in an own store; None when git
    cannot say."""
    paths = existing_paths(root, OWN_PATHS)
    if not paths:
        return 0
    # never recurse into a submodule: its own config and attributes are
    # not pinned (F5's `diff --cached` takes --ignore-submodules=all too)
    r = _store_git(root, "status", "--porcelain", "-z",
                   "--ignore-submodules=all", "--", *paths,
                   timeout=GIT_TIMEOUT)
    if r is None or r.returncode != 0:
        return None
    # -z records are 'XY path'; a rename or copy is followed by its source
    # as a bare record, which is not counted
    n, recs = 0, iter(r.stdout.split("\0"))
    for rec in recs:
        if not rec:
            continue
        n += 1
        if "R" in rec[:2] or "C" in rec[:2]:
            next(recs, None)
    return n


def store_repo_checks(root, rs, full=True):
    """The store-repo findings as (tier, line), in format.md's table order;
    tier 'problem' or 'notice' (d1e9 D6). full=False is prime's set: the
    stat checks and one lock-free status, no host or remote reads. With
    full, the uncommitted check takes the store's lock with a 2 s wait, and
    is skipped, said on stderr, when the lock is busy."""
    out = []
    if rs.state == "missing":
        out.append(("problem", f"wi: WARNING store {root} records `repo: "
                    f"own` in {STORE_FILE} but has no .git; fix: restore the "
                    "store's repo from a backup (the work-items skill's "
                    "references/store-safety.md § Backing up, when present), "
                    "or run `wi init --no-track` to start new history"))
    if rs.state == "broken":
        out.append(("problem", f"wi: WARNING store {root} has a .git that is "
                    f"not a usable store repo: {rs.reason}; wi commits "
                    "nothing there (never `rm -rf` the .git unasked)"))
    if rs.state == "own":
        if full:
            try:
                with Lock(Path(root), timeout=2.0, commit=False):
                    n = _uncommitted(root)
            except (WiError, OSError) as e:
                # busy, or the lock file cannot be opened (a read-only store)
                n = None
                why = (" is locked by a write in progress"
                       if isinstance(e, WiError)
                       else f"'s lock cannot be taken ({e.strerror})")
                print(f"wi: note: store {root}{why}: uncommitted check "
                      "skipped", file=sys.stderr)
        else:
            n = _uncommitted(root)
        if n:
            out.append(("notice", f"wi: note: store {root} has {n} "
                        "uncommitted path(s) in its own repo; fix: "
                        "`wi commit`"))
        lock = os.path.join(rs.git_dir, "index.lock")
        try:
            age = time.time() - os.lstat(lock).st_mtime
        except OSError:
            age = None
        if age is not None and age > STALE_INDEX_LOCK:
            out.append(("problem", f"wi: WARNING {lock} is {_age(age)} old; "
                        "remove it only when no git process runs in the "
                        "store (never while a session works it)"))
        if full and rs.host is not None:
            out.extend(_host_checks(root, rs.host))
        if full:
            r = _store_git(root, "remote", timeout=GIT_TIMEOUT)
            names = (r.stdout.split() if r is not None and r.returncode == 0
                     else [])
            if names:
                # names only: a URL can carry a password
                out.append(("notice", f"wi: note: store {root}'s repo has a "
                            f"remote ({', '.join(names)}); a work-item store "
                            "repo is meant to be local (answer 232 a)"))
    # d1e9 F3: the two shapes `wi init --no-track` turns into an own store
    if rs.state == "unrecorded":
        out.append(("notice", f"wi: note: store {root} is its own git repo, "
                    "not set up by wi, so wi commits nothing there; fix: "
                    "`wi init --no-track` adopts it, history kept"))
    if (rs.state == "plain" and read_tracking(root) == "ignored"
            and not old_location(root) and shutil.which("git") is not None):
        out.append(("notice", f"wi: note: store {root} has no history of "
                    f"its own (tracking: ignored in {STORE_FILE}, no .git); "
                    "fix: `wi init --no-track` gives it its own local repo"))
    values = _store_key_values(root, "repo") or []
    if len(values) > 1:
        out.append(("problem", f"{root / STORE_FILE}: more than one repo: "
                    "line; fix: `wi init --no-track` rewrites it with one"))
    if values and values[0] != REPO_OWN:
        out.append(("problem", f"{root / STORE_FILE}: repo must be "
                    f"{REPO_OWN} (got '{values[0]}'); fix: `wi init "
                    "--no-track` rewrites it"))
    if rs.state == "old":
        out.append(("problem", f"wi: WARNING store {root} holds a git repo "
                    "at an old location; a store with its own repo lives at "
                    f"{DEFAULT_STORE}/: move the store ({MOVING_A_STORE})"))
    return out


def _host_checks(root, host):
    """An own store's host must ignore it and track nothing under it
    (b2df F-R3). Host reads use _git: they read the host, as custody does."""
    out = []
    try:
        rel = Path(os.path.realpath(root)).relative_to(
            os.path.realpath(host)).as_posix()
    except ValueError:
        return out
    # a rule in the store's own .gitignore does not count (_ignore_rule)
    if _ignore_rule(root, "--no-index", where=(host, rel)) is None:
        out.append(("problem", f"wi: WARNING the repo at {host} does not "
                    f"ignore store {root}, which is its own repo (the host "
                    "would commit it as a gitlink); fix: `wi init "
                    "--no-track` (it adds the line)"))
    r = _git(host, "-c", "core.fsmonitor=false", "ls-files", "-s", "--",
             f":(literal){rel}")
    if r is not None and r.returncode == 0 and r.stdout.strip():
        n = len(r.stdout.splitlines())
        out.append(("problem", f"wi: WARNING the repo at {host} tracks {n} "
                    f"path(s) under {rel} (mode 160000 is a gitlink); fix: "
                    f"`git -C {host} rm -r -q --cached -- {rel}` (the files "
                    "stay on disk), then commit in the host"))
    return out


# d1e9 F2: `wi commit`, the one store-commit verb (format.md § Committing
# the store). Other plugins' store commits go through it, so every commit
# into a store's repo is made under the store's lock.
COMMIT_DEFAULT_MESSAGE = "wi commit: outstanding changes"
COMMIT_DEADLINE = 5.0          # an own store's commit steps, all together
INDEX_LOCK_RETRIES = 3         # after the first try, 0.2 s apart
INDEX_LOCK_WAIT = 0.2
TRACKED_COMMIT_TIMEOUT = 60.0  # per call in a host or sidecar repo: its hooks
GC_TIMEOUT = 60.0
# the runner pins gc.auto=0 so no write starts a gc; `wi commit` runs gc on
# purpose, at git's documented default threshold
GC_AUTO = "6700"
# F-R1: used only when git has no identity (git var fails); never written
# to any config, and GIT_AUTHOR_* / GIT_COMMITTER_* still win
WI_IDENT = ("-c", "user.name=wi", "-c", "user.email=wi@localhost")
_IDENT_CACHE = {}


class CommitFailed(Exception):
    """A store commit that did not happen; str() is the one-line why."""


def _why(r):
    """git's first stderr line (else stdout's), cut to 200 characters."""
    lines = r.stderr.strip().splitlines() or r.stdout.strip().splitlines()
    return (lines[0] if lines else f"git exited {r.returncode}")[:200]


def _index_lock_conflict(r):
    """Another git process holds the index (LC_ALL=C in the runner)."""
    return (r.returncode != 0 and "index.lock" in r.stderr
            and "File exists" in r.stderr)


def _failed_why(r):
    """Why a commit step failed: for an index.lock conflict a reason of its
    own, naming the lock file whole (git's line, cut to 200 characters,
    could lose the cause behind a long store path); else _why."""
    if not _index_lock_conflict(r):
        return _why(r)
    m = re.search(r"'([^']*index\.lock)'", r.stderr)
    lock = m.group(1) if m else "the repo's index.lock"
    return (f"another git process holds {lock} (retried "
            f"{INDEX_LOCK_RETRIES} times; never deleted)")


def _own_runner(root, rs):
    """`run(*args)` for an own store's commit: the hardened store runner,
    every call bounded by what is left of one shared deadline (d1e9 D4').
    Raises CommitFailed when the deadline passes or git does not answer."""
    end = time.monotonic() + COMMIT_DEADLINE

    def run(*args):
        left = end - time.monotonic()
        if left <= 0:
            raise CommitFailed("timed out")
        r = _store_git(root, *args, timeout=left)
        if r is None:
            if shutil.which("git") is None:
                raise CommitFailed("git not found")
            lock = os.path.join(rs.git_dir or str(Path(root) / ".git"),
                                "index.lock")
            raise CommitFailed(f"timed out; if {lock} is left, remove it "
                               "only when no git process runs in the store")
        return r
    return run


# a caller's env (a host hook's GIT_COMMON_DIR, a shell's pathspec magic)
# never steers a tracked store's commit or ignore check to other files
TRACKED_SCRUB = STORE_GIT_SCRUB | {"GIT_LITERAL_PATHSPECS"}


def _tracked_runner(root, repo):
    """`run(*args)` for a store its host or sidecar repo `repo` tracks:
    plain _git (that repo's hooks and signing are its own rules, never
    bypassed), the caller's GIT_* steering scrubbed, no prompt, 60 s a
    call."""
    def run(*args):
        r = _git(root, *args, timeout=TRACKED_COMMIT_TIMEOUT,
                 extra_env={"GIT_TERMINAL_PROMPT": "0"}, scrub=TRACKED_SCRUB)
        if r is None:
            if shutil.which("git") is None:
                raise CommitFailed("git not found")
            d = _git(root, "rev-parse", "--absolute-git-dir",
                     scrub=TRACKED_SCRUB)
            gd = (d.stdout.strip() if d is not None and d.returncode == 0
                  and d.stdout.strip() else os.path.join(repo, ".git"))
            lock = os.path.join(gd, "index.lock")
            raise CommitFailed(f"timed out; if {lock} is left, remove it "
                               f"only when no git process runs in {repo}")
        return r
    return run


def _fallback_ident(root, run):
    """WI_IDENT when git has no author or committer identity, else (); asked
    once per process and store (F-R1)."""
    key = os.path.realpath(root)
    if key not in _IDENT_CACHE:
        _IDENT_CACHE[key] = next(
            (WI_IDENT for var in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT")
             if run("var", var).returncode != 0), ())
    return _IDENT_CACHE[key]


def _retrying(run, *args):
    """One git step, retried on an index.lock conflict, never deleting the
    lock file (F-R2)."""
    for attempt in range(INDEX_LOCK_RETRIES + 1):
        r = run(*args)
        if not _index_lock_conflict(r) or attempt == INDEX_LOCK_RETRIES:
            return r
        time.sleep(INDEX_LOCK_WAIT)
    return r


def _commit_own_paths(root, run, message, ident=(), candidates=OWN_PATHS,
                      sha=True, listed=False):
    """Stage and commit the candidates git can match (d1e9 D4 steps 2-5,
    D4'): the store's own paths, or a write's journal (F5). `add -A`,
    `diff --cached --quiet`, `commit -- <paths>`, all on one pathspec, so a
    file staged by hand outside it stays staged and out of the commit. The
    short sha (True with sha=False), or None when nothing changed. With
    `listed`, the candidates already passed existing_paths. Raises
    CommitFailed."""
    paths = (list(candidates) if listed
             else existing_paths(root, candidates, git=run))
    if not paths:
        return None
    spec = ("--", *paths)
    r = _retrying(run, "add", "-A", *spec)
    if r.returncode != 0:
        raise CommitFailed(_failed_why(r))
    r = run("diff", "--cached", "--quiet", "--no-ext-diff", "--no-textconv",
            "--ignore-submodules=all", *spec)
    if r.returncode == 0:
        return None
    if r.returncode != 1:
        raise CommitFailed(_why(r))
    r = _retrying(run, *ident, "commit", "-q", "-m", message, *spec)
    if r.returncode != 0:
        raise CommitFailed(_failed_why(r))
    if not sha:
        return True
    r = run("rev-parse", "--short", "HEAD")
    return r.stdout.strip() if r.returncode == 0 else "HEAD"


NOT_COMMITTED = ("wi: WARNING store not committed: {} (the change is saved; "
                 "`wi commit` commits it)")


def _per_change_state(root):
    """The StoreRepo a write's lock commits into, or None when the store
    does not record `repo: own`, so wi never starts committing into a repo
    no `init` set up (d1e9 D1): one read of store.yaml, no git. For a store
    that records it, the hardened validation (git's 2 s bound), run before
    the lock is taken. Never raises."""
    try:
        if not read_repo_own(root):
            return None
        if shutil.which("git") is None:
            return StoreRepo("unknown", "git not found")
        return store_repo_state(root)
    except Exception as e:  # a commit's trouble never fails the write
        return StoreRepo("unknown", f"{type(e).__name__}: {e}")


def _not_own_why(rs):
    """Why a store recording `repo: own` gets no per-change commit."""
    if rs.state == "missing":
        return f"`repo: own` is recorded in {STORE_FILE} but there is no .git"
    if rs.state == "broken":
        return rs.reason
    if rs.state == "old":
        return (f"a git repo at an old location: move the store "
                f"({MOVING_A_STORE})")
    return rs.reason or "git did not answer"


# what wi itself writes in a store: an item one level under items/, an
# archived one under archive/<year>/, a card record at
# cards/<id>/<N>/<file>.json, and the three store files. A name with a
# leading dot is never an item or a record, so a .gitattributes written
# there (an export aimed into the store) is never committed (d1e9 F5
# review); each cards/ segment but N takes the same rule
_JOURNAL_ITEM = re.compile(r"(items|archive/[0-9]{4})/[^/.][^/]*\.md"
                           r"|cards/[^/.][^/]*/[0-9]+/[^/.][^/]*\.json")


def _journal_own(rel):
    return rel in OWN_PATH_FILES or bool(_JOURNAL_ITEM.fullmatch(rel))


def _journal_paths(root):
    """The journal's store-relative POSIX paths that wi writes
    (_journal_own), in the order first written. A path is placed by its
    parent's real path, so an archive source, gone from disk, still
    resolves."""
    real = os.path.realpath(root)
    out = []
    for p in _JOURNAL:
        full = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(
            p))), os.path.basename(p))
        rel = os.path.relpath(full, real)
        if os.sep != "/":
            rel = rel.replace(os.sep, "/")
        if _journal_own(rel) and rel not in out:
            out.append(rel)
    return out


def _journal_message(verb, rels):
    """The per-change commit message (d1e9 D4): verb and item ids, never
    the item's text. One item: `wi <verb>: <id>`; several, and every
    archive: `wi <verb>: <n> item(s)` and a body of `- <id>` lines, sorted."""
    ids = sorted({os.path.splitext(r.rsplit("/", 1)[-1])[0] for r in rels
                  if r.startswith(("items/", "archive/")) and r.endswith(".md")})
    if not ids:
        return f"wi {verb}: store files"
    if len(ids) == 1 and verb != "archive":
        return f"wi {verb}: {ids[0]}"
    n = len(ids)
    return (f"wi {verb}: {n} item{'' if n == 1 else 's'}\n\n"
            + "\n".join(f"- {i}" for i in ids))


def _commit_journal(root, rs):
    """Commit what this lock's command wrote into an own store's repo
    (d1e9 D4, F5), under the lock, within one 5 s deadline. Nothing written
    (a claim already held, a refused write): no git call. Never raises: a
    failure prints NOT_COMMITTED and leaves the exit code and stdout as
    they are, since a caller seeing a failure could retry a write that
    landed."""
    try:
        rels = _journal_paths(root)
        if not rels:
            return
        if rs.state != "own":
            print(NOT_COMMITTED.format(_not_own_why(rs)), file=sys.stderr)
            return
        # an attribute file or nested repo that appeared since validation
        # would select a filter `add` runs: the same walk, again, no git
        unsafe = _unsafe_walk(root)
        if unsafe:
            print(NOT_COMMITTED.format(unsafe), file=sys.stderr)
            return
        run = _own_runner(root, rs)
        kept = existing_paths(root, rels, git=run)
        # a file wi wrote that git does not list is ignored by a rule (a
        # global excludesFile `*.md`): say so, never drop it silently
        ignored = [r for r in rels if r not in kept
                   and os.path.lexists(os.path.join(root, r))]
        if ignored:
            print(NOT_COMMITTED.format(f"{', '.join(ignored)} ignored by git "
                                       "(see `wi lint`)"), file=sys.stderr)
        if kept:
            _commit_own_paths(root, run,
                              _journal_message(_COMMAND[0], kept),
                              _fallback_ident(root, run), candidates=kept,
                              sha=False, listed=True)
    except CommitFailed as e:
        print(NOT_COMMITTED.format(e), file=sys.stderr)
    except Exception as e:  # never fail a write that landed
        print(NOT_COMMITTED.format(f"{type(e).__name__}: {e}"),
              file=sys.stderr)


def _gc_after_commit(root):
    """`git gc --auto` in an own store, in the foreground, after the lock is
    released, so a slow gc never holds other wi processes. A failure is
    one stderr line: the commit already stands."""
    r = _store_git(root, "-c", f"gc.auto={GC_AUTO}", "-c",
                   "gc.autoDetach=false", "gc", "--auto", "-q",
                   timeout=GC_TIMEOUT)
    if r is None or r.returncode != 0:
        why = "timed out" if r is None else _why(r)
        print(f"wi: WARNING git gc --auto in {root} did not finish: {why}",
              file=sys.stderr)


def _store_ignored(root, repo):
    """True when the repo holding a store without its own repo ignores it
    (`check-ignore` on the store's directory, as the old hand rule asked);
    raises CommitFailed when git cannot say."""
    real = os.path.realpath(root)
    r = _git(real, "check-ignore", "-q", real, scrub=TRACKED_SCRUB)
    if r is None or r.returncode not in (0, 1):
        why = "git did not answer" if r is None else _why(r)
        raise CommitFailed(f"cannot tell whether {repo} ignores the store: "
                           f"{why}")
    return r.returncode == 0


def _commit_refusal(root, rs):
    """Why `wi commit` refuses a store whose repo wi did not set up, or
    cannot trust (exit 1, nothing committed)."""
    if rs.state == "unrecorded":
        return (f"{root} is its own git repo, not set up by wi: "
                "`wi init --no-track` adopts it; nothing committed")
    if rs.state == "missing":
        return (f"store {root} records `repo: own` in {STORE_FILE} but has "
                "no .git; nothing committed")
    if rs.state == "broken":
        return (f"store {root} has a .git that is not a usable store repo: "
                f"{rs.reason}; nothing committed")
    return (f"store {root} holds a git repo at an old location: move "
            f"the store ({MOVING_A_STORE}); nothing committed")


def cmd_commit(args):
    """Commit the store's own paths into the repo that holds them, under the
    store's lock (d1e9 D5, D5'). Validation comes before the lock."""
    message = COMMIT_DEFAULT_MESSAGE if args.message is None else args.message
    if not message.strip():
        raise WiError(1, "the message is empty; nothing committed")
    for _, why in secret_findings(message):
        # never quote the message: it may hold the secret
        raise WiError(1, f"the message: {why}; reword it as path and key "
                         "and re-run; nothing committed")
    root = resolve_root(args.root)
    if shutil.which("git") is None:
        if os.path.lexists(root / ".git") or read_repo_own(root):
            # a store with history of its own: its changes stay uncommitted
            raise WiError(3, f"store {root} not committed: git not found")
        print(f"nothing to commit: {root} is in no git repo (git not found)")
        return 0
    rs = store_repo_state(root)
    try:
        if rs.state == "own":
            with Lock(root, commit=False):
                run = _own_runner(root, rs)
                sha = _commit_own_paths(root, run, message,
                                        _fallback_ident(root, run))
            if sha:
                _gc_after_commit(root)
        elif rs.state in ("plain", "dedicated"):
            repo = (root if rs.state == "dedicated"
                    else _store_repo(root, scrub=TRACKED_SCRUB))
            if repo is None:
                print(f"nothing to commit: {root} is in no git repo")
                return 0
            if read_tracking(root) == "ignored":
                print(f"nothing to commit: {root} is recorded git-ignored "
                      f"(tracking: ignored in {STORE_FILE})")
                return 0
            if rs.state == "plain" and _store_ignored(root, repo):
                print(f"nothing to commit: {root} is git-ignored by {repo}")
                return 0
            with Lock(root, commit=False):
                sha = _commit_own_paths(root, _tracked_runner(root, repo),
                                        message)
        elif rs.state == "unknown":
            raise CommitFailed("git did not answer in the store's repo")
        else:
            raise WiError(1, _commit_refusal(root, rs))
    except CommitFailed as e:
        raise WiError(3, f"store {root} not committed: {e}") from None
    print(f"committed {sha}" if sha else "nothing to commit")
    return 0


def read_raw(path):
    """Read without newline translation, so CRLF survives a rewrite. The one
    place an item file is decoded: a file that does not decode is a WiError
    naming it (the parse-error code), never a traceback, for every caller."""
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read()
    except UnicodeDecodeError as e:
        raise WiError(3, f"{path}: undecodable ({e.encoding}: {e.reason} "
                         f"at byte {e.start}); not an item file") from None


def atomic_write(path, text, create=False):
    """tmp+rename. With create=True the file must not exist yet: the tmp is
    moved into place by _move_no_clobber, which fails rather than replace a
    file that appeared since the caller looked (O_EXCL semantics, and the
    content still lands in one step). The tmp gets a fresh random name,
    created exclusively (mkstemp, O_EXCL), so a planted symlink is never
    written through and a stale tmp from a killed write is never in the
    way; its `<name>.tmp` prefix keeps the stale-reservation glob and the
    store's `*.tmp*` ignore matching it."""
    _atomic_write(path, text, create=create)


def atomic_write_bytes(path, data, create=False, keep_mode=False):
    """atomic_write for bytes; keep_mode copies an existing file's mode."""
    _atomic_write(path, data, create=create, keep_mode=keep_mode)


def _umask():
    mask = os.umask(0o022)
    os.umask(mask)
    return mask


def _atomic_write(path, data, create=False, keep_mode=False):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".tmp")
    tmp = Path(name)
    try:
        # mkstemp makes the file 0600; a plain create would honour the umask
        os.fchmod(fd, 0o666 & ~_umask())
        if isinstance(data, bytes):
            fh = open(fd, "wb")
        else:
            fh = open(fd, "w", encoding="utf-8", newline="")
    except BaseException:
        os.close(fd)
        tmp.unlink()
        raise
    try:
        with fh:
            fh.write(data)
        if keep_mode and os.path.isfile(path) and not os.path.islink(path):
            shutil.copymode(path, tmp)
    except BaseException:
        tmp.unlink()
        raise
    if not create:
        try:
            os.replace(tmp, path)
        except BaseException:
            tmp.unlink()
            raise
        _journal_write(path)
        return
    try:
        _move_no_clobber(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def _refuse_existing(dst):
    return WiError(3, f"refusing to overwrite existing {dst}; nothing written for it")


def _half_moved(a, b):
    """True when `a` and `b` are two hard links to one file — the state a
    kill between link and unlink leaves: same device and inode (the last
    component not followed), at least two links, and parent directories
    that resolve to different directories. One directory entry reached by
    two paths (a symlinked or bind-mounted directory) fails the last two
    tests: unlinking either path would delete the only copy."""
    try:
        sa, sb = os.lstat(a), os.lstat(b)
        pa, pb = (os.path.realpath(os.path.dirname(os.path.abspath(x)))
                  for x in (a, b))
    except OSError:
        return False
    return ((sa.st_dev, sa.st_ino) == (sb.st_dev, sb.st_ino)
            and sa.st_nlink >= 2 and pa != pb)


def _move_no_clobber(src, dst):
    """Move `src` to `dst`, never replacing an existing `dst` (WiError 3).

    A hard link is the atomic no-clobber rename. A `dst` that already is
    `src` (a kill between link and unlink) is the move half done: it is
    finished by unlinking `src`. Where the filesystem has no hard links,
    the name is reserved with O_EXCL and `src` is renamed over that
    empty reservation, so the content still lands in one step; if the rename
    fails, the reservation is removed while it is still ours (same inode,
    size 0) and WiError is raised — never a half-written file under `dst`.
    On any error `src` is left in place."""
    try:
        os.link(src, dst)
        linked = True
    except FileExistsError:
        if not _half_moved(src, dst):
            raise _refuse_existing(dst) from None
        linked = True  # linked by an earlier, killed move
    except OSError:
        linked = False  # no hard links on this filesystem: reserve the name
    if linked:
        _journal_write(dst)  # dst holds the content from here (F5)
        try:
            os.unlink(src)
        except OSError as e:
            raise WiError(3, f"{dst} written but {src} not removed: {e}") from None
        return
    try:
        fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        raise _refuse_existing(dst) from None
    except OSError as e:
        raise WiError(3, f"cannot create {dst}: {e}") from None
    try:
        reserved = os.fstat(fd)
    finally:
        os.close(fd)
    try:
        os.replace(src, dst)
        _journal_write(dst)
    except OSError as e:
        try:
            now = os.lstat(dst)
            if (now.st_dev, now.st_ino) == (reserved.st_dev, reserved.st_ino) \
                    and now.st_size == 0:
                os.unlink(dst)
        except OSError:
            pass
        raise WiError(3, f"cannot write {dst}: {e}; nothing written for it") from None


def taken_ids(root, items):
    """Every id a new item must not take: the loaded items' ids and the file
    stems under items/ and archive/ (a stray file whose stem differs from its
    id still owns its filename)."""
    return {it.id for it in items} | {p.stem for p in item_paths(root, archived=True)}


def save_item(root, item):
    save_items(root, [item])


def save_items(root, items):
    """Render every item before writing any, so a value the writer rejects
    (see _front_one_line) leaves the whole batch unwritten.

    An item without a path is new: it is written only to a file that does
    not exist (anywhere in items/ or archive/) and that no other item in the
    batch claims — a new item never replaces a file nobody read, whatever
    id its caller generated. Any such conflict leaves the batch unwritten."""
    staged, seen = [], set()
    archived = {p.stem for p in (root / "archive").glob("*/*.md")} \
        if (root / "archive").is_dir() else set()
    for item in items:
        new = item.path is None
        path = item.path or root / "items" / (item.id + ".md")
        if path in seen:
            raise WiError(3, f"{item.id}: two items in one write target {path}; "
                             "nothing written")
        seen.add(path)
        if new and (path.exists() or item.id in archived):
            raise WiError(3, f"{item.id}: refusing to overwrite existing item "
                             f"file for a new item; nothing written")
        try:
            staged.append((item, path, item.render(), new))
        except WiError as e:
            # name the item; its path only when it is already on disk
            where = f"{item.id} ({item.path})" if item.path else item.id
            raise WiError(e.code, f"{where}: {e}") from None
    for item, path, text, new in staged:
        atomic_write(path, text, create=new)
        item.path = path


def item_paths(root, archived=False):
    paths = sorted((root / "items").glob("*.md"))
    if archived and (root / "archive").is_dir():
        paths += sorted((root / "archive").glob("*/*.md"))
    return paths


STALE_RESERVATION = ("empty file: a name reserved by a write whose content "
                     "never landed (killed mid-write, unless one is in "
                     "flight this instant)")
_warned_stale = set()


def stale_reservation_fix(path):
    """How to clear an empty item file (see STALE_RESERVATION). The
    no-hard-link create writes its content to `<name>.tmp<pid>` first, so a
    tmp beside the file still holds it; otherwise nothing was written there
    (an interrupted archive left its source in items/)."""
    tmps = sorted(path.parent.glob(glob.escape(path.name) + ".tmp*"))
    if tmps:
        return (f"its content is in {tmps[0]}: "
                f"mv {shlex.quote(str(tmps[0]))} {shlex.quote(str(path))}")
    return f"nothing was written to it: rm {shlex.quote(str(path))}"


def load_all(root, archived=False):
    """Every item under items/ (and archive/). An empty file is a stale
    reservation, not an item: it is skipped with a warning naming it, so
    one interrupted write does not stop every command; `wi lint` reports it
    with the fix. Its name stays taken (taken_ids reads the file stems)."""
    return load_paths(item_paths(root, archived))


def load_paths(paths, lenient=False):
    """Parse each path. `lenient`: a file that does not read or parse is
    skipped with a one-time warning, as if absent (DepIndex's archive read,
    so one bad archived file cannot stop commands that never needed it)."""
    items = []
    for path in paths:
        try:
            text = read_raw(path)
            item = Item.parse(text, path) if text else None
        except (WiError, OSError) as e:
            if not lenient:
                raise
            if path not in _warned_stale:
                _warned_stale.add(path)
                print(f"wi: skipping {path}: unreadable ({e}); "
                      "treated as absent", file=sys.stderr)
            continue
        if not text:
            if path not in _warned_stale:
                _warned_stale.add(path)
                print(f"wi: skipping {path}: {STALE_RESERVATION}; "
                      "`wi lint` names the fix", file=sys.stderr)
            continue
        items.append(item)
    return items


def resolve_id(items, ref):
    exact = [it for it in items if it.id == ref or it.get("alias") == ref]
    if exact:
        return exact[0]
    matches = [it for it in items if it.id.startswith(ref)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise AmbiguousId(2, f"ambiguous id '{ref}': " + ", ".join(it.id for it in matches))
    raise WiError(2, f"no item matching '{ref}'")


def load_item_anywhere(root, ref):
    return resolve_id(load_all(root, archived=True), ref)


# ── Readiness and ranking ───────────────────────────────────────────────────

class DepIndex:
    """The id → item lookup every readiness question resolves deps against:
    the command's loaded items first, then archive/ — an archived item is
    judged by its status like any other, so a done or dropped dep stays met
    after `wi archive`. The archive is read once per command, and only when a
    dep is not among the loaded items (a store whose deps all live in items/
    never reads it). `in`/`[]` see only the loaded items; `get` sees both."""

    def __init__(self, root, items, archived=False):
        """`archived`: `items` already holds archive/ (nothing more to read).
        The first entry for an id wins — load_all lists items/ before
        archive/, and the items/ copy is the current one."""
        self.items = {}
        for it in items:
            self.items.setdefault(it.id, it)
        self.root, self._archive = root, ({} if archived else None)

    def __contains__(self, key):
        return key in self.items

    def __getitem__(self, key):
        return self.items[key]

    def get(self, key, default=None):
        if key in self.items:
            return self.items[key]
        if self._archive is None:
            loaded = set(self.items)
            self._archive = {}
            arch = self.root / "archive" if self.root is not None else None
            if arch is not None and arch.is_dir():
                for it in load_paths(sorted(arch.glob("*/*.md")),
                                     lenient=True):
                    if it.id not in loaded:
                        self._archive.setdefault(it.id, it)
        return self._archive.get(key, default)


def dep_resolved(dep, by_id):
    if dep.startswith("ext:"):
        return False
    target = by_id.get(dep)
    if target is None:
        return False
    return (target.get("status") in ("done", "dropped")
            or (target.get("status") == "doing"
                and target.get("stage") in ("uat", "uat_feedback")))


def unmet_deps(item, by_id):
    """The item's deps that do not resolve (dep_resolved): the one rule the
    ready queue (is_ready: next, ls --ready, prime), `claim` and `show --json`
    apply, over a DepIndex (loaded items, then archive/)."""
    return [d for d in item.get("deps", []) if not dep_resolved(d, by_id)]


def is_ready(item, by_id):
    if item.get("status") != "todo":
        return False
    return not unmet_deps(item, by_id)


def rank_ready(items):
    return sorted(items, key=lambda it: (it.get("priority", 2), it.get("created", ""), it.id))


def split_by_status(items):
    open_items = {"doing": [], "blocked": [], "todo": [], "parked": [],
                  "grooming": []}
    closed = []
    for it in items:
        st = it.get("status")
        (open_items[st] if st in open_items else closed).append(it)
    return open_items, closed


def pipeline_queues(items, by_id):
    """backlog.py next-work order: testing → review → in_progress →
    uat_feedback → ready todo (bugs first). uat waits for a human."""
    queues = {q: [] for q in ("testing", "review", "in_progress", "uat_feedback", "todo")}
    for it in items:
        st, stage = it.get("status"), it.get("stage")
        if st == "doing":
            q = {"testing": "testing", "review": "review",
                 "uat_feedback": "uat_feedback"}.get(stage)
            if q is None and stage != "uat":
                q = "in_progress"
            if q:
                queues[q].append(it)
        elif st == "todo" and is_ready(it, by_id):
            queues["todo"].append(it)

    def key(it):
        return (it.get("priority", 2), it.get("alias") or "~", it.id)

    ordered = []
    for q in ("testing", "review", "in_progress", "uat_feedback"):
        ordered += [(q, it) for it in sorted(queues[q], key=key)]
    todo = sorted(queues["todo"], key=lambda it: (it.get("type") != "bug",) + key(it))
    ordered += [("todo", it) for it in todo]
    return ordered


def item_json(item, by_id=None):
    rec = {k: item.meta.get(k) for k in FIELD_ORDER}
    rec["summary"] = item.summary()
    rec["handoff"] = item.handoff()
    if by_id is not None:
        rec["ready"] = is_ready(item, by_id)
    return rec


def title_cell(title, name):
    """What a text row prints for an item's title: `[<name>] <title>` when
    it has a short display name, else the title alone. One cell, so no
    `--plain` column moves (a name holds no tab: the writer refuses one)."""
    if isinstance(name, str) and name.strip():
        return f"[{name.strip()}] {title}"
    return title


def item_title(item):
    return title_cell(item.get("title"), item.get("short_display_name"))


# ── Commands ────────────────────────────────────────────────────────────────

# Host-.gitignore spellings that ignore the whole .claude-sandbox/ dir.
SANDBOX_IGNORES = ("/.claude-sandbox/", "/.claude-sandbox",
                   ".claude-sandbox/", ".claude-sandbox")


def sandbox_shape(root):
    """Classify a `.claude-sandbox/work` store (an old location, 5f46) per
    agents/decisions/0002: ('private'|'sidecar'|'ignored', repo_dir), or
    (None, None) for `.work-items/`, `.work/` and other non-sandbox stores.
    private = host repo tracks config + work; sidecar = a git repo at
    .claude-sandbox/.git owns the store; ignored = the host .gitignore
    already whole-dir-ignores .claude-sandbox/."""
    sandbox = root.absolute().parent
    if sandbox.name != ".claude-sandbox":
        return None, None
    repo = sandbox.parent
    if (sandbox / ".git").exists():
        return "sidecar", repo
    host_gi = repo / ".gitignore"
    if host_gi.is_file():
        lines = {ln.strip() for ln in host_gi.read_text().splitlines()}
        if lines.intersection(SANDBOX_IGNORES):
            return "ignored", repo
    return "private", repo


def _interactive():
    return sys.stdin.isatty() and sys.stdout.isatty()


def choose_tracking(inp, out, sidecar=False):
    """Ask the init menu and return the choice. Outside a sidecar layout it
    returns 'tracked' or 'ignored', and Enter, or end of input, takes the
    default, git-ignored. In a sidecar layout (3c06) git-ignored is refused,
    so tracked is the default and git-ignored is shown but not taken: the
    menu returns only 'tracked' there."""
    default = "tracked" if sidecar else "ignored"
    if sidecar:
        out.write("wi init: should git track this work-item store?\n"
                  "  1) tracked      items are committed with the sidecar "
                  "repo [default]\n"
                  "  2) git-ignored  refused here: in a sidecar layout new "
                  "items would land in no repo\n")
    else:
        out.write("wi init: should git track this work-item store?\n"
                  "  1) tracked      items are committed with the repo\n"
                  "  2) git-ignored  the repo ignores the store, which keeps "
                  "its own local history [default]\n")
    prompt = f"choose 1 or 2 [{1 if sidecar else 2}]: "
    while True:
        out.write(prompt)
        out.flush()
        line = inp.readline()
        if not line:
            out.write("\n")
            return default
        answer = line.strip().lower()
        if answer == "":
            return default
        if answer in ("1", "t", "track", "tracked"):
            return "tracked"
        if answer in ("2", "i", "ignore", "ignored", "g", "git-ignored",
                      "n", "no-track"):
            if not sidecar:
                return "ignored"
            out.write("git-ignored is refused in a sidecar layout; choose "
                      "1, or Ctrl-C to stop\n")
            continue
        out.write(f"not a choice: {line.strip()!r}\n")


def _store_repo(root, scrub=()):
    """The top of the git repo that holds the store, or None outside git.
    A sidecar store's repo is .claude-sandbox/ itself. scrub: more GIT_*
    names to drop (`wi commit` drops the caller's steering)."""
    shape, _ = sandbox_shape(root)
    if shape == "sidecar":
        return root.absolute().parent
    r = _git(root, "rev-parse", "--show-toplevel", scrub=scrub)
    if r is None or r.returncode != 0 or not r.stdout.strip():
        return None
    return Path(r.stdout.strip())


def _gitignore_escape(rel):
    """A path as a literal .gitignore pattern: glob characters escaped."""
    return re.sub(r"([\\\[*?])", r"\\\1", rel)


def append_gitignore_line(gi, line):
    """Append one line to a .gitignore, atomically and byte-exact: the file
    is created when missing, its line ending (CRLF or LF) is kept, a newline
    is added first when its last line has none, and its mode is kept. A
    symlinked .gitignore is never written through. (ok, message)."""
    if gi.is_symlink():
        return False, f"{gi} is a symlink: no line added; add {line} by hand"
    try:
        data = gi.read_bytes() if gi.exists() else b""
    except OSError as e:
        return False, (f"{gi} unreadable ({e.strerror}): no line added; add "
                       f"{line} by hand")
    nl = b"\r\n" if b"\r\n" in data else b"\n"
    if data and not data.endswith(b"\n"):
        data += nl
    try:
        atomic_write_bytes(gi, data + line.encode("utf-8", "surrogateescape")
                           + nl, keep_mode=True)
    except (OSError, WiError) as e:
        return False, f"{gi} not written ({e}): add {line} by hand"
    return True, f"added {line} to {gi}"


def _gitignore_lines(gi):
    """A .gitignore's lines, stripped; non-UTF-8 bytes kept as surrogates."""
    try:
        data = gi.read_bytes() if gi.is_file() else b""
    except OSError:
        return []
    return [ln.strip() for ln in
            data.decode("utf-8", "surrogateescape").splitlines()]


_FROM_STORE = object()   # ensure_ignored: the repo found from the store


def ensure_ignored(root, repo=_FROM_STORE):
    """Make git ignore the store: add its dir to its repo's root .gitignore
    unless git already ignores it from one of the repo's .gitignore files.
    (ok, message); ok False means the store may not be ignored. repo: the
    repo around the store (None outside git), which `init` passes for a
    store getting its own repo (d1e9 D3 step 4: _host_repo, asked from the
    store's parent); by default, the repo that holds the store."""
    if repo is _FROM_STORE:
        repo = _store_repo(root)
    if repo is None:
        return True, "not in a git repo: no .gitignore written"
    try:
        rel = root.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return False, (f"{root} is outside the repo at {repo}: no "
                       ".gitignore written")
    if rel == ".":
        return False, "store is the repo root: no .gitignore written"
    gi = repo / ".gitignore"
    esc = _gitignore_escape(rel)
    line = f"/{esc}/"
    if gi.is_symlink():
        return False, f"{gi} is a symlink: no line added; add {line} by hand"
    # git decides (a negation after a literal line un-ignores it); a rule
    # only in info/exclude or an excludesFile does not travel with the
    # repo, so the line is still added for those
    rule = _ignore_rule(root, "--no-index", where=(repo, rel))
    if rule is False:
        # git unavailable: the literal lines are all there is to go on
        for ln in _gitignore_lines(gi):
            if ln in {f"/{esc}/", f"/{esc}", f"{esc}/", esc}:
                return True, (f"{gi} already ignores the store ('{ln}'): no "
                              "line added")
            if rel == ".claude-sandbox/work" and ln in SANDBOX_IGNORES:
                return True, (f"{gi} already ignores .claude-sandbox/ as a "
                              f"whole ('{ln}'), which covers the store: no "
                              "line added")
    elif rule:
        src, lineno, pattern = rule
        if not os.path.isabs(src) and Path(src).name == ".gitignore":
            if (rel == ".claude-sandbox/work"
                    and pattern.strip() in SANDBOX_IGNORES):
                return True, (f"{src}:{lineno} already ignores "
                              f".claude-sandbox/ as a whole ('{pattern}'), "
                              "which covers the store: no line added")
            return True, (f"already ignored by git ({src}:{lineno} "
                          f"'{pattern}'): no line added")
    ok, msg = append_gitignore_line(gi, line)
    if not ok:
        return ok, msg
    after = _ignore_rule(root, "--no-index", where=(repo, rel))
    if after is not False and not after:
        return False, f"{line} did not make git ignore the store"
    return True, msg


def _store_outside_repo(root):
    """The refusal when a symlink on the store's path that is repo content
    (it sits inside a git repo) points outside that repo, else None. A link
    above every repo (a /home/claude -> /home/rt style alias) is left
    alone."""
    p = Path(os.path.abspath(root))
    for comp in (p, *p.parents):
        if not comp.is_symlink():
            continue
        r = _git(comp.parent, "rev-parse", "--show-toplevel")
        if r is None or r.returncode != 0 or not r.stdout.strip():
            continue
        top = os.path.realpath(r.stdout.strip())
        target = os.path.realpath(comp)
        if target != top and not target.startswith(top + os.sep):
            return (f"{comp} is a symlink to {target}, outside the repo at "
                    f"{top}: refusing to init there; nothing written")
    return None


def _create_if_absent(path, text):
    """Write a new file atomically; an existing path, a symlink included,
    is left alone."""
    if os.path.lexists(path):
        return
    try:
        atomic_write(path, text, create=True)
    except WiError:
        if not os.path.lexists(path):
            raise
        # appeared since the check: it is there, leave it


# d1e9 F3: `init` and a git-ignored store's own repo (format.md § Store
# tracking, § The store's own repo). Every git call init makes, plain _git
# and the store runner alike, runs without a caller's steering: a host
# hook's GIT_DIR, GIT_COMMON_DIR or GIT_INDEX_FILE, pathspec magic, or a
# template directory for `git init`.
INIT_SCRUB = TRACKED_SCRUB | {"GIT_TEMPLATE_DIR"}
# local config an own store's repo gets, so a hand-run git there (the hand
# commit form in store-safety.md) runs no hook or fsmonitor either
STORE_REPO_CONFIG = (("core.hooksPath", "/dev/null"),
                     ("core.fsmonitor", "false"))
INIT_BRANCH = "refs/heads/main"
OWN_PATH_FILES = ("README.md", STORE_FILE, ".gitignore")
STORE_README = ("# Work items\n\nOne markdown file per item, managed by `wi` "
                "(the work-items plugin's skills/work-items).\nStart with "
                "`wi prime`, then `wi show <id> --brief` for the item you "
                "will work.\nFormat: the work-items plugin's "
                "skills/work-items/references/format.md\n")
STORE_GITIGNORE = ".lock\n*.tmp*\n"
_DEDICATED = object()   # _own_repo_check: a store at the top of its own repo
# what a store's directory may hold before `git init` makes it a repo
STORE_ENTRIES = ("items", "archive", "cards", "README.md", STORE_FILE,
                 ".gitignore", ".lock")
# the operator's ruling on d1e9 F3: init refuses while an old-location store
# is not yet moved; this flag is for a project whose `.work/` or
# `.claude-sandbox/work/` is its own, not a work-item store left behind
ALLOW_OLD_FLAG = "--allow-old-location"
OLD_LOCATIONS = STORE_LOCATIONS[1:]


@contextlib.contextmanager
def _env_without(names):
    """os.environ without `names` for the block, put back after it."""
    saved = {k: os.environ.pop(k) for k in list(os.environ) if k in names}
    try:
        yield
    finally:
        os.environ.update(saved)


def _is_own_path(path):
    """True for a store-relative path among the store's own paths."""
    return path in OWN_PATH_FILES or path.startswith(
        ("items/", "archive/", "cards/"))


def _foreign_entry(root):
    """The first name at the store's top that is not a store file (nor the
    lock or a write's tmp file), else None: `git init` there would make a
    repo of whatever else the directory holds."""
    try:
        names = sorted(os.listdir(root))
    except OSError:
        return None
    return next((n for n in names if n not in STORE_ENTRIES
                 and not fnmatch.fnmatchcase(n, "*.tmp*")), None)


def _unmigrated_stores(root):
    """The old locations init refuses at or beside the root (the operator's
    ruling on d1e9 F3): the root itself when it is an old location, a new
    store included, and any old location holding items/ beside the top of
    the repo around the root, or beside the root's own parent directory. A
    store beside counts only by its items/ directory, never by name alone or
    by an ignore line naming it."""
    real = os.path.realpath(root)
    found = {}
    if old_location(root):
        # made or kept there: a new store too, which the next init refuses
        found[real] = Path(root)
    bases = []
    host = _host_repo(root)
    if isinstance(host, Path):
        bases.append(host)
    parent = _store_parent(Path(real))
    if parent is not None:
        bases.append(parent)
    for base in bases:
        for rel in OLD_LOCATIONS:
            cand = Path(base) / rel
            if (cand / "items").is_dir():
                found.setdefault(os.path.realpath(cand), cand)
    return list(found.values())


def _old_location_refusal(root, stores, named):
    """init's refusal while an old-location store is not yet moved."""
    where = ", ".join(str(s) for s in stores)
    export = ("" if named else "; then change any WORK_ITEMS_ROOT export "
              "that names the old path")
    return (f"{where}: an old store location ({', '.join(OLD_LOCATIONS)}); "
            "init makes no store at one, keeps none there, and makes none "
            f"beside one holding items/: use {DEFAULT_STORE}/, moving the old "
            f"store first if there is one ({MOVING_A_STORE}){export}; nothing "
            f"written. Pass {ALLOW_OLD_FLAG} only when the operator keeps the "
            "store there, or the directory is this project's own and not a "
            "work-item store")


def _own_repo_check(root):
    """d1e9 D3 step 2: refuse (WiError 1, nothing written) a store that may
    not get its own repo; else the repo around it (None outside git).
    _DEDICATED for a store at the top of a repo with no repo around it and
    no `repo: own` recorded, which keeps the repo-root refusal it had."""
    host = _host_repo(root)
    if host is HOST_UNKNOWN:
        raise WiError(1, f"git did not say whether a repo is around {root}; "
                         "nothing written")
    adopt = "refusing to adopt it as a store repo; nothing written"
    if os.path.lexists(root / ".git"):
        git_dir, common, reason = _validate_store_git(root)
        if reason:
            raise WiError(1, f"{root} has a .git that is not a usable store "
                             f"repo: {reason}; {adopt}")
        if git_dir is None:
            raise WiError(1, f"git did not answer in {root}'s repo; nothing "
                             "written")
        if host is None and not read_repo_own(root):
            return _DEDICATED
        reason = _unsafe_path(root, git_dir, common)
        if reason:
            raise WiError(1, f"{root}: {reason}; {adopt}")
        r = _store_git(root, "ls-files", "-z")
        if r is None or r.returncode != 0:
            why = "git did not answer" if r is None else _why(r)
            raise WiError(1, f"cannot list the files {root}'s repo tracks "
                             f"({why}); {adopt}")
        listed = r.stdout.split("\0")
        # the commit HEAD names too: a file removed from the index only
        r = _store_git(root, "rev-parse", "-q", "--verify", "HEAD^{commit}")
        if r is not None and r.returncode == 0:
            r = _store_git(root, "ls-tree", "-r", "-z", "--name-only", "HEAD")
            if r is None or r.returncode != 0:
                why = "git did not answer" if r is None else _why(r)
                raise WiError(1, f"cannot list the files {root}'s HEAD holds "
                                 f"({why}); {adopt}")
            listed += r.stdout.split("\0")
        other = next((p for p in listed if p and not _is_own_path(p)), None)
        if other is not None:
            raise WiError(1, f"{root} is a git repo holding other files "
                             f"({other}): {adopt}")
        # an include in its own config can set core.hooksPath over the
        # /dev/null wi writes, for a hand-run git there; key names print
        # lowercased (includeIf is includeif)
        r = _store_git(root, "config", "--local", "--get-regexp",
                       r"^include(if\..*)?\.path$")
        if r is None or r.returncode not in (0, 1):
            why = "git did not answer" if r is None else _why(r)
            raise WiError(1, f"cannot read {root}'s git config ({why}); "
                             f"{adopt}")
        if r.returncode == 0 and r.stdout.strip():
            raise WiError(1, f"{root}'s git config includes another file "
                             f"({r.stdout.split()[0]}), which can set its "
                             f"hooks; remove it: {adopt}")
    elif all(os.path.isdir(root / d) for d in ("objects", "refs")) \
            and os.path.isfile(root / "HEAD"):
        raise WiError(1, f"{root} is a git directory, not a store; nothing "
                         "written")
    else:
        other = _foreign_entry(root)
        if other is not None:
            raise WiError(1, f"{root} holds {other}, which is not a store "
                             "file: refusing to give it its own repo; "
                             "nothing written")
        reason = _unsafe_walk(root)
        if reason:
            raise WiError(1, f"{root}: {reason}; refusing to give it its own "
                             "repo; nothing written")
    if host is not None:
        try:
            rel = Path(os.path.realpath(root)).relative_to(
                os.path.realpath(host)).as_posix()
        except ValueError:
            rel = None
        if rel:
            r = _git(host, "-c", "core.fsmonitor=false", "ls-files", "-z",
                     "--", f":(literal){rel}")
            if r is None or r.returncode != 0:
                why = "git did not answer" if r is None else _why(r)
                raise WiError(1, f"cannot tell whether the repo at {host} "
                                 f"tracks files under {rel} ({why}); "
                                 "nothing written")
            n = len([p for p in r.stdout.split("\0") if p])
            if n:
                raise WiError(1, f"the host repo at {host} tracks {n} "
                                 f"path(s) under {rel}: untrack them first "
                                 f"({MOVING_A_STORE}); nothing written")
    return host


def _track_refusal(root):
    """`--track` on a store with its own valid repo inside a host: the host
    would commit a gitlink (d1e9 D3). None when it may be tracked."""
    if old_location(root) or not os.path.lexists(root / ".git"):
        return None
    git_dir, _, reason = _validate_store_git(root)
    if reason or git_dir is None or not isinstance(_host_repo(root), Path):
        return None
    return (f"{root} is its own git repo; the host cannot track it (that "
            "commits a gitlink, mode 160000): use `wi init --no-track`; "
            "nothing written")


def _set_up_store_repo(root, adopt):
    """D3 step 5: a new repo (`git init` with an empty template, so no
    sample hooks; HEAD on main), or an existing one adopted as it is; both
    get STORE_REPO_CONFIG. Every call through the store runner. None on
    success, else why not."""
    steps = [] if adopt else [("init", "-q", "--template="),
                              ("symbolic-ref", "HEAD", INIT_BRANCH)]
    steps += [("config", key, value) for key, value in STORE_REPO_CONFIG]
    for args in steps:
        r = _store_git(root, *args)
        if r is None:
            return ("git not found" if shutil.which("git") is None
                    else "git did not answer")
        if r.returncode != 0:
            return _why(r)
    # what a hand-run git there resolves, read without the -c pins: an
    # include, an includeIf or a worktree config (extensions.worktreeConfig)
    # can set either key over the value just written
    for key, want in STORE_REPO_CONFIG:
        r = _store_git(root, "config", "--get", key, pins=False)
        got = r.stdout.strip() if r is not None and r.returncode == 0 else None
        if got != want:
            return (f"{key} resolves to {got!r} for a hand-run git there, not "
                    f"{want!r} (an include, includeIf or worktree config "
                    "sets it); remove that setting")
    git_dir, common, reason = _validate_store_git(root)
    if reason or git_dir is None:
        return reason or "git did not answer"
    return None


def _init_own(root, host, defaulted):
    """D3 steps 3-7, under the store's lock: the store files, the host
    ignore line (before any `git init`, F-R4), the repo, the record, then
    the first commit through `wi commit`'s own-store path."""
    adopt = os.path.lexists(root / ".git")
    (root / "items").mkdir(parents=True, exist_ok=True)
    # init commits by itself, every own path, so its lock commits nothing
    with Lock(root, commit=False):
        if os.path.lexists(root / ".git") != adopt:
            # a .git came or went while init waited for the lock: check again
            host = _own_repo_check(root)
            if host is _DEDICATED:
                raise WiError(1, f"{root} became the top of its own repo "
                                 "while init waited; run it again")
            adopt = not adopt
        _create_if_absent(root / "README.md", STORE_README)
        _create_if_absent(root / ".gitignore", STORE_GITIGNORE)
        ok, msg = ensure_ignored(root, host)
        if not ok:
            print(f"wi: WARNING {msg}; own repo not set up and tracking not "
                  "recorded (run `wi init --no-track` again once that is "
                  "fixed)", file=sys.stderr)
            print(f"created {root}; tracking not recorded")
            return 1
        print(msg)
        why = _set_up_store_repo(root, adopt)
        if why:
            print(f"wi: WARNING own repo not set up: {why}; tracking not "
                  "recorded (a rerun of `wi init --no-track` is safe)",
                  file=sys.stderr)
            print(f"created {root}; own repo not set up; tracking not "
                  "recorded")
            return 1
        print(f"own repo: {'adopted' if adopt else 'created'} "
              f"{root / '.git'}"
              + (" (its history kept)" if adopt else " (branch main)"))
        write_tracking(root, "tracked", repo=REPO_OWN)
        # 8805 F3: outside any git repo there is no host to ignore it
        around = ("no repo is around the store; it keeps its own local "
                  "history" if host is None else "the repo around the store "
                  "ignores it, and it keeps its own local history")
        print(f"tracking: tracked, repo: {REPO_OWN} (recorded in "
              f"{root / STORE_FILE}): {around}")
        n = len(item_paths(root, archived=True))
        message = (f"wi init: adopted {n} item{'' if n == 1 else 's'}"
                   if n or adopt else "wi init: store created")
        run = _own_runner(root, store_repo_state(root))
        try:
            sha = _commit_own_paths(root, run, message,
                                    _fallback_ident(root, run))
            print(f"committed {sha} ({message})" if sha
                  else "nothing to commit")
        except CommitFailed as e:
            print(NOT_COMMITTED.format(e), file=sys.stderr)
    if defaulted and host is None:
        print(f"wi: WARNING no terminal and no --track/--no-track: created "
              f"{root} with its own local repo (no git repo is around it)",
              file=sys.stderr)
    elif defaulted:
        print(f"wi: WARNING no terminal and no --track/--no-track: created "
              f"{root} as a git-ignored store with its own local repo. To "
              "have the repo around it track it instead, the store's .git "
              "must go first (`wi init --track` refuses a store with its "
              "own repo): ask the operator", file=sys.stderr)
    print(f"initialised {root}")
    return 0


def cmd_init(args):
    with _env_without(INIT_SCRUB):
        return _init(args)


def _init(args):
    for notice in env_notices():
        print(notice, file=sys.stderr)
    refusal = worktree_init_refusal() if not args.root else None
    if refusal:
        # 5f46: a store made here would be a stray copy no other session sees
        print(refusal, file=sys.stderr)
        return 1
    root = resolve_root(args.root, must_exist=False)
    refusal = _store_outside_repo(root)
    if refusal:
        raise WiError(1, refusal)
    if args.no_track and sandbox_shape(root)[0] == "sidecar":
        # 3c06, before the old-location refusal, so it keeps its message
        raise WiError(1, f"{root} is {SIDECAR_NO_REPO}: a git-ignored store "
                         "there lands in no repo; nothing written (use "
                         "`wi init --track`)")
    old = _unmigrated_stores(root)
    if old and not args.allow_old_location:
        # the operator's ruling: move an old-location store before any
        # init, the no-flag note included; no deprecation line besides
        raise WiError(1, _old_location_refusal(root, old, bool(args.root)))
    if args.allow_old_location and not old:
        raise WiError(1, f"{ALLOW_OLD_FLAG} overrides only a root at an old "
                         f"location ({', '.join(OLD_LOCATIONS)}), or one "
                         "holding items/ beside the root, and "
                         f"{root} has neither; nothing written")
    for notice in location_notices(root):
        print(notice, file=sys.stderr)
    existed = (root / "items").is_dir()
    recorded = read_tracking(root)
    choice = "tracked" if args.track else "ignored" if args.no_track else None
    defaulted = False
    if (choice is None and existed and os.path.lexists(root / ".git")
            and store_repo_state(root).state == "unrecorded"):
        print(f"wi: note: {root} is its own git repo, not set up by wi; "
              "`wi init --no-track` adopts it, history kept", file=sys.stderr)
    elif choice is None and not (existed and recorded):
        if existed:
            # an existing store with no recorded choice is left as it is:
            # an Enter or a missing terminal must not ignore a tracked store
            # 3c06: a sidecar store cannot be ignored, so only --track
            flags = ("`wi init --track`" if sandbox_shape(root)[0] == "sidecar"
                     else "`wi init --track` or `wi init --no-track`")
            print(f"wi: note: {root} has no recorded tracking choice; record "
                  f"one with {flags}", file=sys.stderr)
        elif _interactive():
            try:
                choice = choose_tracking(
                    sys.stdin, sys.stdout,
                    sidecar=sandbox_shape(root)[0] == "sidecar")
            except KeyboardInterrupt:
                print("\nwi init: interrupted; nothing written",
                      file=sys.stderr)
                return 130
        else:
            choice, defaulted = "ignored", True
    how = (" (no terminal and no --track/--no-track picked git-ignored)"
           if defaulted else "")
    if choice == "ignored" and sandbox_shape(root)[0] == "sidecar":
        # 3c06: the host ignores a sidecar's .claude-sandbox/, so a store
        # its own repo ignores lands in no repo; refuse first, as for the
        # repo root below
        raise WiError(1, f"{root} is {SIDECAR_NO_REPO}: a git-ignored store "
                         f"there lands in no repo{how}; nothing written (use "
                         "`wi init --track`)")
    if choice == "tracked":
        refusal = _track_refusal(root)
        if refusal:
            raise WiError(1, refusal)
    git_found = shutil.which("git") is not None
    # d1e9 D3: a git-ignored store gets its own repo, except at an old
    # location, which never holds one (it keeps today's plain ignored
    # store, with a note to move it), or with no git to make one
    if choice == "ignored" and git_found and not old_location(root):
        host = _own_repo_check(root)
        if host is not _DEDICATED:
            return _init_own(root, host, defaulted)
    if choice == "ignored" and not existed:
        # a store at the repo root cannot be ignored, and its own *.tmp*
        # line would ignore files across the whole repo: refuse first
        repo_top = _store_repo(root)
        if repo_top is not None and (os.path.realpath(root)
                                     == os.path.realpath(repo_top)):
            raise WiError(1, f"{root} is the repo root: a store there "
                             "cannot be git-ignored; nothing written (use "
                             "`wi init --track`, or put the store in a "
                             "subdirectory)")
    (root / "items").mkdir(parents=True, exist_ok=True)
    _create_if_absent(root / "README.md", STORE_README)
    _create_if_absent(root / ".gitignore", STORE_GITIGNORE)
    shape, repo = sandbox_shape(root)
    effective = choice or recorded
    if shape == "private" and effective == "tracked":
        print("private-shaped repo (no sidecar git, .claude-sandbox/ not "
              "gitignored): host .gitignore left alone so the store stays "
              "tracked")
    elif shape == "sidecar":
        host_gi = repo / ".gitignore"
        if not set(_gitignore_lines(host_gi)).intersection(SANDBOX_IGNORES):
            ok, msg = append_gitignore_line(host_gi, "/.claude-sandbox/")
            if ok:
                print("sidecar git at .claude-sandbox/.git: added "
                      "/.claude-sandbox/ to host .gitignore")
            else:
                print(f"wi: WARNING sidecar git at .claude-sandbox/.git: "
                      f"{msg}", file=sys.stderr)
    # shape 'ignored' (already whole-dir-ignored) and non-sandbox stores:
    # never duplicate the line; a tracked choice never touches the host
    # .gitignore, an ignored one adds only the store's own line
    rc = 0
    if choice == "ignored":
        # ignore first, record after: a store git does not ignore is never
        # recorded as ignored
        ok, msg = ensure_ignored(root)
        if ok:
            write_tracking(root, choice)
            print(f"tracking: {choice} (recorded in {root / STORE_FILE})")
            print(msg)
        else:
            print(f"wi: WARNING {msg}; tracking not recorded (run `wi init "
                  "--no-track` again once that is fixed, or `wi init "
                  "--track`)", file=sys.stderr)
            rc = 1
        # d1e9 D3: today's plain ignored store, said to have no history
        if rc == 0 and old_location(root):
            print(f"wi: note: {root} is at an old location, so it gets no "
                  "repo of its own and keeps no history; move it to "
                  f"{DEFAULT_STORE}/ for one ({MOVING_A_STORE})",
                  file=sys.stderr)
        elif rc == 0 and not git_found:
            print(f"wi: WARNING git not found: {root} has no history of its "
                  "own; run `wi init --no-track` again where git is "
                  "available", file=sys.stderr)
    elif choice == "tracked":
        write_tracking(root, choice)
        print(f"tracking: {choice} (recorded in {root / STORE_FILE})")
        if _host_repo(root) is None:
            # 8805 F3: tracked names a repo, and there is none around it
            fix = (f"move it to {DEFAULT_STORE}/ for one ({MOVING_A_STORE})"
                   if old_location(root) else
                   "`wi init --no-track` gives it its own repo")
            print(f"wi: note: {root} is in no git repo, so nothing tracks "
                  f"it and it keeps no history; {fix}", file=sys.stderr)
        warning = custody_warning(root)
        if warning:
            print(warning, file=sys.stderr)
    if defaulted and rc == 0:
        print(f"wi: WARNING no terminal and no --track/--no-track: created "
              f"{root} as a git-ignored store. To track it instead, run "
              "`wi init --track` and remove the store's line from "
              ".gitignore (the `wi init --track` warning names it)",
              file=sys.stderr)
    print(f"initialised {root}" if rc == 0
          else f"created {root}; tracking not recorded")
    return rc


def _short_name_arg(value):
    """A short_display_name given to `add` or `set`, stripped; None when it
    is blank or the `—` placeholder (the field is then absent, never `""`
    or a literal dash). Over SHORT_NAME_MAX exits 1: the caller checks
    before anything is read or written, as the title check does."""
    if value is None:
        return None
    value = value.strip()
    if value in ("", "—"):
        return None
    if len(value) > SHORT_NAME_MAX:
        raise WiError(1, f"short_display_name must be 1-{SHORT_NAME_MAX} "
                         f"chars (got {len(value)})")
    return value


def cmd_add(args):
    _one_line("title", args.title)
    _one_line("--short-display-name", args.short_display_name)
    root = resolve_root(args.root)
    created = today()
    title = args.title.strip()
    if not title or len(title) > 120:
        raise WiError(1, "title must be 1-120 chars")
    short_name = _short_name_arg(args.short_display_name)
    with Lock(root):
        items = load_all(root, archived=True)
        by_id = {it.id: it for it in items}
        for dep in args.dep or []:
            if not dep.startswith("ext:") and dep not in by_id and not args.force:
                raise WiError(1, f"dep '{dep}' does not resolve (--force to add anyway)")
        if args.parent and args.parent not in by_id and not args.force:
            raise WiError(1, f"parent '{args.parent}' does not resolve")
        iid = make_id(title, created, taken_ids(root, items), slug=args.slug)
        desc = sys.stdin.read().strip() if args.desc == "-" else (args.desc or "")
        meta = {"id": iid, "title": title, "short_display_name": short_name,
                "type": args.type, "status": "todo",
                "priority": args.priority, "tags": args.tag or [],
                "deps": args.dep or [], "parent": args.parent,
                "refs": args.ref or [], "created": created, "updated": created}
        item = Item(meta, [], desc, [("Handoff", emit_handoff({}))])
        errs = item.validate()
        if errs:
            raise WiError(3, "; ".join(errs))
        save_item(root, item)
    print(json.dumps(item_json(item)) if args.json else f"added {iid}")
    return 0


# A derived claimant name is one owner token: letters, digits, `.`, `_`, `-`.
# A space would split `wi status`'s columns, an `@` the `user@host` split, a
# leading `-` would read as a flag to `wi ls --owner`; each run of anything
# else becomes one `-`, and edge punctuation is trimmed.
_OWNER_UNSAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _owner_token(name):
    """`name` as an owner token, or None when nothing usable is left."""
    tok = _OWNER_UNSAFE_RE.sub("-", str(name or "")).strip("-._")
    return tok or None


def _git_user_name(root):
    """`git config user.name` as judged from the store's repo; None on any
    failure (no git, not a repo, unset, timeout)."""
    cwd = root if root is not None and Path(root).is_dir() else None
    git = _custody_git(cwd) if cwd is not None else _git
    r = git(cwd, "config", "user.name")
    if r is None or r.returncode != 0:
        return None
    return _owner_token(r.stdout.strip())


def _getpass_user():
    """getpass.getuser(), which raises when neither the login env vars nor
    the password database name the uid (a container's remapped uid)."""
    try:
        return _owner_token(getpass.getuser())
    except Exception:
        return None


def default_owner(root=None):
    """The claimant: WORK_ITEMS_OWNER verbatim (the explicit override, host
    included; the deprecated WI_OWNER when it is unset), else `<user>@<host>`
    with the user from the first of $USER (verbatim, as before), `git config
    user.name` run from the store's repo, getpass.getuser(), and `unknown`.
    The last two are sanitized to an owner token; an empty value counts as
    unset."""
    explicit = _env("WORK_ITEMS_OWNER", "WI_OWNER")[0]
    if explicit:
        return explicit
    user = os.environ.get("USER") or _git_user_name(root) \
        or _getpass_user() or "unknown"
    return f"{user}@{os.uname().nodename.split('.')[0]}"


def _claim(item, owner, steal=False):
    if item.get("status") == "blocked":
        raise WiError(1, f"{item.id} is blocked ({item.get('blocked')}); unblock first")
    if item.get("status") == "parked":
        raise WiError(1, f"{item.id} is parked ({item.get('parked')}); unpark first")
    if item.get("status") == "grooming":
        raise WiError(1, f"{item.id} is grooming ({item.get('grooming')}); "
                         "ungroom first")
    held_by = item.get("owner")
    if held_by and held_by != owner:
        if not steal:
            raise WiError(4, f"{item.id} held by {held_by} since "
                             f"{item.get('claimed')} ({age_str(item.get('claimed'))})")
        item.append_note(f"- {today()} stolen from {held_by} by {owner}")
    if held_by == owner:
        return False
    item.meta.update(owner=owner, claimed=now_minute(), status="doing")
    item.append_note(f"- {today()} claimed by {owner}")
    item.touch()
    return True


def cmd_claim(args):
    root = resolve_root(args.root)
    owner = args.as_owner or default_owner(root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        if item.get("status") == "todo":
            # the ready queue's own rule over the ready queue's own lookup
            # (items/, then archive/): claim takes nothing `next` hides
            by_id = DepIndex(root, load_all(root))
            unmet = unmet_deps(item, by_id)
            if unmet:
                def why(d):
                    if d.startswith("ext:"):
                        return f"{d} (external, never resolves)"
                    dep = by_id.get(d)
                    return f"{d} ({dep.get('status')})" if dep else \
                        f"{d} (unknown: in neither items/ nor archive/)"
                raise WiError(1, f"{item.id} waits on unmet deps: "
                                 + ", ".join(why(d) for d in unmet)
                                 + f"; finish or drop them, or `wi unblock "
                                 f"{item.id} --dep <id>`")
        if _claim(item, owner, args.steal):
            save_item(root, item)
    print(f"claimed {item.id} as {owner}")
    return 0


def cmd_release(args):
    root = resolve_root(args.root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        item.meta.update(owner=None, claimed=None, stage=None)
        # releasing a claim never unparks or ungrooms
        if item.get("status") not in ("parked", "grooming"):
            item.meta["status"] = "todo"
        item.touch()
        save_item(root, item)
    print(f"released {item.id}")
    return 0


# every character str.splitlines (or a YAML 1.1 loader: NEL, U+2028/U+2029)
# reads as a line break
_LINE_BREAK_RE = re.compile("[\n\r\x0b\x0c\x1c-\x1e\x85\u2028\u2029]")


def _one_line(what, val):
    """Values written into front matter, a Handoff bullet or a Notes line are
    one line (format.md): a line break would add front-matter keys, leave
    lines the next rewrite does not own, or inject a `## ` heading. Every
    Unicode line separator counts (U+2028 in a Notes line splits the
    exported `notes: |-` block). Called before anything is read or written,
    so a rejected value writes nothing."""
    m = val is not None and _LINE_BREAK_RE.search(val)
    if m:
        c = ord(m.group())
        raise WiError(1, f"{what} must be one line; it contains a line break"
                         + ("" if c in (10, 13) else f" (U+{c:04X})"))


def cmd_handoff(args):
    for key in HANDOFF_KEYS:
        _one_line(f"--{key}", getattr(args, key))
    root = resolve_root(args.root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        h = item.handoff()
        for key in HANDOFF_KEYS:
            val = getattr(args, key)
            if val is not None:
                h[key] = val
        item.set_handoff(h)
        if args.learned:
            line = f"- {today()} learned: {args.learned.strip()}"
            # Whole lines, not a substring: `L1` is new beside `L10`. Trailing
            # whitespace is ignored: section() strips the last Notes line.
            notes = (item.section("Notes") or "").split("\n")
            if line.rstrip() not in (n.rstrip() for n in notes):
                item.append_note(line)
        item.touch()
        save_item(root, item)
    print(f"handoff {item.id}")
    return 0


def cmd_done(args):
    root = resolve_root(args.root)
    _one_line("--note", args.note)
    status = "dropped" if args.drop else "done"
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        item.meta.update(status=status, closed=today(), owner=None,
                         claimed=None, stage=None)
        item.append_note(f"- {today()} {status}: {args.note}" if args.note
                         else f"- {today()} {status}")
        item.touch()
        save_item(root, item)
    print(f"{status} {item.id}")
    return 0


def _note_line(n, text, raw):
    """The Notes line for text `n` (1-based), or WiError(1). Every refusal
    starts `text <n>:` (the prefix a caller matches to reword that text) and
    never quotes the text, so a refused secret never reaches stderr."""
    line = text if raw else f"- {today()} {(text or '').strip()}"
    why = _line_refusal(text, line, raw)
    if why:
        raise WiError(1, f"text {n}: {why}; nothing written")
    return line


def _line_refusal(text, line, raw):
    """Why `text`, to be written as the Notes line `line`, is refused, or
    None: a line break, an empty text, and under raw a `## ` line or a
    fence opener; any line lint would flag as a secret. The reason never
    quotes the text. note and raise share it."""
    try:
        _one_line("the text", text)
    except WiError as e:
        return str(e)
    if not (text or "").strip():
        return "empty"
    if raw and line.startswith("## "):
        return "starts '## ', which would add a section"
    if raw and _fence_open(line):
        return "opens a code fence"
    for _, why in secret_findings(line):
        return why
    return None


def _abbrev(tok, name):
    """True when `tok` is the long option `name` or a prefix of it (at least
    `--` and one letter), bare or with `=value`. It does not check that the
    prefix is unambiguous: the caller names only options whose prefixes
    argparse accepts."""
    head = tok.split("=", 1)[0]
    return len(head) > 2 and name.startswith(head)


def _stray_separator(argv):
    """1-based position of the first text that is exactly `--`, judged from
    the raw argv, else None. argparse takes the first `--` as the end of
    options, and may silently drop a later one rather than hand it over as
    a text (it varies by Python version), so a note would lose a text.
    Texts are counted as argparse counts them: only the id and note's own
    options (--raw, -h, --help, or a prefix argparse accepts) are not
    texts; a token such as `-5` is one."""
    toks, i = list(argv or ()), 0
    while i < len(toks) and toks[i] != "note":  # the subcommand, past --root
        root_opt = _abbrev(toks[i], "--root")
        i += 2 if root_opt and "=" not in toks[i] else 1
    toks = toks[i + 1:]
    if "--" not in toks:
        return None
    sep = toks.index("--")
    after = toks[sep + 1:]
    # these option names must follow note's parser spec in build_parser
    before = [t for t in toks[:sep]  # the id, then texts
              if not (t == "-h" or _abbrev(t, "--raw") or _abbrev(t, "--help"))]
    start = 0 if before else 1  # no id before the separator: after[0] is it
    if "--" not in after[start:]:
        return None
    return len(before) + after.index("--", start)


def cmd_note(args):
    n = _stray_separator(getattr(args, "argv", None))
    if n:
        raise WiError(1, f"text {n}: is exactly '--', which the command line "
                         "cannot carry as a text; nothing written")
    lines = [_note_line(n, t, args.raw) for n, t in enumerate(args.lines, 1)]
    root = resolve_root(args.root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        for line in lines:
            item.append_note(line)
        item.touch()
        save_item(root, item)
    print(f"noted {item.id}" + (f" ({len(lines)} lines)" if len(lines) > 1 else ""))
    return 0


def now_second():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _question_refusal(question):
    """Why a raise's question line is refused, or None: note --raw's
    refusals, and a question that starts `decision` (it would read as a
    second headline). Checked before the lock, so a refusal writes
    nothing; the reason never quotes the question."""
    if question is None:
        return "no question line: put it after --"
    if question.strip() == "--":
        return "is exactly '--', which reads as the end of options"
    if re.match(r"\s*decision\b", question, re.I):
        return "starts 'decision'; give only the question, wi numbers it"
    return _line_refusal(question, question, raw=True)


# ── Card records: raise --record / --revise / --lines (3b51 W2) ────────────
# format.md § Card records. Every check runs before the first write, and the
# file is written before the item's `card:` line, under the one store lock.

RECORD_CAP = 262144          # 256 KiB: a levelled page card runs to ~14 KB
# deepest nesting of objects and lists a record may have (the record is 1):
# indent grows with depth, so a deep record's written bytes far outgrow
# its input; the written bytes are capped at RECORD_CAP too
RECORD_DEPTH = 64
# the write pattern for `rev` and `--raised`: to the second, ASCII digits
REV_WRITE = r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z"
REV_MINUTE = r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z"
# k has 1-4 digits and a written item id at most 128 characters, so a
# record's path stays far below every filesystem's name limit and a raise
# that passes its checks (and --check) cannot then fail to make its file
CARD_FORMAT_RE = re.compile(r"decision-card/([1-9][0-9]{0,3})")
CARD_ITEM_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,127}")
# the longest key a record may hold: a list under a key is scanned with
# its key per item, so a long key over many items costs key x items
RECORD_KEY_MAX = 256
DECISION_N_RE = re.compile(r"[1-9][0-9]{0,8}")   # at most 9 digits
# the machine lines a card carries under its `card:` line, each key's
# grammar its own plan's: delegation:/terms: (answer changes), act: and
# grant: (signed grants). raised:, revised: and card: are wi's own.
MACHINE_KEYS = ("delegation", "terms", "act", "grant")
_MACHINE_RE = re.compile(r"[ \t]+([A-Za-z][A-Za-z0-9 _-]*):(?:[ \t].*)?")
_CARD_TAIL = (" — the card is this record; read it with the decisions "
              "skill's card-record reference; never backfill this card from "
              "lines")
# a key named in an error: letters, `_` and `-`, at most two trailing
# digits, at most 32 characters; any other key (a token-shaped one, a
# long one) is named by its place
_JSON_KEY = re.compile(r"(?=.{1,32}\Z)[A-Za-z][A-Za-z_-]*[0-9]{0,2}")


# the label's delimiters and their lookalikes: full-width parentheses,
# U+0387 (the Greek ano teleia, NFKC's twin of the middle dot)
_LABEL_DELIMS = "()·\uff08\uff09\u0387"
# an option marker as a reader would take it: a bracketed lone a-z letter
# not touching a letter before it (file(s) and a[i] are text), followed
# by a space or the end of the text
_MARKER_RE = re.compile(r"(?<![A-Za-z])[\[(]\s*[a-z]\s*[\])](?= |$)")
# the head of a headline raised from one labelled item
_LABEL_SHAPE = re.compile(r"\S+ \([^)]*\) · ")
# variation selectors: not format characters (Unicode Mn), so NFKC keeps
# them; dropped before the second token check (`⚠` + U+FE0F)
_VARIATION_RE = re.compile("[\ufe00-\ufe0f\U000e0100-\U000e01ef]")


class _BadJson(ValueError):
    pass


def _no_constant(name):
    raise _BadJson(f"holds {name}, which is not JSON")


def _finite(text):
    val = float(text)
    if val in (float("inf"), float("-inf")):
        raise _BadJson("holds a number too large for JSON")
    if val == 0 and re.search("[1-9]", re.split("[eE]", text)[0]):
        raise _BadJson("holds a number too small for JSON (it reads as 0)")
    return val


def _no_dup_keys(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise _BadJson("holds a duplicate key")
        out[k] = v
    return out


def _read_input(what, src):
    """Bytes of --record or --lines: a path, or `-` for stdin (read only
    when named). At most RECORD_CAP bytes; more is refused."""
    try:
        if src == "-":
            data = sys.stdin.buffer.read(RECORD_CAP + 1)
        else:
            with open(src, "rb") as fh:
                data = fh.read(RECORD_CAP + 1)
    except OSError as e:
        raise WiError(1, f"{what}: cannot read {src}: {e.strerror}; "
                         "nothing written") from None
    if len(data) > RECORD_CAP:
        raise WiError(1, f"{what} over 256 KB; nothing written")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise WiError(1, f"{what}: not UTF-8 at byte {e.start}; "
                         "nothing written") from None


def _parse_record(text):
    """The record as a dict: strict JSON (no NaN or Infinity, no number
    that overflows to one, no duplicate key at any depth), one object.
    Errors name a position, never content."""
    try:
        rec = json.loads(text, parse_constant=_no_constant,
                         parse_float=_finite, object_pairs_hook=_no_dup_keys)
    except _BadJson as e:
        raise WiError(1, f"record {e}; nothing written") from None
    except json.JSONDecodeError as e:
        raise WiError(1, f"record is not valid JSON (line {e.lineno} "
                         f"column {e.colno}); nothing written") from None
    except RecursionError:
        raise WiError(1, "record is nested too deep; nothing written") from None
    except ValueError:  # e.g. an integer past the digit limit
        raise WiError(1, "record holds a value JSON here cannot read; "
                         "nothing written") from None
    if not isinstance(rec, dict):
        raise WiError(1, "record is not a JSON object; nothing written")
    if _depth(rec) > RECORD_DEPTH:
        raise WiError(1, f"record is nested more than {RECORD_DEPTH} deep; "
                         "nothing written")
    return rec


def _depth(val):
    """The deepest nesting of objects and lists in `val` (a scalar is 0),
    walked without recursion; a key over RECORD_KEY_MAX is refused on
    the way."""
    best, stack = 0, [(val, 1)]
    while stack:
        v, d = stack.pop()
        if isinstance(v, dict):
            if any(len(k) > RECORD_KEY_MAX for k in v):
                raise WiError(1, f"record holds a key over {RECORD_KEY_MAX} "
                                 "characters; nothing written")
            kids = v.values()
        elif isinstance(v, list):
            kids = v
        else:
            continue
        best = max(best, d)
        stack.extend((k, d + 1) for k in kids)
    return best


def _headline_field(what, val, in_q=False, label_name=False,
                    norec_title=False):
    """Refuse a text the headline is built from unless it is non-empty and
    one line, with no control or line-separator character and none of the
    headline's own tokens. Inside q only ` — options: `, ` | `,
    `[recommended]` and `⚠ one-way` are tokens (readers split at the
    first ` — options: `, so a question's own `(b) ` never reaches the
    option list), and q may not start with whitespace; a title, label or
    norec also refuses an option marker. A format character (Unicode Cf:
    zero-width, bidi, soft hyphen, BOM, tags) is refused everywhere, so
    no token is forged from invisible parts. label.name refuses `(`, `)` and `·` (its own
    delimiters); with no recommendation a title refuses ` — `, the norec
    boundary. Never quotes the text."""
    def no(why):
        raise WiError(1, f"record {what}: {why}; nothing written")
    if not isinstance(val, str) or not val.strip():
        no("must be non-empty text")
    try:
        _one_line(f"record {what}", val)
    except WiError as e:
        raise WiError(1, f"{e}; nothing written") from None
    if any(unicodedata.category(c) == "Cc" for c in val):
        no("holds a control character")
    if any(unicodedata.category(c) == "Cf" for c in val):
        no("holds a format character (zero-width, bidi or similar)")
    if "⚠ one-way" in val:
        no("holds '⚠ one-way', the headline's mark")
    if in_q and val[:1].isspace():
        no("starts with whitespace")
    if label_name and any(c in val for c in _LABEL_DELIMS):
        no("holds '(', ')' or '·', the label's delimiters")
    if norec_title and " — " in val:
        no("holds ' — ', which with no recommendation marks the norec label")
    if " — options: " in val:
        no("holds ' — options: ', which splits the headline")
    if " | " in val:
        no("holds ' | ', which separates the headline's options")
    if "[recommended]" in val.lower():
        no("holds '[recommended]', the headline's mark")
    if not in_q and _MARKER_RE.search(val):
        no("holds an option marker (x)")


def _check_record(rec, n):
    """Check what wi relies on to write the record and build its headline
    (format, rev, n, q, options, rec/norec, label, oneway); the record's
    other fields are the card-record reference's. Returns k, the format's
    number. `n` is N for a revision (the record's n must equal it), None
    for a new raise (wi writes n)."""
    def no(why):
        raise WiError(1, f"record {why}; nothing written")
    fmt = rec.get("format")
    m = CARD_FORMAT_RE.fullmatch(fmt) if isinstance(fmt, str) else None
    if not m:
        no("format: must be decision-card/<k>")
    rev = rec.get("rev")
    if not isinstance(rev, str) or not re.fullmatch(REV_WRITE, rev):
        if isinstance(rev, str) and re.fullmatch(REV_MINUTE, rev):
            no("rev: is to the minute; write it to the second, …:00Z")
        no("rev: must be YYYY-MM-DDTHH:MM:SSZ (UTC, to the second)")
    if n is not None:
        got = rec.get("n")
        if type(got) is not int or got != n:
            no(f"n: must equal the revised decision's number, {n}")
    _headline_field("q", rec.get("q"), in_q=True)
    if re.match(r"decision\b", rec["q"], re.I):
        no("q: starts 'decision'; give only the question, wi numbers it")
    if "label" not in rec and _LABEL_SHAPE.match(rec["q"]):
        no("q: reads as a label (`<id> (<name>) · `); give it as `label`")
    opts = rec.get("options")
    if not isinstance(opts, list) or not opts:
        no("options: must be a non-empty list")
    last = ""
    for i, opt in enumerate(opts):
        if not isinstance(opt, dict):
            no(f"options[{i}]: must be an object")
        k = opt.get("k")
        if not isinstance(k, str) or not re.fullmatch("[a-z]", k):
            no(f"options[{i}].k: must be one letter a-z")
        if k <= last:
            no(f"options[{i}].k: letters go in order, each once, (z) last")
        last = k
        _headline_field(f"options[{i}].title", opt.get("title"),
                        norec_title=rec.get("rec") is None)
    letters = {opt["k"] for opt in opts}
    r = rec.get("rec")
    if r is None:
        _headline_field("norec", rec.get("norec"))
    elif not isinstance(r, str) or r not in letters:
        no("rec: must be one option's letter, or null with norec")
    if "label" in rec:
        lab = rec["label"]
        if not isinstance(lab, dict):
            no("label: must be an object {id, name}")
        lid = lab.get("id")
        if not isinstance(lid, str) or not re.fullmatch(r"\S+", lid):
            no("label.id: must be one word")
        _headline_field("label.id", lid, label_name=True)
        _headline_field("label.name", lab.get("name"), label_name=True)
    if "oneway" in rec and not isinstance(rec["oneway"], bool):
        no("oneway: must be true or false")
    return int(m.group(1))


def _record_headline(n, rec):
    """`decision N: [<id> (<name>) · ]<q>[ ⚠ one-way] — options: (a) <title>
    [recommended] | … [ — <norec>]`, the form format.md § Operator questions
    gives, so every headline reader is unchanged."""
    head = rec["q"]
    if "label" in rec:
        head = f"{rec['label']['id']} ({rec['label']['name']}) · {head}"
    if rec.get("oneway") is True:
        head += " ⚠ one-way"
    opts = []
    for opt in rec["options"]:
        text = f"({opt['k']}) {opt['title']}"
        if rec.get("rec") == opt["k"]:
            text += " [recommended]"
        opts.append(text)
    line = f"decision {n}: {head} — options: " + " | ".join(opts)
    if rec.get("rec") is None:
        line += f" — {rec['norec']}"
    return line


def _headline_reads_back(line, n, rec):
    """Refuse (exit 1) a built headline a reader would not split back into
    the record's parts, on the text as built and again on its NFKC form
    with variation selectors dropped (lookalikes: a no-break or em space
    around a dash, full-width brackets and bars, `⚠` + U+FE0F): exactly
    one ` — options: `; a head holding `⚠` only as the one-way mark and
    ending in no token character; with `rec` null, ` — ` only as the
    norec boundary, the norec after it exactly; `split(' | ')` giving one
    `(k) ` part per option in letter order, no other option marker (a
    bracketed lone letter that touches no letter before it: file(s) and
    a[i] are text) and no part starting or ending in a token character (a
    leading tag such as [WIP] or (Re) is text); `[recommended]` only
    once, closing the rec's option. Never quotes the text."""
    def norm(t):
        return _VARIATION_RE.sub("", unicodedata.normalize("NFKC", t))

    def no(why):
        raise WiError(1, f"record: the built headline would not read back "
                         f"({why}); nothing written")
    # a part may start with a bracket ([WIP] ship it, (Re)start the job?):
    # only these may not open a part, and these with an open bracket may
    # not close one
    starts = ("—", "|", "·", "⚠")
    ends = starts + ("[", "(")
    names = {"—": "a dash, the norec boundary",
             "|": "the options separator", "·": "the label separator",
             "⚠": "the one-way mark", "[": "an open bracket",
             "(": "an open bracket"}

    def edge(text, where):
        t = text.strip()
        c = t[:1] if where == "starts" else t[-1:]
        return names.get(c) if c in (starts if where == "starts" else ends) \
            else None
    for t, norec in ((line, rec.get("norec")),
                     (norm(line), norm(rec.get("norec") or ""))):
        body = t[len(f"decision {n}: "):]
        if len(re.findall("(?= — options: )", body)) != 1:  # overlaps too
            no("' — options: ' must appear once")
        head, tail = body.split(" — options: ")
        if rec.get("oneway") is True:
            if not head.endswith(" ⚠ one-way"):
                no("the one-way mark is not where it goes")
            head = head[:-len(" ⚠ one-way")]
        if "⚠" in head:
            no("the question holds the one-way mark ⚠")
        if "[recommended" in head.lower():
            no("the question holds the recommended mark")
        if edge(head, "ends"):
            no(f"the question ends in {edge(head, 'ends')}")
        if "label" in rec:
            head = head.split(" · ", 1)[-1]
        if edge(head, "starts"):
            no(f"the question starts with {edge(head, 'starts')}")
        if rec.get("rec") is None:
            if " — " not in tail:
                no("no norec boundary")
            tail, after = tail.split(" — ", 1)
            if after != norec or edge(after, "starts"):
                no("a dash ' — ' other than the norec boundary")
        parts = tail.split(" | ")
        if len(parts) != len(rec["options"]):
            no("the options separator ' | ' inside a part")
        for part, opt in zip(parts, rec["options"]):
            m = re.fullmatch(r"\(([a-z])\) (.*)", part)
            if not m or m.group(1) != opt["k"]:
                no(f"option ({opt['k']}) does not open its part")
            rest = m.group(2)
            if rec.get("rec") == opt["k"]:
                if not rest.endswith(" [recommended]"):
                    no("the recommended mark does not close the rec's "
                       "option")
                rest = rest[:-len(" [recommended]")]
            title = f"option ({opt['k']})'s title"
            if "[recommended" in rest.lower():
                no(f"{title} holds the recommended mark")
            if _MARKER_RE.search(rest):
                no(f"{title} holds an option marker (x)")
            for where in ("starts", "ends"):
                if edge(rest, where):
                    word = "starts with" if where == "starts" else "ends in"
                    no(f"{title} {word} {edge(rest, where)}")


def _json_strings(val, path="", key=None):
    """(JSON path, text) for every string in the record, keys too. An
    item of a list under a key is also given as the line scan sees an
    object's member, `"<key>": "<item>"` (a number or boolean re-rendered
    by json.dumps, `true`/`false` or the number as Python prints it, then
    quoted as a string), so a secret listed under its key (`"api_key": ["…"]`) reads
    as the assignment it is; a multi-line item is also given as
    `<key>: <item>`, so its continued lines join. A key that does not look
    harmless (_JSON_KEY) is named by its place, never its text."""
    if isinstance(val, dict):
        for i, (k, v) in enumerate(val.items()):
            seg = k if _JSON_KEY.fullmatch(k) else f"<key {i}>"
            p = f"{path}.{seg}" if path else seg
            yield f"{p} (its key)", k
            yield from _json_strings(v, p, k)
    elif isinstance(val, list):
        for i, v in enumerate(val):
            p = f"{path}[{i}]"
            if key is not None and isinstance(v, (str, int, float)):
                sv = v if isinstance(v, str) else \
                    json.dumps(v)   # true/false, or the number as written
                yield p, json.dumps(key, ensure_ascii=False) + ": " + \
                    json.dumps(sv, ensure_ascii=False)
                if isinstance(v, str) and "\n" in v:
                    yield p, f"{key}: {v}"
            yield from _json_strings(v, p, key)
    elif isinstance(val, str):
        yield path or "(the record)", val


def _record_bytes(rec):
    """(text, bytes) the record is written as, refused (exit 1) when it
    does not encode as UTF-8 or the bytes pass RECORD_CAP."""
    try:
        text = json.dumps(rec, ensure_ascii=False, indent=2) + "\n"
        data = text.encode("utf-8")
    except RecursionError:
        raise WiError(1, "record is nested too deep; nothing written") \
            from None
    except UnicodeEncodeError:
        raise WiError(1, "record holds a lone surrogate, which UTF-8 cannot "
                         "carry; nothing written") from None
    if len(data) > RECORD_CAP:
        raise WiError(1, "record as written over 256 KB; nothing written")
    return text, data


def _record_secrets(text, rec):
    """Two scans, both clean or refused: every line of the bytes to be
    written, then every decoded string value whole (a secret laid over
    lines inside one value), reported by JSON path and line within it."""
    for k, why in secret_findings(text):
        raise WiError(1, f"record line {k}: {why}; nothing written")
    for path, val in _json_strings(rec):
        for k, why in secret_findings(val):
            raise WiError(1, f"record {path} line {k}: {why}; nothing written")


def _machine_lines(text):
    """The --lines text as lines: each one indented physical line keyed
    by MACHINE_KEYS, secret-clean. A final newline is allowed."""
    if text.endswith("\n"):
        text = text[:-1]
    out = text.split("\n") if text else []
    if not out:
        raise WiError(1, "lines: no line given; nothing written")
    for i, line in enumerate(out, 1):
        def no(why):
            raise WiError(1, f"lines line {i}: {why}; nothing written")
        try:
            _one_line("it", line)
        except WiError as e:
            no(str(e))
        m = _MACHINE_RE.fullmatch(line)
        if not m:
            no("must be indented and open with its key ("
               + ", ".join(k + ":" for k in MACHINE_KEYS) + ")")
        key = m.group(1)
        if key in ("raised", "revised", "card"):
            no(f"{key}: is wi's own line")
        if key not in MACHINE_KEYS:
            no("a card's content goes in the record; lines take only "
               + ", ".join(k + ":" for k in MACHINE_KEYS))
        if key == "grant" and not line.split(":", 1)[1].strip():
            no("grant: needs the grant's id")
        why = _line_refusal(line, line, raw=True)
        if why:
            no(why)
    return out


def _store_texts(root):
    """(item file stem, unfenced lines) for every item in items/ and
    archive/; a file that does not read is skipped (load_all, run first,
    refuses an undecodable one)."""
    for path in item_paths(root, archived=True):
        try:
            text = read_raw(path)
        except (WiError, OSError):
            continue
        lines = text.replace("\r\n", "\n").split("\n")
        fenced = set()
        for i, j in _fence_spans(lines):
            fenced.update(range(i, j + 1))
        yield path.stem, [ln for i, ln in enumerate(lines) if i not in fenced]


def _answer_holder(root, n):
    """The item holding an `answer N:` line, store-wide, else None: any
    answer line is final (a follow-up is never stored as one)."""
    for stem, lines in _store_texts(root):
        for line in lines:
            m = ANSWER_RE.match(line)
            if m and int(m.group(1)) == n:
                return stem
    return None


def _named_records(root):
    """Every record path a `card:` line names, store-wide."""
    out = set()
    for _, lines in _store_texts(root):
        for line in lines:
            m = CARD_RE.fullmatch(line)
            if m:
                out.add(m.group(1))
    return out


def _item_has_decision(item, n):
    lines = item.body.replace("\r\n", "\n").split("\n")
    fenced = set()
    for i, j in _fence_spans(lines):
        fenced.update(range(i, j + 1))
    return any(i not in fenced and (m := DECISION_RE.match(line))
               and int(m.group(1)) == n for i, line in enumerate(lines))


def _card_dir(root, iid, n, make, tail="nothing written"):
    """cards/<id>/<N> walked level by level: each level lstat-ed, a
    symlink or non-directory refused (exit 3), a missing level made with
    os.mkdir (never makedirs, which follows a link) when `make`; then the
    real path must lie under the store's cards/. `tail` ends a refusal
    (the read path says nothing read)."""
    level = Path(root)
    for seg in ("cards", iid, str(n)):
        level = level / seg
        try:
            st = os.lstat(level)
        except FileNotFoundError:
            if not make:
                continue
            try:
                os.mkdir(level)
            except FileExistsError:
                pass
            except OSError as e:
                raise WiError(3, f"cannot create {level}: {e.strerror}; "
                                 "nothing written") from None
            st = os.lstat(level)
        if stat.S_ISLNK(st.st_mode):
            raise WiError(3, f"{level} is a symbolic link; a card record is "
                             f"never written or read through one; {tail}")
        if not stat.S_ISDIR(st.st_mode):
            raise WiError(3, f"{level} is not a directory; {tail}")
    # defence in depth: the lstat walk above already refuses every link,
    # so this is unreachable today; kept should a later change loosen it
    under = os.path.join(os.path.realpath(root), "cards") + os.sep
    if not os.path.realpath(level).startswith(under):
        raise WiError(3, f"{level} resolves outside the store's cards/; "
                         f"{tail}")
    return level


def _existing_record(root, rel, path, data):
    """None when nothing is at the record's path; "adopt" for an orphan
    with these exact bytes (a raise that stopped between the file and its
    line); otherwise WiError(3)."""
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(st.st_mode):
        kind = "a symbolic link" if stat.S_ISLNK(st.st_mode) else \
            "not a regular file"
        raise WiError(3, f"{path} is {kind}; a card record is never written "
                         "or read through one; nothing written")
    if rel in _named_records(root):
        raise WiError(3, f"refusing to overwrite existing {path}: a card "
                         "record is immutable; give the revision a new rev; "
                         "nothing written")
    try:
        # O_NOFOLLOW: a link swapped in since the lstat is refused, not read
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with open(fd, "rb") as fh:
            same = fh.read(len(data) + 1) == data
    except OSError as e:
        raise WiError(3, f"cannot read {path}: {e.strerror}; "
                         "nothing written") from None
    if not same:
        raise WiError(3, f"the file at {path} is named by no card: line and "
                         "differs from this record: delete it (an orphan "
                         "from a stopped write), then run the raise again; "
                         "nothing written")
    return "adopt"


def read_card_record(root, iid, n, rel, rev, fmt):
    """(bytes, record) of the card record a `card:` line names (3b51 W3,
    format.md § Card records, Reading a record): the path's segments are
    the item id, N and the name the line's rev and format give; no level
    and not the file is a symlink (the level walk, never followed); the
    file parses as the strict JSON the write took, and its n, rev and
    format are the line's. The bytes are the file's as read, never
    re-serialized. Any failure is WiError(3), never quoting content."""
    def changed(what):
        return WiError(3, f"card record {what} ({rel}); restore it from the "
                          f"store's history (git -C {root} log -- {rel}); "
                          "never backfill it")
    parts = rel.split("/")
    name = rev.replace(":", "-") + f".card{fmt.split('/', 1)[1]}.json"
    if len(parts) != 4 or parts[0] != "cards" or parts[1] != iid \
            or parts[2] != str(n) or parts[3] != name:
        raise WiError(3, f"the card: line for decision {n} on {iid} names "
                         f"{rel}, which is not this decision's record path "
                         f"(cards/{iid}/{n}/{name}); nothing read")
    path = _card_dir(root, iid, n, make=False, tail="nothing read") / name
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        raise changed("missing") from None
    except OSError:
        raise changed("unreadable") from None
    if stat.S_ISLNK(st.st_mode):
        raise WiError(3, f"{path} is a symbolic link; a card record is never "
                         "written or read through one; nothing read")
    if not stat.S_ISREG(st.st_mode):
        raise changed("not a regular file")
    try:
        # O_NOFOLLOW: a link swapped in since the lstat is refused, not read
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with open(fd, "rb") as fh:
            data = fh.read(RECORD_CAP + 1)
    except OSError:
        raise changed("unreadable") from None
    if len(data) > RECORD_CAP:
        raise changed("changed")
    try:
        rec = _parse_record(data.decode("utf-8"))
    except (UnicodeDecodeError, WiError):
        raise changed("changed") from None
    got_n = rec.get("n")
    if type(got_n) is not int or got_n != n or rec.get("rev") != rev \
            or rec.get("format") != fmt:
        raise changed("changed")
    return data, rec


def _encodable(what, line):
    try:
        line.encode("utf-8")
    except UnicodeEncodeError:
        raise WiError(1, f"{what}: holds a lone surrogate, which UTF-8 cannot "
                         "carry; nothing written") from None


def _raise_args(question, record, revise, why, lines, raised):
    """Refuse a combination of raise's forms (exit 1), before anything is
    read: the record and a question line are exclusive; --why goes with
    --revise, as --raised does; --lines goes with --record, or alone with
    --revise N (machine lines under the current card)."""
    def no(text):
        raise WiError(1, f"{text}; nothing written")
    if record is not None and question is not None:
        no("--record and a question line are exclusive: the headline is "
           "built from the record")
    if record == "-" and lines == "-":
        no("--record - and --lines - cannot both read stdin")
    if revise is None:
        if why is not None:
            no("--why goes with --revise")
        if raised is not None:
            no("--raised goes with --revise")
        if lines is not None and record is None:
            no("--lines goes with --record, or with --revise N alone")
        return None
    if not DECISION_N_RE.fullmatch(revise):
        no("--revise takes a decision number (1-9 digits)")
    if why is None:
        no("--revise needs --why '<why>'")
    if lines is not None and question is not None:
        no("--lines goes under a card record, never with a question line")
    if record is None and question is None and lines is None:
        no("--revise needs --record, a question line, or --lines")
    if raised is not None and record is None and question is None:
        no("--raised goes with a restated headline (--record or a question "
           "line)")
    if raised is not None and not re.fullmatch(REV_WRITE, raised):
        no("--raised must be YYYY-MM-DDTHH:MM:SSZ (UTC, to the second)")
    return int(revise)


def _insert_after_card_block(item, n, new_lines):
    """Insert `new_lines` directly after decision N's current card block:
    its last `card:` line and the indented lines already under it, so the
    block stays one block. The one place wi writes inside a body rather
    than at the end of `## Notes`."""
    idx = [i for m, i, _ in _card_scan(item) if m == n][-1]
    raw = _raw_lines(item.body)
    end = idx + 1
    while end < len(raw) and _content(raw[end])[:1].isspace():
        end += 1
    if not raw[end - 1].endswith("\n"):
        raw[end - 1] += item.eol
    raw[end:end] = [line + item.eol for line in new_lines]
    item.body = "".join(raw)


def raise_decision(root, ref, question, *, record=None, revise=None,
                   why=None, lines=None, raised=None, check=False):
    """Give out the next decision number and write its headline, all under
    one Lock (03ab F8): allocate N, build the lines, append them to item
    `ref`'s Notes, save, then advance the counter. Returns (N, item).

    One step under the lock: a crash after the item is saved and before
    the counter is written loses nothing, since the next reader takes the
    larger of the counter and the items.

    The card-record forms (3b51 W2, format.md § Card records): `record`
    (the record's text) writes cards/<id>/<N>/<rev>.card<k>.json, created
    exclusively, before the item's lines, its `card:` line last; `revise`
    (N) restates an open decision's headline under a `revised:` line, from
    the record or `question`; `lines` (text) adds machine lines, after the
    `card:` line, or alone under N's current card with no new record.
    Every check runs first; `check` runs them all and writes nothing."""
    n_rev = _raise_args(question, record, revise, why, lines, raised)
    form = ("record" if record is not None else
            "question" if question is not None or n_rev is None else "lines")
    if form == "question":
        why_q = _question_refusal(question)
        if why_q:
            raise WiError(1, f"question: {why_q}; nothing written")
    if why is not None:
        why_w = _line_refusal(why, why, raw=True)
        if why_w:
            raise WiError(1, f"--why: {why_w}; nothing written")
    rec = None
    if record is not None:
        rec = _parse_record(record)
        k = _check_record(rec, n_rev)
        # every check that reads the record runs here, before the lock: a
        # new raise's n is not known yet, so 0 stands in; the n wi writes
        # under the lock is a number it chose, and only the size is checked
        # again there
        if n_rev is None:
            rec["n"] = 0
        _headline_reads_back(_record_headline(rec["n"], rec), rec["n"], rec)
        text, _ = _record_bytes(rec)
        try:
            _record_secrets(text, rec)
        except RecursionError:
            raise WiError(1, "record is nested too deep; nothing written") \
                from None
    machine = _machine_lines(lines) if lines is not None else []
    with Lock(root):
        problem = counter_problem(root)
        if problem:
            raise WiError(1, f"{problem}; nothing written")
        item = load_item_anywhere(root, ref)
        now = now_second()
        if n_rev is None:
            n = _decision_floor(root) + 1
        else:
            n = n_rev
            if not _item_has_decision(item, n):
                raise WiError(1, f"decision {n} is not on {item.id}; "
                                 "nothing written")
            holder = _answer_holder(root, n)
            if holder:
                raise WiError(1, f"decision {n} is answered (`answer {n}:` "
                                 f"on {holder}); an answered card is never "
                                 "rewritten. A follow-up (later, tell me, dig "
                                 "into, expand, hold) is never an answer "
                                 "line: if that line is one, rewrite it as a "
                                 f"`wake {n}:` line first (format.md "
                                 "§ Operator questions); nothing written")
            carded = n in card_lines(item)
            if form == "question" and carded:
                raise WiError(1, f"decision {n} has a card record; revise it "
                                 "with `--record`; nothing written")
            if form == "lines" and not carded:
                raise WiError(1, f"decision {n} has no card record on "
                                 f"{item.id}: machine lines go under a card "
                                 "record; nothing written")
            if raised is not None and n in decision_raised(item):
                raise WiError(1, f"decision {n} already has a raised: line; "
                                 "--raised only fills a missing one; nothing "
                                 "written")
        path = data = None
        out = []
        if form == "record":
            if not CARD_ITEM_ID_RE.fullmatch(item.id):
                raise WiError(1, f"{item.id}: not a card record path segment "
                                 "([a-z0-9][a-z0-9-]*, at most 128 "
                                 "characters); nothing written")
            if n_rev is None:
                rec["n"] = n
            headline = _record_headline(n, rec)
            _, data = _record_bytes(rec)
            name = rec["rev"].replace(":", "-") + f".card{k}.json"
            rel = f"cards/{item.id}/{n}/{name}"
            card = f"  card: {rel} rev {rec['rev']} · decision-card/{k}" \
                + _CARD_TAIL
            if not CARD_RE.fullmatch(card):
                raise WiError(1, f"{item.id}: the card: line would not read "
                                 "back; nothing written")
            _card_dir(root, item.id, n, make=False)
            path = Path(root) / "cards" / item.id / str(n) / name
            adopt = _existing_record(root, rel, path, data) == "adopt"
            out.append(headline)
            if n_rev is None:
                out.append(f"  raised: {now}")
        elif form == "question":
            out.append(f"decision {n}: {question}")
            if n_rev is None:
                out.append(f"  raised: {now}")
        if n_rev is not None and form != "lines":
            if raised is not None:
                out.append(f"  raised: {raised}")
            out.append(f"  revised: {now} — {why}")
        if form == "record":
            out.append(card)
        if form == "lines":
            out.append(f"  revised: {now} — {why} (machine lines added; "
                       "record unchanged)")
        out += machine
        for line in out:
            why_l = _line_refusal(line, line, raw=True)
            if why_l:
                what = "question" if form == "question" else "line"
                raise WiError(1, f"{what}: {why_l}; nothing written")
            _encodable("line", line)
        if check:
            return n, item
        if form == "record":
            _card_dir(root, item.id, n, make=True)
            if adopt:
                _journal_write(path)
            else:
                atomic_write_bytes(path, data, create=True)
        if form == "lines":
            _insert_after_card_block(item, n, out)
        else:
            for line in out:
                item.append_note(line)
        item.touch()
        save_item(root, item)
        if n_rev is None:
            write_counter(root, n)
    return n, item


def _decision_floor(root):
    """The number raise allocates above: the larger of the counter and the
    items' highest N (a seam the race test waits in)."""
    return last_decision(root)


def cmd_raise(args):
    # the forms are checked before stdin or any file is read
    _raise_args(args.question, args.record, args.revise, args.why,
                args.lines_file, args.raised)
    record = (_read_input("record", args.record)
              if args.record is not None else None)
    lines = (_read_input("lines", args.lines_file)
             if args.lines_file is not None else None)
    root = resolve_root(args.root)
    n, item = raise_decision(root, args.id, args.question, record=record,
                             revise=args.revise, why=args.why, lines=lines,
                             raised=args.raised, check=args.check)
    if args.check:
        verb = "raise" if args.revise is None else "revise"
        print(f"check: ok, would {verb} decision {n} on {item.id}; "
              "nothing written")
    else:
        print(n)
    return 0


def cmd_counter(args):
    root = resolve_root(args.root)
    problem = counter_problem(root)
    if problem:
        raise WiError(1, problem)
    print(last_decision(root))
    return 0


def cmd_block(args):
    _one_line("reason", args.reason)
    _one_line("--on", args.on)
    root = resolve_root(args.root)
    if bool(args.reason) == bool(args.on):
        raise WiError(1, "block takes a reason or --on <id>, not both/neither")
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        if args.on:
            dep = resolve_id(load_all(root, archived=True), args.on).id
            deps = item.get("deps", [])
            if dep not in deps:
                item.meta["deps"] = deps + [dep]
        else:
            # a block supersedes a park or a grooming: the item is no longer
            # deferred, nor waiting on the operator's answers
            item.meta.update(status="blocked", blocked=args.reason, parked=None,
                             grooming=None)
        item.touch()
        save_item(root, item)
    print(f"blocked {item.id}")
    return 0


def cmd_unblock(args):
    root = resolve_root(args.root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        if args.dep:
            item.meta["deps"] = [d for d in item.get("deps", []) if d != args.dep]
        else:
            item.meta["blocked"] = None
            if item.get("status") == "blocked":
                item.meta["status"] = "doing" if item.get("owner") else "todo"
        item.touch()
        save_item(root, item)
    print(f"unblocked {item.id}")
    return 0


def _park(item, reason, note=None):
    """Park `item`: deliberately deferred, out of every ready queue. A claim
    and pipeline stage are released (nobody is working a parked item); a
    `blocked:` reason is kept, so unpark can return the item to blocked.
    Refuses closed items. Returns False when nothing would change."""
    st = item.get("status")
    if st in ("done", "dropped"):
        raise WiError(1, f"{item.id} is {st}; a closed item cannot be parked")
    if st == "parked" and item.get("parked") == reason:
        return False
    item.meta.update(status="parked", parked=reason, grooming=None, owner=None,
                     claimed=None, stage=None)
    item.append_note(f"- {today()} {note or 'parked: ' + reason}")
    item.touch()
    return True


def cmd_park(args):
    _one_line("reason", args.reason)
    reason = (args.reason or "").strip()
    if not reason:
        raise WiError(1, "park takes a reason")
    root = resolve_root(args.root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        if _park(item, reason):
            save_item(root, item)
    print(f"parked {item.id}")
    return 0


def cmd_unpark(args):
    """Back to `todo`, or to `blocked` when the item still carries a blocked
    reason. The claim was released on park, so never back to `doing`."""
    root = resolve_root(args.root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        if item.get("status") != "parked":
            raise WiError(1, f"{item.id} is {item.get('status')}, not parked")
        status = "blocked" if item.get("blocked") else "todo"
        item.meta.update(status=status, parked=None)
        item.append_note(f"- {today()} unparked")
        item.touch()
        save_item(root, item)
    print(f"unparked {item.id} -> {status}")
    return 0


def _groom(item, questions):
    """Put `item` in grooming: it waits on the operator's answers to
    `questions`, out of every ready queue. Mirrors _park: the claim and stage
    are released, a `blocked:` reason is kept (ungroom returns to blocked), a
    park is superseded. Refuses closed items. False when nothing changes."""
    st = item.get("status")
    if st in ("done", "dropped"):
        raise WiError(1, f"{item.id} is {st}; a closed item cannot be groomed")
    if st == "grooming" and item.get("grooming") == questions:
        return False
    item.meta.update(status="grooming", grooming=questions, parked=None,
                     owner=None, claimed=None, stage=None)
    item.append_note(f"- {today()} grooming: {questions}")
    item.touch()
    return True


def cmd_groom(args):
    _one_line("questions", args.questions)
    questions = (args.questions or "").strip()
    if not questions:
        raise WiError(1, "groom takes the open questions")
    root = resolve_root(args.root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        if _groom(item, questions):
            save_item(root, item)
    print(f"grooming {item.id}")
    return 0


def cmd_ungroom(args):
    """Back to `todo`, or to `blocked` when the item still carries a blocked
    reason; never to `doing` (the claim was released on groom)."""
    root = resolve_root(args.root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        if item.get("status") != "grooming":
            raise WiError(1, f"{item.id} is {item.get('status')}, not grooming")
        status = "blocked" if item.get("blocked") else "todo"
        item.meta.update(status=status, grooming=None)
        item.append_note(f"- {today()} ungroomed")
        item.touch()
        save_item(root, item)
    print(f"ungroomed {item.id} -> {status}")
    return 0


def cmd_migrate_parked(args):
    """Convert `status: blocked` items whose reason starts with PARKED (the
    convention before `parked` existed) to parked. Dry run unless --apply."""
    root = resolve_root(args.root)
    rows = []
    with Lock(root, commit=args.apply):
        changed = []
        for item in load_all(root):
            if item.get("status") != "blocked":
                continue
            reason = parked_reason(item.get("blocked"))
            if reason is None:
                continue
            rows.append((item.id, reason))
            if args.apply:
                original = item.get("blocked")
                item.meta["blocked"] = None
                _park(item, reason, note=f"parked (migrated from blocked: "
                                         f"{original})")
                changed.append(item)
        save_items(root, changed)
    verb = "parked" if args.apply else "would park"
    for iid, reason in rows:
        print(f"{verb}\t{iid}\t{reason}")
    print(f"{len(rows)} {'migrated' if args.apply else 'to migrate (dry run; --apply to write)'}")
    return 0


def cmd_repair_escapes(args):
    """One-time repair of values an older wi escape-amplified: its reader did
    not unescape what its writer escaped, so every rewrite of a quoted value
    added a layer of backslashes (`"` -> `\\"` -> `\\\\\\"`). The file still
    loads. The test is a heuristic: it lists every value (quoted or not — the
    current writer may have rewritten an amplified value bare) whose every
    backslash pairs as `\\\\` or `\\"`, with all such layers peeled — and a
    value can be meant that way (a title about escapes), so review the list
    first: a dry run until --apply; --id and --key narrow what it touches, and
    `wi set` fixes one value by hand instead."""
    root = resolve_root(args.root)
    rows, changed = [], []
    with Lock(root, commit=args.apply):
        for item in load_all(root, archived=True):
            if args.id and item.id != args.id:
                continue
            fixes = []
            for key in [k for k in FIELD_ORDER if k in item.meta] + \
                    [k for k in item.extra if k not in FIELD_ORDER]:
                if args.key and key != args.key:
                    continue
                val = item.meta.get(key)
                fix = (lambda v: _deamplify(v) if isinstance(v, str) else v)
                if isinstance(val, dict):
                    new = {k: fix(v) for k, v in val.items()}
                    pairs = [(val[k], new[k]) for k in val]
                elif isinstance(val, list):
                    new = [fix(v) for v in val]
                    pairs = list(zip(val, new))
                else:
                    new = fix(val) if isinstance(val, str) else val
                    pairs = [(val, new)]
                pairs = [(a, b) for a, b in pairs if a != b]
                if pairs:
                    fixes.append((key, new, pairs))
            for key, new, pairs in fixes:
                rows.extend((item.id, key, a, b) for a, b in pairs)
                if args.apply:
                    item.meta[key] = new
            if args.apply and fixes:
                changed.append(item)
        save_items(root, changed)
    verb = "repaired" if args.apply else "would repair"
    for iid, key, old, new in rows:
        print(f"{verb}\t{iid}\t{key}\t{json.dumps(old, ensure_ascii=False)}"
              f" -> {json.dumps(new, ensure_ascii=False)}")
    print(f"{len(rows)} " + ("repaired" if args.apply else
                             "to repair (dry run; --apply to write)"))
    return 0


def cmd_set(args):
    root = resolve_root(args.root)
    field, value = args.field, args.value
    _one_line("value", value)
    if field in ("id", "created"):
        raise WiError(1, f"'{field}' is immutable")
    if field not in FIELD_ORDER:
        raise WiError(1, f"unknown field '{field}'")
    if field == "short_display_name":
        # stripped; blank (whitespace-only included) clears, as "" does
        value = _short_name_arg(value) or ""
    with Lock(root):
        items = load_all(root, archived=True)
        by_id = {it.id: it for it in items}
        item = resolve_id(items, args.id)
        if value in ("", "—", "--clear"):
            item.meta[field] = None
        elif field in LIST_FIELDS:
            item.meta[field] = [v.strip() for v in value.split(",") if v.strip()]
        elif field in INT_FIELDS:
            # same range as `add -p`; here a clean exit-1 usage error
            try:
                num = int(value)
            except ValueError:
                num = None
            if num is None or not 0 <= num <= 4:
                raise WiError(1, f"{field} must be an integer 0-4, got '{value}'")
            item.meta[field] = num
        elif field == "status" and value == "parked":
            # parking releases the claim and records a reason: `wi park` is
            # the one path in, so set never leaves a half-parked item
            if item.get("status") != "parked":
                raise WiError(1, f"use wi park {item.id} \"<reason>\" to park an item")
        elif field == "status" and value == "grooming":
            # like parked: `wi groom` is the one path in, with the questions
            if item.get("status") != "grooming":
                raise WiError(1, f"use wi groom {item.id} \"<questions>\" to "
                                 "groom an item")
        elif field == "status" and item.get("status") == "parked":
            # leaving parked by set is an unpark: the reason goes with it
            item.meta.update(status=value, parked=None)
            item.append_note(f"- {today()} unparked (set status {value})")
        elif field == "status" and item.get("status") == "grooming":
            # leaving grooming by set is an ungroom: the questions go with it
            item.meta.update(status=value, grooming=None)
            item.append_note(f"- {today()} ungroomed (set status {value})")
        else:
            item.meta[field] = value
        # mirror cmd_add: deps/parent must resolve; ext: never does; --force
        # bypasses a dangling target but never a self-reference
        if field == "deps":
            for dep in item.get("deps", []):
                if dep == item.id:
                    raise WiError(1, f"'{dep}' cannot depend on itself")
                if not dep.startswith("ext:") and dep not in by_id and not args.force:
                    raise WiError(1, f"dep '{dep}' does not resolve (--force to set anyway)")
        if field == "parent" and item.get("parent"):
            if item.get("parent") == item.id:
                raise WiError(1, f"'{item.id}' cannot be its own parent")
            if item.get("parent") not in by_id and not args.force:
                raise WiError(1, f"parent '{item.get('parent')}' does not resolve")
        errs = item.validate()
        if errs:
            raise WiError(3, "; ".join(errs))
        item.touch()
        save_item(root, item)
    print(f"set {item.id} {field}")
    return 0


def cmd_ls(args):
    root = resolve_root(args.root)
    items = load_all(root, archived=args.status == "all")
    by_id = DepIndex(root, items, archived=args.status == "all")
    statuses = (set(STATUSES) if args.status == "all"
                else set((args.status or "todo,doing,blocked,grooming")
                         .split(",")))
    rows = [it for it in items if it.get("status") in statuses]
    if args.dep:
        # items depending on an id: resolve it when it names an item (a
        # prefix or alias works), else match the dep string as written; an
        # ambiguous prefix is an error, not an empty list
        try:
            dep = resolve_id(load_all(root, archived=True), args.dep).id
        except AmbiguousId:
            raise
        except WiError as e:
            if e.code != 2:  # only "no item matching" falls back
                raise
            dep = args.dep
        rows = [it for it in rows if dep in it.get("deps", [])]
    if args.type:
        rows = [it for it in rows if it.get("type", "task") == args.type]
    if args.tag:
        rows = [it for it in rows if args.tag in it.get("tags", [])]
    if args.owner:
        rows = [it for it in rows if it.get("owner") == args.owner]
    if args.ready:
        rows = [it for it in rows if is_ready(it, by_id)]
    rows = rank_ready(rows)
    if args.json:
        print(json.dumps([item_json(it, by_id) for it in rows], indent=1))
    else:
        for it in rows:
            line = (f"{it.id}\tP{it.get('priority', 2)}\t{it.get('status')}\t"
                    f"{it.get('stage') or '-'}\t{it.get('owner') or '-'}\t"
                    f"{item_title(it)}")
            print(line if args.plain else line.expandtabs(2))
    return 0 if rows else 2


def cmd_show(args):
    if args.card is None and args.all:
        raise WiError(1, "--all goes with --card N")
    if args.card is not None:
        if args.brief:
            raise WiError(1, "--brief and --card are exclusive")
        if not DECISION_N_RE.fullmatch(args.card):
            raise WiError(1, "--card takes a decision number (1-9 digits)")
    root = resolve_root(args.root)
    items = load_all(root, archived=True)
    item = resolve_id(items, args.id)
    if args.card is not None:
        return show_card(root, item, int(args.card), args.all, args.json)
    by_id = DepIndex(root, items, archived=True)
    if args.json:
        rec = item_json(item, by_id)
        rec["body"] = item.desc
        rec["sections"] = dict(item.sections)
        rec["acceptance"] = parse_acceptance(item)
        rec["blocked_by_unresolved"] = unmet_deps(item, by_id)
        print(json.dumps(rec, indent=1))
    elif args.brief:
        for key in FIELD_ORDER:
            val = item.meta.get(key)
            if val in (None, [], {}):
                continue
            if isinstance(val, list):
                val = ", ".join(val)
            if key != "refs":
                print(f"{key}: {val}")
        summary = item.summary()
        if summary:
            print("\n" + summary)
        print("\n## Handoff\n" + emit_handoff(item.handoff()))
        if item.get("refs"):
            print("\nrefs:")
            for ref in item.get("refs"):
                print(f"- {ref}")
    else:
        print(item.render(plain=False), end="")
    return 0


def show_card(root, item, n, every, as_json):
    """`show <id> --card N` (3b51 W3): the current card record of decision
    N, the last `card:` line for N, checked by read_card_record; with
    `every`, each revision's line in file order, every file checked, the
    last marked current. Exit 2 when N has no `card:` line on the item;
    3 when a file is missing, unreadable or mismatched. Read-only."""
    lines = card_lines(item).get(n)
    if not lines:
        raise WiError(2, f"decision {n} has no card record on {item.id}: a "
                         "card stored before v5, or a headline only; read it "
                         "by the decisions skill's legacy reference")
    if not every:
        lines = lines[-1:]
    revs = []
    for rel, rev, fmt in lines:
        data, rec = read_card_record(root, item.id, n, rel, rev, fmt)
        revs.append({"path": rel, "rev": rev, "format": fmt,
                     "sha256": hashlib.sha256(data).hexdigest(),
                     "data": data, "record": rec})
    if every:
        if as_json:
            print(json.dumps({"item": item.id, "n": n, "revisions": [
                {"path": r["path"], "rev": r["rev"], "format": r["format"],
                 "sha256": r["sha256"], "current": i == len(revs) - 1}
                for i, r in enumerate(revs)]}, indent=1, ensure_ascii=False))
        else:
            for i, r in enumerate(revs):
                print(f"{r['path']} rev {r['rev']} · {r['format']} "
                      f"sha256:{r['sha256']}"
                      + (" (current)" if i == len(revs) - 1 else ""))
        return 0
    r = revs[0]
    if as_json:
        print(json.dumps({"item": item.id, "n": n, "path": r["path"],
                          "rev": r["rev"], "format": r["format"],
                          "sha256": r["sha256"], "record": r["record"]},
                         indent=1, ensure_ascii=False))
        return 0
    sys.stdout.write(f"card: {r['path']}\nrev: {r['rev']}\n"
                     f"format: {r['format']}\nsha256: {r['sha256']}\n\n")
    sys.stdout.flush()
    # the file's bytes as written, never re-serialized
    sys.stdout.buffer.write(r["data"])
    sys.stdout.buffer.flush()
    return 0


def parse_acceptance(item):
    out = []
    for line in (item.section("Acceptance") or "").split("\n"):
        m = re.match(r"^- \[([ xX])\]\s*(.*)$", line.strip())
        if m:
            out.append({"text": m.group(2), "done": m.group(1) != " "})
    return out


def cmd_next(args):
    root = resolve_root(args.root)
    if args.pipeline:
        return next_pipeline(root, args)
    items = load_all(root)
    by_id = DepIndex(root, items)
    grouped, closed = split_by_status(items)
    doing = sorted(grouped["doing"],
                   key=lambda it: (it.get("priority", 2), it.get("updated", "")))
    ready = rank_ready([it for it in grouped["todo"] if is_ready(it, by_id)])
    waiting = len(grouped["todo"]) - len(ready)
    stale_after = parse_duration(args.stale)
    if args.json:
        print(json.dumps({"doing": [item_json(it) for it in doing],
                          "blocked": [item_json(it) for it in grouped["blocked"]],
                          "ready": [item_json(it) for it in ready[:args.limit]],
                          "counts": {"ready": len(ready), "waiting": waiting,
                                     "parked": len(grouped["parked"]),
                                     "grooming": len(grouped["grooming"]),
                                     "done": len(closed)}}, indent=1))
        return 0
    out = []
    if args.plain:
        for section, its in (("doing", doing), ("blocked", grouped["blocked"]),
                             ("ready", ready[:args.limit])):
            for it in its:
                out.append("\t".join([section, it.id, f"P{it.get('priority', 2)}",
                                      it.get("status"), it.get("stage") or "-",
                                      it.get("owner") or "-", item_title(it)]))
        print("\n".join(out))
        return 0 if (doing or grouped["blocked"] or ready) else 2
    if doing:
        out.append("DOING")
        for it in doing:
            claimed = it.get("claimed")
            stale = ""
            if claimed:
                dt = datetime.strptime(claimed, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
                if (datetime.now(timezone.utc) - dt).total_seconds() > stale_after:
                    stale = " stale?"
            out.append(f"  P{it.get('priority', 2)} {it.id}  {item_title(it)}   "
                       f"{it.get('owner') or '-'} {age_str(claimed)}{stale}")
            nxt = it.handoff().get("next")
            if nxt:
                out.append(f"     next: {nxt}")
    if grouped["blocked"]:
        out.append("BLOCKED")
        for it in grouped["blocked"]:
            out.append(f"  P{it.get('priority', 2)} {it.id}  {item_title(it)}   "
                       f"blocked: {it.get('blocked')}")
    if ready:
        out.append("READY")
        for it in ready[:args.limit]:
            out.append(f"  P{it.get('priority', 2)} {it.id}  {item_title(it)}")
    parked = (f" · {len(grouped['parked'])} parked (wi ls --status parked)"
              if grouped["parked"] else "")
    if grouped["grooming"]:
        parked += f" · {len(grouped['grooming'])} grooming (wi needs-input)"
    out.append(f"{max(0, len(ready) - args.limit)} more ready · {waiting} waiting "
               f"on deps{parked} · {len(closed)} done (wi ls --status done)")
    print("\n".join(out))
    return 0 if (doing or grouped["blocked"] or ready) else 2


def next_pipeline(root, args):
    with Lock(root, commit=bool(args.claim)):
        items = load_all(root)
        by_id = DepIndex(root, items)
        ordered = pipeline_queues(items, by_id)
        if args.non_interactive:
            ordered = [(q, it) for q, it in ordered if it.get("mode") != "interactive"]
        if args.one or args.claim:
            if not ordered:
                print("no eligible work", file=sys.stderr)
                return 2
            queue, item = ordered[0]
            if args.claim:
                _claim(item, args.claim, steal=False)
                if not item.get("stage"):
                    item.meta["stage"] = "implement"
                save_item(root, item)
            rec = item_json(item, by_id)
            rec["queue"] = queue
            print(json.dumps(rec, indent=1) if args.json else
                  f"{queue}\t{item.id}\t{item_title(item)}")
            return 0
    if args.json:
        print(json.dumps([dict(item_json(it, by_id), queue=q)
                          for q, it in ordered], indent=1))
    else:
        for q, it in ordered:
            print(f"{q}\t{it.id}\tP{it.get('priority', 2)}\t{item_title(it)}")
    return 0 if ordered else 2


def cmd_prime(args):
    root = resolve_root(args.root, warn_stores=False)
    items = load_all(root)
    by_id = DepIndex(root, items)
    grouped, closed = split_by_status(items)
    me = default_owner(root)
    doing = sorted(grouped["doing"], key=lambda it: (
        it.get("owner") != me, it.get("priority", 2)))
    ready = rank_ready([it for it in grouped["todo"] if is_ready(it, by_id)])
    n_open = sum(len(v) for v in grouped.values())
    budget = args.budget
    lines = [f"wi: {root} · {n_open} open · {len(grouped['doing'])} doing · "
             f"{len(grouped['blocked'])} blocked · run `wi show <id>` before "
             f"working an item, `wi handoff` at every stop"]
    # the warnings and the deprecation notices are header: their tokens
    # are reserved from the budget, and they are inserted after trimming so
    # trimming never drops them. The two-store check runs however the root
    # was found (5f46).
    # d1e9: at most one store-repo line, the first in table order; prime
    # stays lock-free (stat checks and one status, no host or remote reads)
    rs = store_repo_state(root)
    repo_line = [line for _, line in store_repo_checks(root, rs, full=False)]
    header = [w for w in (custody_warning(root, rs), two_store_warning(root))
              if w] + repo_line[:1] + env_notices() + location_notices(root)
    reserved = sum(tokens(h) + 1 for h in header)
    spent = tokens(lines[0]) + reserved

    def fits(line):
        return spent + tokens(line) + 1 <= budget

    def take(line):
        nonlocal spent
        if fits(line):
            lines.append(line)
            spent += tokens(line) + 1
            return True
        return False

    holds = [it for it in items if it.get("status") not in ("done", "dropped")
             and "hold" in it.get("tags", [])]
    if holds:
        # an operator hold gates what may move: first, before any work line
        take(f"HOLD {len(holds)}: " + " ".join(
            f"{it.id} ({item_title(it)})" for it in holds[:3]))
    for it in doing:
        who = "you" if it.get("owner") == me else it.get("owner", "-")
        take(f"DOING  P{it.get('priority', 2)} {it.id}  {item_title(it)}  "
             f"({who}, {age_str(it.get('claimed'))})")
        h = it.handoff()
        if h.get("next"):
            take(f"       next: {h['next']}")
        if h.get("doing") and spent < budget * 3 // 4:
            take(f"       doing: {h['doing']}")
    if grouped["blocked"]:
        take(f"BLOCKED {len(grouped['blocked'])}: " + " ".join(
            f"{it.id} ({it.get('blocked')})" for it in grouped["blocked"][:3]))
    if grouped["grooming"]:
        # waiting on the operator: a count; wi needs-input lists the questions
        take(f"GROOMING {len(grouped['grooming'])} (wi needs-input)")
    if grouped["parked"]:
        # deliberately deferred: a count, never a list — see wi ls --status parked
        take(f"PARKED {len(grouped['parked'])} (wi ls --status parked)")
    shown = 0
    for i, it in enumerate(ready):
        prefix = "READY  " if shown == 0 else "       "
        if not take(f"{prefix}P{it.get('priority', 2)} {it.id}  {item_title(it)}"):
            break
        shown += 1
    if shown < len(ready):
        lines.append(f"       … (+{len(ready) - shown}, wi next)")
    text = "\n".join(lines)
    while tokens(text) + reserved > budget and len(lines) > 1:
        # never pop the header: with only [header, "…"] left, drop the "…"
        lines.pop(-2 if lines[-1].startswith("       …") and len(lines) > 2
                  else -1)
        text = "\n".join(lines)
    if header:
        lines[1:1] = header
        text = "\n".join(lines)
    print(text)
    return 0


def needs_input(items):
    """Every open item awaiting the operator, as (item, [(kind, n, text)]):
    kind `grooming` (its questions) or `decision` (an unanswered
    `decision N:` line). Parked items count; closed ones never do."""
    out = []
    for it in items:
        if it.get("status") in ("done", "dropped"):
            continue
        asks = []
        if it.get("status") == "grooming":
            asks.append(("grooming", None, it.get("grooming") or ""))
        asks += [("decision", n, text) for n, text in unanswered_decisions(it)]
        if asks:
            out.append((it, asks))
    return out


def _json_decisions(it, asks):
    """needs-input --json's decision records: text, raised and showings."""
    raised, shown = decision_raised(it), decision_showings(it)
    return [dict({"n": n, "text": text, "raised": raised.get(n)},
                 **shown.get(n, _no_showing()))
            for kind, n, text in asks if kind == "decision"]


def cmd_needs_input(args):
    root = resolve_root(args.root)
    rows = needs_input(rank_ready(load_all(root)))
    if args.json:
        print(json.dumps([{"id": it.id, "title": it.get("title"),
                           "short_display_name":
                               it.meta.get("short_display_name"),
                           "status": it.get("status"),
                           "grooming": it.get("grooming"),
                           "decisions": _json_decisions(it, asks)}
                          for it, asks in rows], indent=1))
        return 0 if rows else 2
    for it, asks in rows:
        for kind, n, text in asks:
            if args.plain:
                # the title cell is fourth: id, kind and N keep their
                # columns, and the free text (never checked for tabs) stays
                # last
                print("\t".join([it.id, kind, "-" if n is None else str(n),
                                 item_title(it), text]))
            else:
                label = "grooming" if n is None else f"decision {n}"
                print(f"{it.id}  {item_title(it)}  {label}: {text}")
    return 0 if rows else 2


# ── estate: the read-only cross-repo sweep ─────────────────────────────────

ESTATE_STORES = STORE_LOCATIONS   # .work-items first: it wins a dedupe
ESTATE_COUNTED = ("todo", "doing", "blocked", "parked", "grooming", "done",
                  "dropped")
ESTATE_LISTS = ("decisions", "security", "stale", "problems")
ESTATE_CAP = 20      # per store, per list; the rest is a count in `omitted`
# A hint, not a verdict: the work-review skill judges what is a security item.
SECURITY_TAG_RE = re.compile(r"secur|privacy|vuln|cve", re.I)
SECURITY_TITLE_RE = re.compile(
    r"\b(secur\w*|vulnerab\w*|cve-\d+|secrets?|credentials?|passwords?|"
    r"api[ -]keys?|private keys?|exploit\w*|leak(?:s|ed|ing)?|exposed|"
    r"exposure|privacy)\b", re.I)


def _within(path, base):
    """True when `path` resolves (symlinks followed) inside `base`, a
    resolved directory. The one symlink rule of `estate`."""
    try:
        real = Path(os.path.realpath(path))
    except (OSError, ValueError):
        return False
    return real == base or base in real.parents


def _parse_when(text):
    """A `claimed:` or `raised:` value as an aware datetime, else None."""
    for fmt in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(text), fmt).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def _printable(obj):
    """Every string in `obj` made encodable: a path byte that is not UTF-8
    (a lone surrogate from os.listdir) shows as \\xe9, as _git shows it."""
    if isinstance(obj, str):
        return obj.encode("utf-8", "surrogateescape").decode(
            "utf-8", "backslashreplace")
    if isinstance(obj, list):
        return [_printable(v) for v in obj]
    if isinstance(obj, dict):
        return {_printable(k): _printable(v) for k, v in obj.items()}
    return obj


def estate_default_dirs(cwd=None):
    """The parent of the current repo's main checkout: a linked worktree
    resolves through the common git dir, a submodule to its superproject.
    Refused (WiError 1) outside a repo, and when that parent is $HOME, an
    ancestor of it, or / — a sweep that wide is never a default."""
    cwd = cwd or os.getcwd()
    r = _git(cwd, "rev-parse", "--show-superproject-working-tree")
    if r is not None and r.returncode == 0 and r.stdout.strip():
        cwd = r.stdout.strip()
    r = _git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if r is None or r.returncode != 0 or not r.stdout.strip():
        raise WiError(1, "not in a git repo; name the dir to scan with --dir")
    common = Path(r.stdout.strip())
    top = common.parent if common.name == ".git" else common
    cand = Path(os.path.realpath(top.parent))
    home = Path(os.path.realpath(Path.home()))
    if cand == home or cand in home.parents or cand == Path(cand.anchor):
        raise WiError(1, f"the default scan dir would be {cand}, which is "
                         "$HOME, above it, or /; name the dir with --dir")
    return [cand]


def estate_is_security(item):
    return (any(SECURITY_TAG_RE.search(str(t)) for t in item.get("tags", []))
            or bool(SECURITY_TITLE_RE.search(str(item.get("title", "")))))


def _estate_load(paths, base, problems):
    """Load each item file with wi's own loader, one file at a time, so a
    bad file is a reported problem rather than a crash or a lost store. A
    file that resolves outside `base` is never opened."""
    items = []
    for path in paths:
        if not _within(path, base):
            problems.append({"path": str(path),
                             "error": "symlink out of the scanned dir; not read"})
            continue
        try:
            if not path.is_file():
                problems.append({"path": str(path),
                                 "error": "not a regular file; not read"})
                continue
            if path.stat().st_size == 0:   # reported here, not warned on stderr
                problems.append({"path": str(path), "error": STALE_RESERVATION})
                continue
            items += load_paths([path])
        except Exception as e:  # a foreign store must never stop the sweep
            problems.append({"path": str(path), "error": str(e)})
    return items


def _estate_cap(rec, cap):
    rec["omitted"] = {}
    for key in ESTATE_LISTS:
        rest = len(rec[key]) - cap
        rec["omitted"][key] = max(0, rest)
        if rest > 0:
            rec[key] = rec[key][:cap]
    return rec


def estate_store(store, base, top, stale_after, now, cap=ESTATE_CAP):
    """One store's summary, read-only: no lock, no git, no write."""
    problems = []
    rec = {"store": str(store), "counts": {}, "ready": [], "decisions": [],
           "stale": [], "security": [], "problems": problems}
    try:
        items = _estate_load(item_paths(store), base, problems)
        archived = []
        if (store / "archive").is_dir():
            archived = _estate_load(sorted((store / "archive").glob("*/*.md")),
                                    base, problems)
    except Exception as e:  # the items dir itself unreadable
        problems.append({"path": str(store), "error": str(e)})
        return _estate_cap(rec, cap)
    try:
        by_id = DepIndex(store, items + archived, archived=True)
        grouped, closed = split_by_status(items)
        counts = {k: 0 for k in ESTATE_COUNTED}
        for it in items:
            st = it.get("status")
            if st in counts:
                counts[st] += 1
        ready = rank_ready([it for it in grouped["todo"] if is_ready(it, by_id)])
        counts["open"] = sum(len(v) for v in grouped.values())
        counts["ready"] = len(ready)
        rec["counts"] = counts
        rec["ready"] = [{"id": it.id, "title": it.get("title"),
                         "short_display_name": it.meta.get("short_display_name"),
                         "priority": it.get("priority", 2),
                         "type": it.get("type"), "tags": it.get("tags", [])}
                        for it in ready[:top]]
        open_items = [it for it in items
                      if it.get("status") not in ("done", "dropped")]
        for it in rank_ready(open_items):
            raised, shown = decision_raised(it), decision_showings(it)
            for n, text in unanswered_decisions(it):
                when = raised.get(n)
                dt = _parse_when(when) if when else None
                rec["decisions"].append(dict({
                    "id": it.id, "title": it.get("title"),
                    "short_display_name": it.meta.get("short_display_name"),
                    "n": n, "text": text, "raised": when,
                    "age_days": (now - dt).days if dt else None},
                    **shown.get(n, _no_showing())))
            if estate_is_security(it):
                rec["security"].append({
                    "id": it.id, "title": it.get("title"),
                    "short_display_name": it.meta.get("short_display_name"),
                    "status": it.get("status"),
                    "priority": it.get("priority", 2),
                    "tags": it.get("tags", [])})
        for it in grouped["doing"]:
            dt = _parse_when(it.get("claimed"))
            if dt and (now - dt).total_seconds() > stale_after:
                rec["stale"].append({"id": it.id, "title": it.get("title"),
                                     "short_display_name":
                                         it.meta.get("short_display_name"),
                                     "owner": it.get("owner"),
                                     "claimed": it.get("claimed"),
                                     "age": age_str(it.get("claimed"))})
    except Exception as e:  # a store whose values defeat ranking
        problems.append({"path": str(store), "error": f"summary failed: {e}"})
    return _estate_cap(rec, cap)


def _read_pointer(path, key):
    """The value of a one-line git pointer file (`gitdir: X` in a .git
    file, or a bare `X` in a commondir file), resolved against the file's
    own dir; None when it is missing, not a regular file (a FIFO would hang
    the read, a device never ends), unreadable, or holds a NUL. A file
    read, never a git call."""
    try:
        if not stat.S_ISREG(os.stat(path).st_mode):
            return None
        with open(path, encoding="utf-8", errors="surrogateescape") as fh:
            text = fh.read(4096).strip()
    except (OSError, ValueError):
        return None
    if "\0" in text:
        return None
    if key:
        if not text.startswith(key):
            return None
        text = text[len(key):].strip()
    if not text:
        return None
    try:
        return Path(os.path.realpath(Path(path).parent / text))
    except (OSError, ValueError):
        return None


def git_common_dir(repo):
    """(common dir, is main checkout) for a repo dir, by file reads only.
    A `.git` directory is its own common dir (the main checkout). A `.git`
    file points at its gitdir; that gitdir's `commondir` file, when there is
    one (a linked worktree), points at the shared dir. A submodule's or a
    --separate-git-dir clone's gitdir has none, so it is its own. Not a git
    repo, or an unreadable pointer: the dir's own realpath, not a main."""
    g = repo / ".git"
    if g.is_dir():
        return os.path.realpath(g), True
    if g.is_file():
        gitdir = _read_pointer(g, "gitdir:")
        if gitdir is not None:
            common = _read_pointer(gitdir / "commondir", None)
            return str(common or gitdir), False
    return os.path.realpath(repo), False


def _repo_candidates(dirs):
    """[(d, base, name, repo)] for every repo dir one level under each dir
    (not hidden, resolving inside its dir), one per git common dir: the main
    checkout when it is among them, else the first seen. Also the skipped
    duplicates, each with its reason."""
    found = []
    for d in dirs:
        d = Path(d)
        if not d.is_dir():
            raise WiError(1, f"not a directory: {d}")
        base = Path(os.path.realpath(d))
        try:
            entries = os.listdir(d)
        except OSError as e:
            raise WiError(3, f"{d}: {e}") from None
        # real dirs before symlinked aliases, so a tie keeps the real name
        for name in sorted(entries, key=lambda n: (os.path.islink(d / n), n)):
            repo = d / name
            if (name.startswith(".") or not repo.is_dir()
                    or not _within(repo, base)):
                continue
            key, main = git_common_dir(repo)
            found.append((key, main, d, base, name, repo))
    keep = {}
    for key, main, *rest in found:
        if key not in keep or (main and not keep[key][0]):
            keep[key] = (main, rest)
    kept, skipped = [], []
    for key, main, d, base, name, repo in found:
        winner = keep[key][1]
        if winner[3] is repo:
            kept.append((d, base, name, repo))
            continue
        other = winner[3]
        if os.path.realpath(repo) == os.path.realpath(other):
            reason = f"symlink alias of {other}"
        elif main:
            reason = f"same git dir as {other}"
        else:
            reason = f"linked worktree of {other} (shares {key})"
        skipped.append({"repo": name, "path": str(repo),
                        "path_raw": _raw(repo), "reason": reason})
    return kept, skipped


def _raw(path):
    """A path's exact bytes, base64: round-trips a name that is not UTF-8,
    which the printable `path` cannot (os.fsdecode(b64decode(path_raw)))."""
    return base64.b64encode(os.fsencode(str(path))).decode("ascii")


def estate_scan(dirs, top=5, stale="24h", now=None, cap=ESTATE_CAP):
    """Every work-item store one level under each dir, summarised."""
    if top < 0:
        raise WiError(1, f"--top must be 0 or more, not {top}")
    now = now or datetime.now(timezone.utc)
    stale_after = parse_duration(stale)
    kept, skipped = _repo_candidates(dirs)
    repos = []
    for d, base, name, repo in kept:
        seen = set()   # 5f46: one record per real path; the first spelling
        for rel in ESTATE_STORES:
            store = repo / rel
            if not (store / "items").is_dir():
                continue
            if not (_within(store, base) and _within(store / "items", base)):
                continue
            real = os.path.realpath(store)
            if real in seen:
                continue
            seen.add(real)
            rec = {"repo": name, "path": str(repo), "path_raw": _raw(repo)}
            rec.update(estate_store(store, base, top, stale_after, now, cap))
            rec["store"] = rel
            repos.append(rec)
    repos.sort(key=lambda r: (r["path"], r["store"]))
    return {"dirs": [str(Path(d)) for d in dirs], "stale_after": stale,
            "generated": now.strftime("%Y-%m-%dT%H:%MZ"), "repos": repos,
            "skipped": skipped}


def _estate_title(rec):
    return title_cell(rec["title"], rec["short_display_name"])


def _estate_text(report):
    out = [f"wi estate: scanned {', '.join(report['dirs'])} · "
           f"{len(report['repos'])} store(s)"]
    for r in report["repos"]:
        c = r["counts"]
        head = f"{r['repo']}  ({r['store']})"
        if c:
            head += (f"  {c['open']} open · {c['doing']} doing · "
                     f"{c['blocked']} blocked · {c['ready']} ready")
        out.append(head)
        for s in r["security"]:
            out.append(f"  SECURITY  P{s['priority']} {s['id']}  {_estate_title(s)}"
                       f"  [{s['status']}]")
        for d in r["decisions"]:
            age = f"  ({d['age_days']}d)" if d["age_days"] is not None else ""
            out.append(f"  DECISION  {d['id']}  {_estate_title(d)}  "
                       f"{d['n']}: {d['text']}{age}")
        for s in r["stale"]:
            out.append(f"  STALE     {s['id']}  {_estate_title(s)}  "
                       f"({s['owner'] or '-'}, {s['age']})")
        for it in r["ready"]:
            out.append(f"  READY     P{it['priority']} {it['id']}  "
                       f"{_estate_title(it)}")
        for p in r["problems"]:
            out.append(f"  PROBLEM   {p['path']}: {p['error']}")
        more = [f"{n} {k}" for k, n in r["omitted"].items() if n]
        if more:
            out.append(f"  … and {', '.join(more)} not shown (--json lists "
                       f"the first {ESTATE_CAP} of each)")
    for sk in report["skipped"]:
        out.append(f"skipped {sk['repo']}: {sk['reason']}")
    return "\n".join(out)


def cmd_estate(args):
    if args.root:
        raise WiError(1, "--root names one store; estate scans dirs of "
                         "repos: use --dir")
    dirs = args.dir or estate_default_dirs()
    report = _printable(estate_scan(dirs, top=args.top, stale=args.stale))
    if args.json:
        print(json.dumps(report, indent=1))
    else:
        print(_estate_text(report))
    return 0 if report["repos"] else 2

# ── import-todo ─────────────────────────────────────────────────────────────

def norm_title(title):
    return re.sub(r"\s+", " ", re.sub(r"[*~`]", "", title)).strip().lower()


def todo_marker(title):
    return "todo:" + hashlib.sha1(norm_title(title).encode()).hexdigest()[:8]


STRIKE_RE = re.compile(r"^~~(.+?)~~\s*[—-]+\s*(\w[\w /]*?)\s*(\d{4}-\d{2}-\d{2})?\s*(\(.*\))?\s*$")
REPO_TAG_RE = re.compile(r"\s*\((\S+) repo\)\s*$")
PRIORITY_PREFIX = {"HIGH": 0, "STILL OPEN": 1, "LOW": 4}


def parse_todo(text):
    """Yield dicts {title, desc, notes, status, closed, priority, tags, refs}
    for the three TODO shapes: ## sections, top-level `- **Title.**` bullets,
    and `- [ ]` checkbox lists (optionally inside ## sections)."""
    found = []
    # Historical content folded into <details> blocks (e.g. a resolved entry
    # keeping its original text) must not surface as sections: brainboy's
    # closed etcd item re-imported as open P2 through exactly this hole.
    text = re.sub(r"<details>.*?(</details>|\Z)", "", text, flags=re.S | re.I)
    desc0, sections = parse_body(text)
    blocks = [("", desc0)] + sections
    for heading, body in blocks:
        checkboxes = _parse_checkboxes(body)
        # bold-bullet items are a top-level shape (clustertool); bold bullets
        # inside a ## section are that section's content, not items
        bullets = _parse_bold_bullets(body) if not checkboxes and not heading else []
        if heading and not checkboxes:
            if heading.startswith("#"):  # "# TODO" title line inside desc0
                continue
            found.append(_section_item(heading, body))
        section_tag = slugify(heading)[:20] if heading else None
        for done, text_ in checkboxes:
            item = _bullet_item(text_)
            if section_tag and section_tag not in ("open",):
                item["tags"].append(section_tag)
            if done or section_tag == "done":
                item["status"], item["closed"] = "done", None
            found.append(item)
        for text_ in bullets:
            found.append(_bullet_item(text_))
    return [f for f in found if f]


def _parse_checkboxes(body):
    out, cur = [], None
    for line in body.split("\n"):
        m = re.match(r"^- \[([ xX])\] (.*)$", line)
        if m:
            if cur:
                out.append(cur)
            cur = (m.group(1) != " ", [m.group(2)])
        elif cur and (line.startswith((" ", "\t")) or not line.strip()):
            cur[1].append(line.strip())
        elif cur:
            out.append(cur)
            cur = None
    if cur:
        out.append(cur)
    return [(done, "\n".join(lines).strip()) for done, lines in out]


def _parse_bold_bullets(body):
    out, cur = [], None
    for line in body.split("\n"):
        if re.match(r"^- \*\*", line):
            if cur:
                out.append("\n".join(cur).strip())
            cur = [line[2:]]
        elif cur is not None and (line.startswith((" ", "\t")) or not line.strip()):
            cur.append(line.strip())
        elif cur is not None:
            out.append("\n".join(cur).strip())
            cur = None
    if cur:
        out.append("\n".join(cur).strip())
    return out


def _section_item(heading, body):
    item = {"status": "todo", "closed": None, "priority": None, "tags": [],
            "refs": [], "notes": ""}
    title = heading
    m = STRIKE_RE.match(title)
    if m:
        item["status"], item["closed"] = "done", m.group(3)
        title = m.group(1) + (" " + m.group(4) if m.group(4) else "")
    m = REPO_TAG_RE.search(title)
    if m:
        item["tags"].append("repo:" + m.group(1))
        title = REPO_TAG_RE.sub("", title)
    for prefix, prio in PRIORITY_PREFIX.items():
        if title.startswith(prefix + " —") or title.startswith(prefix + " -"):
            item["priority"] = prio
            title = title[len(prefix):].lstrip(" —-")
            break
    item["title"] = _fold(title)[:120]
    paras = body.strip().split("\n\n")
    item["desc"] = paras[0].strip() if paras else ""
    item["notes"] = "\n\n".join(p for p in paras[1:]).strip()
    for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", body):
        target = m.group(1)
        if not target.startswith(("http://", "https://")) and target not in item["refs"]:
            item["refs"].append(target)
    return item


# A struck entry is closed when the strike covers its whole title. The shapes:
# the bold title alone (`~~**T**~~ rest`, `**~~T~~** rest`); a strike opening
# on the bold title and closing later on the same line (`~~**T** rest~~`,
# anything after it on that line or below is description); and, with no bold,
# a struck first line with nothing after it, or a closure word or a date
# after a dash or opening a parenthesis (`~~T~~`, `~~T~~ (2026-09-01)`,
# `~~T~~ (done)`, `~~T~~ — DONE 2026-09-01`, `~~T~~ — fixed`). Any other text
# after it (`~~Migrate to PG15~~ — PG16 instead`, `~~X~~ (not yet)`) is a
# replacement or a caveat, not a closure. A strike over part of the title or
# only the trailing text is an edit, not a closure either: the entry stays
# open and keeps its markers. ~~ and ** are stripped from a closed entry's
# title; an empty strike never closes.
_NO_TILDES = r"(?:(?!~~).)"
STRUCK_TITLE_RE = re.compile(
    rf"^(?:~~\*\*({_NO_TILDES}+?)\*\*~~|\*\*~~({_NO_TILDES}+?)~~\*\*)"
    r"[.:]?\s*[—-]*\s*(.*)$", re.S)
STRUCK_BOLD_ENTRY_RE = re.compile(
    rf"^~~\*\*({_NO_TILDES}+?)\*\*((?:(?!~~)[^\n])*)~~(.*)$", re.S)
# a whole word: not `fixed-width`, `closed-source`, `done-ish` or `done?`
_CLOSURE_WORD = r"(?:done|fixed|landed|closed|resolved|dropped|merged|wontfix)(?![\w?-])"
_DATE = r"\d{4}-\d{2}-\d{2}"
STRUCK_PLAIN_LINE_RE = re.compile(
    r"^~~((?:(?!~~)[^\n])*\S(?:(?!~~)[^\n])*)~~\s*"
    rf"(?:(?=\(\s*(?:{_CLOSURE_WORD}|{_DATE}))(.*)|[—-]+\s*({_CLOSURE_WORD}.*|{_DATE}[.:]?\s*(?:\(.*\))?))?$",
    re.I)
BOLD_TITLE_RE = re.compile(r"^\*\*(.+?)\*\*[.:]?\s*[—-]*\s*(.*)$", re.S)


def _open_bullet_title(text):
    """(title, rest) by the open-entry rule: the bold title, else the first
    line. It is also every entry's title before bf1b, kept so a re-import
    recognises items imported under it."""
    m = BOLD_TITLE_RE.match(text)
    if m:
        return m.group(1).rstrip("."), m.group(2)
    first, _, rest = text.partition("\n")
    return first, rest


def _struck_bullet_title(text):
    """(title, rest) when a strike covers the entry's whole title, else None."""
    first, _, cont = text.partition("\n")
    found = None
    m = STRUCK_TITLE_RE.match(text)
    m2 = STRUCK_BOLD_ENTRY_RE.match(text)
    m3 = STRUCK_PLAIN_LINE_RE.match(first.rstrip())
    if m:
        found = (m.group(1) or m.group(2)), m.group(3)
    elif m2:
        inner = re.sub(r"^[.:]?\s*[—-]*\s*", "", m2.group(2).strip())
        tail = m2.group(3).lstrip(" \t")
        sep = " " if inner and tail and not tail.startswith("\n") else ""
        found = m2.group(1), (inner + sep + tail).strip()
    elif m3:
        note = (m3.group(2) or m3.group(3) or "").strip()
        found = m3.group(1), (note + "\n" + cont).strip()
    if not found or not _fold(found[0]).strip(" .*~"):
        return None
    return found[0].strip().rstrip("."), found[1]


def _bullet_item(text):
    item = {"status": "todo", "closed": None, "priority": None, "tags": [],
            "refs": [], "notes": ""}
    title, rest = _open_bullet_title(text)
    struck = _struck_bullet_title(text)
    if struck:
        item["status"] = "done"
        item["legacy_title"] = _fold(title)[:120]
        title, rest = struck
    item["title"] = _fold(title)[:120]
    item["desc"] = rest.strip()
    return item


def cmd_import_todo(args):
    root = resolve_root(args.root)
    text = Path(args.path).read_text()
    parsed = parse_todo(text)
    created_rows, skipped_rows, new_items = [], [], []
    with Lock(root, commit=not args.dry_run):
        items = load_all(root, archived=True)
        markers = {r for it in items for r in it.get("refs", [])}
        ids = taken_ids(root, items)
        for rec in parsed:
            marker = todo_marker(rec["title"])
            # an entry imported before bf1b carries its old title's marker
            legacy = rec.get("legacy_title")
            if legacy and todo_marker(legacy) in markers:
                skipped_rows.append((todo_marker(legacy), rec["title"]))
                continue
            if marker in markers:
                skipped_rows.append((marker, rec["title"]))
                continue
            markers.add(marker)
            date = rec["closed"] or today()
            iid = make_id(rec["title"], date, ids)
            meta = {"id": iid, "title": rec["title"], "type": "task",
                    "status": rec["status"], "priority": rec["priority"],
                    "tags": rec["tags"], "refs": rec["refs"] + [marker],
                    "created": date, "updated": date}
            if rec["status"] == "done":
                meta["closed"] = rec["closed"] or date
            sections = [("Handoff", emit_handoff({}))]
            if rec["notes"]:
                sections.append(("Notes", rec["notes"]))
            item = Item(meta, [], rec["desc"], sections)
            created_rows.append((iid, rec["title"]))
            new_items.append(item)
        if not args.dry_run:
            save_items(root, new_items)
    for iid, title in created_rows:
        print(f"{'would create' if args.dry_run else 'created'}\t{iid}\t{title}")
    for marker, title in skipped_rows:
        print(f"skipped\t{marker}\t{title}")
    return 0


# ── backlog-yaml export / import ────────────────────────────────────────────

BACKLOG_DEFAULTS = [("priority_order", "higher_is_more_important"),
                    ("status_field", "status"), ("blocked_field", "blocked"),
                    ("blocked_reason_field", "blocked_reason"),
                    ("review_feedback_field", "review_feedback"),
                    ("requires_field", "requires")]


def _yaml_scalar(v, json_ok=False):
    """A backlog.yaml value, double-quoted. `json_ok` (x_backlog values
    only): a list or mapping import stored JSON-encoded passes through raw,
    since JSON is YAML flow; any other value starting `[` or `{` — a title
    `[wip] x` — is quoted like the rest."""
    if isinstance(v, int):
        return str(v)
    v = str(v)
    if json_ok and v.startswith(("[", "{")):
        try:
            if isinstance(json.loads(v), (list, dict)):
                return v
        except ValueError:
            pass
    return '"' + _dq_escape(v) + '"'


def _yaml_notes(notes):
    """`notes:` as a `|-` block, or — when it holds a character a YAML
    loader reads as a line break or rejects raw (U+2028, NEL, a control
    character) — as a double-quoted scalar with those escaped."""
    if _DQ_ESCAPE_RE.search(notes.replace("\t", " ")):
        return ['    notes: "' + _dq_escape(notes).replace("\n", "\\n") + '"']
    return ["    notes: |-"] + ["      " + ln if ln.strip() else ""
                                for ln in notes.split("\n")]


# export appends an item's `ext:` deps to its blocked_reason (backlog.yaml
# `requires` holds only story ids); import strips that suffix back off
def split_ext_requires(reason, ext=None, whole=True):
    """(reason without the `requires ext:…` suffix export appends, [ext deps]).

    `ext` given (import --update: the store item's own `ext:` deps): strip
    only the exact suffix export wrote for those deps, so a reason that
    merely says "requires ext:" is kept whole. `ext` None (a new item): the
    last `; requires ext:` group is the suffix; a reason that is nothing but
    `requires ext:…` counts only when `whole` (the story is not blocked, so
    its reason can be empty)."""
    if not reason:
        return reason, []
    if ext is not None:
        suffix = "requires " + ", ".join(ext)
        if not ext:
            return reason, []
        if reason == suffix:
            return None, list(ext)
        if reason.endswith("; " + suffix):
            return reason[:-len(suffix) - 2], list(ext)
        return reason, []
    i = reason.rfind("; requires ext:")
    if i >= 0:
        head, group = reason[:i], reason[i + len("; requires "):]
    elif whole and reason.startswith("requires ext:"):
        head, group = None, reason[len("requires "):]
    else:
        return reason, []
    return head or None, [d.strip() for d in re.split(r", (?=ext:)", group)]


def _ext_deps(item):
    return [d for d in item.get("deps", []) if d.startswith("ext:")]


def _yaml_list(w, key, values, indent):
    if not values:
        w.append(f"{indent}{key}: []")
        return
    w.append(f"{indent}{key}:")
    w.extend(f"{indent}  - {_yaml_scalar(v)}" for v in values)


def _notes_for_export(item):
    parts = [item.desc] if item.desc else []
    h = item.handoff()
    if any(h.values()):
        parts.append("\n".join(f"{k}: {h[k] or '—'}" for k in HANDOFF_KEYS))
    notes = item.section("Notes")
    if notes:
        parts.append(notes)
    return "\n\n".join(parts)


def allocate_aliases(root, items):
    """Give every exportable item a stable X-NNN alias; returns items changed."""
    used = {}
    for it in items:
        alias = it.get("alias")
        if alias:
            p, n = alias.split("-")
            used[p] = max(used.get(p, 0), int(n))
    changed = []
    for it in sorted(items, key=lambda i: (i.get("created", ""), i.id)):
        if it.get("alias") or it.get("type", "task") == "epic":
            continue
        prefix = TYPE_PREFIX.get(it.get("type", "task"), "S")
        used[prefix] = used.get(prefix, 0) + 1
        it.meta["alias"] = f"{prefix}-{used[prefix]:03d}"
        changed.append(it)
    return changed


def emit_backlog(project, stories_items, by_id):
    w = [f"schema_version: 2", f"project: {project}", "defaults:"]
    w.extend(f"  {k}: \"{v}\"" for k, v in BACKLOG_DEFAULTS)
    w.append("stories:")
    if not stories_items:
        w[-1] = "stories: []"
    for it in sorted(stories_items, key=lambda i: i.get("alias", "")):
        m = it.meta
        w.append(f"  - id: {m['alias']}")
        w.append(f"    title: {_yaml_scalar(m['title'])}")
        w.append(f"    priority: {PRIO_TO_BACKLOG[it.get('priority', 2)]}")
        status = STATE_TO_BACKLOG.get((m.get("status"), m.get("stage")),
                                      STATE_TO_BACKLOG[(m.get("status"), None)])
        w.append(f"    status: {status}")
        requires, ext = [], []
        for dep in it.get("deps", []):
            if dep.startswith("ext:"):
                ext.append(dep)
            elif dep in by_id and by_id[dep].get("alias"):
                requires.append(by_id[dep].get("alias"))
        _yaml_list(w, "requires", requires, "    ")
        acceptance = [a["text"] for a in parse_acceptance(it)] or [m["title"]]
        _yaml_list(w, "acceptance", acceptance, "    ")
        testing = [re.sub(r"^- (\[[ xX]\] )?", "", ln).strip()
                   for ln in (it.section("Testing") or "").split("\n")
                   if ln.strip().startswith("- ")]
        # backlog.py validate rejects an empty testing list, so a placeholder
        # stands in when the item has no ## Testing section
        _yaml_list(w, "testing", testing or ["<unspecified>"], "    ")
        blocked = it.get("blocked") or ""
        if m.get("status") == "parked":
            blocked = _bridge_encode("PARKED", parked_reason,
                                     it.get("parked") or "")
        elif m.get("status") == "grooming":
            blocked = _bridge_encode("GROOMING", grooming_questions,
                                     it.get("grooming") or "")
        if ext:
            blocked = (blocked + "; " if blocked else "") + "requires " + ", ".join(ext)
        for key, val in (("blocked_reason", blocked),
                         ("review_feedback", it.get("feedback")),
                         ("claimed_by", it.get("owner")),
                         ("ticket_mode", it.get("mode")),
                         ("complexity", it.get("complexity"))):
            if val:
                w.append(f"    {key}: {_yaml_scalar(val)}")
        notes = _notes_for_export(it)
        if notes:
            w.extend(_yaml_notes(notes))
        for key, val in (it.get("x_backlog") or {}).items():
            w.append(f"    {key}: {_yaml_scalar(val, json_ok=True)}")
    return "\n".join(w) + "\n"


def cmd_export(args):
    if args.format != "backlog-yaml":
        raise WiError(1, f"unknown export format '{args.format}'")
    root = resolve_root(args.root)
    out = Path(args.path)
    done_out = Path(args.done_out) if args.done_out else \
        out.with_name(out.stem + "_done" + out.suffix)
    store = os.path.realpath(root)
    for p in (out, done_out):
        # an output inside the store would land among its files: an item
        # overwritten, or a .gitattributes whose filter git then runs
        if _inside(os.path.realpath(p), store):
            raise WiError(1, f"{p} lies inside the store {root}: export "
                             "writes outside it; nothing written")
    with Lock(root):
        items = load_all(root, archived=True)
        by_id = {it.id: it for it in items}
        exportable = [it for it in items if it.get("type", "task") != "epic"]
        written = allocate_aliases(root, exportable)
        for it in written:
            it.touch()
        save_items(root, written)
        active = [it for it in exportable if it.get("status") not in ("done", "dropped")]
        closed = [it for it in exportable if it.get("status") in ("done", "dropped")]
        project = args.project or Path.cwd().name
        atomic_write(out, emit_backlog(project, active, by_id))
        atomic_write(done_out, emit_backlog(project, closed, by_id))
    print(f"exported {len(active)} active -> {out}, {len(closed)} closed -> {done_out}")
    return 0


def _load_yaml_file(path):
    try:
        from ruamel.yaml import YAML
        return YAML(typ="safe").load(Path(path).read_text())
    except ImportError:
        pass
    try:
        import yaml
        return yaml.safe_load(Path(path).read_text())
    except ImportError:
        raise WiError(3, "import needs ruamel.yaml or PyYAML; neither is installed")


def _split_backlog_notes(notes):
    """Invert _notes_for_export: (desc, handoff|None, notes_text)."""
    lines = (notes or "").split("\n")
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^doing: ", ln) and all(
                i + j < len(lines) and lines[i + j].startswith(k + ": ")
                for j, k in enumerate(HANDOFF_KEYS)):
            start = i
            break
    if start is None:
        return (notes or "").strip(), None, ""
    h = {}
    for j, key in enumerate(HANDOFF_KEYS):
        v = lines[start + j].split(": ", 1)[1].strip()
        h[key] = "" if v == "—" else v
    return ("\n".join(lines[:start]).strip(), h,
            "\n".join(lines[start + 4:]).strip())


KNOWN_STORY_FIELDS = {"id", "title", "priority", "status", "requires", "acceptance",
                      "testing", "notes", "blocked_reason", "review_feedback",
                      "claimed_by", "ticket_mode", "complexity"}


def _fold(v):
    """A backlog value written into front matter or one bullet, folded to one
    line (whitespace collapsed, as import-todo folds titles). YAML block
    scalars (`review_feedback: |`) are common in ralph backlogs; folding keeps
    every word and every story, where rejecting would drop the story and
    break the requires links of the stories that name it. Control characters
    fold to a space as line breaks do: the writer refuses them."""
    if not isinstance(v, str):
        return v
    return re.sub(r"\s+", " ", _FRONT_REFUSE_RE.sub(" ", v)).strip()


# story fields that are free text: kept as read when one line (_fold_story);
# every other known field — an id, an enum, an owner — is always folded, so
# a padded `ticket_mode: " x "` lands trimmed. Extra (x_backlog) fields are
# text too.
STORY_TEXT_FIELDS = {"title", "blocked_reason", "review_feedback",
                     "acceptance", "testing"}


def _fold_story(v):
    """A backlog story value as import stores it: folded (_fold) only when it
    holds a line break or a character the writer refuses. A one-line value
    is kept as the YAML loader read it — surrounding spaces, runs of spaces
    and NBSP included — so an exported title imports back unchanged."""
    if isinstance(v, str) and ("\n" in v or _FRONT_REFUSE_RE.search(v)):
        return _fold(v)
    return v


def _story_value(story, key):
    """A backlog field as a front-matter value: empty, blank after strip(),
    or the `—` placeholder wi itself reads as "no value", is None — so a
    `blocked_reason: "—"` never lands as a literal dash now that a quoted
    `—` reads back as one."""
    v = story.get(key) or None
    return None if isinstance(v, str) and v.strip() in ("", "—") else v


def _import_story(story, alias_map, existing_by_alias, update, taken):
    story = {k: ([_fold_story(x) if k in STORY_TEXT_FIELDS else _fold(x)
                  for x in v] if isinstance(v, list) and
                 k in ("requires", "acceptance", "testing") else
                 v if k == "notes" else
                 _fold_story(v) if k in STORY_TEXT_FIELDS or
                 k not in KNOWN_STORY_FIELDS else _fold(v))
             for k, v in story.items()}
    alias = str(story["id"])
    status, stage = BACKLOG_TO_STATE[story.get("status", "todo")]
    p = int(story.get("priority", 50))
    priority = 0 if p >= 80 else 1 if p >= 60 else 2 if p >= 40 else 3 if p >= 20 else 4
    x_backlog = {}
    for key, val in story.items():
        if key not in KNOWN_STORY_FIELDS:
            x_backlog[key] = val if isinstance(val, (str, int)) else \
                json.dumps(val, separators=(", ", ": "))
    existing = existing_by_alias.get(alias) if update else None
    blocked, _ = split_ext_requires(
        _story_value(story, "blocked_reason"),
        ext=_ext_deps(existing) if existing else None,
        whole=story.get("status") != "blocked")
    parked = _bridge_decode("PARKED", parked_reason, blocked) \
        if status == "blocked" else None
    grooming = _bridge_decode("GROOMING", grooming_questions, blocked) \
        if status == "blocked" else None
    if parked is not None:
        status, blocked = "parked", None
    elif grooming is not None:
        status, blocked = "grooming", None
    if update and alias in existing_by_alias:
        it = existing_by_alias[alias]
        if parked is not None or grooming is not None:
            # the export carries only the park (or grooming); a blocked:
            # reason kept under it lives only in the store
            blocked = it.get("blocked")
        it.meta.update(status=status, stage=stage, blocked=blocked, parked=parked,
                       grooming=grooming,
                       feedback=_story_value(story, "review_feedback"),
                       owner=_story_value(story, "claimed_by"),
                       x_backlog=x_backlog or None)
        if status in ("done", "dropped") and not it.get("closed"):
            it.meta["closed"] = today()
        it.touch()
        return it, False
    desc, handoff, notes = _split_backlog_notes(story.get("notes"))
    title = str(story["title"])[:120]
    meta = {"id": make_id(title, today(), taken), "title": title, "status": status,
            "stage": stage, "priority": priority, "alias": alias,
            "blocked": blocked, "parked": parked, "grooming": grooming,
            "feedback": _story_value(story, "review_feedback"),
            "owner": _story_value(story, "claimed_by"),
            "mode": _story_value(story, "ticket_mode"),
            "complexity": _story_value(story, "complexity"),
            "created": today(), "updated": today(),
            "x_backlog": x_backlog or None}
    if status in ("done", "dropped"):
        meta["closed"] = today()
    sections = []
    acceptance = story.get("acceptance") or []
    if acceptance and acceptance != [title]:
        sections.append(("Acceptance", "\n".join(f"- [ ] {a}" for a in acceptance)))
    testing = [t for t in (story.get("testing") or []) if t != "<unspecified>"]
    if testing:
        sections.append(("Testing", "\n".join(f"- {t}" for t in testing)))
    sections.append(("Handoff", emit_handoff(handoff or {})))
    if notes:
        sections.append(("Notes", notes))
    item = Item(meta, [], desc, sections)
    item.meta["deps"] = _story_deps(story, alias_map)
    return item, True


def _story_deps(story, alias_map):
    """A new item's deps: each `requires` id (an unknown one as `ext: <id>`),
    then the `ext:` deps export carried in blocked_reason."""
    deps = [alias_map.get(str(r), f"ext: {r}")
            for r in (story.get("requires") or [])]
    _, ext = split_ext_requires(_fold_story(_story_value(story, "blocked_reason")),
                                whole=story.get("status") != "blocked")
    return deps + [d for d in ext if d not in deps]


def cmd_import(args):
    if args.format != "backlog-yaml":
        raise WiError(1, f"unknown import format '{args.format}'")
    root = resolve_root(args.root)
    stories = []
    for path in [args.path] + ([args.done_path] if args.done_path else []):
        data = _load_yaml_file(path)
        stories.extend(data.get("stories") or [])
    n_new = n_upd = 0
    with Lock(root):
        items = load_all(root, archived=True)
        existing_by_alias = {it.get("alias"): it for it in items if it.get("alias")}
        alias_map = {a: it.id for a, it in existing_by_alias.items()}
        # two passes so requires can point at stories created in this run
        pending, taken = [], taken_ids(root, items)
        for story in stories:
            item, created = _import_story(story, alias_map, existing_by_alias,
                                          args.update, taken)
            if created:
                alias_map[item.get("alias")] = item.id
            pending.append((story, item, created))
        for story, item, created in pending:
            if created:
                item.meta["deps"] = _story_deps(story, alias_map)
                n_new += 1
            else:
                n_upd += 1
        save_items(root, [item for _, item, _ in pending])
    print(f"imported {n_new} new, updated {n_upd}")
    return 0


# ── lint, archive ───────────────────────────────────────────────────────────

# KEY=value anywhere a token starts: at line start or after any character
# but a letter, digit, underscore, ? or &, so a bullet, date, tag, bold
# (**KEY=...**), em dash or other prefix ("- 2026-10-08 checkpoint: KEY=...")
# no longer hides it. The value rule is the bare form's, unchanged: 8+
# non-space characters, not a $VAR, <placeholder> or {template}. A KEY glued
# to a word, or after a URL's ? or & (a query string), stays unmatched.
# Each match is then judged by _assign_secret (0f7e): a value that is
# plainly a filesystem path or a : list of them (XAUTHORITY=/tmp/.x,
# PATH=/usr/bin:/bin) is no secret under a key without a secret word or
# under a location key (SSH_AUTH_SOCK, TOKEN_DIR), and a -D<NAME>=value
# define (cmake, a compiler) whose NAME holds no secret word counts only
# a live or token-shaped value (see _define_flagged).
SECRET_ASSIGN_RE = re.compile(
    r"(?:^|(?P<lead>[^A-Za-z0-9_?&]))(?P<key>[A-Z][A-Z0-9_]{2,})="
    r"(?![$<{])(?P<value>\S{8,})")
SECRET_KV_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|passwd|credential|webhook[_-]?url)\b"
    r"['\"]?\s*[:=]\s*['\"]?"
    r"(?!\$\{|\$\(|\$[A-Za-z_][A-Za-z0-9_]*(?:[\s\"'`,;)}\]]|\.(?=\s|$)|$)|[<{*])"
    r"(\$?[A-Za-z0-9+/_.$=-]{12,})")

# The looser shapes the two rules above miss (b9fb): a lowercase or
# mixed-case key (db_pass=..., app.db_pass=...), spaces around = and the
# => and := forms (KEY = value, key => value), KEY: value and KEY :value
# (an env-style or snake_case key, so a prose "next:" never qualifies), a
# JSON "key": "value" pair and --flag=value, each with the value bare or
# quoted. Which value counts is the key's call: see _shape_value_flagged.
# A camelCase or PascalCase colon key (clientSecret: ..., JWTSecret: ...)
# counts only when it mixes case, splits into 2+ segments, does not open
# with one capital before a capitalised word (OAuth) and holds a secret
# word (ac83, see _shape_secret; db2Password and k8sToken count), so prose
# such as "GitHub: ...", "OAuth: ..." or "Token: ..." never qualifies.
# The lookbehind lets _shape_secret resume at a value's start (at its
# opening quote, so a quoted pair after a spaced flag or kebab key,
# --a-b "db_pass":"...", is read whole), so a later pair joined to it
# (a=b;db_pass=..., {"a":"b","db_pass":...}) is still examined; the
# value is capped so the scan stays linear.
#
# dc23 adds the looser key forms, each counted only under a secret-word key
# and never for a plain word or a date (_loose_flagged): a spaced flag
# (--password v), a kebab-case colon key (db-pass: v), and a bare
# one-case colon key that is itself a secret word (dbpass:, passphrase:,
# pw:; not key:, auth:, cred:). The = forms also take a kebab-case key
# (db-pass=v) and pw (pw=v), judged as every other = key.
SECRET_SHAPE_RE = re.compile(
    r"(?:^|(?<=[^A-Za-z0-9_?&-]))(?:"
    r"(?P<flag>--[A-Za-z][A-Za-z0-9-]*)=|"
    r"(?P<sflag>--[A-Za-z][A-Za-z0-9-]*)[ \t]+(?=[^\s-])|"
    r"[\"'](?P<json>[A-Za-z_][A-Za-z0-9_.-]*)[\"']\s*:\s*|"
    r"(?P<kv>[A-Za-z](?:[A-Za-z0-9_]|-(?=[A-Za-z0-9_])){2,}|[Pp][Ww])"
    r"\s*(?:=>|:=|=(?!=))\s*|"
    r"(?P<colon>[A-Z][A-Z0-9_]{2,}|[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+)\s*:\s*|"
    r"(?P<kcolon>[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+)\s*:\s*|"
    r"(?P<camel>[A-Za-z][A-Za-z0-9]+)\s*:\s*"
    r")(?P<quote>[\"']?)(?P<value>\S{1,256})")
# An Authorization header with a Bearer, Basic or Token credential, any
# case, after :, = or => (a header, a config pair, a hash), the credential
# bare or quoted, the quote may carry a string prefix (f"Bearer ...", dc23);
# the credential is judged by _auth_secret.
SECRET_AUTH_RE = re.compile(
    r"(?i)\bauthorization[\"']?\s*(?:=>|[:=])\s*(?:[fbru]{1,2}(?=[\"']))?[\"']?"
    r"(?:bearer|basic|token)\s+[\"']?(\S{1,300})")
# a credential's run of token characters: base64, JWT, hex, and the : and %
# of a raw user:pass or a percent-encoded value
_AUTH_TOKEN_RE = re.compile(r"[A-Za-z0-9+/_.=~:%-]+")
# A key is a secret-word key when one of its segments (split on _ - . and
# camelCase) is one of these whole words, or ends with one of the suffixes
# (dbpassword, apitoken, clientsecret, dbpass, userpasscode); a plural
# (tokens, keys) is not, key counts only as a whole segment (monkey stays
# clean), and a word ending in pass from _PASS_WORDS is no secret word
# (bypass, compass). A key of two or more segments whose last is one of
# _META_WORDS names something about a secret, not the secret
# (password_policy, token_file, secret_name), and is judged as other keys.
_SECRET_WORDS = frozenset((
    "pass", "passwd", "password", "passphrase", "passcode", "pw", "pwd",
    "secret", "token", "auth", "cred", "creds", "credential", "credentials",
    "key", "apikey", "webhook", "secretkey", "privatekey"))
_SECRET_SUFFIXES = ("password", "passwd", "secret", "token", "apikey",
                    "pass", "passphrase", "passcode")
_PASS_WORDS = frozenset((
    "bypass", "compass", "surpass", "trespass", "overpass", "underpass",
    "encompass", "subpass", "renderpass", "multipass"))
_META_WORDS = frozenset((
    "policy", "policies", "rotation", "hint", "prompt", "field", "label",
    "name", "names", "type", "mode", "file", "path", "var", "ref"))
# a bare number under a secret-word key is a count only beside one of these
_COUNT_WORDS = frozenset((
    "count", "len", "max", "min", "budget", "total", "size", "limit", "num"))
_KEY_SEG_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|[0-9]+")
_VALUE_TOKEN_RE = re.compile(r"[A-Za-z0-9+/_.=~-]+")
_HEX_RE = re.compile(r"(?i)[0-9a-f]+")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_SEG_SPLIT_RE = re.compile(r"[-_./~]+")
_CODE_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)([(\[]?)")
_ATTR_RE = re.compile(r"[A-Za-z_]+(?:\.[A-Za-z_]+)+")
_COUNT_RE = re.compile(r"[0-9][0-9,._]*")
_PLACEHOLDER_RE = re.compile(r"<[a-z][a-z _-]*>")
# a whole-value variable or template, ending where the value ends
_TEMPLATE_RE = re.compile(
    r"(?:\$[A-Za-z_][A-Za-z0-9_]*|\$\{[A-Za-z_][A-Za-z0-9_]*\}"
    r"|\$\{\{ ?[A-Za-z_][A-Za-z0-9_.-]* ?\}\}|\$\([^()]{1,200}\)"
    r"|\{[A-Za-z_][A-Za-z0-9_.-]*\}|\{\{ ?[A-Za-z_][A-Za-z0-9_.-]* ?\}\})"
    r"(?=$|[\s\"'`,;)\]}]|\.(?=\s|$))")
_CLOSE = {"(": ")", "[": "]"}
_MARKDOWN_RE = re.compile(r"`|\*|__")


def _key_segments(key):
    return [seg.lower() for seg in _KEY_SEG_RE.findall(key)]


def _secret_key(key):
    segs = _key_segments(key)
    if len(segs) >= 2 and segs[-1] in _META_WORDS:
        return False
    return any(_secret_word(seg) for seg in segs)


def _secret_word(seg):
    return seg in _SECRET_WORDS or (seg.endswith(_SECRET_SUFFIXES)
                                    and seg not in _PASS_WORDS)


def _harmless_segment(seg):
    """Letters and digits only (a + or = makes a segment live): all letters,
    all digits or all hex at any length; otherwise 12 characters or fewer
    that do not mix upper case, lower case and digits."""
    if not re.fullmatch(r"[A-Za-z0-9]+", seg):
        return False
    if re.fullmatch(r"[A-Za-z]+|[0-9]+|(?i:[0-9a-f]+)", seg):
        return True
    return len(seg) <= 12 and not (re.search(r"[a-z]", seg)
                                   and re.search(r"[A-Z]", seg)
                                   and re.search(r"[0-9]", seg))


def _harmless_segments(text):
    return all(_harmless_segment(seg) for seg in _SEG_SPLIT_RE.split(text) if seg)


def _looks_live(value):
    """True when `value`, under a key with no secret word, looks like a live
    secret rather than a word, a hex sha, a date, or an id, slug, path,
    version or UUID: 12+ characters holding both a letter and a digit, not
    all hex, no date at its start, and not two or more segments (split on
    - _ . / ~) that are each harmless (see _harmless_segment)."""
    value = value.rstrip(".")
    if (len(value) < 12 or not re.search(r"[A-Za-z]", value)
            or not re.search(r"[0-9]", value)
            or _HEX_RE.fullmatch(value) or _DATE_RE.match(value)):
        return False
    segs = [seg for seg in _SEG_SPLIT_RE.split(value) if seg]
    return not (len(segs) >= 2 and all(_harmless_segment(seg) for seg in segs))


def _quoted_code(key, raw, value):
    """True when an unquoted value under a secret-word key is code, a count
    or a path a note may quote, not a secret:
    - a call f(...) or subscript x[...] on a name of harmless segments, when
      nothing follows the closing bracket and no comma-separated argument
      inside would itself flag (len(tokens), os.environ['API_KEY'],
      get_token(user, scope));
    - a dotted attribute of letters and _ only (config.api_key, self.token);
    - a number with separators (1,234,567), or a bare number when another
      key segment is a count word (token_count, key_limit);
    - a path starting ~/, ./ or / of two or more harmless segments.
    So a dotted JWT-like token, a base64 value that starts with /, words
    with a digit (abc.def.ghi1) and a bare 12-digit PIN still count."""
    m = _CODE_RE.match(raw)
    if m and m.group(2) and _harmless_segments(m.group(1)):
        body = raw.rstrip("\"'`,;")
        if body.endswith(_CLOSE[m.group(2)]):
            args = [arg.strip().strip("\"'")
                    for arg in _split_args(body[m.end():-1])]
            if not any(arg and _arg_flagged(key, arg) for arg in args):
                return True
    if _ATTR_RE.fullmatch(value):
        return True
    if _COUNT_RE.fullmatch(value):
        if re.search(r"[,._]", value):
            return True
        return any(seg in _COUNT_WORDS for seg in _key_segments(key))
    if value.startswith(("~/", "./", "/")):
        segs = [seg for seg in _SEG_SPLIT_RE.split(value) if seg]
        return len(segs) >= 2 and all(_harmless_segment(seg) for seg in segs)
    return False


def _arg_flagged(key, arg):
    """A call argument that would flag on its own. One holding a space is
    prose or an expression, not one secret, so it flags only when one of
    its words looks live as under other keys (_looks_live: login(user,
    "Bearer <live token>")) (dc23)."""
    if re.search(r"\s", arg):
        return any(_looks_live(tok.group())
                   for tok in _VALUE_TOKEN_RE.finditer(arg))
    return _secret_value_flagged(key, arg, "", arg)


def _placeholder(value, rest):
    """A whole-value $NAME, ${NAME}, ${{ name }}, $(command), {name} or
    {{ name }} (_TEMPLATE_RE); all * or all . (masked or elided, an
    ellipsis included); or <words>: lowercase words, spaces, _ or - inside,
    with the closing >. rest is the next 300 characters of the line from
    the value's start, so <your key> and {{ name }} count. A value that
    only starts with $ or { is no placeholder ($2b$12$..., $TOKENabc+1)."""
    if not value.strip("*") or not value.strip(".…"):
        return True
    return (_PLACEHOLDER_RE.match(rest) is not None
            or _TEMPLATE_RE.match(rest) is not None)


def _match_close(text, open_at):
    """The index of the bracket that closes the ( or [ at open_at, counting
    nested ( [ pairs, or -1 when text (a bounded slice) does not close it."""
    depth = 0
    for i in range(open_at, len(text)):
        if text[i] in "([":
            depth += 1
        elif text[i] in ")]":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _split_args(text):
    """text split at its commas outside any ( or [ pair."""
    out, depth, start = [], 0, 0
    for i, c in enumerate(text):
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif c == "," and depth == 0:
            out.append(text[start:i])
            start = i + 1
    out.append(text[start:])
    return out


def _spaced_call(raw, rest):
    """An unquoted value that opens a call or subscript the value's first
    run of non-space characters does not close (get(user, value)): the call
    up to its matching closing bracket and any text glued after it, read from rest,
    so a spaced second argument is examined. Otherwise raw unchanged."""
    m = _CODE_RE.match(raw)
    if not (m and m.group(2)):
        return raw
    close = _match_close(rest, m.end() - 1)
    if close < len(raw):
        return raw
    return rest[:close + 1] + re.match(r"\S*", rest[close + 1:]).group()


def _secret_value_flagged(key, raw, quote, rest):
    """Under a secret-word key: any 8+ non-space characters, symbols, hex,
    letters-only and UUIDs included, unless the value is unquoted code, a
    count or a path (_quoted_code). A quoted value skips nothing."""
    if not quote:
        raw = _spaced_call(raw, rest)
    value = raw.rstrip("\"'`,;)]}")
    if not value or _placeholder(value, rest) or len(value) < 8:
        return False
    return bool(quote) or not _quoted_code(key, raw, value)


def _meta_secret_flagged(key, raw, quote, rest):
    """Under a meta key (last segment in _META_WORDS) whose other segments
    hold a secret word (secret_ref, password_var, auth_token_file): any
    value that is no placeholder and no name, word, attribute or path such
    a key holds (_meta_name) is judged as under a secret-word key."""
    segs = _key_segments(key)
    if not (len(segs) >= 2 and segs[-1] in _META_WORDS
            and any(_secret_word(seg) for seg in segs[:-1])):
        return False
    value = raw.rstrip("\"'`,;)]}")
    if not value or _placeholder(value, rest):
        return False
    if _meta_name(value):
        return False
    return _secret_value_flagged(key, raw, quote, rest)


_META_NAME_RE = re.compile(
    r"[a-z]{1,15}(?:[-_.:][a-z0-9]{1,15})*|[A-Z]{1,15}(?:_[A-Z0-9]{1,15})*")
_UUID_RE = re.compile(r"(?i)[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")


def _meta_name(value):
    """A name, word, attribute or path a meta key may hold: a lowercase
    name of runs of 15 or fewer letters (prod-db-creds,
    urn:ietf:params:oauth), an env-var name (GITHUB_TOKEN), a letters-only
    identifier whose case segments are 3 to 15 letters (Bearer,
    ClientCredentials), a dotted attribute, or a ~/ ./ / or $NAME/ path of
    harmless segments. A run of 16+ lowercase letters, digits mixed into a
    word, a digit run, a UUID (even one whose groups read as words) or a
    run of 16+ capitals is none of these."""
    if _UUID_RE.fullmatch(value):
        return False
    if _META_NAME_RE.fullmatch(value) or _ATTR_RE.fullmatch(value):
        return True
    if (re.fullmatch(r"[A-Za-z]+", value)
            and all(3 <= len(seg) <= 15 for seg in _KEY_SEG_RE.findall(value))):
        return True
    path = re.sub(r"^\$[A-Za-z_][A-Za-z0-9_]*(?=/)", "", value)
    if path.startswith(("~/", "./", "/")):
        segs = [seg for seg in _SEG_SPLIT_RE.split(path) if seg]
        return len(segs) >= 2 and all(_harmless_segment(seg) for seg in segs)
    return False


def _shape_value_flagged(key, raw, quote="", rest=None):
    """A key holding a secret word (see _secret_key) flags as
    _secret_value_flagged says, as strictly as the KEY=value rule. Any other
    key (sha, commit, *_id, ...) flags only a value _looks_live passes, and
    never a call like name(...)."""
    rest = raw if rest is None else rest
    if _meta_secret_flagged(key, raw, quote, rest):
        return True
    if _secret_key(key):
        return _secret_value_flagged(key, raw, quote, rest)
    value = raw.rstrip("\"'`,;)]}")
    if not value or _placeholder(value, rest):
        return False
    # a plain path is no secret under such a key (0f7e: CXX=/usr/bin/g++-12)
    if _plain_path(value):
        return False
    tok = _VALUE_TOKEN_RE.match(raw)
    if not tok or raw[tok.end():tok.end() + 1] == "(":
        return False
    return _looks_live(tok.group())


# bare one-case colon keys that count (pw:, dbpass:, passphrase:): a
# secret-word suffix, or one of these whole words; key, auth, cred(s),
# webhook and pass itself are left out, as prose ("key: the main point",
# "pass: 12 of 12") uses them
_BARE_WORDS = frozenset(("pw", "pwd", "apikey", "secretkey", "privatekey"))
# a plain value: a word or words joined by - _ or ' (required, read-only,
# NOT_SET), each a lowercase or capitalised word or all capitals, so a
# mixed-case run such as FakeSecretPass is no plain word
_PLAIN_WORD = r"(?:[A-Za-z][a-z]*|[A-Z]+)"
_PLAIN_RE = re.compile(_PLAIN_WORD + r"(?:[-_']" + _PLAIN_WORD + r")*")


def _bare_secret_key(key):
    if not re.fullmatch(r"[A-Za-z][a-z0-9]*|[A-Z][A-Z0-9]*", key):
        return False
    word = key.lower()
    return word in _BARE_WORDS or (word.endswith(_SECRET_SUFFIXES)
                                   and word not in _PASS_WORDS
                                   and word != "pass")


def _plain_value(raw):
    """A plain word or words (_PLAIN_RE) or a whole date, once quotes,
    brackets, markdown and prose punctuation around it are dropped
    ((required), _(unset)_, <optional>)."""
    value = raw.strip("\"'`,;:.()[]{}<>_*~!?")
    return (not value or _PLAIN_RE.fullmatch(value) is not None
            or _DATE_RE.fullmatch(value) is not None)


def _loose_flagged(key, raw, quote, rest):
    """The looser key forms (a spaced flag, a kebab or bare colon key, a
    Markdown table cell, dc23) count only under a key holding a secret word,
    judged as _shape_value_flagged judges it, and never a plain word or
    a date (prose: "--auth required", "| password | required |")."""
    if not any(_secret_word(seg) for seg in _key_segments(key)):
        return False
    # a closing ** or ` is markdown around the pair, and an unbalanced } a
    # brace around it, not the value's (**token: ${TOKEN}**, {pw: f(x)})
    stripped = re.sub(r"[*`]+[,;:.]*$", "", raw)
    if stripped.endswith("}") and stripped.count("}") > stripped.count("{"):
        stripped = stripped[:-1]
    if stripped != raw:
        raw, rest = stripped, stripped
    return (not _plain_value(raw)
            and _shape_value_flagged(key, raw, quote, rest))


def _shape_secret(line):
    # rest is bounded (the value is at most 256 characters), so each pair
    # costs a constant and a long line of pairs stays linear
    pos = 0
    while True:
        m = SECRET_SHAPE_RE.search(line, pos)
        if not m:
            return False
        loose = m.group("sflag") or m.group("kcolon")
        key = m.group("flag") or m.group("json") or m.group("kv") or m.group("colon")
        if m.group("camel"):
            # mixed case, 2+ segments, no lone capital before a capitalised
            # word, a secret word: JWTSecret, AWSSecretKey, clientSecret,
            # db2Password, k8sToken; not OAuth, Token, GitHub. A one-case
            # single word counts only as a bare secret word (dc23), and a
            # key that is both (Q9token) is judged as camelCase, as on main.
            key = m.group("camel")
            segs = _KEY_SEG_RE.findall(key)
            camel = (re.search(r"[a-z]", key) and re.search(r"[A-Z]", key)
                     and len(segs) >= 2
                     and not re.match(r"[A-Z][A-Z][a-z]", key)
                     and _secret_key(key))
            if not camel and _bare_secret_key(key):
                loose = key
            elif not camel:
                # resume at the quote, so a quoted pair the value
                # swallowed ("db_pass":"...") is still examined
                pos = m.start("quote")
                continue
        # a loose colon key needs a space after its colon, as YAML does,
        # so prose such as "dbpass:/dbpassword:" never qualifies
        if (not loose or m.group("sflag")
                or re.search(r":\s", line[m.start():m.start("value")])):
            rest = line[m.start("value"):m.start("value") + 300]
            if (_loose_flagged if loose else _shape_value_flagged)(
                    loose or key, m.group("value"), m.group("quote"), rest):
                return True
        pos = m.start("quote")


# A Markdown table row (| db_pass | value |): a cell that is one key-shaped
# token, then a cell that is one token (dc23)
_TABLE_KEY_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}")


def _table_secret(line):
    """A Markdown table row whose key cell holds a secret word and whose
    next cell is a single token that _loose_flagged counts. A cell with a
    space in it is prose, and a cell over 256 characters is skipped."""
    if not line.lstrip().startswith("|"):
        return False
    # a code span or emphasis around a cell is markdown, not the value's
    cells = [cell.strip().strip("`*") for cell in line.split("|")]
    for key, value in zip(cells, cells[1:]):
        if (not value or len(value) > 256 or not _TABLE_KEY_RE.fullmatch(key)
                or re.search(r"\s", value)):
            continue
        quote = value[0] if value[0] in "\"'" else ""
        raw = value[1:] if quote else value
        if _loose_flagged(key, raw, quote, raw):
            return True
    return False


# a URL's user:password@ part, read from just after each :// (dc23)
_URL_USERINFO_RE = re.compile(r"[^\s:/@]{0,64}:([^\s/@]{1,256})@")


def _url_secret(line):
    """A password inside a URL (scheme://user:value@host, the user may be
    empty: redis://:value@host): 8+ characters,
    not a whole-value placeholder (${DB_PASS}, <password>, ****), not one or
    two repeated characters, and not a plain word (password, changeme)."""
    for m in re.finditer("://", line):
        u = _URL_USERINFO_RE.match(line, m.end())
        if not u:
            continue
        value = u.group(1)
        if (len(value) < 8 or _placeholder(value, value + " ")
                or len(set(value)) <= 2 or _plain_value(value)):
            continue
        return True
    return False


def _secret_line(line):
    """The cleaned line: NFKC-normalised (a fullwidth equals sign, U+FF1D,
    is =), Unicode format characters (category Cf, such as a zero-width
    space) dropped, and the markdown ` * ** __ around keys and values
    removed. Look-alike letters (confusables) are out of scope."""
    line = "".join(c for c in unicodedata.normalize("NFKC", line)
                   if unicodedata.category(c) != "Cf")
    return _MARKDOWN_RE.sub("", line)


def _auth_secret(line):
    """An Authorization: Bearer/Basic/Token header whose credential looks
    like one: 12+ characters, not a placeholder (<token>, $TOKEN,
    ${TOKEN}, ..., masked), not one or two repeated characters (XXXX...),
    and not a plain word (prose: "Authorization: Bearer authentication")."""
    for m in SECRET_AUTH_RE.finditer(line):
        # the credential is its run of token characters (base64, JWT, hex),
        # so closing quotes and prose punctuation after it never count
        value = _AUTH_TOKEN_RE.match(m.group(1))
        value = value.group().rstrip(".:") if value else ""
        rest = line[m.start(1):m.start(1) + 300]
        if (len(value) < 12 or _placeholder(value, rest)
                or len(set(value)) <= 2
                or re.fullmatch(r"[A-Za-z][a-z]*(?::[A-Za-z][a-z]*)*",
                                value)):
            continue
        return True
    return False


# a path's start: /, ~/, ./, ../, or a $NAME/ or ${NAME}/ variable
_PATH_START_RE = re.compile(
    r"(?:~|\.\.?|\$[A-Za-z_][A-Za-z0-9_]*|\$\{[A-Za-z_][A-Za-z0-9_]*\})?/")


def _path_segment(seg):
    """A path segment that is harmless (_harmless_segment), save one of 16+
    characters that is all hex, all digits, or letters only in mixed case:
    a key or token, not a directory name (0f7e fix round 2). A long
    lowercase name (x86_64-linux-gnu, site-packages) stays harmless, as
    its segments are split on - and _ before this."""
    if len(seg) >= 16 and (_HEX_RE.fullmatch(seg) or seg.isdigit()
                           or (seg.isalpha() and not seg.islower()
                               and not seg.isupper())):
        return False
    return _harmless_segment(seg)


def _one_path(value, bare=2):
    """One path (_plain_path): it starts as _PATH_START_RE says, and every
    segment after that start (split on - _ . / ~) is a harmless path
    segment (_path_segment), a trailing run of + allowed (g++, c++). A path
    after a bare / needs `bare` segments (two alone, one in a list), one
    after ~/ ./ ../ or a variable one: /tmp/.docker.xauth, ./.Xauthority, $HOME/.Xauthority,
    /usr/bin/g++-12. A token behind a slash (/FAKEfake0000FAKEfake,
    ./<40 hex>) is no path: its segment is live."""
    m = _PATH_START_RE.match(value)
    if not m:
        return False
    segs = [seg.rstrip("+") for seg in _SEG_SPLIT_RE.split(value[m.end():])
            if seg]
    need = bare if value.startswith("/") else 1
    return (len(segs) >= need
            and all(seg and _path_segment(seg) for seg in segs))


# a whole $NAME or ${NAME} in a path list (PATH=$HOME/bin:$PATH)
_LIST_VAR_RE = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*|\$\{[A-Za-z_][A-Za-z0-9_]*\}")


def _plain_path(value):
    """A value that is plainly a filesystem path (0f7e), quotes around it
    dropped: one path (_one_path), or a :-separated list of them (PATH,
    LD_LIBRARY_PATH, KUBECONFIG; fix round 3) whose every part is a path
    or a whole $NAME / ${NAME}, at least one a path as _one_path takes it
    alone (so /bin may sit in /usr/bin:/bin). A list with any other
    part (a token, an empty part, a URL's scheme) is no plain path."""
    value = value.strip("\"'`").rstrip(",;")
    parts = value.split(":")
    return (all(_one_path(p, 1) or _LIST_VAR_RE.fullmatch(p) for p in parts)
            and any(_one_path(p) for p in parts))


# A secret-word key whose last segment is one of these names where the
# secret lives, not the secret (SSH_AUTH_SOCK, PASSWORD_STORE_DIR,
# TOKEN_DIR), so a plain path under it is no secret (fix round 3). key is
# not one: GIT_SSH_KEY=~/.ssh/id_ed25519 is judged as before.
_LOCATION_WORDS = frozenset((
    "sock", "socket", "dir", "home", "root", "store", "prefix", "path"))
# a hex value under a define whose last word is one of these is a hash,
# not a secret, unless another word qualifies it as keyed material
# (HMAC_SHA256, SALT_HASH, TOTP_SEED_SHA1; finish round)
_HASH_WORDS = frozenset(("sha", "commit", "hash", "rev"))
_HASH_QUALIFIERS = frozenset((
    "hmac", "salt", "seed", "pepper", "signing", "sign", "api", "otp",
    "totp", "nonce", "key", "secret", "token"))


def _hash_name(name):
    """A define NAME that names a hash: its last word segment (digit runs
    dropped, so SHA256 is sha) is in _HASH_WORDS and no segment is in
    _HASH_QUALIFIERS. GIT_SHA, BUILD_COMMIT, SRC_REV and COMMIT_HASH are;
    SHA256_SALT, HMAC_SHA, API_HASH, SHARED and REVIEW are not."""
    words = [seg for seg in _key_segments(name) if not seg.isdigit()]
    return (bool(words) and words[-1] in _HASH_WORDS
            and not _HASH_QUALIFIERS.intersection(words))


def _define_flagged(name, value):
    """A -D<NAME>=value define whose NAME holds no secret word and whose
    value is no plain path (fix round 3): it flags when the value looks
    live (_looks_live) or any of its segments (split on - _ . / ~) is a
    token by _path_segment (a long hex, digit or mixed-case letter run,
    a + or = inside), save a whole hex value under a hash NAME
    (_hash_name: -DGIT_SHA=<40 hex>). RelWithDebInfo, ON and 1.2.3-beta
    stay clean."""
    if _HEX_RE.fullmatch(value) and _hash_name(name):
        return False
    return _looks_live(value) or not all(
        _path_segment(seg) for seg in _SEG_SPLIT_RE.split(value) if seg)


def _assign_secret(line):
    """A KEY=value match (SECRET_ASSIGN_RE) that counts (0f7e): the value is
    no plain path (_plain_path) unless the KEY holds a secret word and is
    no location key (PGPASSWORD=/hunter22/abc still flags,
    SSH_AUTH_SOCK=/run/... does not; see _LOCATION_WORDS), and a
    -D<NAME>=value define (the D glued to a single -, as cmake and
    compilers take it: -DCMAKE_BUILD_TYPE=...) whose NAME holds no secret
    word counts only as _define_flagged says, so
    -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-12 and
    -DCMAKE_BUILD_TYPE=RelWithDebInfo stay clean. A secret-word KEY with a
    token value (API_TOKEN=ghp_...) still flags."""
    for m in SECRET_ASSIGN_RE.finditer(line):
        key, value = m.group("key"), m.group("value")
        lead = m.start("key") - 1
        define = (m.group("lead") == "-" and key.startswith("D")
                  and (lead == 0 or line[lead - 1] != "-"))
        # a define's name is the key without its D (-DKEY: KEY)
        secret = _secret_key(key) or (define and _secret_key(key[1:]))
        location = _key_segments(key)[-1] in _LOCATION_WORDS
        if _plain_path(value) and (not secret or location):
            continue
        if (define and not secret
                and not _define_flagged(key[1:], value.strip("\"'`"))):
            continue
        return True
    return False


def _secret_hit(line):
    if "PRIVATE KEY-----" in line:
        return "PEM private key material"
    if (_assign_secret(line) or SECRET_KV_RE.search(line)
            or _shape_secret(line) or _auth_secret(line)
            or _table_secret(line) or _url_secret(line)):
        return "likely secret value (record the path and key, never the value)"
    return None


# A value on the next line (dc23): a YAML block scalar (key: | or key: >,
# with its - + or digit indicators), a \ continuation (shell, Dockerfile),
# or an Authorization header whose credential, or scheme and credential,
# is on the next line
_YAML_BLOCK_RE = re.compile(r"[:=]\s*[|>][-+0-9]{0,2}$")
_AUTH_OPEN_RE = re.compile(
    r"(?i)\bauthorization[\"']?\s*(?:=>|[:=])\s*(?:[fbru]{1,2}(?=[\"']))?"
    r"[\"']?(?:(?:bearer|basic|token)\s*)?$")


def _joined(line, nxt):
    """The line's last 300 characters joined to the next line's first 300
    when the line ends in a continuation, else None. Each line is read in at
    most one join as the first and one as the second, a bounded slice of
    each, so the scan stays linear."""
    tail, head = line[-300:].rstrip(), nxt[:300].lstrip()
    if not head.strip():
        return None
    if tail.endswith("\\"):
        return tail[:-1] + head
    m = _YAML_BLOCK_RE.search(tail)
    if m:
        return tail[:m.start() + 1] + " " + head
    if _AUTH_OPEN_RE.search(tail):
        return tail + " " + head
    return None


def _line_hit(line):
    clean = _secret_line(line)
    raw_why = _secret_hit(line)
    clean_why = raw_why if clean == line else _secret_hit(clean)
    return ("PEM private key material"
            if "PEM private key material" in (raw_why, clean_why)
            else raw_why or clean_why)


def secret_findings(text):
    """Every rule runs on the raw line and on the cleaned line
    (_secret_line), and either one flagging flags the line, so the cleanup
    never hides what the raw line shows (*my*password:, a value with * in
    it, a fullwidth $ before a value). The scan reads line by line and
    carries one line of state, the previous line: when that line was clean
    and ends in a continuation (_joined), the two joined are checked too,
    and a hit is reported on the line that holds the value."""
    out, prev, prev_hit = [], "", True
    for n, line in enumerate(text.split("\n"), 1):
        why = _line_hit(line)
        if not why and not prev_hit:
            joined = _joined(prev, line)
            if joined is not None:
                why = _line_hit(joined)
        if why:
            out.append((n, why))
        prev, prev_hit = line, bool(why)
    return out


def cmd_lint(args):
    # a deprecated name is a migration state, not a defect: stderr, and the
    # exit is unchanged
    for notice in env_notices():
        print(notice, file=sys.stderr)
    root = resolve_root(args.root, warn_stores=False)
    for notice in location_notices(root):
        print(notice, file=sys.stderr)
    problems = []
    items, texts = [], {}
    for path in item_paths(root, archived=True):
        try:
            text = texts[path] = read_raw(path)
        except WiError as e:
            problems.append(str(e))
            continue
        if not text:
            problems.append(f"{path}: {STALE_RESERVATION}; "
                            f"{stale_reservation_fix(path)}")
            continue
        if re.search(r"^(<{7}|={7}|>{7})", text, re.M):
            problems.append(f"{path}: unresolved merge conflict markers")
            continue
        try:
            item = Item.parse(text, path)
        except WiError as e:
            problems.append(str(e))
            continue
        items.append(item)
    by_id = {}
    for it in items:
        if it.id in by_id and _half_moved(by_id[it.id].path, it.path):
            problems.append(f"{it.path}: the same file as {by_id[it.id].path} "
                            "(an archive killed between link and unlink); "
                            "`wi archive` finishes the move")
        elif it.id in by_id:
            problems.append(f"{it.path}: duplicate id {it.id}")
        by_id[it.id] = it
    aliases = {}
    for it in items:
        problems.extend(f"{it.path}: {e}" for e in it.validate())
        alias = it.get("alias")
        if alias:
            if alias in aliases:
                problems.append(f"{it.path}: duplicate alias {alias} (also {aliases[alias]})")
            aliases[alias] = it.id
        for dep in it.get("deps", []):
            if not dep.startswith("ext:") and dep not in by_id:
                problems.append(f"{it.path}: dangling dep '{dep}'")
        parent = it.get("parent")
        if parent and parent not in by_id:
            problems.append(f"{it.path}: dangling parent '{parent}'")
        if it.get("status") == "doing":
            h = it.handoff()
            if it.section("Handoff") is None:
                problems.append(f"{it.path}: doing without a ## Handoff block")
            elif not h.get("next"):
                problems.append(f"{it.path}: doing with empty handoff next:")
        for key in [k for k in FIELD_ORDER if k in it.meta] + \
                [k for k in it.extra if k not in FIELD_ORDER]:
            val = it.meta[key]
            vals = val.values() if isinstance(val, dict) else \
                val if isinstance(val, list) else [val]
            if any(isinstance(v, str) and _FRONT_REFUSE_RE.search(v)
                   for v in vals):
                problems.append(
                    f"{it.path}: front-matter '{key}' holds a control"
                    " character — a quoted value decodes YAML escapes, so a"
                    " hand-written backslash (\"C:\\temp\" holds a tab)"
                    " must be written \\\\;"
                    f" fix it with `wi set {it.id} {key} ...`")
        for n, why in secret_findings(texts[it.path]):
            problems.append(f"{it.path}:{n}: {why}")
    # cycle detection over deps
    state = {}

    def visit(iid, stack):
        if state.get(iid) == 1:
            problems.append("dependency cycle: " + " -> ".join(stack + [iid]))
            return
        if state.get(iid) or iid not in by_id:
            return
        state[iid] = 1
        for dep in by_id[iid].get("deps", []):
            if not dep.startswith("ext:"):
                visit(dep, stack + [iid])
        state[iid] = 2

    for iid in by_id:
        visit(iid, [])
    raw = _store_tracking_raw(root)
    if len(_store_tracking_values(root) or ()) > 1:
        problems.append(f"{root / STORE_FILE}: more than one tracking: line; "
                        "fix: `wi init --track` or `wi init --no-track` "
                        "rewrites it with one")
    if raw is not None and raw not in TRACKING_CHOICES:
        problems.append(f"{root / STORE_FILE}: tracking must be one of "
                        f"{', '.join(TRACKING_CHOICES)} (got '{raw}'); fix: "
                        "`wi init --track` or `wi init --no-track`")
    # 03ab F8: the decision counter. A problem (conflict markers, a value
    # that is not a whole number) is never reseeded over; a counter behind
    # the items is reseeded, a notice on stderr, the exit unchanged
    problems.extend(counter_duplicates(root))
    problem = counter_problem(root)
    if problem:
        problems.append(problem)
    else:
        notice = reseed_counter(root)
        if notice:
            print(notice, file=sys.stderr)
    # lint has no warning tier: every finding it prints is a problem, exit 3
    # 5f46: a second store under the same dir, however the root was found
    rs = store_repo_state(root)
    for warning in (custody_warning(root, rs), two_store_warning(root)):
        if warning:
            problems.append(warning)
    # d1e9: the store-repo checks; a notice goes to stderr, exit unchanged
    for tier, line in store_repo_checks(root, rs):
        if tier == "problem":
            problems.append(line)
        else:
            print(line, file=sys.stderr)
    for p in problems:
        print(p)
    if problems:
        return 3
    print(f"lint clean: {len(items)} items")
    return 0


def reseed_counter(root):
    """Raise store.yaml's decision counter to the items' highest N when it
    is behind (03ab F8), and return the notice to print, or None. Never
    lowers it: a counter ahead of the items is a gap, which is valid.
    Inside Lock (which commits an own store's store.yaml), it re-reads the
    counter and rescans the items, and writes only when the larger of the
    two is above the counter it re-read. Never raises: a lock or write that
    fails is the notice, and lint's exit stays as it was."""
    if not (root / STORE_FILE).is_file():
        return None
    if read_counter(root) >= items_decision_max(root):
        return None
    try:
        with Lock(root):
            if counter_problem(root):
                return None
            old = read_counter(root)
            new = max(old, items_decision_max(root))
            if new <= old or not write_counter(root, new):
                return None
    except (WiError, OSError) as e:
        return f"counter: decision not reseeded ({e})"
    return f"counter: decision reseeded {old} \u2192 {new}"


def cmd_archive(args):
    root = resolve_root(args.root)
    cutoff = parse_duration(args.older_than)
    now = datetime.now(timezone.utc)
    moves = []
    with Lock(root):
        for item in load_all(root):
            if item.get("status") not in ("done", "dropped") or not item.get("closed"):
                continue
            dest = root / "archive" / item.get("closed")[:4] / item.path.name
            if _half_moved(item.path, dest):
                # a move killed between link and unlink: finish it, whatever
                # the cutoff (_move_no_clobber unlinks the source)
                moves.append((item.path, dest))
                continue
            closed = datetime.strptime(item.get("closed"), "%Y-%m-%d").replace(
                tzinfo=timezone.utc)
            if (now - closed).total_seconds() < cutoff:
                continue
            if dest.exists():
                why = f"{STALE_RESERVATION}; `wi lint` names the fix" \
                    if dest.stat().st_size == 0 else "already exists"
                raise WiError(3, f"refusing to archive {item.path}: {dest}: "
                                 f"{why}; nothing archived")
            moves.append((item.path, dest))
        for src, dest in moves:
            dest.parent.mkdir(parents=True, exist_ok=True)
            _move_no_clobber(src, dest)
            # the source's removal is committed with the destination, so an
            # own store's history shows the move as a rename (d1e9 D4')
            _journal_write(src)
        moved = len(moves)
    print(f"archived {moved}")
    return 0


# ── CLI ─────────────────────────────────────────────────────────────────────

# `wi install-launcher` (8805 F1): the launcher beside wi.py, copied on a
# person's request to $HOME/.local/bin/wi. Its line 2 starts with this marker,
# which is how the install knows a file at the target is one it made.
LAUNCHER_MARKER = b"# wi launcher (work-items plugin)."


def _launcher_marked(data):
    lines = data.split(b"\n", 2)
    return len(lines) > 1 and lines[1].startswith(LAUNCHER_MARKER)


def _launcher_dir(home):
    """Walk HOME/.local and HOME/.local/bin: create an absent one as a real
    directory, use a real one, and accept a symlinked one only when it
    resolves to a directory this uid owns that no group or other can write.
    Returns (the directory to write in, whether a symlink was followed).
    Anything else that is not a directory raises NotADirectoryError."""
    cur, linked = home, False
    for name in (".local", "bin"):
        comp = os.path.join(cur, name)
        try:
            st = os.lstat(comp)
        except FileNotFoundError:
            os.mkdir(comp)
            cur = comp
            continue
        if stat.S_ISLNK(st.st_mode):
            real = os.path.realpath(comp)
            try:
                rst = os.stat(real)
            except FileNotFoundError:
                rst = None
            if (rst is None or not stat.S_ISDIR(rst.st_mode)
                    or rst.st_uid != os.getuid() or rst.st_mode & 0o022):
                raise WiError(1, f"refused: {comp} is a symlink to {real}, "
                                 "which is not a directory you own that only "
                                 "you can write")
            # Known limit: only the resolved directory's own owner and mode
            # are checked, not its parents'; a parent another user can write
            # could still swap the directory out. Not checked here.
            cur, linked = real, True
        elif stat.S_ISDIR(st.st_mode):
            cur = comp
        else:
            raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR),
                                     comp)
    return cur, linked


def cmd_install_launcher(args):
    src = Path(__file__).resolve().with_name("wi")
    try:
        launcher = src.read_bytes()
    except OSError:
        launcher = None
    if launcher is None or not _launcher_marked(launcher):
        raise WiError(3, f"launcher not found beside wi.py: {src}")
    # HOME from the environment only: Path.home() and expanduser() fall back
    # to the passwd home when HOME is unset, which is not what was asked
    home = os.environ.get("HOME")
    if (not home or not os.path.isabs(home)
            or os.path.normpath(home).lstrip("/") == ""
            or not os.path.isdir(home)):
        raise WiError(1, "refused: HOME must be an absolute directory")
    home = os.path.normpath(home)
    shown = os.path.join(home, ".local", "bin", "wi")
    refusal = (f"refused: {shown} exists and was not made by "
               "install-launcher; it is left as it is")
    tmp = None
    try:
        d, linked = _launcher_dir(home)
        target = os.path.join(d, "wi")
        where = f" (in {d})" if linked else ""
        try:
            st = os.lstat(target)
        except FileNotFoundError:
            st = None
        if st is None:
            # a new target: the whole launcher in a temp file, then an
            # exclusive link, so a file that appears meanwhile is refused and
            # the target never holds a partial launcher
            fd, tmp = tempfile.mkstemp(dir=d, prefix=".wi-")
            with os.fdopen(fd, "wb") as f:
                f.write(launcher)
                os.fchmod(f.fileno(), 0o755)
            try:
                os.link(tmp, target)
            except FileExistsError:
                raise WiError(1, refusal)
            print(f"installed: {shown}{where}")
        elif not stat.S_ISREG(st.st_mode):
            raise WiError(1, refusal)
        else:
            fd = os.open(target, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, "rb") as f:
                fst = os.fstat(f.fileno())
                data = f.read()
                if data == launcher:
                    note = ""
                    if stat.S_IMODE(fst.st_mode) & 0o111 != 0o111:
                        os.fchmod(f.fileno(), 0o755)
                        note = "; made executable"
                    print(f"already installed: {shown}{where} (unchanged"
                          f"{note})")
            if data != launcher:
                if not _launcher_marked(data):
                    raise WiError(1, refusal)
                # an earlier launcher: replace it, unless the target changed
                # between the marker read and the rename
                seen = (fst.st_ino, fst.st_mtime_ns)
                fd, tmp = tempfile.mkstemp(dir=d, prefix=".wi-")
                with os.fdopen(fd, "wb") as f:
                    f.write(launcher)
                    os.fchmod(f.fileno(), 0o755)
                try:
                    now = os.lstat(target)
                except FileNotFoundError:
                    raise WiError(1, refusal)
                if (stat.S_ISLNK(now.st_mode)
                        or (now.st_ino, now.st_mtime_ns) != seen):
                    raise WiError(1, refusal)
                os.replace(tmp, target)
                tmp = None
                print(f"updated: {shown}{where}")
    except OSError as e:
        raise WiError(3, f"cannot write {shown}: {e}")
    finally:
        if tmp is not None:
            with contextlib.suppress(OSError):
                os.unlink(tmp)
    print(f"remove it with: rm {shlex.quote(shown)}")
    real_d = os.path.realpath(d)
    entries = [e for e in os.environ.get("PATH", "").split(os.pathsep)
               if os.path.isabs(e)]
    if not any(os.path.realpath(e) == real_d for e in entries):
        print(f"note: {os.path.dirname(shown)} is not on your PATH; add it in "
              "your shell's startup file yourself (install-launcher never "
              "edits one)")
    others = []
    for e in entries:
        p = os.path.join(e, "wi")
        if (os.path.realpath(e) != real_d and os.path.isfile(p)
                and os.access(p, os.X_OK)
                and os.path.realpath(p) != os.path.realpath(target)
                and p not in others):
            others.append(p)
    for p in others:
        print(f"note: another wi is on your PATH at {p}; whichever PATH "
              "directory comes first runs")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="wi", description=__doc__.split("\n")[0],
        epilog="environment: WORK_ITEMS_ROOT names the work-item root; "
               "WORK_ITEMS_OWNER names the claimant. The old names WI_ROOT "
               "and WI_OWNER still work but are deprecated; the new name "
               "wins when both are set.")
    p.add_argument("--root",
                   help="work-item root (default: $WORK_ITEMS_ROOT, else "
                        "the first of .work-items, .claude-sandbox/work, "
                        ".work that holds items/, else .work-items)")
    sub = p.add_subparsers(dest="command", required=True)
    spec = {
        ("init", cmd_init, "create the work-item root, or record an "
         "existing one's tracking choice; a git-ignored store gets its own "
         "local repo"): [],
        ("next", cmd_next, "what to work on"): [
            ("--json",), ("--plain",), ("--limit", dict(type=int, default=7)),
            ("--stale", dict(default="24h")), ("--pipeline",), ("--one",),
            ("--claim", dict(metavar="WORKER")), ("--non-interactive",)],
        ("show", cmd_show, "show one item; --card N prints decision N's "
         "current card record (path, rev, format, the sha256 of the file's "
         "bytes, then the bytes), --all every revision's line; read-only"): [
            ("id", {}), ("--brief",), ("--json",),
            ("--card", dict(metavar="N")), ("--all",)],
        ("add", cmd_add, "create an item"): [
            ("title", {}), ("-t", "--type", dict(default="task", choices=sorted(TYPES))),
            ("-p", "--priority", dict(type=int, default=2, choices=range(5))),
            ("--tag", dict(action="append")), ("--dep", dict(action="append")),
            ("--parent", {}), ("--ref", dict(action="append")), ("--slug", {}),
            ("--short-display-name", {}), ("--desc", {}), ("--force",),
            ("--json",)],
        ("claim", cmd_claim, "claim an item"): [
            ("id", {}), ("--as", dict(dest="as_owner")), ("--steal",)],
        ("release", cmd_release, "release a claim"): [("id", {})],
        ("handoff", cmd_handoff, "rewrite the Handoff block"): [
            ("id", {}), ("--doing", {}), ("--next", {}), ("--blocked", {}),
            ("--learned", {})],
        ("done", cmd_done, "close an item"): [
            ("id", {}), ("--drop",), ("--note", {})],
        ("note", cmd_note, "append dated lines (or --raw lines) to an "
         "item's Notes, under the lock; texts go after --"): [
            ("id", {}), ("lines", dict(nargs="+", metavar="text")),
            ("--raw",)],
        ("raise", cmd_raise, "give out the next decision number under the "
         "lock and append its `decision N:` headline and `raised:` line to "
         "an item; the question goes after --, or --record FILE|- writes "
         "the card record (cards/<id>/<N>/<rev>.card<k>.json, immutable) "
         "and builds the headline from it; --revise N --why restates an "
         "open decision; --lines adds machine lines; prints N"): [
            ("id", {}),
            ("--record", dict(metavar="FILE|-")),
            ("--revise", dict(metavar="N")), ("--why", {}),
            ("--lines", dict(metavar="FILE|-", dest="lines_file")),
            ("--raised", dict(metavar="UTC")), ("--check",)],
        ("counter", cmd_counter, "print the last decision number given out "
         "(the larger of store.yaml's counter and the items' highest N); "
         "read-only"): [],
        ("block", cmd_block, "block on a reason or another item"): [
            ("id", {}), ("reason", dict(nargs="?")), ("--on", {})],
        ("unblock", cmd_unblock, "clear a block"): [("id", {}), ("--dep", {})],
        ("park", cmd_park, "defer an item deliberately, with a reason"): [
            ("id", {}), ("reason", {})],
        ("unpark", cmd_unpark, "return a parked item to todo (or blocked)"): [
            ("id", {})],
        ("groom", cmd_groom, "hold an item for the operator's answers to its "
         "open questions"): [("id", {}), ("questions", {})],
        ("ungroom", cmd_ungroom, "return a grooming item to todo (or blocked)"): [
            ("id", {})],
        ("needs-input", cmd_needs_input, "list every item awaiting the "
         "operator: grooming items and unanswered decision N: lines"): [
            ("--json",), ("--plain",)],
        ("estate", cmd_estate, "read-only sweep of every work-item store "
         "one level under a dir: counts, top ready, unanswered decisions, "
         "stale claims"): [
            ("--dir", dict(action="append")), ("--top", dict(type=int, default=5)),
            ("--stale", dict(default="24h")), ("--json",)],
        ("migrate-parked", cmd_migrate_parked,
         "convert blocked items whose reason starts PARKED to parked"): [
            ("--apply",)],
        ("repair-escapes", cmd_repair_escapes,
         "list (or --apply) a heuristic repair of backslash layers an older "
         "wi added to quoted values"): [
            ("--id", {}), ("--key", {}), ("--apply",)],
        ("ls", cmd_ls, "list items"): [
            ("--status", {}), ("--type", {}), ("--tag", {}), ("--owner", {}),
            ("--dep", {}), ("--ready",), ("--json",), ("--plain",)],
        ("set", cmd_set, "set one front-matter field"): [
            ("id", {}), ("field", {}), ("value", {}), ("--force",)],
        ("import-todo", cmd_import_todo, "import a TODO.md"): [
            ("path", {}), ("--dry-run",)],
        ("export", cmd_export, "export to backlog-yaml"): [
            ("path", {}), ("--format", dict(required=True)), ("--done-out", {}),
            ("--project", {})],
        ("import", cmd_import, "import from backlog-yaml"): [
            ("path", {}), ("done_path", dict(nargs="?")),
            ("--format", dict(required=True)), ("--update",)],
        ("prime", cmd_prime, "budgeted rehydration manifest"): [
            ("--budget", dict(type=int, default=300))],
        ("lint", cmd_lint, "validate every item"): [],
        ("commit", cmd_commit, "commit the store's own files, under its "
         "lock, into the repo that holds them"): [
            ("-m", "--message", {})],
        ("archive", cmd_archive, "move closed items to archive/"): [
            ("--older-than", dict(default="90d"))],
        ("install-launcher", cmd_install_launcher, "copy the wi launcher to "
         "~/.local/bin, on request; refuses a file it did not make"): [],
    }
    for (name, func, help_text), flags in spec.items():
        sp = sub.add_parser(name, help=help_text)
        sp.set_defaults(func=func)
        for flag in flags:
            kw = flag[-1] if isinstance(flag[-1], dict) else {"action": "store_true"}
            names = [f for f in flag if isinstance(f, str)]
            sp.add_argument(*names, **kw)
    track = sub.choices["init"].add_mutually_exclusive_group()
    track.add_argument("--track", action="store_true",
                       help="git tracks the store")
    sub.choices["init"].add_argument(
        ALLOW_OLD_FLAG, action="store_true",
        help="init at an old location (.work, .claude-sandbox/work), or "
             "beside one holding items/, when the operator keeps the store "
             "there or the directory is the project's own; never recorded, "
             "needed on every such init")
    track.add_argument("--no-track", action="store_true",
                       help="the repo ignores the store (its line added to "
                            ".gitignore), which keeps its own local git "
                            "repo: created, or adopted with its history")
    return p


def _raise_question(parser, extra, argv):
    """raise's question line, from what argparse left over. It is not a
    positional: an optional positional after the id is consumed, empty, as
    soon as an option follows the id, and `-- '<question>'` after options
    would then be refused. One text, after `--` when it starts with `-`."""
    if "--" in argv and argv[argv.index("--") + 1:] == ["--"]:
        return "--"  # `-- --`: a question _question_refusal refuses
    left = list(extra)
    if "--" in left:  # kept or dropped by Python version
        left.remove("--")
    # a usage error counts and places the leftover texts, never echoes
    # them: a mistyped question may hold a secret
    after = argv[argv.index("--") + 1:] if "--" in argv else []
    if len(left) > 1:
        where = "after --" if len(after) == len(left) else \
            "outside the options" if not after else "before and after --"
        parser.error(f"{len(left)} texts {where}; expected one question "
                     "after --")
    question = left[-1] if left else None
    # a text starting `-` is a question only as the one text after `--`;
    # anything else is a misspelled option (`--chek`), never a question
    if question is not None and question.startswith("-") and \
            after != [question]:
        parser.error("an unrecognized option (1 text starting '-' before "
                     "--); a question starting '-' goes after --")
    return question


def main(argv=None):
    parser = build_parser()
    args, extra = parser.parse_known_args(argv)
    args.argv = list(sys.argv[1:] if argv is None else argv)
    if args.command == "raise":
        args.question = _raise_question(parser, extra, args.argv)
    elif extra:
        parser.error("unrecognized arguments: " + " ".join(extra))
    _COMMAND[0] = args.command
    try:
        return args.func(args) or 0
    except WiError as e:
        print(f"wi: {e}", file=sys.stderr)
        return e.code
    except FileNotFoundError as e:
        print(f"wi: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
