#!/usr/bin/env python3
"""check-sheet — the research verifier's score sheet, checked against itself.

The orchestrator runs it on `verification.md` once the verifier has written it. The
verifier has no shell, so this is the part of its procedure it cannot type by hand:

- the counts are tallied from the Sampled claims table, never read from the header; a
  header that disagrees with its own table is a defect;
- a row whose Opened cell says the source was not opened (`—`, `-`, `no`, empty) may only
  carry `UNREACHABLE` or `NOT_FOUND`;
- any other Opened cell is `WebFetch <url>` or `Read <path>`, either with ` p. N`, and its
  target is a URL or path named in the row's Source cell (a row already UNREACHABLE is not
  held to this);
- a row whose Source is one of the run's own files (anything under the sheet's own
  directory, or under an `--own` directory such as the investigation series) may only
  carry `UNREACHABLE` or `NOT_FOUND`: a run's findings, brief, synthesis or sheet is not
  a source for that run's claims;
- the sheet's sections are all present, its claims table is not empty, and every row has
  the header's cell count.

Usage:
    check-sheet.py SHEET [--own DIR]...

Output, one line per defect, then the tally and a summary:
    <path>:<line>: <rule>
    TALLY: sampled <n>, supported <n>, partial <n>, contradicted <n>, not_found <n>, unreachable <n>, demoted <n>
    CHECK: <n> defects
The TALLY is the count to record. A row with a `bad-opened`, `opened-elsewhere` or
`unopened-verdict` defect is tallied as unreachable, a row with an `own-run-source` defect
as not_found, and `demoted` counts the rows whose tally differs from their verdict.

Run it from the project root: a relative path in a Source cell is resolved from the
sheet's directory, its findings/ directory, every --own directory and the working
directory.

Exit: 0 clean, 1 any defect, 2 usage (sheet missing or unreadable, no Sampled claims
section, table or Verdict column).
A caller treats any exit other than 0 or 1, or output with no TALLY line, as an unchecked
sheet.

Stdout never carries the sheet's text: positions, rule names, field names and counts
only, as scan-findings.py does, since the sheet quotes fetched sources.

Stdlib only.
"""
import argparse
import os
import re
import sys

VERDICTS = ("SUPPORTED", "PARTIAL", "CONTRADICTED", "NOT_FOUND", "UNREACHABLE")
FIELDS = ("sampled", "supported", "partial", "contradicted", "not_found", "unreachable")
SECTIONS = ("Security check", "Sampled claims", "Axis scores", "Gate", "Suggested follow-ups")
NOT_OPENED = {"", "-", "—", "–", "no", "none", "not opened", "n/a"}
ALLOWED_UNOPENED = {"UNREACHABLE", "NOT_FOUND"}
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]*)\)")
FILE_EXT = re.compile(r"\.(?:md|txt|json|jsonl|ya?ml|csv|tsv|py|sh|js|ts|html?|pdf|log)$", re.I)
PAGE = re.compile(r"\s+pp?\.\s*\d+(?:\s*-\s*\d+)?$")
TRAIL = re.compile(r"(?:#L?\d+(?:-L?\d+)?|:\d+(?:[-:]\d+)*|[.,;:)\]>]+)$")


def cells(line):
    """A markdown table row's cells, split on unescaped pipes."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def frontmatter(lines):
    """{field: (int value or None, line number)} for the count fields in the header."""
    out = {}
    if not lines or lines[0].strip() != "---":
        return out
    for n, line in enumerate(lines[1:], 2):
        if line.strip() == "---":
            break
        m = re.match(r"\s*([a-z_]+)\s*:\s*(.*?)\s*$", line)
        if m and m.group(1) in FIELDS:
            v = m.group(2)
            out[m.group(1)] = (int(v) if re.fullmatch(r"[0-9]+", v) else None, n)
    return out


def sections(lines):
    """{heading: line number} for every `## ` heading."""
    return {l[3:].strip(): n for n, l in enumerate(lines, 1) if l.startswith("## ")}


def claims_rows(lines, start):
    """(header cells, [(line number, cells)]) of the first table after line `start`."""
    header, rows, n = None, [], start
    while n < len(lines):
        line = lines[n]
        n += 1
        if line.startswith("## "):
            break
        if not line.lstrip().startswith("|"):
            if header is not None and rows:
                break
            continue
        c = cells(line)
        if header is None:
            header = [h.lower() for h in c]
        elif all(re.fullmatch(r":?-{2,}:?", x) for x in c if x):
            continue
        else:
            rows.append((n, c))
    return header, rows


class SheetError(Exception):
    """An unusable sheet; its message is fixed text, never the sheet's."""


def clean(tok):
    """A token with wrapping quotes and brackets, a trailing #anchor, :line or punctuation
    removed; a URL's http scheme read as https and its trailing slash dropped."""
    tok = tok.strip("<>\"'(")
    prev = None
    while prev != tok:
        prev, tok = tok, TRAIL.sub("", tok)
        tok = tok.split("#", 1)[0] if "://" in tok or "/" in tok else tok
        if "://" in tok:
            tok = re.sub(r"^https?://", "https://", tok, flags=re.I).rstrip("/")
    return tok


def targets(cell):
    """Every URL and path-like token in a cell, cleaned, for matching an Opened target."""
    text = cell.replace("`", " ")
    found = [m.group(1) for m in LINK.finditer(text)]
    found += LINK.sub(" ", text).split()
    out = {clean(t) for t in found}
    return {t for t in out if "://" in t or "/" in t or FILE_EXT.search(t)}


def opened_target(cell):
    """("none" | "bad" | "ok", target) for an Opened cell."""
    o = cell.strip("*` ")
    if o.lower() in NOT_OPENED:
        return "none", None
    for tool in ("WebFetch ", "Read "):
        if o.startswith(tool):
            rest = o[len(tool):].strip()
            lm = LINK.fullmatch(rest)
            t = clean(PAGE.sub("", lm.group(1) if lm else rest).strip("`"))
            if tool == "WebFetch " and "://" not in t:
                return "bad", None  # a WebFetch target is a URL
            if tool == "Read " and "/" not in t and not FILE_EXT.search(t):
                return "bad", None  # a Read target is a path
            return "ok", t
    return "bad", None


def path_tokens(cell):
    """Local paths named in a Source cell; URLs are never paths."""
    text = cell.replace("`", " ")
    found = [m.group(1) for m in LINK.finditer(text)]
    text = LINK.sub(" ", text)
    found += text.split()
    out = []
    for tok in found:
        tok = tok.strip("<>\"'(")
        if tok.lower().startswith("file://"):
            tok = tok[len("file://"):]
            if tok.startswith("localhost/"):
                tok = tok[len("localhost"):]
        if not tok or "://" in tok or tok.startswith(("mailto:", "data:")):
            continue
        prev = None
        while prev != tok:
            prev, tok = tok, TRAIL.sub("", tok)
        if "/" in tok or FILE_EXT.search(tok):
            out.append(tok)
    return out


def opened_matches(target, cell, base, owns):
    """Whether an Opened target is a URL or path the Source cell names. A path also matches
    one the Source names relative to the project root, the sheet's directory, its findings/
    or an own directory, so an absolute Opened path fits a repo-relative Source."""
    if target in targets(cell):
        return True
    if "://" in target:
        return False
    t = os.path.realpath(os.path.expanduser(target))
    roots = [os.getcwd(), base, os.path.join(base, "findings")] + owns
    return any(t == os.path.realpath(os.path.join(root, os.path.expanduser(s)))
               for s in path_tokens(cell) for root in roots)


def under(p, owns):
    return any(p == own or p.startswith(own.rstrip(os.sep) + os.sep) for own in owns)


def own_source(cell, base, owns):
    """Whether a Source cell names a file of this run. An absolute path (a file:// URL
    included) counts by where it points. A relative one that exists from the working
    directory (the project root) counts by that path alone; otherwise it counts when it
    exists from the sheet's directory, its findings/ or an own directory. Prose such as
    "TCP/IP" exists nowhere, so it is never taken for a run file."""
    for tok in path_tokens(cell):
        p = os.path.expanduser(tok)
        if os.path.isabs(p):
            if under(os.path.realpath(p), owns):
                return True
            continue
        q = os.path.realpath(os.path.join(os.getcwd(), p))
        if os.path.exists(q):
            if under(q, owns):
                return True
            continue
        for root in [base, os.path.join(base, "findings")] + owns:
            q = os.path.realpath(os.path.join(root, p))
            if os.path.exists(q) and under(q, owns):
                return True
    return False


def check(path, own_dirs):
    """(defects as (line, rule), tally dict); raises SheetError on an unusable sheet."""
    with open(path, encoding="utf-8-sig") as fh:
        lines = fh.read().split("\n")
    base = os.path.dirname(os.path.realpath(path))
    owns = [base] + [os.path.realpath(d) for d in own_dirs]
    heads = sections(lines)
    defects = [(0, f"missing-section {s.lower().replace(' ', '-')}")
               for s in SECTIONS if s not in heads]
    if "Sampled claims" not in heads:
        raise SheetError("no Sampled claims section")
    header, rows = claims_rows(lines, heads["Sampled claims"])
    if header is None:
        raise SheetError("no claims table")
    col = {name: header.index(name) if name in header else None
           for name in ("verdict", "source", "opened")}
    vi = col["verdict"]
    if vi is None:
        raise SheetError("no Verdict column")
    if not rows:
        defects.append((heads["Sampled claims"], "no-claims"))
    for name in ("source", "opened"):
        if col[name] is None:
            defects.append((heads["Sampled claims"], f"missing-column {name}"))
    tally: dict[str, int] = dict.fromkeys(FIELDS + ("demoted",), 0)
    for n, c in rows:
        def get(k, c=c):
            i = col[k]
            return c[i] if i is not None and i < len(c) else ""

        if len(c) != len(header):
            defects.append((n, "row-shape"))
        verdict = get("verdict").strip("*` ").upper()
        if verdict not in VERDICTS:
            defects.append((n, "bad-verdict"))
            tally["sampled"] += 1
            continue
        counted = verdict
        state, target = opened_target(get("opened")) if col["opened"] is not None \
            else ("ok", None)
        if verdict == "UNREACHABLE":
            pass  # already the lowest tally; what was tried is the Note's to say
        elif state == "bad":
            defects.append((n, "bad-opened"))
            counted = "UNREACHABLE"
        elif state == "ok" and target is not None and col["source"] is not None \
                and not opened_matches(target, get("source"), base, owns):
            defects.append((n, "opened-elsewhere"))
            counted = "UNREACHABLE"
        elif state == "ok" and target is not None and "://" not in target \
                and verdict not in ALLOWED_UNOPENED \
                and under(os.path.realpath(os.path.expanduser(target)), owns):
            defects.append((n, "own-run-source"))
            counted = "NOT_FOUND"
        elif state == "none" and verdict not in ALLOWED_UNOPENED:
            defects.append((n, "unopened-verdict"))
            counted = "UNREACHABLE"
        elif col["source"] is not None and verdict not in ALLOWED_UNOPENED \
                and own_source(get("source"), base, owns):
            defects.append((n, "own-run-source"))
            counted = "NOT_FOUND"
        if counted != verdict:
            tally["demoted"] += 1
        tally["sampled"] += 1
        tally[counted.lower()] += 1
    raw: dict[str, int] = dict.fromkeys(FIELDS, 0)
    for n, c in rows:
        v = (c[vi] if vi < len(c) else "").strip("*` ").upper()
        raw["sampled"] += 1
        if v in VERDICTS:
            raw[v.lower()] += 1
    fm = frontmatter(lines)
    for field in FIELDS:
        if field not in fm:
            defects.append((1, f"header-missing {field}"))
        elif fm[field][0] != raw[field]:
            defects.append((fm[field][1], f"header-mismatch {field}"))
    return sorted(defects), tally


def main(argv=None):
    ap = argparse.ArgumentParser(prog="check-sheet.py",
                                 description="Check a research verifier's score sheet.")
    ap.add_argument("sheet")
    ap.add_argument("--own", action="append", default=[], metavar="DIR",
                    help="a directory of this run's own files (repeatable); the sheet's "
                         "own directory is always one")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    shown = os.path.basename(args.sheet)
    try:
        defects, tally = check(args.sheet, args.own)
    except Exception as e:  # any failure is an unchecked sheet; never echo its text
        kind = str(e) if isinstance(e, SheetError) else type(e).__name__
        print(f"check-sheet: unusable sheet {shown}: {kind}", file=sys.stderr)
        return 2
    for line, rule in defects:
        print(f"{shown}:{line}: {rule}")
    print("TALLY: " + ", ".join(f"{k} {tally[k]}" for k in FIELDS + ("demoted",)))
    print(f"CHECK: {len(defects)} defects")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
