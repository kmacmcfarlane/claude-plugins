#!/usr/bin/env python3
"""UserPromptSubmit: tell the operator how deep the context is, before it bites.

Fires at most once per threshold band per session, so it informs rather than
nags. The operator cannot see context depth naturally; this makes it visible at
the moments where a decision is still cheap.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L

# (pct, label, guidance to Claude)
BANDS = [
    (60, "NOTICE", "Context is past halfway. No action needed yet, but prefer subagents for "
                   "read-heavy searches from here on, and keep writing findings to files."),
    (75, "WARN",   "Context is getting deep. Before starting any NEW thread of work, flush "
                   "durable state to disk (commit, or write the investigation/plan file). "
                   "Mention the depth to the user once, briefly."),
    (88, "URGENT", "Context is nearly full; auto-compact is close. STOP starting new work. "
                   "Run the `checkpoint` skill now: land uncommitted state, then tell the "
                   "user what is in flight and let THEM choose how to compact."),
]


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    tok, win, pct = L.depth(inp.get("transcript_path", ""))
    if not tok:
        print(json.dumps({})); return

    st = L.load_state(sid)
    fired = st.get("bands_fired", [])

    band = None
    for threshold, label, guidance in BANDS:
        if pct >= threshold and threshold not in fired:
            band = (threshold, label, guidance)
    if band is None:
        st.update(tokens=tok, pct=round(pct, 1))
        L.save_state(sid, st)
        print(json.dumps({})); return

    threshold, label, guidance = band
    # Mark every band at or below the current depth as fired, not just the one
    # we are reporting. A session that jumps straight past several thresholds
    # must not then warn *downward* on subsequent turns.
    fired = sorted({t for t, _, _ in BANDS if pct >= t} | set(fired))
    st.update(bands_fired=fired, tokens=tok, pct=round(pct, 1), window=win)
    L.save_state(sid, st)

    ctx = (f"[claude-kit context gate] {label}: context is {pct:.0f}% full "
           f"({tok:,} of {win:,} tokens). {guidance}")
    out = {
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ctx},
        "systemMessage": f"Context {pct:.0f}% full ({tok:,}/{win:,}). "
                         + ("Consider /checkpoint before continuing."
                            if threshold >= 75 else "Still plenty of room."),
    }
    print(json.dumps(out))


main()
