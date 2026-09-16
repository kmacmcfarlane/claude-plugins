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

Install (user settings, ~/.claude/settings.json):
  "statusLine": {"type": "command", "command": "python3 /path/to/statusline.py"}
"""
import json, math, os, sys, time
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
    name = d.get("session_name") or ""
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
