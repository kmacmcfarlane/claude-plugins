#!/usr/bin/env python3
"""UserPromptSubmit: depth advisories, DUE, and the HARD gate — per epoch.

Advisories (60/75% full) inform once per epoch. DUE fires when remaining
tokens drop under thresholds(window)['due'] with no checkpoint recorded this
epoch, and re-fires every 3 prompts or 25K tokens so it cannot be scrolled
past. HARD blocks the prompt itself (exit 2 — Claude Code shows stderr to the
user and ERASES the prompt) unless the prompt is /checkpoint, /compact or
/clear, in the bare or the plugin-prefixed form (/context-guard:checkpoint).
A HARD stop requires a depth source in L.BLOCKING_SOURCES: EXACT (a fresh
status-line record) or DERIVED (the window mirrored from Claude Code's own
selection logic, every input resolved; see window_rules.py). When the depth
is inferred from the transcript, or the derived window is unresolved, it is a
guess, so under `hard` the hook emits the DUE-style advisory saying a hard
stop was not applied and exits 0 (live-fired 2026-09-16: a 1M session was
blocked against a guessed 200K). The window scored is the gate window
(L.measure): the model window, lowered to a configured auto-compact window.
A hard stop is measured against `block_window` - the gate window when every
input to it resolved, else the model window - so an unresolved auto-compact
window warns but never blocks.
The first time the mirror disagrees with the status line in a session (the
Claude Code version is then distrusted: derived depth warns only), a one-line
systemMessage says so.
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


_UNSET = object()


def decide(st, tok, win, pct, src, whitelisted, block_win=_UNSET):
    """Apply one prompt's accounting to `st` (in place, under the state lock)
    and return the action: None, "hard_inferred", "hard", "due" or "band".
    block_win: the window a hard stop may be measured against (None: the
    depth may not block); by default `win` when src is a blocking source."""
    if block_win is _UNSET:
        block_win = win if src in L.BLOCKING_SOURCES else None
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
        if block_win and max(block_win - tok, 0) <= L.thresholds(block_win)["hard"]:
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
    m = L.measure(inp.get("transcript_path", ""), sid, cwd=inp.get("cwd"))
    tok, win, pct, src = m["tokens"], m["window"], m["pct"], m["source"]
    note = m["note"]
    whitelisted = bool(WHITELIST.match(prompt))
    dr = L.derived_record(m)

    act, mismatch = [], []

    def apply(st):
        act.append(decide(st, tok, win, pct, src, whitelisted, m["block_window"]))
        if dr:
            st["derived"] = dr
        wm = st.get("window_mismatch")
        if isinstance(wm, dict) and not wm.get("notified"):
            wm["notified"] = True
            mismatch.append(wm)

    L.update_state(sid, apply)
    act = act[0] if act else None
    remaining = max(win - tok, 0)
    th = L.thresholds(win)
    extra = f" [{note}]" if note else ""
    notice = ""
    if mismatch:
        wm = mismatch[0]
        notice = (f"context-guard: the context window mirror disagreed with the "
                  f"status line on Claude Code {wm.get('cc_version')} "
                  f"(derived {wm.get('derived'):,}, status line {wm.get('exact'):,}); "
                  f"derived depth is warn-only on this version until the rules "
                  f"are updated.")

    def emit(out):
        if notice:
            out["systemMessage"] = (notice + " " + out.get("systemMessage", "")).strip()
        print(json.dumps(out))

    if act == "hard_inferred":
        guess = "INFERRED" if src.startswith("inferred") else "UNRESOLVED"
        how = "inferred" if src.startswith("inferred") else "not fully resolved"
        emit({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext":
                    f"[context-guard context gate] HARD threshold reached by an "
                    f"{guess} depth: {remaining:,} tokens left of {win:,} "
                    f"({src}){extra}; a hard stop was NOT applied because the depth "
                    f"is {how}, not exact. A checkpoint has not run this "
                    f"epoch. Run the checkpoint skill now; do not start new "
                    f"work. If the real window is larger, tell the operator: "
                    f"CLAUDE_KIT_CONTEXT_WINDOW=<tokens> in the launch "
                    f"environment pins it, and the statusline plugin gives exact depth."},
            "systemMessage":
                f"Context: {remaining:,} tokens left of {win:,} ({src}) — "
                f"under the hard threshold ({th['hard']:,}); not blocked because "
                f"the depth is {how}. Checkpoint now, or pin the window with "
                f"CLAUDE_KIT_CONTEXT_WINDOW if {win:,} is wrong.",
        })
        return
    if act == "hard":
        bw = m["block_window"] or win
        sys.stderr.write(
            (notice + "\n" if notice else "") +
            f"[context-guard context gate] HARD STOP: {max(bw - tok, 0):,} tokens left of "
            f"{bw:,} ({src}){extra}. Your prompt was NOT processed and was erased.\n"
            f"Run /checkpoint (or /context-guard:checkpoint - both forms are "
            f"whitelisted) first, then re-send:\n"
            f"  {prompt[:200]}\n")
        sys.exit(2)
    if act == "due":
        emit({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext":
                    f"[context-guard context gate] DUE: {remaining:,} tokens left "
                    f"({src}){extra}; a checkpoint has not run this epoch. Finish the "
                    f"current thought, then run the checkpoint skill. Do not "
                    f"start new threads of work. HARD stop at {th['hard']:,} left."},
            "systemMessage":
                f"Context: {remaining:,} tokens left — checkpoint is due "
                f"(hard stop at {th['hard']:,}).",
        })
        return
    if act == "band":
        emit({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext":
                    f"[context-guard context gate] {pct:.0f}% of the window is used "
                    f"({tok:,}/{win:,}, {src}){extra}. Prefer subagents for read-heavy "
                    f"work; keep writing findings to disk."},
            "systemMessage": f"Context {pct:.0f}% used ({remaining:,} left).",
        })
        return
    emit({})

main()
