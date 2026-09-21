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
- Exit codes: 0 ok, 1 usage/validation, 2 not found/empty, 3 file/parser
  error, 4 lock or claim conflict.
"""
import argparse
import fcntl
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

FIELD_ORDER = ["id", "title", "type", "status", "stage", "priority", "tags",
               "deps", "parent", "owner", "claimed", "blocked", "parked",
               "feedback",
               "mode", "complexity", "alias", "created", "updated", "closed",
               "refs", "x_backlog"]
FLOW_LIST_FIELDS = {"tags"}
BLOCK_LIST_FIELDS = {"deps", "refs"}
LIST_FIELDS = FLOW_LIST_FIELDS | BLOCK_LIST_FIELDS
MAP_FIELDS = {"x_backlog"}
INT_FIELDS = {"priority"}
TYPES = {"task", "bug", "feature", "refactor", "workflow", "chore", "epic", "spike"}
STATUSES = {"todo", "doing", "blocked", "parked", "done", "dropped"}
STAGES = {"implement", "review", "testing", "uat", "uat_feedback"}
MODES = {"autonomous", "interactive", "mixed"}
COMPLEXITIES = {"low", "medium", "high"}
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


class WiError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now_minute():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def tokens(text):
    return (len(text) + 3) // 4


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:40].rstrip("-") or "item"


def make_id(title, created):
    suffix = hashlib.sha1((title + created).encode() + os.urandom(8)).hexdigest()[:4]
    return f"{slugify(title)}-{suffix}"


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
# C0/C1 controls, DEL, and the characters YAML or str.splitlines treat as
# line or byte-order marks are written as escapes, never raw
_DQ_ESCAPE_RE = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f\u2028\u2029\ufeff]")


def _dq_escape(v):
    v = v.replace("\\", "\\\\").replace('"', '\\"')
    return _DQ_ESCAPE_RE.sub(
        lambda m: (f"\\x{ord(m.group()):02x}" if ord(m.group()) < 0x100
                   else f"\\u{ord(m.group()):04x}"), v)


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
        if width and len(digits) == width and re.fullmatch(r"[0-9A-Fa-f]+", digits):
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


def parse_front(lines, suspects=None):
    """Return (meta, extra_keys, errors). Scalars stay strings; a bare `—` or
    an empty value → None. When `suspects` is a dict, each key whose quoted
    scalars look escape-amplified (see _looks_amplified) maps to that set."""
    meta, extra, errors = {}, [], []

    def scalar(key, token):
        val, quoted = _parse_scalar(token)
        if quoted and suspects is not None and _looks_amplified(val):
            suspects.setdefault(key, set()).add(val)
        return val, quoted

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
            val = [scalar(key, x)[0] for x in _split_flow(inner)] if inner else []
        elif rest:
            val, quoted = scalar(key, rest)
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
                    item, quoted = scalar(key, sub[2:])
                    if item.endswith(":") and not quoted:
                        errors.append(f"nested structure under {key}: {sub!r}")
                    block.append(item)
                elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", sub):
                    sk, sv = sub.split(":", 1)
                    submap[sk.strip()] = scalar(key, sv)[0]
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
    """Bare when a bare scalar reads back unchanged (by wi and by a YAML
    loader), else double-quoted with _dq_escape: mapping/comment indicators,
    structure chars, surrounding whitespace, a leading YAML indicator, the
    `—` that reads as empty, control characters, or (in a flow list) a comma."""
    v = str(v)
    if (v == "" or v != v.strip() or v == "—" or v.endswith(":")
            or re.search(r":[ \t]|[ \t]#|[\[\]{}]", v)
            or v.startswith(_BARE_UNSAFE_START) or _DQ_ESCAPE_RE.search(v)
            or (flow and "," in v)):
        return '"' + _dq_escape(v) + '"'
    return v


def _front_one_line(key, val):
    """Every front-matter value is one line: a line break would forge keys
    (`status: done`) or leave a file no later command can parse. This is the
    backstop behind the per-command checks; render() runs before any write,
    so a rejected value writes nothing."""
    vals = val.values() if isinstance(val, dict) else \
        val if isinstance(val, list) else [val]
    for v in vals:
        if isinstance(v, str) and ("\n" in v or "\r" in v):
            raise WiError(1, f"front-matter '{key}' must be one line; "
                             "it contains a line break")


def emit_front(meta, extra=()):
    out = []
    for key in list(FIELD_ORDER) + [k for k in extra if k not in FIELD_ORDER]:
        if key not in meta:
            continue
        val = meta[key]
        if val is None or val == [] or val == {}:
            continue
        _front_one_line(key, val)
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
        self.escape_suspects = {}

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
        suspects = {}
        meta, extra, errors = parse_front(front.rstrip("\n").split("\n"),
                                          suspects)
        if errors:
            raise WiError(3, f"{path}: " + "; ".join(errors))
        item = cls(meta, extra, None, None, path, body=body, eol=eol)
        item.escape_suspects = suspects
        return item

    def render(self):
        eol = self.eol
        front = emit_front(self.meta, self.extra).replace("\n", eol)
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
        if m.get("status") == "blocked" and not m.get("blocked"):
            errs.append("blocked without a reason")
        if m.get("status") == "parked" and not m.get("parked"):
            errs.append("parked without a reason")
        if m.get("parked") and m.get("status") in ("todo", "doing", "blocked"):
            errs.append(f"parked reason on a {m['status']} item (wi unpark "
                        "clears it; or clear the field with wi set)")
        if m.get("status") in ("done", "dropped") and not m.get("closed"):
            errs.append(f"{m['status']} without closed date")
        return errs


# ── Store: root, lock, load/save ────────────────────────────────────────────

def resolve_root(explicit=None, must_exist=True):
    root = explicit or os.environ.get("WI_ROOT")
    if root:
        root = Path(root)
    elif Path(".claude-sandbox").is_dir():
        root = Path(".claude-sandbox/work")
    else:
        root = Path(".work")
    if must_exist and not (root / "items").is_dir():
        raise WiError(1, f"no work-item root at {root} (run `wi init`)")
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


def _git(cwd, *args, stdin=None):
    """Run git; None when it is missing, the cwd is gone, or it times out.
    Output is decoded here, not by subprocess: -z output is raw bytes (no
    quotePath), and a non-UTF-8 path must neither crash nor depend on the
    locale; backslashreplace shows such a byte readably, as \\xe9."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    try:
        r = subprocess.run(["git"] + list(args), cwd=cwd, env=env,
                           input=None if stdin is None else stdin.encode(),
                           capture_output=True, timeout=GIT_TIMEOUT)
        r.stdout = r.stdout.decode("utf-8", "backslashreplace")
        r.stderr = r.stderr.decode("utf-8", "backslashreplace")
        return r
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _dir_level(pattern, root):
    """True when an ignore pattern excludes a directory on the store's path
    (a trailing '/', or its last segment matches a parent dir of the probe
    item). git cannot re-include a path under an excluded directory, so a
    negation is dead advice for such a rule. Heuristic: the parents checked
    are every component of the store's absolute path, plus items/."""
    p = pattern.strip()
    if p.endswith("/"):
        return True
    last = p.rsplit("/", 1)[-1]
    parents = list(root.absolute().parts[1:]) + ["items"]
    return any(fnmatch.fnmatchcase(d, last) for d in parents)


def custody_warning(root):
    """One-line warning when the store is silently untracked, else None.
    Silent outside git, when git is missing or slow, or on any git error."""
    # the probe path, not only `items`, catches a store whose tracked files
    # mask the ignore rule: check-ignore skips tracked paths, but a new
    # item's path is still matched against the rule. -v names the rule; -z
    # (which git allows only with --stdin) gives NUL-separated fields with
    # paths unquoted, so a source path holding ':N:', a tab or a non-ASCII
    # byte parses; _git decodes the raw bytes without failing.
    r = _git(root, "check-ignore", "-v", "-z", "--stdin",
             stdin=f"items\0{PROBE_ITEM}\0")
    if r is None or r.returncode not in (0, 1):
        return None
    fields = r.stdout.split("\0")
    rule = None
    for i in range(0, len(fields) - 3, 4):   # source, linenum, pattern, path
        src, lineno, pattern = fields[i:i + 3]
        if pattern and not pattern.startswith("!"):   # a negation un-ignores
            rule = (src, lineno, pattern)
            break
    head = f"wi: WARNING store {root} is silently untracked: "
    if rule:
        src, lineno, pattern = rule
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
            return head + f"new items are git-ignored by {where}; fix: {remedy}"
        fix = [f"new items are git-ignored by {where}; fix: {remedy}"]
        if shape is not None:
            fix.append(" and set trackInHost: true in the sandbox config (a "
                       "claude-sandbox launcher at 490d8ca or later warns "
                       "about this)")
            if whole_dir:
                # agents 0002: a public-shaped repo keeps the whole-dir
                # ignore; removing it would publish private items
                fix.append(", or, for a public repo, give .claude-sandbox/ "
                           "its own sidecar git")
        return head + "".join(fix)
    n = len(item_paths(root))
    if n < UNTRACKED_MIN_ITEMS:
        return None
    r = _git(root, "ls-files", "--", ".")
    if r is None or r.returncode != 0 or r.stdout.strip():
        return None
    return head + f"it holds {n} items and git tracks none; fix: `git add` the store"


class Lock:
    """flock on <root>/.lock; 10s wait then exit 4."""

    def __init__(self, root, timeout=10.0):
        self.path, self.timeout, self.fh = root / ".lock", timeout, None

    def __enter__(self):
        self.fh = open(self.path, "a")
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if time.monotonic() >= deadline:
                    self.fh.close()
                    raise WiError(4, "lock timeout on " + str(self.path))
                time.sleep(0.05)

    def __exit__(self, *exc):
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()


def read_raw(path):
    """Read without newline translation, so CRLF survives a rewrite."""
    with open(path, newline="") as fh:
        return fh.read()


def atomic_write(path, text):
    tmp = path.with_name(path.name + ".tmp" + str(os.getpid()))
    with open(tmp, "w", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def save_item(root, item):
    save_items(root, [item])


def save_items(root, items):
    """Render every item before writing any, so a value the writer rejects
    (see _front_one_line) leaves the whole batch unwritten."""
    staged = [(item, item.path or root / "items" / (item.id + ".md"),
               item.render()) for item in items]
    for item, path, text in staged:
        item.path = path
        atomic_write(path, text)


def item_paths(root, archived=False):
    paths = sorted((root / "items").glob("*.md"))
    if archived and (root / "archive").is_dir():
        paths += sorted((root / "archive").glob("*/*.md"))
    return paths


def load_all(root, archived=False):
    items = []
    for path in item_paths(root, archived):
        items.append(Item.parse(read_raw(path), path))
    return items


def resolve_id(items, ref):
    exact = [it for it in items if it.id == ref or it.get("alias") == ref]
    if exact:
        return exact[0]
    matches = [it for it in items if it.id.startswith(ref)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise WiError(2, f"ambiguous id '{ref}': " + ", ".join(it.id for it in matches))
    raise WiError(2, f"no item matching '{ref}'")


def load_item_anywhere(root, ref):
    return resolve_id(load_all(root, archived=True), ref)


# ── Readiness and ranking ───────────────────────────────────────────────────

def dep_resolved(dep, by_id):
    if dep.startswith("ext:"):
        return False
    target = by_id.get(dep)
    if target is None:
        return False
    return (target.get("status") in ("done", "dropped")
            or (target.get("status") == "doing"
                and target.get("stage") in ("uat", "uat_feedback")))


def is_ready(item, by_id):
    if item.get("status") != "todo":
        return False
    return all(dep_resolved(d, by_id) for d in item.get("deps", []))


def rank_ready(items):
    return sorted(items, key=lambda it: (it.get("priority", 2), it.get("created", ""), it.id))


def split_by_status(items):
    open_items = {"doing": [], "blocked": [], "todo": [], "parked": []}
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


# ── Commands ────────────────────────────────────────────────────────────────

# Host-.gitignore spellings that ignore the whole .claude-sandbox/ dir.
SANDBOX_IGNORES = ("/.claude-sandbox/", "/.claude-sandbox",
                   ".claude-sandbox/", ".claude-sandbox")


def sandbox_shape(root):
    """Classify a `.claude-sandbox/work` store per agents/decisions/0002:
    ('private'|'sidecar'|'ignored', repo_dir), or (None, None) for `.work/`
    and other non-sandbox stores. private = host repo tracks config + work;
    sidecar = a git repo at .claude-sandbox/.git owns the store; ignored =
    the host .gitignore already whole-dir-ignores .claude-sandbox/."""
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


def cmd_init(args):
    root = resolve_root(args.root, must_exist=False)
    (root / "items").mkdir(parents=True, exist_ok=True)
    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Work items\n\nOne markdown file per item, managed by `wi` "
            "(the work-items plugin's skills/work-items).\nStart with "
            "`wi prime`, then `wi show <id> --brief` for the item you will "
            "work.\nFormat: the work-items plugin's "
            "skills/work-items/references/format.md\n")
    gi = root / ".gitignore"
    if not gi.exists():
        gi.write_text(".lock\n*.tmp*\n")
    shape, repo = sandbox_shape(root)
    if shape == "private":
        print("private-shaped repo (no sidecar git, .claude-sandbox/ not "
              "gitignored): host .gitignore left alone so the store stays "
              "tracked")
    elif shape == "sidecar":
        host_gi = repo / ".gitignore"
        text = host_gi.read_text() if host_gi.is_file() else ""
        lines = {ln.strip() for ln in text.splitlines()}
        if not lines.intersection(SANDBOX_IGNORES):
            if text and not text.endswith("\n"):
                text += "\n"
            host_gi.write_text(text + "/.claude-sandbox/\n")
            print("sidecar git at .claude-sandbox/.git: added "
                  "/.claude-sandbox/ to host .gitignore")
    # shape 'ignored' (already whole-dir-ignored) and non-sandbox stores:
    # never duplicate the line, never touch the host .gitignore.
    print(f"initialised {root}")
    return 0


def cmd_add(args):
    _one_line("title", args.title)
    root = resolve_root(args.root)
    created = today()
    title = args.title.strip()
    if not title or len(title) > 120:
        raise WiError(1, "title must be 1-120 chars")
    with Lock(root):
        items = load_all(root, archived=True)
        by_id = {it.id: it for it in items}
        for dep in args.dep or []:
            if not dep.startswith("ext:") and dep not in by_id and not args.force:
                raise WiError(1, f"dep '{dep}' does not resolve (--force to add anyway)")
        if args.parent and args.parent not in by_id and not args.force:
            raise WiError(1, f"parent '{args.parent}' does not resolve")
        while True:
            iid = (slugify(args.slug) if args.slug else slugify(title))
            iid += "-" + hashlib.sha1(
                (title + created).encode() + os.urandom(8)).hexdigest()[:4]
            if iid not in by_id:
                break
        desc = sys.stdin.read().strip() if args.desc == "-" else (args.desc or "")
        meta = {"id": iid, "title": title, "type": args.type, "status": "todo",
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


def default_owner():
    return os.environ.get("WI_OWNER") or \
        f"{os.environ.get('USER', 'unknown')}@{os.uname().nodename.split('.')[0]}"


def _claim(item, owner, steal=False):
    if item.get("status") == "blocked":
        raise WiError(1, f"{item.id} is blocked ({item.get('blocked')}); unblock first")
    if item.get("status") == "parked":
        raise WiError(1, f"{item.id} is parked ({item.get('parked')}); unpark first")
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
    owner = args.as_owner or default_owner()
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        if _claim(item, owner, args.steal):
            save_item(root, item)
    print(f"claimed {item.id} as {owner}")
    return 0


def cmd_release(args):
    root = resolve_root(args.root)
    with Lock(root):
        item = load_item_anywhere(root, args.id)
        item.meta.update(owner=None, claimed=None, stage=None)
        if item.get("status") != "parked":   # releasing a claim never unparks
            item.meta["status"] = "todo"
        item.touch()
        save_item(root, item)
    print(f"released {item.id}")
    return 0


def _one_line(what, val):
    """Values written into front matter, a Handoff bullet or a Notes line are
    one line (format.md): a line break would add front-matter keys, leave
    lines the next rewrite does not own, or inject a `## ` heading. Called
    before anything is read or written, so a rejected value writes nothing."""
    if val is not None and ("\n" in val or "\r" in val):
        raise WiError(1, f"{what} must be one line; it contains a line break")


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
            line = f"- {today()} learned: {args.learned}"
            if line not in (item.section("Notes") or ""):
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
            # a block supersedes a park: the item is no longer deferred
            item.meta.update(status="blocked", blocked=args.reason, parked=None)
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
    item.meta.update(status="parked", parked=reason, owner=None, claimed=None,
                     stage=None)
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


def cmd_migrate_parked(args):
    """Convert `status: blocked` items whose reason starts with PARKED (the
    convention before `parked` existed) to parked. Dry run unless --apply."""
    root = resolve_root(args.root)
    rows = []
    with Lock(root):
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
    loads; this lists each quoted value whose every backslash pairs as `\\\\`
    or `\\"` and the value with those layers peeled. That pattern can also be
    meant (a title about escapes), so it is a dry run until --apply; to keep
    one value, fix it by hand with `wi set` instead."""
    root = resolve_root(args.root)
    rows, changed = [], []
    with Lock(root):
        for item in load_all(root, archived=True):
            if args.id and item.id != args.id:
                continue
            fixes = []
            for key, bad in sorted(item.escape_suspects.items()):
                val = item.meta.get(key)
                fix = (lambda v: _deamplify(v) if v in bad else v)
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
    print(f"{len(rows)} {'repaired' if args.apply else 'to repair (dry run; --apply to write)'}")
    return 0


def cmd_set(args):
    root = resolve_root(args.root)
    field, value = args.field, args.value
    _one_line("value", value)
    if field in ("id", "created"):
        raise WiError(1, f"'{field}' is immutable")
    if field not in FIELD_ORDER:
        raise WiError(1, f"unknown field '{field}'")
    with Lock(root):
        items = load_all(root, archived=True)
        by_id = {it.id: it for it in items}
        item = resolve_id(items, args.id)
        if value in ("", "—", "--clear"):
            item.meta[field] = None
        elif field in LIST_FIELDS:
            item.meta[field] = [v.strip() for v in value.split(",") if v.strip()]
        elif field in INT_FIELDS:
            item.meta[field] = int(value)
        elif field == "status" and value == "parked":
            # parking releases the claim and records a reason: `wi park` is
            # the one path in, so set never leaves a half-parked item
            if item.get("status") != "parked":
                raise WiError(1, f"use wi park {item.id} \"<reason>\" to park an item")
        elif field == "status" and item.get("status") == "parked":
            # leaving parked by set is an unpark: the reason goes with it
            item.meta.update(status=value, parked=None)
            item.append_note(f"- {today()} unparked (set status {value})")
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
    by_id = {it.id: it for it in items}
    statuses = (set(STATUSES) if args.status == "all"
                else set((args.status or "todo,doing,blocked").split(",")))
    rows = [it for it in items if it.get("status") in statuses]
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
                    f"{it.get('stage') or '-'}\t{it.get('owner') or '-'}\t{it.get('title')}")
            print(line if args.plain else line.expandtabs(2))
    return 0 if rows else 2


def cmd_show(args):
    root = resolve_root(args.root)
    items = load_all(root, archived=True)
    by_id = {it.id: it for it in items}
    item = resolve_id(items, args.id)
    if args.json:
        rec = item_json(item, by_id)
        rec["body"] = item.desc
        rec["sections"] = dict(item.sections)
        rec["acceptance"] = parse_acceptance(item)
        rec["blocked_by_unresolved"] = [d for d in item.get("deps", [])
                                        if not dep_resolved(d, by_id)]
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
        print(item.render(), end="")
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
    by_id = {it.id: it for it in items}
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
                                     "done": len(closed)}}, indent=1))
        return 0
    out = []
    if args.plain:
        for section, its in (("doing", doing), ("blocked", grouped["blocked"]),
                             ("ready", ready[:args.limit])):
            for it in its:
                out.append("\t".join([section, it.id, f"P{it.get('priority', 2)}",
                                      it.get("status"), it.get("stage") or "-",
                                      it.get("owner") or "-", it.get("title")]))
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
            out.append(f"  P{it.get('priority', 2)} {it.id}  {it.get('title')}   "
                       f"{it.get('owner') or '-'} {age_str(claimed)}{stale}")
            nxt = it.handoff().get("next")
            if nxt:
                out.append(f"     next: {nxt}")
    if grouped["blocked"]:
        out.append("BLOCKED")
        for it in grouped["blocked"]:
            out.append(f"  P{it.get('priority', 2)} {it.id}  {it.get('title')}   "
                       f"blocked: {it.get('blocked')}")
    if ready:
        out.append("READY")
        for it in ready[:args.limit]:
            out.append(f"  P{it.get('priority', 2)} {it.id}  {it.get('title')}")
    parked = (f" · {len(grouped['parked'])} parked (wi ls --status parked)"
              if grouped["parked"] else "")
    out.append(f"{max(0, len(ready) - args.limit)} more ready · {waiting} waiting "
               f"on deps{parked} · {len(closed)} done (wi ls --status done)")
    print("\n".join(out))
    return 0 if (doing or grouped["blocked"] or ready) else 2


def next_pipeline(root, args):
    with Lock(root):
        items = load_all(root)
        by_id = {it.id: it for it in items}
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
                  f"{queue}\t{item.id}\t{item.get('title')}")
            return 0
    if args.json:
        print(json.dumps([dict(item_json(it, by_id), queue=q)
                          for q, it in ordered], indent=1))
    else:
        for q, it in ordered:
            print(f"{q}\t{it.id}\tP{it.get('priority', 2)}\t{it.get('title')}")
    return 0 if ordered else 2


def cmd_prime(args):
    root = resolve_root(args.root)
    items = load_all(root)
    by_id = {it.id: it for it in items}
    grouped, closed = split_by_status(items)
    doing = sorted(grouped["doing"], key=lambda it: (
        it.get("owner") != default_owner(), it.get("priority", 2)))
    ready = rank_ready([it for it in grouped["todo"] if is_ready(it, by_id)])
    n_open = sum(len(v) for v in grouped.values())
    budget = args.budget
    lines = [f"wi: {root} · {n_open} open · {len(grouped['doing'])} doing · "
             f"{len(grouped['blocked'])} blocked · run `wi show <id>` before "
             f"working an item, `wi handoff` at every stop"]
    warning = custody_warning(root)
    # the warning is header: its tokens are reserved from the budget, and it
    # is inserted after trimming so trimming never drops it
    reserved = tokens(warning) + 1 if warning else 0
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

    for it in doing:
        who = "you" if it.get("owner") == default_owner() else it.get("owner", "-")
        take(f"DOING  P{it.get('priority', 2)} {it.id}  {it.get('title')}  "
             f"({who}, {age_str(it.get('claimed'))})")
        h = it.handoff()
        if h.get("next"):
            take(f"       next: {h['next']}")
        if h.get("doing") and spent < budget * 3 // 4:
            take(f"       doing: {h['doing']}")
    if grouped["blocked"]:
        take(f"BLOCKED {len(grouped['blocked'])}: " + " ".join(
            f"{it.id} ({it.get('blocked')})" for it in grouped["blocked"][:3]))
    if grouped["parked"]:
        # deliberately deferred: a count, never a list — see wi ls --status parked
        take(f"PARKED {len(grouped['parked'])} (wi ls --status parked)")
    shown = 0
    for i, it in enumerate(ready):
        prefix = "READY  " if shown == 0 else "       "
        if not take(f"{prefix}P{it.get('priority', 2)} {it.id}  {it.get('title')}"):
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
    if warning:
        lines.insert(1, warning)
        text = "\n".join(lines)
    print(text)
    return 0


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
    item["title"] = re.sub(r"\s+", " ", title).strip()[:120]
    paras = body.strip().split("\n\n")
    item["desc"] = paras[0].strip() if paras else ""
    item["notes"] = "\n\n".join(p for p in paras[1:]).strip()
    for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", body):
        target = m.group(1)
        if not target.startswith(("http://", "https://")) and target not in item["refs"]:
            item["refs"].append(target)
    return item


def _bullet_item(text):
    item = {"status": "todo", "closed": None, "priority": None, "tags": [],
            "refs": [], "notes": ""}
    m = re.match(r"^\*\*(.+?)\*\*[.:]?\s*[—-]*\s*(.*)$", text, re.S)
    if m:
        title, rest = m.group(1).rstrip("."), m.group(2)
    else:
        first, _, rest = text.partition("\n")
        title, rest = first, rest
    item["title"] = re.sub(r"\s+", " ", title).strip()[:120]
    item["desc"] = rest.strip()
    return item


def cmd_import_todo(args):
    root = resolve_root(args.root)
    text = Path(args.path).read_text()
    parsed = parse_todo(text)
    created_rows, skipped_rows, new_items = [], [], []
    with Lock(root):
        items = load_all(root, archived=True)
        markers = {r for it in items for r in it.get("refs", [])}
        ids = {it.id for it in items}
        for rec in parsed:
            marker = todo_marker(rec["title"])
            if marker in markers:
                skipped_rows.append((marker, rec["title"]))
                continue
            markers.add(marker)
            date = rec["closed"] or today()
            while True:
                iid = make_id(rec["title"], date)
                if iid not in ids:
                    break
            ids.add(iid)
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


def _yaml_scalar(v):
    if isinstance(v, int):
        return str(v)
    v = str(v)
    if v.startswith(("[", "{")):  # JSON-encoded passthrough; JSON is YAML flow
        return v
    return '"' + _dq_escape(v) + '"'


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
            blocked = "PARKED: " + (it.get("parked") or "")
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
            w.append("    notes: |-")
            w.extend("      " + ln if ln.strip() else "" for ln in notes.split("\n"))
        for key, val in (it.get("x_backlog") or {}).items():
            w.append(f"    {key}: {_yaml_scalar(val)}")
    return "\n".join(w) + "\n"


def cmd_export(args):
    if args.format != "backlog-yaml":
        raise WiError(1, f"unknown export format '{args.format}'")
    root = resolve_root(args.root)
    out = Path(args.path)
    done_out = Path(args.done_out) if args.done_out else \
        out.with_name(out.stem + "_done" + out.suffix)
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
    break the requires links of the stories that name it."""
    return v if not isinstance(v, str) else re.sub(r"\s+", " ", v).strip()


def _import_story(story, alias_map, existing_by_alias, update):
    story = {k: ([_fold(x) for x in v] if isinstance(v, list) and
                 k in ("requires", "acceptance", "testing") else
                 v if k == "notes" else _fold(v))
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
    blocked = story.get("blocked_reason") or None
    parked = parked_reason(blocked) if status == "blocked" else None
    if parked is not None:
        status, blocked = "parked", None
    if update and alias in existing_by_alias:
        it = existing_by_alias[alias]
        if parked is not None:
            # the export carries only the park; a blocked: reason kept under
            # it (unpark returns to blocked) lives only in the store
            blocked = it.get("blocked")
        it.meta.update(status=status, stage=stage, blocked=blocked, parked=parked,
                       feedback=story.get("review_feedback") or None,
                       owner=story.get("claimed_by") or None,
                       x_backlog=x_backlog or None)
        if status in ("done", "dropped") and not it.get("closed"):
            it.meta["closed"] = today()
        it.touch()
        return it, False
    desc, handoff, notes = _split_backlog_notes(story.get("notes"))
    title = str(story["title"])[:120]
    meta = {"id": make_id(title, today()), "title": title, "status": status,
            "stage": stage, "priority": priority, "alias": alias,
            "blocked": blocked, "parked": parked,
            "feedback": story.get("review_feedback") or None,
            "owner": story.get("claimed_by") or None,
            "mode": story.get("ticket_mode") or None,
            "complexity": story.get("complexity") or None,
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
    deps = []
    for req in story.get("requires") or []:
        deps.append(alias_map.get(str(req), f"ext: {req}"))
    item.meta["deps"] = deps
    return item, True


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
        pending = []
        for story in stories:
            item, created = _import_story(story, alias_map, existing_by_alias,
                                          args.update)
            if created:
                alias_map[item.get("alias")] = item.id
            pending.append((story, item, created))
        for story, item, created in pending:
            if created:
                item.meta["deps"] = [alias_map.get(str(r), f"ext: {r}")
                                     for r in (story.get("requires") or [])]
                n_new += 1
            else:
                n_upd += 1
        save_items(root, [item for _, item, _ in pending])
    print(f"imported {n_new} new, updated {n_upd}")
    return 0


# ── lint, archive ───────────────────────────────────────────────────────────

SECRET_ASSIGN_RE = re.compile(r"^\s*(?:export\s+)?[A-Z][A-Z0-9_]{2,}=(?![$<{])\S{8,}")
SECRET_KV_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|passwd|credential|webhook[_-]?url)\b"
    r"['\"]?\s*[:=]\s*['\"]?(?![$<{*])([A-Za-z0-9+/_.-]{12,})")


def secret_findings(text):
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        if "PRIVATE KEY-----" in line:
            out.append((n, "PEM private key material"))
        elif SECRET_ASSIGN_RE.match(line) or SECRET_KV_RE.search(line):
            out.append((n, "likely secret value (record the path and key, never the value)"))
    return out


def cmd_lint(args):
    root = resolve_root(args.root)
    problems = []
    items = []
    for path in item_paths(root, archived=True):
        text = path.read_text()
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
        if it.id in by_id:
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
        for n, why in secret_findings(it.render()):
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
    # lint has no warning tier: every finding it prints is a problem, exit 3
    warning = custody_warning(root)
    if warning:
        problems.append(warning)
    for p in problems:
        print(p)
    if problems:
        return 3
    print(f"lint clean: {len(items)} items")
    return 0


def cmd_archive(args):
    root = resolve_root(args.root)
    cutoff = parse_duration(args.older_than)
    now = datetime.now(timezone.utc)
    moved = 0
    with Lock(root):
        for item in load_all(root):
            if item.get("status") not in ("done", "dropped") or not item.get("closed"):
                continue
            closed = datetime.strptime(item.get("closed"), "%Y-%m-%d").replace(
                tzinfo=timezone.utc)
            if (now - closed).total_seconds() < cutoff:
                continue
            year_dir = root / "archive" / item.get("closed")[:4]
            year_dir.mkdir(parents=True, exist_ok=True)
            os.replace(item.path, year_dir / item.path.name)
            moved += 1
    print(f"archived {moved}")
    return 0


# ── CLI ─────────────────────────────────────────────────────────────────────

def build_parser():
    p = argparse.ArgumentParser(prog="wi", description=__doc__.split("\n")[0])
    p.add_argument("--root", help="work-item root (default: $WI_ROOT or auto)")
    sub = p.add_subparsers(dest="command", required=True)
    spec = {
        ("init", cmd_init, "create the work-item root"): [],
        ("next", cmd_next, "what to work on"): [
            ("--json",), ("--plain",), ("--limit", dict(type=int, default=7)),
            ("--stale", dict(default="24h")), ("--pipeline",), ("--one",),
            ("--claim", dict(metavar="WORKER")), ("--non-interactive",)],
        ("show", cmd_show, "show one item"): [
            ("id", {}), ("--brief",), ("--json",)],
        ("add", cmd_add, "create an item"): [
            ("title", {}), ("-t", "--type", dict(default="task", choices=sorted(TYPES))),
            ("-p", "--priority", dict(type=int, default=2, choices=range(5))),
            ("--tag", dict(action="append")), ("--dep", dict(action="append")),
            ("--parent", {}), ("--ref", dict(action="append")), ("--slug", {}),
            ("--desc", {}), ("--force",), ("--json",)],
        ("claim", cmd_claim, "claim an item"): [
            ("id", {}), ("--as", dict(dest="as_owner")), ("--steal",)],
        ("release", cmd_release, "release a claim"): [("id", {})],
        ("handoff", cmd_handoff, "rewrite the Handoff block"): [
            ("id", {}), ("--doing", {}), ("--next", {}), ("--blocked", {}),
            ("--learned", {})],
        ("done", cmd_done, "close an item"): [
            ("id", {}), ("--drop",), ("--note", {})],
        ("block", cmd_block, "block on a reason or another item"): [
            ("id", {}), ("reason", dict(nargs="?")), ("--on", {})],
        ("unblock", cmd_unblock, "clear a block"): [("id", {}), ("--dep", {})],
        ("park", cmd_park, "defer an item deliberately, with a reason"): [
            ("id", {}), ("reason", {})],
        ("unpark", cmd_unpark, "return a parked item to todo (or blocked)"): [
            ("id", {})],
        ("migrate-parked", cmd_migrate_parked,
         "convert blocked items whose reason starts PARKED to parked"): [
            ("--apply",)],
        ("repair-escapes", cmd_repair_escapes,
         "peel the backslash layers an older wi added to quoted values"): [
            ("--id", {}), ("--apply",)],
        ("ls", cmd_ls, "list items"): [
            ("--status", {}), ("--type", {}), ("--tag", {}), ("--owner", {}),
            ("--ready",), ("--json",), ("--plain",)],
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
        ("archive", cmd_archive, "move closed items to archive/"): [
            ("--older-than", dict(default="90d"))],
    }
    for (name, func, help_text), flags in spec.items():
        sp = sub.add_parser(name, help=help_text)
        sp.set_defaults(func=func)
        for flag in flags:
            kw = flag[-1] if isinstance(flag[-1], dict) else {"action": "store_true"}
            names = [f for f in flag if isinstance(f, str)]
            sp.add_argument(*names, **kw)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
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
