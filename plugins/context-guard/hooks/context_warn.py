#!/usr/bin/env python3
"""UserPromptSubmit: depth advisories, DUE, and the HARD gate — per epoch.

Advisories (60/75% full) inform once per epoch. DUE fires when remaining
tokens drop under thresholds(window)['due'] with no checkpoint recorded this
epoch, and re-fires every 3 prompts or 25K tokens so it cannot be scrolled
past. HARD blocks the prompt itself (exit 2 — Claude Code shows stderr to the
user and ERASES the prompt) unless the prompt is /checkpoint, /compact or
/clear, in the bare or the plugin-prefixed form (/context-guard:checkpoint).
A HARD stop requires an EXACT depth (fresh status-line record): when the
depth is inferred from the transcript it is a guess, so under `hard` the hook
emits the DUE-style advisory saying a hard stop was not applied and exits 0
(live-fired 2026-09-16: a 1M session was blocked against a guessed 200K).
Set timeout: 10 in hooks.json: this event is fail-open on timeout, so a slow
hook silently disables the gate.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L

DUE_EVERY_PROMPTS = 3
DUE_EVERY_TOKENS = 25_000
BANDS = (60, 75)
# /checkpoint, /compact, /clear - bare or plugin-qualified (/context-guard:checkpoint).
WHITELIST = re.compile(r"^/(?:[\w-]+:)?(?:checkpoint|compact|clear)(?=\s|$)")


def due_fires(st, tok):
    """DUE cadence: first time, then every DUE_EVERY_PROMPTS or DUE_EVERY_TOKENS."""
    due = st.get("due") or {}
    return (not due
            or st["prompt_n"] - due.get("prompt_n", 0) >= DUE_EVERY_PROMPTS
            or tok - due.get("tok", 0) >= DUE_EVERY_TOKENS)


def decide(st, tok, win, pct, src, whitelisted):
    """Apply one prompt's accounting to `st` (in place, under the state lock)
    and return the action: None, "hard_inferred", "hard", "due" or "band"."""
    ep = L.epoch(st)
    st["prompt_n"] = int(st.get("prompt_n", 0)) + 1
    st.update(tokens=tok, pct=round(pct, 1), window=win)
    if not tok:
        return None
    remaining = max(win - tok, 0)
    th = L.thresholds(win)
    if L.checkpointed_this_epoch(st):
        # A checkpoint this epoch stands the whole gate down - DUE, HARD and
        # the advisories. The operator has already acted on the depth.
        return None
    if remaining <= th["hard"] and not whitelisted:
        if src == "exact":
            return "hard"
        # A guess never blocks: the window may be larger than inferred.
        # Same cadence as DUE so a long stretch under a guessed 200K
        # window does not nag on every prompt.
        if not due_fires(st, tok):
            return None
        st["due"] = {"prompt_n": st["prompt_n"], "tok": tok}
        return "hard_inferred"
    if remaining <= th["due"]:
        if due_fires(st, tok):
            st["due"] = {"prompt_n": st["prompt_n"], "tok": tok}
            return "due"
        return None
    bands = st.get("bands") or {}
    if [b for b in BANDS if pct >= b and bands.get(str(b)) != ep]:
        # Crossing latches every band at or below current depth for this epoch,
        # so a jump straight past 60 to 75 never warns downward next prompt.
        st["bands"] = {str(x): ep for x in BANDS if pct >= x}
        return "band"
    return None


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    prompt = (inp.get("prompt") or "").strip()
    tok, win, pct, src = L.depth(inp.get("transcript_path", ""), sid)
    whitelisted = bool(WHITELIST.match(prompt))

    act = []
    L.update_state(sid, lambda st: act.append(decide(st, tok, win, pct, src, whitelisted)))
    act = act[0] if act else None
    remaining = max(win - tok, 0)
    th = L.thresholds(win)

    if act == "hard_inferred":
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext":
                    f"[context-guard context gate] HARD threshold reached by an "
                    f"INFERRED depth: {remaining:,} tokens left of {win:,} "
                    f"({src}); a hard stop was NOT applied because the depth "
                    f"is inferred, not exact. A checkpoint has not run this "
                    f"epoch. Run the checkpoint skill now; do not start new "
                    f"work. If the real window is larger, tell the operator: "
                    f"CLAUDE_KIT_CONTEXT_WINDOW=<tokens> in the launch "
                    f"environment pins it, and the statusline plugin gives exact depth."},
            "systemMessage":
                f"Context: {remaining:,} tokens left of {win:,} ({src}) — "
                f"under the hard threshold ({th['hard']:,}); not blocked because "
                f"the depth is inferred. Checkpoint now, or pin the window with "
                f"CLAUDE_KIT_CONTEXT_WINDOW if {win:,} is wrong.",
        }))
        return
    if act == "hard":
        sys.stderr.write(
            f"[context-guard context gate] HARD STOP: {remaining:,} tokens left of "
            f"{win:,} ({src}). Your prompt was NOT processed and was erased.\n"
            f"Run /checkpoint (or /context-guard:checkpoint - both forms are "
            f"whitelisted) first, then re-send:\n"
            f"  {prompt[:200]}\n")
        sys.exit(2)
    if act == "due":
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext":
                    f"[context-guard context gate] DUE: {remaining:,} tokens left "
                    f"({src}); a checkpoint has not run this epoch. Finish the "
                    f"current thought, then run the checkpoint skill. Do not "
                    f"start new threads of work. HARD stop at {th['hard']:,} left."},
            "systemMessage":
                f"Context: {remaining:,} tokens left — checkpoint is due "
                f"(hard stop at {th['hard']:,}).",
        }))
        return
    if act == "band":
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext":
                    f"[context-guard context gate] {pct:.0f}% of the window is used "
                    f"({tok:,}/{win:,}, {src}). Prefer subagents for read-heavy "
                    f"work; keep writing findings to disk."},
            "systemMessage": f"Context {pct:.0f}% used ({remaining:,} left).",
        }))
        return
    print(json.dumps({}))

main()
