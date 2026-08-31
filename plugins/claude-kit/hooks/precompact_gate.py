#!/usr/bin/env python3
"""PreCompact: defer automatic compaction while it is safe and unexamined.

Manual /compact is never touched; its custom_instructions are recorded so the
rehydration hook can replay the operator's own words after the summary.

Auto: per the hooks reference, blocking a PROACTIVE compaction is free (the
conversation continues uncompacted), but blocking one that fired to recover
from a context-limit error fails the in-flight request — and hook input cannot
distinguish them. So the gate defers only while BOTH hold: no checkpoint has
been recorded this epoch, AND tokens < window - thresholds(window)['hard'],
which with the auto-compact window lowered (e.g. /autocompact 900k on a 1M
model) proves the trigger was proactive. Otherwise it always allows.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    st = L.load_state(sid)
    st["last_compact_trigger"] = inp.get("trigger")
    st["last_compact_at"] = time.strftime("%F %T")

    if inp.get("trigger") == "manual":
        ci = inp.get("custom_instructions")
        if ci:
            st["custom_instructions"] = ci[:4000]
        L.save_state(sid, st)
        print(json.dumps({})); return

    tok, win, _, src = L.depth(inp.get("transcript_path", ""), sid)
    th = L.thresholds(win)
    proactive = tok and tok < win - th["hard"]

    if L.checkpointed_this_epoch(st) or not proactive:
        st.pop("compact_deferred", None)
        L.save_state(sid, st)
        print(json.dumps({})); return

    st["compact_deferred"] = True
    L.save_state(sid, st)
    sys.stderr.write(
        f"[claude-kit context gate] Auto-compaction deferred: no checkpoint has "
        f"run this epoch and there is headroom ({win - tok:,} tokens, {src}). "
        f"Run the checkpoint skill; compaction proceeds once it records, or "
        f"when headroom drops below {th['hard']:,}.\n")
    sys.exit(2)


main()
