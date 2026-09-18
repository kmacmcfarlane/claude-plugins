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
sessions never receive `rate_limits`, so they see none.

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
    field may be missing or the wrong type (bool, NaN and infinity included). A
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
        used, resets = w.get("used_percentage"), w.get("resets_at")
        if isinstance(used, bool) or isinstance(resets, bool):
            continue
        try:
            used, resets = float(used), float(resets)
        except (TypeError, ValueError):
            continue
        if not (math.isfinite(used) and math.isfinite(resets)):
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


REGISTRY_MAX_BYTES = 65536  # a registry entry is a few hundred bytes; cap the read
ANCESTORS = 4  # python -> [sh ->] claude: how far up to look for the session pid
EXPLICIT = ("user", "peer", "hook", "collision")  # nameSource values the operator set
NAME_MAX = 60  # widest name shown, in terminal columns; wider ones end in an ellipsis
SCAN_MAX = 8 * NAME_MAX  # code points looked at: a flood of zero-width marks ends here
_UNSAFE = re.compile(r"[\s\x00-\x1f\x7f-\x9f]+")  # whitespace, C0, DEL, C1
ZWJ = "\u200d"
FLAG = "\U0001F3F4"  # the base of the tag-sequence flags (England, Scotland, Wales)
# A ZWJ with no visible non-ASCII character on either side joins nothing and is
# only invisible padding; inside an emoji sequence (or Indic text) it stays.
_LONE_ZWJ = re.compile(r"(?<![^\x00-\x9f\s\u200d])\u200d|\u200d(?![^\x00-\x9f\s\u200d])")


def _visible(name):
    """`name` without format (Cf) or surrogate (Cs) characters.

    Cf covers the bidi overrides and isolates (U+202A-202E, U+2066-2069) that
    can visually reverse the row, and the zero-width spaces, joiners and BOM
    (U+200B-200F, U+2060-2064, U+FEFF) that pad it invisibly. Two exceptions:
    a ZWJ, which _LONE_ZWJ then keeps only between visible characters, and the
    tag characters that spell a subdivision flag right after its FLAG base. A
    lone surrogate cannot be printed at all.
    """
    out = []
    for ch in name:
        cat = unicodedata.category(ch)
        if cat == "Cs":
            continue
        if cat == "Cf" and ch != ZWJ:
            tag = "\U000E0020" <= ch <= "\U000E007F"
            if not (tag and out and (out[-1] == FLAG or "\U000E0020" <= out[-1] <= "\U000E007F")):
                continue
        out.append(ch)
    return _LONE_ZWJ.sub("", "".join(out))


def columns(ch):
    """Terminal columns one code point takes: 0 for combining and format
    characters, 2 for East Asian wide/fullwidth (CJK, most emoji), else 1."""
    if unicodedata.combining(ch) or unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def clean(name):
    """One-line, printable form of a name from any source, or "" for a non-string.

    Format characters are dropped (see _visible), runs of whitespace or C0/C1
    control characters (ESC, BEL, DEL, newlines) collapse to a single space,
    and the ends are stripped, so a name made only of such characters is "".
    Anything wider than NAME_MAX terminal columns (see columns(); a wide
    character counts 2, a combining mark 0) is cut to at most NAME_MAX - 1
    columns plus an ellipsis, never between a character and its combining
    marks. Only the first SCAN_MAX code points (after whitespace collapses) are
    looked at; a name longer than that also ends in the ellipsis. Never raises.
    """
    if not isinstance(name, str):
        return ""
    try:
        name = _UNSAFE.sub(" ", name).strip()
        over = len(name) > SCAN_MAX
        name = _UNSAFE.sub(" ", _visible(name[:SCAN_MAX])).strip()
        if not name:
            return ""
        widths = [columns(ch) for ch in name]
        if not over and sum(widths) <= NAME_MAX:
            return name
        used = cut = 0
        for i, w in enumerate(widths):
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


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        print(""); return
    cw = d.get("context_window") or {}
    pct = cw.get("used_percentage")
    size = cw.get("context_window_size") or 0
    tok = cw.get("total_input_tokens") or 0
    sid = d.get("session_id")

    if sid and pct is not None and size:
        st = L.load_state(sid)
        st["exact"] = {"pct": float(pct), "tokens": int(tok), "window": int(size), "at": time.time()}
        L.save_state(sid, st)

    model = (d.get("model") or {}).get("display_name", "?")
    name = session_name(d)
    cwd = os.path.basename((d.get("workspace") or {}).get("current_dir") or d.get("cwd") or "")
    eff = ((d.get("effort") or {}).get("level") or "")

    if pct is None:
        gauge = "ctx --"
    else:
        p = int(pct)
        left = max(size - tok, 0)
        th = L.thresholds(size)
        ep = L.epoch(L.load_state(sid)) if sid else 0
        filled = p // 10
        bar = "█" * filled + "░" * (10 - filled)
        color = ("\033[32m" if left > th["due"] else
                 "\033[33m" if left > th["hard"] else "\033[31m")
        hint = ("" if left > th["due"] else
                "  ·  checkpoint DUE" if left > th["hard"] else "  ·  HARD gate")
        gauge = f"{color}{bar}\033[0m {p}%  {left // 1000}k left  e{ep}{hint}"

    head = f"[{model}{'·' + eff if eff else ''}] {cwd}"
    if name:
        head += f"  ({name})"
    line = f"{head}  {gauge}"
    for bar in usage_bars(d.get("rate_limits")):
        line += f"  {bar}"
    print(line)


main()
