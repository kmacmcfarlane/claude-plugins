#!/usr/bin/env python3
"""Stop: the reliable channel to the model, end of every turn.

Two duties, each firing at most once per epoch (Stop feedback continues the
conversation and costs a turn — the 8-continuation cap and stop_hook_active
are honoured, but single-fire is the real guard):

1. Relay a deferred auto-compaction or an unanswered DUE: PreCompact's stderr
   is only documented to reach the user for manual triggers, so the model
   hears about a deferral here.
2. The ledger nudge: every CLAUDE_KIT_LEDGER_EVERY tokens of growth (default
   60K), ask for ledger lines — skipped when the last assistant message
   already contains them, and 'nothing new' is an acceptable one-line answer.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L

LEDGER_LINE = re.compile(r"^- [DXCURQ] ", re.M)


def ctx(text):
    return {"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": text}}


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return
    if inp.get("stop_hook_active"):
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    st = L.load_state(sid)
    ep = L.epoch(st)
    tok, win, _, src = L.depth(inp.get("transcript_path", ""), sid)
    if not tok:
        print(json.dumps({})); return
    remaining = max(win - tok, 0)
    th = L.thresholds(win)
    done = L.checkpointed_this_epoch(st)

    if not done and st.get("relay_epoch") != ep and (
            st.get("compact_deferred") or remaining <= th["due"]):
        st["relay_epoch"] = ep
        st.update(tokens=tok, window=win)
        L.save_state(sid, st)
        why = ("an automatic compaction was deferred by the context gate"
               if st.get("compact_deferred") else
               f"only {remaining:,} tokens remain ({src})")
        print(json.dumps(ctx(
            f"[claude-kit context gate] Before anything else: {why} and no "
            f"checkpoint has run this epoch. Run the checkpoint skill now — "
            f"ask the operator the goal (land / continue / handoff), write the "
            f"reasoning residue, then mark_checkpoint.py. Do not start new work.")))
        return

    every = int(os.environ.get("CLAUDE_KIT_LEDGER_EVERY", "60000") or 60000)
    if "ledger" not in st:
        # First observation: set the baseline silently. The nudge measures
        # growth the relay has watched, not absolute depth - otherwise a
        # session resumed deep would open with a spurious 'N tokens since'.
        st["ledger"] = {"tok": tok}
        st.update(tokens=tok, window=win)
        L.save_state(sid, st)
        print(json.dumps({}))
        return
    last = int(st["ledger"].get("tok", 0))
    if tok - last >= every:
        st["ledger"] = {"tok": tok}
        L.save_state(sid, st)
        if LEDGER_LINE.search(inp.get("last_assistant_message") or ""):
            print(json.dumps({})); return
        print(json.dumps(ctx(
            f"[claude-kit ledger] ~{tok - last:,} tokens since the last ledger "
            f"entry. Append one line per new decision/rejection/correction/"
            f"refusal since then to {L.ledger_path(sid)} in the form "
            f"`- <D|X|C|U|R|Q> <text> [-> path]`, or reply 'nothing new'. "
            f"One short turn; then stop.")))
        return

    st.update(tokens=tok, window=win)
    L.save_state(sid, st)
    print(json.dumps({}))


main()
