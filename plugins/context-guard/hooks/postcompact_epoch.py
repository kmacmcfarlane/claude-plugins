#!/usr/bin/env python3
"""PostCompact + SessionStart(clear): start a new epoch.

Advisories, DUE/HARD accounting and any deferred-compaction flag reset; the
checkpoint requirement re-arms. The ledger survives (it is re-injected by the
rehydration hook, not reset). PostCompact carries the generated summary —
saved to state so rehydration can name a summary/manifest conflict instead of
only asserting precedence.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L
import ledger


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return

    ev = inp.get("hook_event_name")
    if ev == "SessionStart" and inp.get("source") != "clear":
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    st_before = L.load_state(sid)
    st = L.reset_epoch(sid, compact_summary=inp.get("compact_summary")
                       if ev == "PostCompact" else None)
    ledger.epoch_header(sid, L.epoch(st), int(st_before.get("tokens") or 0))
    print(json.dumps({}))


main()
