#!/usr/bin/env python3
"""claim_check: the read-only claim check for CLAIM.md files.

Checks one repo's CLAIM.md (and the claims of the siblings it names), or with --estate
every sibling checkout beside it, against the format in this skill's
references/format.md, and prints flags. The flags, the command line and the output
contract are in its references/checks.md.

It never writes, never opens the network, and never follows a symlink out of a repo or
the sibling dir. It runs git with fixed arguments, drops git's stderr, reads git's stdout
only for the two paths `rev-parse` prints (the top level and the common git dir), and
judges `ls-files` by its exit code alone. It never prints text read from a file: a flag
carries a fixed word, a location found on disk, and a section name from a fixed list.

Exit codes: 0 no flag, 1 flags, 2 a usage error or a refusal, 3 an internal error.

Python 3 standard library only.

    claim_check.py [--repo DIR] [--claim PATH] [--estate] [--dir DIR]
                   [--today YYYY-MM-DD] [--json]
"""
import argparse
import datetime as dt
import functools
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

VERSION = 1
STALE_DAYS = 180       # Reviewed: older than this gives STALE
PENDING_DAYS = 30      # Status: proposed older than this gives PENDING
MAX_BYTES = 256 * 1024
GIT_TIMEOUT_S = 30

CLAIM = "CLAIM.md"
CLAUDE = "CLAUDE.md"
STORES = (".work/items", ".claude-sandbox/work/items")
FORMAT_MD = Path(__file__).resolve().parent.parent / "references" / "format.md"

EM = " — "  # an em dash with a space on each side
DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
STATUS_APPROVED_RE = re.compile(
    r"^Status: approved by the operator (\S+?)(?: \(([^\s()#]+)#(\d+)\))?\.?$")
STATUS_PROPOSED_RE = re.compile(r"^Status: proposed (\S+?), pending the operator\.?$")
REVIEWED_RE = re.compile(r"^Reviewed: (\S+?)\.?$")
ITEM_RE = re.compile(r"^- (.+?) — (Defined\b.*)$")
HERE_RE = re.compile(r"^Defined here\.?$")
NOCLAIM_RE = re.compile(r"^Defined in (\S+) \(no claim yet\)\.?$")
POINTER_RE = re.compile(r"^Defined in (\S+) (\S+) § (.+?)\.?$")
TRANSIT_RE = re.compile(r"(?<![\w./-])([A-Za-z0-9][A-Za-z0-9._-]*):([^\s|]+)")

INTERNAL = "claim_check: internal error; details are not printed"


class Refusal(Exception):
    """A usage error or a refusal: exit 2 with a fixed message (never file text)."""


def N(x):
    """The one normalization: strip, collapse whitespace, drop backticks, case-fold."""
    return re.sub(r"\s+", " ", x.replace("`", "")).strip().casefold()


def printable(s):
    """A path made encodable: a byte that is not UTF-8 shows as \\xe9."""
    return s.encode("utf-8", "surrogateescape").decode("utf-8", "backslashreplace")


def parse_date(text):
    """A YYYY-MM-DD string as a date, else None. By regex, never strptime (whose error
    text repeats its input)."""
    m = DATE_RE.match(text)
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def git(cwd, *args):
    """Run git with fixed arguments; (returncode, stdout). stderr is captured and dropped."""
    try:
        r = subprocess.run(["git", "-C", str(cwd), *args], stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None, ""
    return r.returncode, r.stdout.decode("utf-8", "surrogateescape").strip()


def within(path, base):
    """True when `path` resolves (symlinks followed) inside the resolved dir `base`."""
    try:
        real = Path(os.path.realpath(path))
    except (OSError, ValueError):
        return False
    return real == base or base in real.parents


def read_text(path, base):
    """(text, problem): the file's text, or a PROBLEM kind. (None, None) when absent."""
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return None, None
    except OSError:
        return None, "unreadable"
    if stat.S_ISLNK(st.st_mode):
        if not within(path, base):
            return None, "symlink-out"
        try:
            st = os.stat(path)
        except OSError:
            return None, "unreadable"
    if not stat.S_ISREG(st.st_mode):
        return None, "not-regular"
    if st.st_size > MAX_BYTES:
        return None, "too-large"
    try:
        with open(path, "rb") as f:
            data = f.read(MAX_BYTES + 1)
    except OSError:
        return None, "unreadable"
    if len(data) > MAX_BYTES:
        return None, "too-large"
    try:
        return data.decode("utf-8"), None
    except UnicodeDecodeError:
        return None, "not-utf8"


def lines_outside_fences(text):
    """(line_no, line) for each line outside a code fence; fence lines are not returned."""
    fence = None
    for n, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if m:
            run, rest = m.groups()
            if fence is None:
                fence = (run[0], len(run))
            elif run[0] == fence[0] and len(run) >= fence[1] and not rest.strip():
                fence = None
            continue
        if fence is None:
            yield n, line


def heading(line):
    """(level, text) of an ATX heading, else None."""
    m = HEADING_RE.match(line)
    if not m:
        return None
    text = (m.group(2) or "")
    text = re.sub(r"[ \t]+#+$", "", text).strip()
    if text.startswith("#"):
        return None
    return len(m.group(1)), text


def headings_of(text):
    """[(level, N(text))] of a file's headings, outside fences."""
    out = []
    for _, line in lines_outside_fences(text):
        h = heading(line)
        if h:
            out.append((h[0], N(h[1])))
    return out


def has_heading(text, target):
    """Whether `target` (a heading's text, or `parent / child`) is a heading of `text`,
    compared under N."""
    hs = headings_of(text)
    if any(t == N(target) for _, t in hs):
        return True
    parts = [p for p in target.split(" / ")]
    if len(parts) < 2:
        return False
    return _nested(hs, [N(p) for p in parts], 0, 0)


def _nested(hs, parts, start, min_level):
    for i in range(start, len(hs)):
        level, t = hs[i]
        if level <= min_level:
            return False
        if t == parts[0]:
            if len(parts) == 1:
                return True
            if _nested(hs, parts[1:], i + 1, level):
                return True
    return False


def table_rows(lines):
    """[(line_no, [cells])] of a Markdown table's rows, the separator row dropped."""
    rows = []
    for n, line in lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{1,}:?", c) for c in cells if c) and any(cells):
            continue
        rows.append((n, cells))
    return rows


def owner_form(owner):
    o = N(owner)
    if o == "operator":
        return "operator"
    if o.startswith("external:"):
        return "external"
    return "repo"


def is_none_known(line):
    s = line.strip()
    if s.startswith("- "):
        s = s[2:]
    return N(s).rstrip(".") == "none known"


@functools.lru_cache(maxsize=1)
def standard_text():
    """format.md § 7's standard text under N, or None when it cannot be read."""
    text, _ = read_text(str(FORMAT_MD), Path(os.path.realpath(FORMAT_MD.parent)))
    if not text:
        return None
    lines = text.splitlines()
    try:
        i = next(k for k, l in enumerate(lines) if N(l) == "### the standard text")
    except StopIteration:
        return None
    quote, started = [], False
    for l in lines[i + 1:]:
        if l.startswith(">"):
            started = True
            quote.append(l[1:].strip())
        elif started:
            break
    return N(" ".join(quote)) if quote else None


# A test hook: tests set it to raise inside the parser, to prove the guard prints nothing
# of the exception.
_parse_hook = None


class Claim:
    """The parsed structure of one CLAIM.md. Holds normalized names and line numbers only."""

    def __init__(self, text, repo_name):
        if _parse_hook:
            _parse_hook(text)
        self.shape = []          # (kind, line)
        self.status = None       # ("approved"|"proposed", date)
        self.reviewed = None
        self.areas = []          # (N(area), line)
        self.not_ours = []       # (N(name), N(owner), form, line)
        self.boundaries = {}     # N(neighbour) -> {"line", "items": [...], "rule"}
        self.boundaries_line = 0
        self.transit = []        # (repo, path, line)
        self.changing = None     # N(joined text)
        self._parse(text, repo_name)

    def _parse(self, text, repo_name):
        body = list(lines_outside_fences(text))
        sections, current, head = {}, None, []
        title = None
        for n, line in body:
            h = heading(line)
            if h and title is None:
                title = (n, h)
            if h and h[0] == 2:
                current = N(h[1])
                sections.setdefault(current, {"line": n, "lines": []})
                continue
            if current is None:
                head.append((n, line))
            else:
                sections[current]["lines"].append((n, line))
        self._title(title, repo_name)
        self._head(head)
        self._claim(sections.get("claim"))
        self._not_ours(sections.get("not ours"))
        self._boundaries(sections.get("boundaries"))
        self._transit(sections.get("in transit"))
        self._changing(sections.get("changing this claim"))

    def _title(self, title, repo_name):
        if title is None or title[1][0] != 1:
            self.shape.append(("title", title[0] if title else 0))
            return
        n, (_, text) = title
        m = re.match(r"^CLAIM:\s*(.+)$", text)
        if not m or N(m.group(1)) != N(repo_name):
            self.shape.append(("title", n))

    def _head(self, head):
        status = reviewed = None
        for n, line in head:
            s = line.strip()
            if s.startswith("Status:") and status is None:
                status = (n, s)
            elif s.startswith("Reviewed:") and reviewed is None:
                reviewed = (n, s)
        if status is None:
            self.shape.append(("status", 0))
        else:
            n, s = status
            m = STATUS_APPROVED_RE.match(s)
            kind = "approved"
            if not m:
                m = STATUS_PROPOSED_RE.match(s)
                kind = "proposed"
            d = parse_date(m.group(1)) if m else None
            if d is None:
                self.shape.append(("status", n))
            else:
                self.status = (kind, d, n)
        if reviewed is None:
            self.shape.append(("reviewed", 0))
        else:
            n, s = reviewed
            m = REVIEWED_RE.match(s)
            d = parse_date(m.group(1)) if m else None
            if d is None:
                self.shape.append(("reviewed", n))
            else:
                self.reviewed = (d, n)

    def _claim(self, sec):
        if sec is None:
            self.shape.append(("claim", 0))
            return
        rows = table_rows(sec["lines"])
        header = None
        for n, cells in rows:
            if header is None:
                if cells and N(cells[0]) == "area":
                    header = n
                continue
            if cells and cells[0].strip():
                self.areas.append((N(cells[0]), n))
        if header is None or not self.areas:
            self.shape.append(("claim", sec["line"]))

    def _not_ours(self, sec):
        if sec is None:
            self.shape.append(("not-ours", 0))
            return
        none_line, items = None, 0
        for n, line in sec["lines"]:
            if not line.strip():
                continue
            if is_none_known(line) and not line.startswith((" ", "\t")):
                none_line = n
                continue
            if not line.startswith("- "):
                continue
            items += 1
            name, sep, owner = line[2:].partition(EM)
            if not sep or not N(name) or not N(owner) or N(owner) == "external:":
                self.shape.append(("not-ours", n))
                continue
            self.not_ours.append((N(name), N(owner), owner_form(owner), n))
        if (none_line is None and items == 0) or (none_line is not None and items):
            self.shape.append(("not-ours", none_line or sec["line"]))

    def _boundaries(self, sec):
        if sec is None:
            self.shape.append(("boundaries", 0))
            return
        self.boundaries_line = sec["line"]
        none_line, sub = None, None
        for n, line in sec["lines"]:
            h = heading(line)
            if h and h[0] >= 3:
                if h[0] == 3:
                    key = N(h[1])
                    sub = self.boundaries.setdefault(
                        key, {"line": n, "items": [], "rule": False})
                continue
            if not line.strip():
                continue
            if sub is None:
                if is_none_known(line):
                    none_line = n
                continue
            if line.startswith((" ", "\t")):
                continue  # Ours:/Theirs: and other indented lines are not read
            if line.startswith("Rule:"):
                sub["rule"] = bool(line[5:].strip())
                continue
            if not line.startswith("- "):
                continue  # prose
            m = ITEM_RE.match(line.rstrip())
            item = self._item(m) if m else None
            if item is None:
                self.shape.append(("boundaries", n))
                continue
            item["line"] = n
            sub["items"].append(item)
        if not self.boundaries:
            if none_line is None:
                self.shape.append(("boundaries", sec["line"]))
            return
        if none_line is not None:
            self.shape.append(("boundaries", none_line))
        for s in self.boundaries.values():
            if not s["rule"] or not s["items"]:
                self.shape.append(("boundaries", s["line"]))

    @staticmethod
    def _item(m):
        name, where = N(m.group(1)), m.group(2).strip()
        if not name:
            return None
        if HERE_RE.match(where):
            return {"name": name, "kind": "here"}
        p = NOCLAIM_RE.match(where)
        if p:
            return {"name": name, "kind": "noclaim", "repo": p.group(1)}
        p = POINTER_RE.match(where)
        if p:
            return {"name": name, "kind": "pointer", "repo": p.group(1),
                    "file": p.group(2), "heading": p.group(3)}
        return None

    def _transit(self, sec):
        if sec is None:
            return
        col = None
        for n, cells in table_rows(sec["lines"]):
            if col is None:
                names = [N(c) for c in cells]
                if "thing" in names:
                    col = names.index("thing")
                continue
            if col >= len(cells):
                continue
            m = TRANSIT_RE.search(cells[col].replace("`", ""))
            if m:
                self.transit.append((m.group(1), m.group(2), n))

    def _changing(self, sec):
        if sec is None:
            self.shape.append(("changing", 0))
            return
        text = " ".join(l.strip() for _, l in sec["lines"] if l.strip())
        if not text:
            self.shape.append(("changing", sec["line"]))
            return
        self.changing = (N(text), sec["line"])


def librarian_not_owned(text):
    """[(N(name), N(owner), form, line)] from CLAUDE.md's ## Librarian Not owned: list,
    or None when the section or the line is absent."""
    in_lib, found, out = False, False, []
    listing = False
    for n, line in lines_outside_fences(text):
        h = heading(line)
        if h and h[0] <= 2:
            if in_lib:
                break
            in_lib = h[0] == 2 and N(h[1]) == "librarian"
            continue
        if not in_lib:
            continue
        if listing:
            if line.startswith("- "):
                name, sep, owner = line[2:].partition(EM)
                if sep and N(name):
                    out.append((N(name), N(owner), owner_form(owner), n))
                continue
            listing = False
        if line.strip() == "Not owned:" and not found:
            found, listing = True, True
    return out if found else None


class Repo:
    def __init__(self, name, path, is_self=False, claim_override=None):
        self.name = printable(name)       # directory listing spelling, escaped once
        self.path = Path(path)            # the tree read: a worktree for this repo
        self.base = Path(os.path.realpath(path))
        self.is_self = is_self
        self.claim_override = claim_override
        self.store = any((self.path / s).is_dir() for s in STORES)
        self._claim = None
        self._loaded = False
        self.claim_problem = None
        self.claim_exists = False

    @property
    def claim_file(self):
        """The file name flags give: CLAIM.md, or the --claim path."""
        return str(self.claim_override) if self.claim_override else CLAIM

    @property
    def claim_path(self):
        return Path(self.claim_override) if self.claim_override else self.path / CLAIM

    def claim(self):
        if not self._loaded:
            self._loaded = True
            p = self.claim_path
            base = (Path(os.path.realpath(p.parent)) if self.claim_override else self.base)
            text, prob = read_text(str(p), base)
            self.claim_exists = text is not None or prob is not None
            self.claim_problem = prob
            if text is not None:
                self._claim = Claim(text, self.name)
        return self._claim

    def has_claim(self):
        self.claim()
        return self.claim_exists


class Check:
    def __init__(self, today, sibling_dir, repos, self_repo, estate, notes, skipped):
        self.today = today
        self.dir = sibling_dir
        self.repos = repos                # N(name) -> Repo
        self.me = self_repo
        self.estate = estate
        self.notes = notes
        self.skipped = skipped
        self.flags = []
        self.siblings_known = sibling_dir is not None

    # -- output ------------------------------------------------------------------------

    def flag(self, flag, kind, repo, file, line, section, other=None, form=None):
        self.flags.append({"flag": flag, "kind": kind, "repo": repo.name,
                           "file": printable(file), "line": line, "section": section,
                           "other": other, "owner_form": form})

    def section_for(self, key):
        """A Boundaries subsection's printed name: the sibling's spelling, or a fixed word."""
        r = self.repos.get(key)
        return f"Boundaries / {r.name}" if r else "Boundaries subsection"

    @staticmethod
    def loc(repo, file, line):
        return f"{repo.name}:{printable(file)}:{line}"

    # -- per-claim ---------------------------------------------------------------------

    def checked(self):
        """The repos whose own files are checked: every repo with --estate, else this one."""
        if self.estate:
            return [self.repos[k] for k in sorted(self.repos)]
        return [self.me]

    def run(self):
        for r in self.checked():
            c = r.claim()
            if r.claim_problem:
                self.flag("PROBLEM", r.claim_problem, r, r.claim_file, 0, "file")
            if not r.claim_exists:
                if r.is_self and not self.estate or (self.estate and r.store):
                    self.flag("UNCLAIMED", None, r, CLAIM, 0, "file")
                continue
            if c is None:
                continue
            self.shape(r, c)
            self.age(r, c)
            self.resolve(r, c)
            self.pointers(r, c)
            self.transit(r, c)
            self.mismatch(r, c)
        self.pairs()
        self.flags.sort(key=lambda f: (f["repo"], f["file"], f["line"], f["flag"],
                                       f["kind"] or "", f["other"] or ""))
        return self.flags

    def shape(self, r, c):
        sections = {"title": "title", "status": "Status", "reviewed": "Reviewed",
                    "claim": "Claim", "not-ours": "Not ours", "boundaries": "Boundaries",
                    "changing": "Changing this claim"}
        for kind, line in c.shape:
            self.flag("SHAPE", kind, r, r.claim_file, line, sections[kind])
        if c.changing is not None:
            std = standard_text()
            if std is None:
                note = "standard text not compared: the format reference was not found"
                if note not in self.notes:
                    self.notes.append(note)
            elif c.changing[0] != std:
                self.flag("SHAPE", "changing", r, r.claim_file, c.changing[1],
                          "Changing this claim")

    def age(self, r, c):
        if c.reviewed and (self.today - c.reviewed[0]).days > STALE_DAYS:
            self.flag("STALE", None, r, r.claim_file, c.reviewed[1], "Reviewed")
        if c.status and c.status[0] == "proposed" and \
                (self.today - c.status[1]).days > PENDING_DAYS:
            self.flag("PENDING", None, r, r.claim_file, c.status[2], "Status")

    def resolve(self, r, c):
        if not self.siblings_known:
            return
        for name, owner, form, line in c.not_ours:
            if form == "repo" and owner not in self.repos:
                self.flag("UNRESOLVED", "owner", r, r.claim_file, line, "Not ours")
        for key, sub in c.boundaries.items():
            if key not in self.repos:
                self.flag("UNRESOLVED", "neighbour", r, r.claim_file, sub["line"],
                          "Boundaries subsection")
            for it in sub["items"]:
                if it["kind"] != "here" and N(it["repo"]) not in self.repos:
                    self.flag("UNRESOLVED", "pointer", r, r.claim_file, it["line"],
                              self.section_for(key))

    def target(self, name):
        """The Repo a name in a claim resolves to, or None."""
        return self.repos.get(N(name))

    def pointers(self, r, c):
        for key, sub in c.boundaries.items():
            sec = self.section_for(key)
            for it in sub["items"]:
                t = self.target(it["repo"]) if it["kind"] != "here" else None
                if t is None:
                    continue
                if it["kind"] == "noclaim":
                    if t is not r and t.has_claim():
                        self.flag("AWAITING", None, r, r.claim_file, it["line"], sec)
                    continue
                kind = self.dangling(t, it["file"], it["heading"])
                if kind in ("file", "heading", "outside"):
                    self.flag("DANGLING", kind, r, r.claim_file, it["line"], sec)
                elif kind:
                    self.flag("PROBLEM", kind, r, r.claim_file, it["line"], sec)

    def dangling(self, t, file, head):
        """None when the pointer resolves; else a DANGLING kind, or a PROBLEM kind."""
        rel = Path(file)
        if rel.is_absolute() or ".." in rel.parts or not file:
            return "outside"
        stand_in = t.claim_override is not None and N(file) == N(CLAIM)
        if stand_in:
            path, base = Path(t.claim_override), Path(os.path.realpath(
                Path(t.claim_override).parent))
        else:
            path, base = t.path / rel, t.base
            if os.path.lexists(path) and not within(path, t.base):
                return "outside"
        text, prob = read_text(str(path), base)
        if prob == "symlink-out":
            return "outside"
        if prob:
            return prob
        if text is None:
            return "file"
        if not stand_in:
            code, _ = git(t.path, "--literal-pathspecs", "ls-files", "--error-unmatch",
                          "--", str(rel))
            if code != 0:
                return "file"
        if not has_heading(text, head):
            return "heading"
        return None

    def transit(self, r, c):
        for repo, path, line in c.transit:
            t = self.target(repo)
            if t is None:
                continue
            rel = Path(path)
            if rel.is_absolute() or ".." in rel.parts:
                self.flag("MOVED?", "outside", r, r.claim_file, line, "In transit")
                continue
            p = t.path / rel
            if not os.path.lexists(p):
                self.flag("MOVED?", "missing", r, r.claim_file, line, "In transit")
            elif not within(p, t.base):
                self.flag("MOVED?", "outside", r, r.claim_file, line, "In transit")

    def mismatch(self, r, c):
        text, prob = read_text(str(r.path / CLAUDE), r.base)
        if prob:
            self.flag("PROBLEM", prob, r, CLAUDE, 0, "file")
            return
        if text is None:
            return
        lib = librarian_not_owned(text)
        if lib is None:
            return
        sec = "Librarian Not owned"
        claim_by = {}
        for name, owner, form, line in c.not_ours:
            claim_by.setdefault(name, (owner, form, line))
        lib_by = {}
        for name, owner, form, line in lib:
            lib_by.setdefault(name, (owner, form, line))
        for name, (owner, form, line) in lib_by.items():
            if name not in claim_by:
                self.flag("MISMATCH", "librarian-only", r, CLAUDE, line, sec, form=form)
        for name, (owner, form, line) in claim_by.items():
            if name not in lib_by:
                self.flag("MISMATCH", "claim-only", r, r.claim_file, line, "Not ours",
                          form=form)
            elif lib_by[name][0] != owner:
                self.flag("MISMATCH", "owner", r, r.claim_file, line, "Not ours",
                          other=self.loc(r, CLAUDE, lib_by[name][2]), form=form)

    # -- pairs -------------------------------------------------------------------------

    def loaded(self):
        """Repos with a parsed claim: all with --estate, else this one and those it names."""
        if self.estate:
            keys = sorted(self.repos)
        else:
            keys = [N(self.me.name)]
            c = self.me.claim()
            if c is not None:
                named = set(c.boundaries)
                for sub in c.boundaries.values():
                    named |= {N(i["repo"]) for i in sub["items"] if i["kind"] != "here"}
                named |= {o for _, o, f, _ in c.not_ours if f == "repo"}
                keys += sorted(k for k in named if k in self.repos and k not in keys)
        return [self.repos[k] for k in keys if k in self.repos
                and self.repos[k].claim() is not None]

    def pairs(self):
        repos = self.loaded()
        for i, a in enumerate(repos):
            for b in repos[i + 1:]:
                if not self.estate and not (a.is_self or b.is_self):
                    continue
                x, y = (b, a) if b.is_self else (a, b)
                self.one_sided(x, y)
                self.one_sided(y, x)
                self.defined_twice(x, y)
                self.owner_conflict(x, y)
                self.claimed_not_ours(x, y)
                self.claimed_not_ours(y, x)

    def one_sided(self, a, b):
        ca, cb = a.claim(), b.claim()
        sub = ca.boundaries.get(N(b.name))
        if not sub or N(a.name) in cb.boundaries:
            return
        here = [it for it in sub["items"] if it["kind"] == "here"]
        if here:
            self.flag("ONE-SIDED", None, a, a.claim_file, here[0]["line"],
                      self.section_for(N(b.name)),
                      other=self.loc(b, b.claim_file, cb.boundaries_line))

    def defined_twice(self, a, b):
        ca, cb = a.claim(), b.claim()
        sa, sb = ca.boundaries.get(N(b.name)), cb.boundaries.get(N(a.name))
        if not sa or not sb:
            return
        theirs = {it["name"]: it["line"] for it in sb["items"] if it["kind"] == "here"}
        for it in sa["items"]:
            if it["kind"] == "here" and it["name"] in theirs:
                self.flag("CONFLICT", "defined-twice", a, a.claim_file, it["line"],
                          self.section_for(N(b.name)),
                          other=self.loc(b, b.claim_file, theirs[it["name"]]))

    def owner_conflict(self, a, b):
        theirs = {}
        for name, owner, _, line in b.claim().not_ours:
            theirs.setdefault(name, (owner, line))
        for name, owner, _, line in a.claim().not_ours:
            if name in theirs and theirs[name][0] != owner:
                self.flag("CONFLICT", "owner", a, a.claim_file, line, "Not ours",
                          other=self.loc(b, b.claim_file, theirs[name][1]))

    def claimed_not_ours(self, a, b):
        """An area a claims that b lists under Not ours with an owner other than a."""
        theirs = {}
        for name, owner, _, line in b.claim().not_ours:
            theirs.setdefault(name, (owner, line))
        for area, line in a.claim().areas:
            if area in theirs and theirs[area][0] != N(a.name):
                self.flag("CONFLICT", "claimed-and-not-ours", a, a.claim_file, line, "Claim",
                          other=self.loc(b, b.claim_file, theirs[area][1]))


# -- discovery ---------------------------------------------------------------------------


def toplevel(path):
    code, out = git(path, "rev-parse", "--show-toplevel")
    return Path(out) if code == 0 and out else None


def main_checkout(top):
    """The main checkout of the repo at `top`: through the common git dir, so a linked
    worktree gives its main checkout. Its directory name is the repo's name."""
    code, out = git(top, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if code != 0 or not out:
        return None
    common = Path(out)
    return common.parent if common.name == ".git" else common


def refused(d):
    home = Path(os.path.realpath(Path.home()))
    return d == home or d in home.parents or d == Path(d.anchor)


def siblings(d, skipped):
    """{realpath: name} of the direct children of `d` holding a .git directory."""
    out = {}
    try:
        names = sorted(os.listdir(d))
    except OSError:
        raise Refusal("claim_check: the sibling dir cannot be read")
    for name in names:
        p = d / name
        try:
            if not p.is_dir():
                continue
        except OSError:
            continue
        if not within(p, d):
            skipped.append({"path": printable(str(p)), "reason": "resolves outside the dir"})
            continue
        g = p / ".git"
        if g.is_dir() and not g.is_symlink():
            out[Path(os.path.realpath(p))] = name
        elif g.exists() or g.is_symlink():
            skipped.append({"path": printable(str(p)),
                            "reason": ".git is a file (a linked worktree or a submodule)"})
    return out


def build(args):
    notes, skipped = [], []
    today = dt.date.today()
    if args.today is not None:
        today = parse_date(args.today)
        if today is None:
            raise Refusal("claim_check: --today must be a date, YYYY-MM-DD")
    claim = None
    if args.claim is not None:
        claim = Path(os.path.abspath(args.claim))
        if not os.path.lexists(claim):
            raise Refusal("claim_check: the --claim file does not exist")

    top = toplevel(args.repo or os.getcwd())
    if args.repo is not None and top is None:
        raise Refusal("claim_check: --repo is not a git repo")
    if top is None and not args.estate:
        raise Refusal("claim_check: not in a git repo; name the repo with --repo")
    if top is None and args.dir is None:
        raise Refusal("claim_check: not in a git repo; name the dir with --dir")
    main = main_checkout(top) if top is not None else None
    if top is not None and main is None:
        raise Refusal("claim_check: the repo's main checkout cannot be found")

    if args.dir is not None:
        d = Path(os.path.realpath(args.dir))
        if not d.is_dir():
            raise Refusal("claim_check: --dir is not a directory")
    else:
        d = Path(os.path.realpath(main.parent))
        if refused(d):
            if args.estate:
                raise Refusal("claim_check: the default sibling dir would be $HOME or "
                              "above; name it with --dir")
            notes.append("neighbour checks skipped: the sibling dir would be $HOME or "
                         "above; name it with --dir")
            d = None

    repos, me = {}, None
    if top is not None:
        me = Repo(main.name, top, is_self=True, claim_override=claim)
    found = siblings(d, skipped) if d is not None else {}
    main_real = Path(os.path.realpath(main)) if main is not None else None
    for real, name in found.items():
        if me is not None and real == main_real:
            continue  # this repo is read from --repo's tree, never also from main
        r = Repo(name, real)
        repos[N(r.name)] = r
    if me is not None:
        in_dir = main_real is not None and d is not None and main_real.parent == d
        if args.estate and not in_dir:
            if claim is not None:
                raise Refusal("claim_check: with --estate, --claim needs the repo in the dir")
            me = None
        else:
            repos[N(me.name)] = me
    return Check(today, d, repos, me, args.estate, notes, skipped), today, d


def emit(check, today, d, flags, as_json, out):
    repos = list(check.repos.values()) if check.estate else [check.me]
    n_claims = sum(1 for r in check.repos.values() if r._loaded and r.claim_exists)
    if as_json:
        doc = {
            "version": VERSION,
            "today": today.isoformat(),
            "dir": printable(str(d)) if d is not None else None,
            "repos": [{"repo": r.name, "path": printable(str(r.path)),
                       "claim": (printable(str(r.claim_path.absolute()))
                                 if r.has_claim() else False),
                       "store": r.store}
                      for r in sorted(repos, key=lambda r: N(r.name))],
            "flags": flags,
            "skipped": check.skipped,
            "notes": check.notes + [f"checked {len(repos)} repos, "
                                    f"{n_claims} claims read"],
        }
        out.write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        return
    for f in flags:
        line = (f"{f['flag']} {f['kind'] or '-'} {f['repo']}:{f['file']}:{f['line']} "
                f"{f['section']}")
        if f["other"]:
            line += f" other: {f['other']}"
        if f["owner_form"]:
            line += f" owner_form: {f['owner_form']}"
        out.write(line + "\n")
    for s in check.skipped:
        out.write(f"skipped: {s['path']} ({s['reason']})\n")
    for n in check.notes:
        out.write(f"notes: {n}\n")
    out.write(f"notes: checked {len(repos)} repos, {n_claims} claims read, "
              f"{len(flags)} flags\n")


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Refusal("claim_check: usage error; see --help")


def parse_args(argv):
    p = Parser(prog="claim_check.py", description="The read-only claim check.")
    p.add_argument("--repo", help="the repo to check (default: the working directory's)")
    p.add_argument("--claim", help="check this file as the repo's CLAIM.md (a draft)")
    p.add_argument("--estate", action="store_true", help="check every sibling checkout")
    p.add_argument("--dir", help="the sibling dir (default: the main checkout's parent)")
    p.add_argument("--today", help="fix the date, YYYY-MM-DD (tests)")
    p.add_argument("--json", action="store_true", help="JSON output")
    return p.parse_args(argv)


def main(argv=None, out=None, err=None):
    out = out or sys.stdout
    err = err or sys.stderr
    try:
        args = parse_args(argv)
        check, today, d = build(args)
        flags = check.run()
        emit(check, today, d, flags, args.json, out)
        return 1 if flags else 0
    except Refusal as e:
        err.write(str(e) + "\n")
        return 2
    except SystemExit as e:  # --help
        return e.code if isinstance(e.code, int) else 0
    except Exception:  # never the exception text: it may carry a file's content
        err.write(INTERNAL + "\n")
        return 3


if __name__ == "__main__":
    sys.exit(main())
