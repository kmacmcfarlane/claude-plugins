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

Exit: 0 clean, 1 any HOLD, 3 FLAG only, 2 usage (nothing scanned or changed).

Stdout never carries a file's text: positions, rule names and counts only. That is what
lets the orchestrator read the result, and what lets `--strip` remove lines a verifier
named without anything reading them.

Tiers:
- HOLD (structural; holds the run): invisible, bidi, Unicode-tag and control characters
  (on raw text, anywhere); control-tag, special-token and chat-role shapes, override
  phrasing and pipe-to-shell outside code.
- FLAG (semantic; the verifier adjudicates each line): agent-addressed phrasing,
  second-person obligations, authority claims, execution requests, long base64; any
  HOLD shape inside a code span or a closed fence (inside a quoted string, in a script);
  in toolkit mode, network use, subprocesses, file writes, secret paths and env reads.
Prose rules match NFKC-normalised text with invisible characters removed, so full-width
and zero-width evasions still match. A clean scan is not a clean file.

Stdlib only.
"""
import argparse
import os
import re
import sys
import unicodedata

HOLD, FLAG = "HOLD", "FLAG"
RAW, PROSE, SCRIPT = "raw", "prose", "script"


class Rule:
    __slots__ = ("name", "tier", "kind", "rx", "check")

    def __init__(self, name, tier, kind, pattern, check=None):
        self.name, self.tier, self.kind, self.check = name, tier, kind, check
        self.rx = re.compile(pattern, re.IGNORECASE | re.MULTILINE)

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
    Rule("chat-role-prefix", HOLD, PROSE, r"^\s{0,3}(?:>\s*)*(?:\*\*|__)?(?:human|assistant)(?:\*\*|__)?\s*:"),
    Rule("override-phrase", HOLD, PROSE, r"\b(?:ignore|disregard|forget)\b(?:\W+\w+){0,3}?\W+(?:previous|prior|above|earlier|preceding|foregoing|all|any|every|system|original|initial|your)\b(?:\W+\w+){0,3}?\W+(?:instructions?|directions?|directives?|rules|prompts?|guidelines|guidance|constraints|messages)\b"),
    Rule("pipe-to-shell", HOLD, PROSE, r"\b(?:curl|wget|iwr|irm|invoke-webrequest|invoke-restmethod)\b[^|\n]{0,300}\|\s*(?:sudo\s+(?:-\S+\s+)*)?(?:(?:ba|z|da|k|fi)?sh|python3?|perl|ruby|node|iex)\b|\b(?:ba|z)?sh\s+(?:-c\s+)?[\"']?(?:<\(|\$\()\s*(?:curl|wget)\b"),
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

_INVISIBLE = re.compile("[\u200b-\u200d\u2060-\u2064\ufeff\u00ad\u180e\u200e\u200f\u061c\u202a-\u202e\u2066-\u2069\U000e0000-\U000e007f]")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_SAFE_PATH = re.compile(r"[A-Za-z0-9._/@+,=-]")


def _norm(s):
    return unicodedata.normalize("NFKC", _INVISIBLE.sub("", s))


def fences(lines):
    """Set of 0-based line indexes inside a closed fence (the fence lines included).
    An unclosed fence is not a fence: it would otherwise demote the rest of the file."""
    inside, i, n = set(), 0, len(lines)
    while i < n:
        m = _FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        mark = m.group(1)
        close = re.compile(r"^ {0,3}" + re.escape(mark[0]) + "{%d,}\\s*$" % len(mark))
        j = next((k for k in range(i + 1, n) if close.match(lines[k])), None)
        if j is None:
            i += 1
            continue
        inside.update(range(i, j + 1))
        i = j + 1
    return inside


def md_segments(line):
    """[(text, is_code)] for one markdown line: inline code spans are backtick runs
    closed by a run of the same length on the same line. Raw ASCII backticks only."""
    out, pos, i, n = [], 0, 0, len(line)
    while i < n:
        if line[i] != "`":
            i += 1
            continue
        j = i
        while j < n and line[j] == "`":
            j += 1
        run = j - i
        k = j
        close = None
        while k < n:
            if line[k] == "`":
                e = k
                while e < n and line[e] == "`":
                    e += 1
                if e - k == run:
                    close = (k, e)
                    break
                k = e
            else:
                k += 1
        if close is None:
            i = j
            continue
        if i > pos:
            out.append((line[pos:i], False))
        out.append((line[i:close[1]], True))
        pos = i = close[1]
    if pos < n:
        out.append((line[pos:], False))
    return out


def script_segments(line):
    """[(text, is_quoted)] for one script line: closed single- or double-quoted string
    literals on the line are the script's analogue of a code span."""
    out, pos, i, n = [], 0, 0, len(line)
    while i < n:
        q = line[i]
        if q not in "'\"":
            i += 1
            continue
        k = i + 1
        while k < n and line[k] != q:
            k += 2 if line[k] == "\\" else 1
        if k >= n:
            i += 1
            continue
        if i > pos:
            out.append((line[pos:i], False))
        out.append((line[i:k + 1], True))
        pos = i = k + 1
    if pos < n:
        out.append((line[pos:], False))
    return out


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
        for seg, is_code in segs:
            ns = _norm(seg)
            for r in RULES:
                if r.kind == PROSE and r.hit(ns):
                    found.add((no, r.name, FLAG if is_code else r.tier))
        if scripts and not markdown:
            nl = _norm(line)
            for r in RULES:
                if r.kind == SCRIPT and r.hit(nl):
                    found.add((no, r.name, r.tier))
    # A rule found at HOLD on a line needs no FLAG row beside it.
    return {h for h in found if not (h[2] == FLAG and (h[0], h[1], HOLD) in found)}


def display(path):
    """The path as printed: characters outside a safe set escaped, so a lane-chosen
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
    """[(path, extra_hits)] to scan: explicit files as given; directories walked without
    following links, *.md only in findings mode, every file in toolkit mode."""
    out = []
    for p in paths:
        if os.path.isdir(p) and not os.path.islink(p):
            for root, dirs, files in os.walk(p):
                dirs.sort()
                for d in list(dirs):
                    if os.path.islink(os.path.join(root, d)):
                        dirs.remove(d)
                        out.append((os.path.join(root, d), "link"))
                for name in sorted(files):
                    fp = os.path.join(root, name)
                    if os.path.islink(fp):
                        if scripts or name.lower().endswith(".md"):
                            out.append((fp, "link"))
                    elif scripts or name.lower().endswith(".md"):
                        out.append((fp, None))
        else:
            out.append((p, None))
    return out


def report(targets, scripts):
    rows, n_files = [], 0
    for path, kind in targets:
        shown, escaped = display(path)
        if kind == "link":
            found = {(0, "symlink", FLAG)}
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
    if not os.path.isfile(path) or os.path.islink(path):
        return usage("--strip takes a regular file")
    with open(path, "rb") as f:
        data = f.read()
    lines = data.split(b"\n")
    chunks = [ln + b"\n" for ln in lines[:-1]] + ([lines[-1]] if lines[-1] else [])
    if max(nums) > len(chunks):
        return usage("--lines names a line past the end of the file")
    kept = b"".join(c for i, c in enumerate(chunks, 1) if i not in nums)
    tmp = "%s.strip-%d" % (path, os.getpid())
    try:
        with open(tmp, "wb") as f:
            f.write(kept)
        os.chmod(tmp, os.stat(path).st_mode & 0o7777)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print("STRIPPED: %d lines, %s" % (len(nums), display(path)[0]))
    return report([(path, None)], scripts)


def usage(msg):
    print("scan-findings: " + msg, file=sys.stderr)
    return 2


def main(argv=None):
    ap = argparse.ArgumentParser(prog="scan-findings.py",
                                 description="Deterministic scan floor for research files.")
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
    missing = [p for p in a.paths if not os.path.lexists(p)]
    if missing:
        return usage("no such path (%d)" % len(missing))
    return report(collect(a.paths, a.scripts), a.scripts)


if __name__ == "__main__":
    sys.exit(main())
