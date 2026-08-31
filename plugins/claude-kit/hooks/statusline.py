#!/usr/bin/env python3
"""Status line: the always-on context gauge, and the sensor for the gate hooks.

Claude Code hands the status line `context_window.used_percentage` and
`context_window_size` on every render -- the only place those exact figures are
exposed. This prints a one-line gauge for the operator and writes the same
numbers to the context-gate state file so context_warn.py / precompact_gate.py
act on exact depth instead of an inferred one.

Install (user settings, ~/.claude/settings.json):
  "statusLine": {"type": "command", "command": "python3 /path/to/statusline.py"}
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L


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
    print(f"{head}  {gauge}")


main()
