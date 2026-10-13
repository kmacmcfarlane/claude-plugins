#!/usr/bin/env python3
"""PreCompact: defer automatic compaction until the window is really full.

Manual /compact is never touched; its custom_instructions are recorded so the
rehydration hook can replay the operator's own words after the summary.

Auto: Claude Code also starts an automatic compaction after a session sits
idle, at any fill (observed from transcripts on Claude Code 2.1.292: the idle
attempts arrived about 54 minutes after the last turn end), and the operator
expects compaction only when the window is really full. So on a usable depth
the gate defers while remaining > thresholds(window)['due']. Before a
checkpoint this epoch it always does; after one, only while the session is
idle at its last measured fill (L.input_since_usage: no prompt or tool result
since the last usage line). Input since then may have overflowed a fill the
gate never saw (a batch of reads, or a model switch that leaves a 1M guess on
a 200K model), so after a checkpoint such an attempt goes through, as it did
before. At or under due it releases once a checkpoint has been recorded this
epoch, and keeps deferring until one has.

Per the hooks reference, blocking a PROACTIVE compaction is free (the
conversation continues uncompacted), but blocking one that fired to recover
from a context-limit error fails the in-flight request - and hook input cannot
distinguish them. So the gate defers only while tokens < window -
thresholds(window)['hard'], which with the auto-compact window lowered (e.g.
/autocompact 900k on a 1M model) proves the trigger was proactive; at or past
that line it always allows, checkpoint or not. An unknown depth always allows.
The depth here is the pre-mirror one (L.depth(mirror=False): exact, else
inferred) - exactly what it was before the window mirror. A derived window
never defers a compaction: if it overestimated the window, deferring would
block a compaction Claude Code needs. It is also the MODEL window, never the
lower auto-compact window the prompt gate may score against.
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
    manual = inp.get("trigger") == "manual"
    path = inp.get("transcript_path", "")
    if not manual:
        tok, win, _, src = L.depth(path, sid, mirror=False)
        th = L.thresholds(win)
        proactive = bool(tok) and tok < win - th["hard"]
        # Above the due line the window is not full.
        headroom = proactive and win - tok > th["due"]
        pending = headroom and L.input_since_usage(path)
    res = {}

    def apply(st):
        st["last_compact_trigger"] = inp.get("trigger")
        st["last_compact_at"] = time.strftime("%F %T")
        if manual:
            ci = inp.get("custom_instructions")
            if ci:
                st["custom_instructions"] = ci[:4000]
            return
        cp = L.checkpointed_this_epoch(st)
        # Above due: hold, checkpoint or not - but after a checkpoint only
        # while idle at the measured fill (input since may have overflowed it).
        res["hold"] = headroom and (not cp or not pending)
        # compact_deferred means a deferral a checkpoint would release (the
        # checkpoint skill's Step 0 reads it so); one above due is not that.
        if proactive and not headroom and not cp:
            st["compact_deferred"] = True
        else:
            st.pop("compact_deferred", None)

    st = L.update_state(sid, apply)
    if manual or not (res.get("hold") or st.get("compact_deferred")):
        print(json.dumps({})); return

    if res.get("hold"):
        why = (f"the window is not full: {win - tok:,} tokens remain ({src}), "
               f"above the due line of {th['due']:,}. Nothing to do; it proceeds "
               f"once headroom is at or under {th['due']:,} and a checkpoint has "
               f"run this epoch, or after a checkpoint once input follows the "
               f"last response, or when headroom drops to {th['hard']:,} or below")
    else:
        why = (f"no checkpoint has run this epoch and {win - tok:,} tokens "
               f"remain ({src}), at or under the due line of {th['due']:,}. "
               f"Run the checkpoint skill; compaction proceeds once it records, "
               f"or when headroom drops to {th['hard']:,} or below")
    sys.stderr.write(
        f"[context-guard context gate] Auto-compaction deferred: {why}.\n")
    sys.exit(2)


main()
