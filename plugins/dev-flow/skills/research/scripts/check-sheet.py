#!/usr/bin/env python3
"""check-sheet — the research verifier's score sheet, checked against itself.

The orchestrator runs it on `verification.md` once the verifier has written it. The
verifier has no shell, so this is the part of its procedure it cannot type by hand:

- the counts are tallied from the Sampled claims table, never read from the header; a
  header that disagrees with its own table is a defect;
- a row whose Opened cell says the source was not opened (`—`, `-`, `no`, empty) may only
  carry `UNREACHABLE` or `NOT_FOUND`;
- a row whose Source is one of the run's own files (anything under the sheet's own
  directory, or under an `--own` directory such as the investigation series) may only
  carry `UNREACHABLE` or `NOT_FOUND`: a run's findings, brief, synthesis or sheet is not
  a source for that run's claims;
- the sheet's sections are all present.

Usage:
    check-sheet.py SHEET [--own DIR]...

Output, one line per defect, then the tally and a summary:
    <path>:<line>: <rule>
    TALLY: sampled <n>, supported <n>, partial <n>, contradicted <n>, not_found <n>, unreachable <n>, demoted <n>
    CHECK: <n> defects
The TALLY is the count to record. A row with an `unopened-verdict` defect is tallied as
unreachable, a row with an `own-run-source` defect as not_found, and `demoted` counts
those rows.

Exit: 0 clean, 1 any defect, 2 usage (sheet missing or unreadable, or no claims table).
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
            out[m.group(1)] = (int(v) if v.isdigit() else None, n)
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


def path_tokens(cell):
    """Local paths named in a Source cell; URLs are never paths."""
    text = cell.replace("`", " ")
    found = [m.group(1) for m in LINK.finditer(text)]
    text = LINK.sub(" ", text)
    found += text.split()
    out = []
    for tok in found:
        tok = tok.strip("<>\"'(")
        if not tok or "://" in tok or tok.startswith(("mailto:", "data:")):
            continue
        prev = None
        while prev != tok:
            prev, tok = tok, TRAIL.sub("", tok)
        if "/" in tok or FILE_EXT.search(tok):
            out.append(tok)
    return out


def under(p, owns):
    return any(p == own or p.startswith(own.rstrip(os.sep) + os.sep) for own in owns)


def own_source(cell, base, owns):
    """Whether a Source cell names a file of this run. An absolute path counts by where it
    points; a relative one only when it exists, resolved from the sheet's directory or the
    working directory, so prose such as "TCP/IP" is never taken for a run file."""
    for tok in path_tokens(cell):
        p = os.path.expanduser(tok)
        if os.path.isabs(p):
            if under(os.path.realpath(p), owns):
                return True
            continue
        for root in (base, os.getcwd()):
            q = os.path.realpath(os.path.join(root, p))
            if os.path.exists(q) and under(q, owns):
                return True
    return False


def check(path, own_dirs):
    """(defects as (line, rule), tally dict); raises ValueError on an unusable sheet."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    base = os.path.dirname(os.path.realpath(path))
    owns = [base] + [os.path.realpath(d) for d in own_dirs]
    heads = sections(lines)
    defects = [(0, f"missing-section {s.lower().replace(' ', '-')}")
               for s in SECTIONS if s not in heads]
    if "Sampled claims" not in heads:
        raise ValueError("no Sampled claims section")
    header, rows = claims_rows(lines, heads["Sampled claims"])
    if header is None:
        raise ValueError("no claims table")
    col = {name: header.index(name) if name in header else None
           for name in ("verdict", "source", "opened")}
    if col["verdict"] is None:
        raise ValueError("no Verdict column")
    for name in ("source", "opened"):
        if col[name] is None:
            defects.append((heads["Sampled claims"], f"missing-column {name}"))
    tally = dict.fromkeys(FIELDS, 0)
    tally["demoted"] = 0
    for n, c in rows:
        get = lambda k: c[col[k]] if col[k] is not None and col[k] < len(c) else ""
        verdict = get("verdict").strip("*` ").upper()
        if verdict not in VERDICTS:
            defects.append((n, "bad-verdict"))
            tally["sampled"] += 1
            continue
        counted = verdict
        if col["opened"] is not None and get("opened").strip("*` ").lower() in NOT_OPENED \
                and verdict not in ALLOWED_UNOPENED:
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
    raw = dict.fromkeys(FIELDS, 0)
    for n, c in rows:
        v = (c[col["verdict"]] if col["verdict"] < len(c) else "").strip("*` ").upper()
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
    except (OSError, UnicodeDecodeError, ValueError) as e:
        kind = type(e).__name__ if not isinstance(e, ValueError) else str(e)
        print(f"check-sheet: unusable sheet {shown}: {kind}", file=sys.stderr)
        return 2
    for line, rule in defects:
        print(f"{shown}:{line}: {rule}")
    print("TALLY: " + ", ".join(f"{k} {tally[k]}" for k in FIELDS + ("demoted",)))
    print(f"CHECK: {len(defects)} defects")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
