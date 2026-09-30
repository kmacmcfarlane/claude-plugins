#!/usr/bin/env python3
"""scan-findings \u2014 the research family's deterministic scan floor.

A line scanner for fetched-derived research files. The orchestrator runs it over staged
findings before the research-verifier and again before landing, and over a toolkit
lane's `tools/` before any mining lane runs those scripts. The verifier is one cheap
model reading attacker text; this floor is the part of the gate it cannot be talked
out of.

Usage:
    scan-findings.py PATH...              findings mode: files as given; directories
                                          recurse to their *.md files
    scan-findings.py --scripts PATH...    toolkit mode: every file under PATH; the prose
                                          tiers plus the script rules
    scan-findings.py --strip FILE --lines N[,N...]
                                          delete those lines by position, then rescan

Output, one line per hit, then a summary:
    <path>:<line>: <rule> <HOLD|FLAG>
    SCAN: <n> hold, <n> flag, <n> files
`--strip` prints `STRIPPED: <n> lines, <path>` first. Line 0 means the whole file.

Exit: 0 clean, 1 any HOLD, 3 FLAG only, 2 usage (nothing scanned or changed). A caller
treats any exit other than 0 or 3, or output with no SCAN line, as a hold.

Stdout never carries a file's text: positions, rule names and counts only. That is what
lets the orchestrator read the result, and what lets `--strip` remove lines a verifier
named without anything reading them.

Tiers:
- HOLD (structural; holds the run): invisible, bidi, Unicode-tag and control characters
  (on raw text, anywhere); control-tag, special-token and chat-role shapes, override
  phrasing and pipe-to-shell outside code.
- FLAG (semantic; the verifier adjudicates each line): agent-addressed phrasing,
  second-person obligations, authority claims, execution requests, long base64; any
  HOLD shape inside a markdown code span or a closed fence; a control-tag or
  special-token shape inside a quoted string in a script (override, chat-role and
  pipe-to-shell shapes hold everywhere in a script); in toolkit mode, on every file,
  network use, subprocesses, file writes, secret paths and env reads.
- At line 0, the whole file: HOLD for a symlink (never followed), an entry that is not a
  regular file (never opened), an unreadable or undecodable file, or a directory that
  cannot be listed; FLAG for an unsafe file name.
- A HOLD phrase split by a code span or a quote boundary still holds: the rules also run
  on the joined line. Runtime construction in a script (chr, base64, joins across lines)
  gets past any static floor; for toolkit code the verifier's script review is the gate.
Prose rules match text with invisible characters and combining marks removed, common
Cyrillic and Greek look-alikes mapped to Latin, and NFKC applied, so full-width,
zero-width and look-alike evasions still match. Every pass is linear in the input.
A clean scan is not a clean file.

Stdlib only.
"""
import argparse
import os
import re
import stat
import sys
import tempfile
import unicodedata

HOLD, FLAG = "HOLD", "FLAG"
RAW, PROSE, SCRIPT = "raw", "prose", "script"


class Rule:
    __slots__ = ("name", "tier", "kind", "rx", "check", "line_start")

    def __init__(self, name, tier, kind, pattern, check=None):
        self.name, self.tier, self.kind, self.check = name, tier, kind, check
        self.rx = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.line_start = pattern.startswith("^")  # only matched where the line starts

    def hit(self, text):
        for m in self.rx.finditer(text):
            if self.check is None or self.check(m.group(0)):
                return True
        return False


def _mixed(s):
    return (any(c.isdigit() for c in s) and any(c.islower() for c in s)
            and any(c.isupper() for c in s))


# Control-tag names: harness, chat-template and tool-call markup. Common placeholders
# (<path>, <user>, <host>) and ordinary HTML are deliberately absent.
_TAGS = (r"(?:system(?:[-_](?:reminder|prompt|message))?|instructions?|assistant|human|"
         r"developer|tool_(?:use|result|call)s?|function_(?:calls|results)|invoke|"
         r"command-(?:name|message|args)|local-command-std(?:out|err)|"
         r"user-prompt-submit-hook|thinking|antml:[a-z_]+)")
_ATTRS = r"(?:\s+[\w:-]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))*"
_ADDRESSEE = r"(?:ai|llm|language model|assistant|agent|bot|chatbot|claude|chatgpt|gpt|model)"

# One row per rule, each on one line: the tests' negative control deletes a row by name.
RULES = [
    Rule("zero-width", HOLD, RAW, "[\u200b-\u200d\u2060-\u2064\ufeff\u00ad\u180e]"),
    Rule("bidi-control", HOLD, RAW, "[\u200e\u200f\u061c\u202a-\u202e\u2066-\u2069]"),
    Rule("unicode-tag", HOLD, RAW, "[\U000e0000-\U000e007f]"),
    Rule("control-char", HOLD, RAW, "[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]"),
    Rule("control-tag", HOLD, PROSE, r"<\s*/?\s*" + _TAGS + r"(?![\w-])" + _ATTRS + r"\s*/?\s*>"),
    Rule("special-token", HOLD, PROSE, r"<\|[\w-]{2,40}\|>|\[/?inst\]|<</?sys>>|<(?:start|end)_of_turn>"),
    Rule("chat-role-prefix", HOLD, PROSE, r"^\s{0,3}(?:>\s*)*[\"']?(?:\*\*|__)?(?:human|assistant)(?:\*\*|__)?\s*:(?![\"'])"),
    Rule("override-phrase", HOLD, PROSE, r"\b(?:ignore|disregard|forget)\b(?:\W+\w+){0,3}?\W+(?:previous|prior|above|earlier|preceding|foregoing|all|any|every|system|original|initial|your)\b(?:\W+\w+){0,3}?\W+(?:instructions?|directions?|directives?|rules|prompts?|guidelines|guidance|constraints|messages)\b"),
    Rule("pipe-to-shell", HOLD, PROSE, r"\b(?:curl|wget|iwr|irm|invoke-webrequest|invoke-restmethod)\b[^\n]{0,300}?\|\s*(?:sudo\s+(?:-\S+\s+)*)?(?:(?:ba|z|da|k|fi)?sh|pyth[o]n3?|p[e]rl|r[u]by|n[o]de|i[e]x)\b|\b(?:ba|z)?sh\s+(?:-c\s+)?[\"']?(?:<\(|\$\()\s*(?:curl|wget)\b"),
    Rule("agent-addressed", FLAG, PROSE, r"\b(?:if|when)\s+you(?:'re|\s+are)\s+an?\s+" + _ADDRESSEE + r"\b|\b(?:dear|attention|note to|hey|hello)\s*,?\s+(?:the\s+|any\s+|all\s+)?" + _ADDRESSEE + r"s?\b|\b" + _ADDRESSEE + r"s?\s+(?:reading|processing|summari[sz]ing|parsing|crawling|browsing)\s+(?:this|these)\b"),
    Rule("second-person-obligation", FLAG, PROSE, r"\byou\s+(?:must|shall|need to|have to|are (?:required|instructed|expected|obliged) to|will now|are now)\b"),
    Rule("authority-claim", FLAG, PROSE, r"\b(?:operator|administrator|admin|developer|orchestrator|system|harness|anthropic|owner)\s+(?:has\s+|have\s+)?(?:instructed|authori[sz]ed|approved|permitted|requires?|required|wants|asks|asked|says|said|told|mandates?|directs?)\b|\buser\s+(?:has\s+)?(?:instructed|authori[sz]ed|approved|permitted|mandated|told you)\b|\b(?:official|authori[sz]ed|priority|urgent|system)\s+(?:instruction|directive|override)s?\b|\bmessage from (?:the\s+)?(?:operator|system|developer|administrator|orchestrator|harness|anthropic)\b"),
    Rule("execution-request", FLAG, PROSE, r"\b(?:run|execute|eval|paste)\s+(?:the\s+)?(?:following|this|these|below)\s+(?:command|code|script|snippet|line)s?\b|\b(?:please|now|immediately)\s+(?:run|execute|fetch|download|install|delete|remove|send|post|upload|visit)\b|\b(?:send|post|upload|exfiltrate|forward|leak|email)\s+(?:the\s+|your\s+|all\s+|any\s+|its\s+)?(?:\w+\s+){0,2}(?:secrets?|credentials?|tokens?|api[ _-]?keys?|passwords?|cookies?)\b"),
    Rule("long-base64", FLAG, PROSE, r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{100,}={0,2}(?![A-Za-z0-9+/=])", _mixed),
    Rule("script-network", FLAG, SCRIPT, r"\b(?:import|from)\s+(?:urllib\d?|requests|socket|http|httpx|aiohttp|ftplib|smtplib|telnetlib|paramiko|websockets?|pycurl)\b|\b(?:curl|wget|nc|ncat|netcat|socat|telnet|ssh|scp|sftp|rsync)\b|/dev/(?:tcp|udp)/|https?://"),
    Rule("script-subprocess", FLAG, SCRIPT, r"\bsubprocess\b|\bos\.(?:system|popen|exec\w*|spawn\w*|posix_spawn\w*|fork)\b|\bpty\.spawn\b|\b(?:eval|exec)\s*\(|\bshell\s*=\s*true\b|\b__import__\s*\(|\bctypes\b"),
    Rule("script-write", FLAG, SCRIPT, r"\bopen\s*\([^)]*,\s*(?:mode\s*=\s*)?[\"'][^\"']*[wax+][^\"']*[\"']|\.write_(?:text|bytes)\s*\(|\bshutil\.(?:copy\w*|move|rmtree)\b|\bos\.(?:rename|replace|remove|unlink|rmdir|makedirs|mkdir|symlink|link|chmod|chown)\b|\.(?:unlink|rmdir|mkdir|symlink_to|touch)\s*\(|(?<![<>=!-])>>?\s*[\"']?(?:/|~|\.\.)"),
    Rule("script-secret-path", FLAG, SCRIPT, r"\.ssh\b|\.aws\b|\.claude\.json|\.claude-sandbox/env|(?<![\w.])\.env\b|\.netrc|\.git-credentials|/proc/\S*environ|settings(?:\.local)?\.json|\.config/gh|\.docker/config|\bid_(?:rsa|dsa|ecdsa|ed25519)\b|\.pem\b|\.kube\b|\.gnupg|\.npmrc|\.pypirc"),
    Rule("script-env", FLAG, SCRIPT, r"\bos\.environ\b|\bgetenv\s*\(|\benviron\b|\$\{?[A-Z_]*(?:TOKEN|SECRET|KEY|PASSWORD)"),
]

# In a script, these shapes inside a quoted string are FLAG (a parser matching harness
# markup names it as a string); every other prose HOLD holds wherever it is.
DEMOTE_IN_STRINGS = {"control-tag", "special-token"}

# A phrase split by a code span or a quote boundary matches no single segment. These
# rules also run on the joined line (backticks dropped; a script's literals joined), and
# a hit there that no segment explains is HOLD for the rules below, FLAG for the rest.
JOINED_HOLD = {"override-phrase", "chat-role-prefix", "pipe-to-shell"}
_ESCAPED_BREAK = re.compile(r"\\[nr]")

# Common Cyrillic and Greek look-alikes of Latin letters, for matching only.
_CONFUSABLE = str.maketrans(
    "\u0430\u0435\u043e\u0440\u0441\u0443\u0445\u0456\u0458\u0455\u0501\u04bb\u04cf\u051b\u051d"
    "\u0410\u0412\u0415\u041a\u041c\u041d\u041e\u0420\u0421\u0422\u0425\u0406\u0408\u0405"
    "\u03b1\u03bf\u03b5\u03b9\u03ba\u03bd\u03c1\u03c4\u03c5\u03c7"
    "\u0391\u0392\u0395\u0396\u0397\u0399\u039a\u039c\u039d\u039f\u03a1\u03a4\u03a5\u03a7",
    "aeopcyxijsdhlqw"
    "ABEKMHOPCTXIJS"
    "aoeikvptux"
    "ABEZHIKMNOPTYX")

_INVISIBLE = re.compile("[\u200b-\u200d\u2060-\u2064\ufeff\u00ad\u180e\u200e\u200f\u061c\u202a-\u202e\u2066-\u2069\U000e0000-\U000e007f]")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_CLOSER = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*$")
_SAFE_PATH = re.compile(r"[A-Za-z0-9._/@+,=-]")


def _norm(s):
    s = unicodedata.normalize("NFKD", _INVISIBLE.sub("", s))
    s = "".join(c for c in s if not unicodedata.combining(c)).translate(_CONFUSABLE)
    return unicodedata.normalize("NFKC", s)


def fences(lines):
    """Set of 0-based line indexes inside a closed fence (the fence lines included).
    An unclosed fence is not a fence: it would otherwise demote the rest of the file."""
    n = len(lines)
    closer = [None] * n          # (char, length) when the line could close a fence
    for k, ln in enumerate(lines):
        m = _CLOSER.match(ln)
        if m:
            closer[k] = (m.group(1)[0], len(m.group(1)))
    # sufmax[c][k]: the longest closer of char c at index >= k, so an opener with no
    # closer after it is rejected in O(1); a found closer is reached by a scan the
    # outer loop then jumps past, so the whole pass is linear.
    sufmax = {"`": [0] * (n + 1), "~": [0] * (n + 1)}
    for k in range(n - 1, -1, -1):
        for c in sufmax:
            sufmax[c][k] = sufmax[c][k + 1]
        if closer[k]:
            c, ln = closer[k]
            sufmax[c][k] = max(sufmax[c][k], ln)
    inside, i = set(), 0
    while i < n:
        m = _FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        c, ln = m.group(1)[0], len(m.group(1))
        if sufmax[c][i + 1] < ln:
            i += 1
            continue
        j = i + 1
        while not (closer[j] and closer[j][0] == c and closer[j][1] >= ln):
            j += 1
        inside.update(range(i, j + 1))
        i = j + 1
    return inside


def md_segments(line):
    """[(text, is_code)] for one markdown line: inline code spans are backtick runs
    closed by a run of the same length on the same line. Raw ASCII backticks only."""
    runs = [(m.start(), m.end()) for m in re.finditer(r"`+", line)]
    nxt, seen = [None] * len(runs), {}
    for k in range(len(runs) - 1, -1, -1):   # next run of the same length, in one pass
        ln = runs[k][1] - runs[k][0]
        nxt[k] = seen.get(ln)
        seen[ln] = k
    out, pos, k = [], 0, 0
    while k < len(runs):
        m = nxt[k]
        if m is None:
            k += 1
            continue
        s, e = runs[k][0], runs[m][1]
        if s > pos:
            out.append((line[pos:s], False))
        out.append((line[s:e], True))
        pos, k = e, m + 1
    if pos < len(line):
        out.append((line[pos:], False))
    return out


def script_segments(line):
    """[(text, is_quoted)] for one script line: closed single- or double-quoted string
    literals on the line are the script's analogue of a code span."""
    out, pos, i, n, dead = [], 0, 0, len(line), set()
    while i < n:
        q = line[i]
        if q not in "'\"" or q in dead:
            i += 1
            continue
        k = i + 1
        while k < n and line[k] != q:
            k += 2 if line[k] == "\\" else 1
        if k >= n:
            dead.add(q)   # no close for this quote from here on: stop looking (linear)
            i += 1
            continue
        if i > pos:
            out.append((line[pos:i], False))
        out.append((line[i:k + 1], True))
        pos = i = k + 1
    if pos < n:
        out.append((line[pos:], False))
    return out


def joined_views(line, segs, markdown):
    """Whole-line views a split phrase cannot hide from: the markdown line with its
    backticks dropped; a script line's string literals joined (with and without a space),
    each also cut at escaped line breaks, so a literal's own start is a line start."""
    if markdown:
        return [line.replace("`", "")] if "`" in line else []
    lits = [seg[1:-1] for seg, quoted in segs if quoted]
    if not lits:
        return []
    views = []
    for text in ["".join(lits), " ".join(lits)] + lits:
        views.extend(_ESCAPED_BREAK.split(text))
    return views


def scan_text(text, markdown, scripts):
    """{(line, rule, tier)} for one decoded file."""
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.split("\n")
    fenced = fences(lines) if markdown else set()
    found = set()
    for idx, line in enumerate(lines):
        no = idx + 1
        for r in RULES:
            if r.kind == RAW and r.hit(line):
                found.add((no, r.name, r.tier))
        if idx in fenced:
            segs = [(line, True)]
        elif markdown:
            segs = md_segments(line)
        else:
            segs = script_segments(line)
        start = 0
        for seg, is_code in segs:
            ns = _norm(seg)
            for r in RULES:
                if r.kind != PROSE or (r.line_start and start):
                    continue
                demote = is_code and (markdown or r.name in DEMOTE_IN_STRINGS)
                if r.hit(ns):
                    found.add((no, r.name, FLAG if demote else r.tier))
            start += len(seg)
        if idx not in fenced:
            have = {r for n, r, _ in found if n == no}
            for v in joined_views(line, segs, markdown):
                nv = _norm(v)
                for r in RULES:
                    if r.kind == PROSE and r.name not in have and r.hit(nv):
                        have.add(r.name)
                        found.add((no, r.name, HOLD if r.name in JOINED_HOLD else FLAG))
        if scripts:
            nl = _norm(line)
            for r in RULES:
                if r.kind == SCRIPT and r.hit(nl):
                    found.add((no, r.name, r.tier))
    # A rule found at HOLD on a line needs no FLAG row beside it.
    return {h for h in found if not (h[2] == FLAG and (h[0], h[1], HOLD) in found)}


def display(path):
    """A lane-chosen path part as printed: characters outside a safe set escaped, so a
    file name cannot carry text to stdout. Returns (shown, was_escaped)."""
    out, esc = [], False
    for c in path:
        if _SAFE_PATH.match(c):
            out.append(c)
        else:
            esc = True
            o = ord(c)
            out.append("\\x%02x" % o if o < 0x100 else
                       "\\u%04x" % o if o < 0x10000 else "\\U%08x" % o)
    return "".join(out), esc


def kind_of(path):
    """'link', 'dir', 'file', 'other' (FIFO, socket, device) or 'missing', never
    following a link and never opening anything."""
    try:
        st = os.lstat(path)
    except OSError:
        return "missing"
    if stat.S_ISLNK(st.st_mode):
        return "link"
    if stat.S_ISDIR(st.st_mode):
        return "dir"
    return "file" if stat.S_ISREG(st.st_mode) else "other"


def scan_file(path, scripts):
    """(hits) for one regular file; undecodable or unreadable files hold."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return {(0, "unreadable", HOLD)}
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return {(0, "undecodable", HOLD)}
    markdown = path.lower().endswith(".md") or not scripts
    return scan_text(text, markdown, scripts)


def collect(paths, scripts):
    """[(path, shown, escaped, kind)] to scan. An argument is printed as given (the
    orchestrator chose it); only the part below it, which a lane chose, is escaped.
    Directories are walked without following links: *.md only in findings mode, every
    file in toolkit mode; a symlink or a non-regular entry is listed whatever its name."""
    out = []
    for p in paths:
        k = kind_of(p)
        if k != "dir":
            out.append((p, p, False, k))
            continue
        def unlistable(err, p=p):
            rel, esc = display(os.path.relpath(err.filename, p))
            out.append((err.filename, os.path.join(p, rel), esc, "unlistable"))
        for root, dirs, files in os.walk(p, onerror=unlistable):
            dirs.sort()
            for d in list(dirs):
                if kind_of(os.path.join(root, d)) != "dir":
                    dirs.remove(d)
                    files.append(d)
            for name in sorted(files):
                fp = os.path.join(root, name)
                fk = kind_of(fp)
                if fk == "file" and not (scripts or name.lower().endswith(".md")):
                    continue
                rel, esc = display(os.path.relpath(fp, p))
                out.append((fp, os.path.join(p, rel), esc, fk))
    return out


def report(targets, scripts):
    rows, n_files = [], 0
    for path, shown, escaped, kind in targets:
        if kind == "link":
            found = {(0, "symlink", HOLD)}
        elif kind == "unlistable":
            found = {(0, "unreadable", HOLD)}
        elif kind != "file":
            found = {(0, "not-regular", HOLD)}
        else:
            n_files += 1
            found = set(scan_file(path, scripts))
        if escaped:
            found.add((0, "unsafe-filename", FLAG))
        for no, rule, tier in found:
            rows.append((shown, no, rule, tier))
    rows.sort()
    for shown, no, rule, tier in rows:
        print("%s:%d: %s %s" % (shown, no, rule, tier))
    holds = sum(1 for r in rows if r[3] == HOLD)
    flags = len(rows) - holds
    print("SCAN: %d hold, %d flag, %d files" % (holds, flags, n_files))
    return 1 if holds else 3 if flags else 0


def parse_lines(spec):
    parts = spec.split(",")
    if not spec or any(not re.fullmatch(r"[0-9]+", p) for p in parts):
        raise ValueError
    nums = {int(p) for p in parts}
    if 0 in nums:
        raise ValueError
    return nums


def strip(path, spec, scripts):
    """Delete lines by 1-based position (split on LF, endings kept), atomically."""
    try:
        nums = parse_lines(spec)
    except ValueError:
        return usage("--lines takes positive line numbers, comma-separated")
    if kind_of(path) != "file":
        return usage("--strip takes a regular file, not a link")
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        return usage("--strip cannot read the file (%s)" % e.__class__.__name__)
    lines = data.split(b"\n")
    chunks = [ln + b"\n" for ln in lines[:-1]] + ([lines[-1]] if lines[-1] else [])
    if max(nums) > len(chunks):
        return usage("--lines names a line past the end of the file")
    kept = b"".join(c for i, c in enumerate(chunks, 1) if i not in nums)
    tmp = None
    try:   # a fresh, unpredictable temp file beside the target (O_EXCL, no link followed)
        fd, tmp = tempfile.mkstemp(prefix=".strip-", dir=os.path.dirname(path) or ".")
        with os.fdopen(fd, "wb") as f:
            f.write(kept)
            os.fchmod(f.fileno(), os.stat(path).st_mode & 0o7777)
        os.replace(tmp, path)
        tmp = None
    except OSError as e:
        return usage("--strip cannot write the file (%s)" % e.__class__.__name__)
    finally:
        if tmp and os.path.lexists(tmp):
            os.unlink(tmp)
    print("STRIPPED: %d lines, %s" % (len(nums), path))
    return report([(path, path, False, "file")], scripts)


def usage(msg):
    print("scan-findings: " + msg, file=sys.stderr)
    return 2


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="scan-findings.py", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Deterministic scan floor for research files.",
        epilog="output: one line per hit, '<path>:<line>: <rule> <HOLD|FLAG>' (line 0 is the\n"
               "whole file), then 'SCAN: <n> hold, <n> flag, <n> files'; --strip prints\n"
               "'STRIPPED: <n> lines, <path>' first. Never a file's text.\n"
               "exit: 0 clean, 1 any HOLD, 3 FLAG only, 2 usage error. Treat any other exit,\n"
               "or no SCAN line, as a HOLD.")
    ap.add_argument("--scripts", action="store_true",
                    help="toolkit mode: every file under PATH; prose tiers plus script rules")
    ap.add_argument("--strip", metavar="FILE", help="delete lines by position, then rescan")
    ap.add_argument("--lines", metavar="N[,N...]", help="with --strip: the line numbers")
    ap.add_argument("paths", nargs="*", metavar="PATH")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.strip is not None or a.lines is not None:
        if a.strip is None or a.lines is None or a.paths:
            return usage("--strip FILE and --lines N[,N...] go together, with no PATH")
        return strip(a.strip, a.lines, a.scripts)
    if not a.paths:
        return usage("no PATH given")
    missing = [p for p in a.paths if kind_of(p) == "missing"]
    if missing:
        return usage("no such path (%d)" % len(missing))
    return report(collect(a.paths, a.scripts), a.scripts)


if __name__ == "__main__":
    sys.exit(main())
