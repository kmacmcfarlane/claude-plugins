#!/usr/bin/env python3
"""UserPromptSubmit: depth advisories, DUE, and the HARD gate — per epoch.

Advisories (60/75% full) inform once per epoch. DUE fires when remaining
tokens drop under thresholds(window)['due'] with no checkpoint recorded this
epoch, and re-fires every 3 prompts or 25K tokens so it cannot be scrolled
past. HARD blocks the prompt itself (exit 2 — Claude Code shows stderr to the
user and ERASES the prompt) unless the prompt is /checkpoint, /compact or
/clear, in the bare or the plugin-prefixed form (/claude-kit:checkpoint).
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
# /checkpoint, /compact, /clear - bare or plugin-qualified (/claude-kit:checkpoint).
WHITELIST = re.compile(r"^/(?:[\w-]+:)?(?:checkpoint|compact|clear)(?=\s|$)")


def due_fires(st, tok):
    """DUE cadence: first time, then every DUE_EVERY_PROMPTS or DUE_EVERY_TOKENS."""
    due = st.get("due") or {}
    return (not due
            or st["prompt_n"] - due.get("prompt_n", 0) >= DUE_EVERY_PROMPTS
            or tok - due.get("tok", 0) >= DUE_EVERY_TOKENS)


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    prompt = (inp.get("prompt") or "").strip()
    tok, win, pct, src = L.depth(inp.get("transcript_path", ""), sid)

    st = L.load_state(sid)
    ep = L.epoch(st)
    st["prompt_n"] = int(st.get("prompt_n", 0)) + 1
    st.update(tokens=tok, pct=round(pct, 1), window=win)

    if not tok:
        L.save_state(sid, st); print(json.dumps({})); return

    remaining = max(win - tok, 0)
    th = L.thresholds(win)
    done = L.checkpointed_this_epoch(st)
    whitelisted = bool(WHITELIST.match(prompt))

    if done:
        # A checkpoint this epoch stands the whole gate down - DUE, HARD and
        # the advisories. The operator has already acted on the depth.
        L.save_state(sid, st)
        print(json.dumps({}))
        return

    if remaining <= th["hard"] and not done and not whitelisted:
        L.save_state(sid, st)
        if src != "exact":
            # A guess never blocks: the window may be larger than inferred.
            # Same cadence as DUE so a long stretch under a guessed 200K
            # window does not nag on every prompt.
            if not due_fires(st, tok):
                print(json.dumps({})); return
            st["due"] = {"prompt_n": st["prompt_n"], "tok": tok}
            L.save_state(sid, st)
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext":
                        f"[claude-kit context gate] HARD threshold reached by an "
                        f"INFERRED depth: {remaining:,} tokens left of {win:,} "
                        f"({src}); a hard stop was NOT applied because the depth "
                        f"is inferred, not exact. A checkpoint has not run this "
                        f"epoch. Run the checkpoint skill now; do not start new "
                        f"work. If the real window is larger, tell the operator: "
                        f"CLAUDE_KIT_CONTEXT_WINDOW=<tokens> in the launch "
                        f"environment pins it, and the status line gives exact depth."},
                "systemMessage":
                    f"Context: {remaining:,} tokens left of {win:,} ({src}) — "
                    f"under the hard threshold ({th['hard']:,}); not blocked because "
                    f"the depth is inferred. Checkpoint now, or pin the window with "
                    f"CLAUDE_KIT_CONTEXT_WINDOW if {win:,} is wrong.",
            }))
            return
        sys.stderr.write(
            f"[claude-kit context gate] HARD STOP: {remaining:,} tokens left of "
            f"{win:,} ({src}). Your prompt was NOT processed and was erased.\n"
            f"Run /checkpoint (or /claude-kit:checkpoint - both forms are "
            f"whitelisted) first, then re-send:\n"
            f"  {prompt[:200]}\n")
        sys.exit(2)

    if remaining <= th["due"] and not done:
        if due_fires(st, tok):
            st["due"] = {"prompt_n": st["prompt_n"], "tok": tok}
            L.save_state(sid, st)
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext":
                        f"[claude-kit context gate] DUE: {remaining:,} tokens left "
                        f"({src}); a checkpoint has not run this epoch. Finish the "
                        f"current thought, then run the checkpoint skill. Do not "
                        f"start new threads of work. HARD stop at {th['hard']:,} left."},
                "systemMessage":
                    f"Context: {remaining:,} tokens left — checkpoint is due "
                    f"(hard stop at {th['hard']:,}).",
            }))
            return
        L.save_state(sid, st)
        print(json.dumps({})); return

    bands = st.get("bands") or {}
    unfired = [b for b in BANDS if pct >= b and bands.get(str(b)) != ep]
    if unfired:
        # Crossing latches every band at or below current depth for this epoch,
        # so a jump straight past 60 to 75 never warns downward next prompt.
        st["bands"] = {str(x): ep for x in BANDS if pct >= x}
        L.save_state(sid, st)
        if True:
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext":
                        f"[claude-kit context gate] {pct:.0f}% of the window is used "
                        f"({tok:,}/{win:,}, {src}). Prefer subagents for read-heavy "
                        f"work; keep writing findings to disk."},
                "systemMessage": f"Context {pct:.0f}% used ({remaining:,} left).",
            }))
            return
    L.save_state(sid, st)
    print(json.dumps({}))


main()
