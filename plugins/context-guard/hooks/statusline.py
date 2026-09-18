#!/usr/bin/env python3
"""Status line: the always-on context gauge, and the sensor for the gate hooks.

Claude Code hands the status line `context_window.used_percentage` and
`context_window_size` on every render -- the only place those exact figures are
exposed. This prints a one-line gauge for the operator and writes the same
numbers to the context-gate state file so context_warn.py / precompact_gate.py
act on exact depth instead of an inferred one.

On Pro/Max subscriptions (Claude Code >= 2.1.251) the payload also carries
`rate_limits` -- the plan's usage windows (`five_hour`, `seven_day`, and
`spend_limit` where enabled), each with `used_percentage` and `resets_at` (epoch
seconds). Those render as compact bars after the context gauge; API-key
sessions never receive `rate_limits`, so they see none. The same windows are
recorded in the state file under `rate_limits` (see limits_record) for
librarian-mode's fable-unavailable fallback, which reads a window's reset time.

The session name shown in parentheses comes from a documented fallback chain
(Claude Code 2.1.273, docs/en/statusline). First Claude Code's local session
registry, `$CLAUDE_CONFIG_DIR/sessions/<pid>.json` (keys `sessionId`, `name`,
`nameSource` in user|peer|hook|collision|auto|derived), but only when the entry
for this session carries an explicit nameSource -- user, peer, hook or
collision: those are the names the operator sets (/rename, an agent naming
itself through the peer channel), and the payload lags them or never carries
them. Then the payload's `session_name` -- the custom name from `/rename` or
`--name` when one exists, else the AI-generated title, absent otherwise --
which covers the AI title and the window before the registry write. A
`derived` or `auto` registry name (the my-app-3f default) is never shown, as
the payload skips it too. The registry read is one small file per ancestor pid
(the status line runs as a child of the session, possibly through a shell),
walked lazily -- the direct parent's entry first, then one /proc read per
further ancestor, stopping at the first entry for this session -- at most
ANCESTORS reads and never a directory scan; any missing or malformed source
just falls through. Without /proc (non-Linux) only the direct parent is
checked, so the chain degrades to payload-only when a shell sits between the
session and this script. Either name is sanitised before it is shown: runs of
whitespace or control characters collapse to one space (a peer or hook name is
an arbitrary string set by another agent), invisible format characters (bidi
overrides, zero-width spaces; Unicode category Cf) are dropped, and it is
capped at NAME_MAX terminal columns.

Install (user settings, ~/.claude/settings.json):
  "statusLine": {"type": "command", "command": "python3 /path/to/statusline.py"}
"""
import json, math, os, re, sys, time, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L

WINDOWS = (("five_hour", "5h"), ("seven_day", "7d"), ("spend_limit", "$"))
MAX_AHEAD = 366 * 86400  # a reset further out than this is not a window we know


def countdown(secs):
    """Compact 'in how long' for a reset, rounded up to the minute: 3d2h, 2h10m, 45m."""
    secs = max(math.ceil(secs / 60), 1) * 60
    d, r = divmod(secs, 86400)
    h, r = divmod(r, 3600)
    m = r // 60
    if d:
        return f"{d}d{h}h" if h else f"{d}d"
    if h:
        return f"{h}h{m:02d}m" if m else f"{h}h"
    return f"{m}m"


def usage_bars(rate_limits, now=None):
    """Bars for the plan usage windows in `rate_limits`, or [] when there are none.

    Defensive by design: the block is optional, each window is optional, and any
    field may be missing or the wrong type (bool, NaN, infinity and an integer
    too large for a float included; see num()). A
    window whose reset is already past is stale (Claude Code drops it after the
    next response) and is skipped, as is one more than MAX_AHEAD out -- the
    official field is epoch seconds, so that is a unit mix-up, not a window.
    """
    if not isinstance(rate_limits, dict):
        return []
    now = time.time() if now is None else now
    out = []
    for key, label in WINDOWS:
        w = rate_limits.get(key)
        if not isinstance(w, dict):
            continue
        used, resets = num(w.get("used_percentage")), num(w.get("resets_at"))
        if used is None or resets is None:
            continue
        if resets <= now or resets - now > MAX_AHEAD:
            continue
        used = min(max(used, 0.0), 100.0)
        p = int(used)
        filled = min(p // 10, 10)
        bar = "█" * filled + "░" * (10 - filled)
        color = ("\033[32m" if used < 70 else
                 "\033[33m" if used < 90 else "\033[31m")
        out.append(f"{label} {color}{bar}\033[0m {p}% resets {countdown(resets - now)}")
    return out


def num(v):
    """`v` as a finite float, or None: a missing, bool, text, NaN or infinite
    field is not a number the gauge or the state record can use."""
    if isinstance(v, bool):
        return None
    try:
        v = float(v)
    except (TypeError, ValueError, OverflowError):
        return None
    return v if math.isfinite(v) else None


_WINDOW_KEY = re.compile(r"[a-z0-9_]{1,40}")  # a window name, not free text
LIMIT_FIELDS = ("used_percentage", "resets_at")
WINDOWS_MAX = 16  # windows recorded at most: the payload is not ours to bound


def limits_record(rate_limits, now=None):
    """The state-file form of `rate_limits`, or None when there is nothing to record.

    `{<window>: {"used_percentage": float, "resets_at": float}, ..., "at": now}`
    with every window the payload carries -- five_hour, seven_day, spend_limit,
    and any other (a per-model window such as seven_day_opus lands under its own
    name) -- as long as its name is a short lowercase identifier. At most
    WINDOWS_MAX windows are kept: the first ones, in payload order (JSON object
    order, which json.load preserves), that pass the checks below, so the same
    payload always yields the same set. Only the two
    numeric fields are kept, each only when it is a finite number, and a
    resets_at more than MAX_AHEAD out (a milliseconds mix-up) is dropped; a
    window left with neither field is skipped. A past resets_at is kept: the
    reader compares it with the clock. Never raises.
    """
    try:
        if not isinstance(rate_limits, dict):
            return None
        now = time.time() if now is None else now
        rec = {}
        for key, w in rate_limits.items():
            if len(rec) >= WINDOWS_MAX:
                break
            if key == "at" or not isinstance(key, str) or not _WINDOW_KEY.fullmatch(key):
                continue
            if not isinstance(w, dict):
                continue
            fields = {f: num(w.get(f)) for f in LIMIT_FIELDS}
            if fields["resets_at"] is not None and fields["resets_at"] - now > MAX_AHEAD:
                fields["resets_at"] = None
            fields = {f: v for f, v in fields.items() if v is not None}
            if fields:
                rec[key] = fields
        if not rec:
            return None
        rec["at"] = now
        return rec
    except Exception:
        return None


REGISTRY_MAX_BYTES = 65536  # a registry entry is a few hundred bytes; cap the read
ANCESTORS = 4  # python -> [sh ->] claude: how far up to look for the session pid
EXPLICIT = ("user", "peer", "hook", "collision")  # nameSource values the operator set
NAME_MAX = 60  # widest name shown, in terminal columns; wider ones end in an ellipsis
SCAN_MAX = 8 * NAME_MAX  # code points kept from a name: a flood of combining marks ends here
SCAN_HARD = 64 * NAME_MAX  # code points read while looking for them: format padding ends here
_UNSAFE = re.compile(r"[\s\x00-\x1f\x7f-\x9f]+")  # whitespace, C0, DEL, C1
ZWJ = "\u200d"
VS16 = "\ufe0f"  # emoji presentation selector: the character before it is drawn 2 wide
FLAG = "\U0001F3F4"  # the base of the tag-sequence flags (England, Scotland, Wales)
# A subdivision flag is FLAG, a short tag spelling (gbeng, gbsct, usca...), and
# the CANCEL TAG terminator; tag characters anywhere else are invisible padding.
_FLAG_TAGS = re.compile("[\U000E0020-\U000E007E]{2,7}\U000E007F")


def _joins(ch, mark_ok):
    """Whether `ch` can sit beside a kept ZWJ: visible and non-ASCII (emoji,
    Indic), and on the right-hand side a base character, not a combining mark,
    so a mark-ZWJ-mark chain cannot pad a name with joiners."""
    if ch is None or ch <= "\x9f" or ch == ZWJ or ch.isspace():
        return False
    return mark_ok or not unicodedata.category(ch).startswith("M")


def _visible(name):
    """(`name` without format or surrogate characters, whether it was cut short).

    Drops Unicode category Cf -- the bidi overrides and isolates (U+202A-202E,
    U+2066-2069) that can visually reverse the row, and the zero-width spaces,
    joiners and BOM (U+200B-200F, U+2060-2064, U+FEFF) that pad it invisibly --
    and lone surrogates (Cs), which cannot be printed at all. Two exceptions:
    a ZWJ with a visible non-ASCII character before it and a base character
    after it (inside an emoji sequence or Indic text), and a whole subdivision
    flag (FLAG + _FLAG_TAGS). Stops once SCAN_MAX characters are kept or
    SCAN_HARD have been read, so the cost is bounded whatever the input.
    """
    out, i, n = [], 0, len(name)
    while i < n and i < SCAN_HARD and len(out) < SCAN_MAX:
        ch = name[i]
        i += 1
        if ch == FLAG:
            m = _FLAG_TAGS.match(name, i)
            out.append(ch)
            if m:
                out.extend(m.group())
                i = m.end()
            continue
        cat = unicodedata.category(ch)
        if cat == "Cs" or (cat == "Cf" and ch != ZWJ):
            continue
        out.append(ch)
    kept = []
    for j, ch in enumerate(out):
        if ch == ZWJ and not (_joins(kept[-1] if kept else None, True) and
                              _joins(out[j + 1] if j + 1 < len(out) else None, False)):
            continue
        kept.append(ch)
    return "".join(kept), i < n


def columns(ch):
    """Terminal columns one code point takes on its own: 0 for combining and
    format characters, 2 for East Asian wide/fullwidth (CJK, and emoji whose
    default presentation is emoji), else 1. widths() adds the VS16 rule."""
    if unicodedata.combining(ch) or unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def widths(name):
    """columns() of each code point in `name`, with a text-default character
    followed by VS16 (the heart, sun or victory hand as emoji) counted 2 wide,
    as terminals draw it."""
    ws = [columns(ch) for ch in name]
    for i in range(len(ws) - 1):
        if ws[i] == 1 and name[i + 1] == VS16:
            ws[i] = 2
    return ws


def clean(name):
    """One-line, printable form of a name from any source, or "" for a non-string.

    Format characters are dropped (see _visible), runs of whitespace or C0/C1
    control characters (ESC, BEL, DEL, newlines) collapse to a single space,
    and the ends are stripped, so a name made only of such characters is "".
    Anything wider than NAME_MAX terminal columns (see widths(); a wide
    character counts 2, a combining mark 0) is cut to at most NAME_MAX - 1
    columns plus an ellipsis, never between a character and its combining
    marks. Reading stops after SCAN_MAX kept code points or SCAN_HARD read
    ones (after whitespace collapses), and a name cut short there also ends in
    the ellipsis. The trade-off: a real name hidden behind more than SCAN_HARD
    format characters is not found, and shows as "". Never raises.
    """
    if not isinstance(name, str):
        return ""
    try:
        name, over = _visible(_UNSAFE.sub(" ", name).strip())
        name = _UNSAFE.sub(" ", name).strip()
        if not name:
            return ""
        ws = widths(name)
        if not over and sum(ws) <= NAME_MAX:
            return name
        used = cut = 0
        for i, w in enumerate(ws):
            if used + w > NAME_MAX - 1:
                break
            used, cut = used + w, i + 1
        return name[:cut].rstrip().rstrip(ZWJ).rstrip() + "\u2026"
    except Exception:
        return ""


def ancestor_pids():
    """Yield the parent pid, then its ancestors through /proc where that exists.

    Lazy: each further ancestor costs one /proc read, taken only if the caller
    asks for it. Without /proc (non-Linux) the walk ends after the direct
    parent, so a shell between the session and this script hides the registry
    there and the name falls back to the payload.
    """
    pids, pid = [], os.getppid()
    for _ in range(ANCESTORS):
        if not pid or pid <= 1 or pid in pids:
            return
        pids.append(pid)
        yield pid
        try:
            with open(f"/proc/{pid}/status") as f:
                pid = next((int(ln.split()[1]) for ln in f if ln.startswith("PPid:")), 0)
        except Exception:
            return


def registry_name(sid, base=None):
    """Explicitly set session name from the local session registry, or "".

    Reads `<config dir>/sessions/<pid>.json` for each ancestor pid, nearest
    first, and stops at the first entry whose `sessionId` is ours, so a reused
    pid or a sibling session never leaks a name and the common case (a direct
    child of the session) costs one open. Only a name with an EXPLICIT
    nameSource counts; a derived/auto default yields "". Anything missing,
    oversized or malformed yields "".
    """
    if not sid:
        return ""
    base = base or L._base_dir()
    for pid in ancestor_pids():
        try:
            with open(os.path.join(base, "sessions", f"{pid}.json")) as f:
                d = json.loads(f.read(REGISTRY_MAX_BYTES))
        except Exception:
            continue
        if not isinstance(d, dict) or d.get("sessionId") != sid:
            continue
        name = clean(d.get("name"))
        return name if name and d.get("nameSource") in EXPLICIT else ""
    return ""


def session_name(d):
    """Current name by the chain: registry explicit name -> payload session_name -> "".

    Both sources pass through clean(): a peer/hook name is set by another agent
    and the payload title is free text, and the status line is one line.
    """
    try:
        name = clean(registry_name(d.get("session_id")))
    except Exception:
        name = ""
    if name:
        return name
    return clean(d.get("session_name"))


def obj(v):
    """`v` when it is a JSON object, else {}: any payload block may be missing,
    null, or the wrong type."""
    return v if isinstance(v, dict) else {}


def main():
    try:
        # A lone surrogate in any field (cwd, model name) must not make print() raise.
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    try:
        d = obj(json.load(sys.stdin))
    except Exception:
        print(""); return
    cw = obj(d.get("context_window"))
    # A field that is present but not a number (text, bool, NaN) spoils the
    # gauge: it shows "ctx --" and records nothing, never a blank line.
    # A window size below 1 (or none) is unknown: no gauge, and no exact
    # record that would tell the gate hooks there is nothing left - a
    # fractional size would otherwise truncate to 0. The used percentage is
    # clamped to 0-100.
    pct = num(cw.get("used_percentage"))
    size = num(cw.get("context_window_size") or 0)
    tok = num(cw.get("total_input_tokens") or 0)
    if size is None or tok is None or size < 1:
        pct = None
    else:
        size, tok = int(size), max(int(tok), 0)
    if pct is not None:
        pct = min(max(pct, 0.0), 100.0)
    sid = d.get("session_id")
    if not isinstance(sid, str):
        sid = None

    st = None
    if sid:
        try:
            now = time.time()
            limits = limits_record(d.get("rate_limits"), now)
            if (pct is not None and size) or limits:
                def record(s):
                    if pct is not None and size:
                        s["exact"] = {"pct": pct, "tokens": tok, "window": size, "at": now}
                    if limits:
                        s["rate_limits"] = limits
                st = L.update_state(sid, record)
        except Exception:
            pass

    model = obj(d.get("model")).get("display_name", "?")
    name = session_name(d)
    cwd = obj(d.get("workspace")).get("current_dir") or d.get("cwd") or ""
    cwd = os.path.basename(cwd) if isinstance(cwd, str) else ""
    eff = obj(d.get("effort")).get("level") or ""

    gauge = "ctx --"
    if pct is not None:
        try:
            p = int(pct)
            left = max(size - tok, 0)
            th = L.thresholds(size)
            ep = L.epoch(st if st is not None else L.load_state(sid)) if sid else 0
            filled = min(max(p // 10, 0), 10)
            bar = "█" * filled + "░" * (10 - filled)
            color = ("\033[32m" if left > th["due"] else
                     "\033[33m" if left > th["hard"] else "\033[31m")
            hint = ("" if left > th["due"] else
                    "  ·  checkpoint DUE" if left > th["hard"] else "  ·  HARD gate")
            gauge = f"{color}{bar}\033[0m {p}%  {left // 1000}k left  e{ep}{hint}"
        except Exception:
            gauge = "ctx --"

    head = f"[{model}{'·' + eff if eff else ''}] {cwd}"
    if name:
        head += f"  ({name})"
    line = f"{head}  {gauge}"
    for bar in usage_bars(d.get("rate_limits")):
        line += f"  {bar}"
    print(line)


try:
    main()
except Exception:  # the status line never raises: a blank line beats a traceback
    print("")
