#!/usr/bin/env python3
"""PostToolUse (every tool): the mid-turn depth check. Advisory only.

The prompt gate (context_warn.py) and the Stop relay see only turn
boundaries. An unattended turn has none: a 53-minute tool loop filled a 1M
window from 860K to 999K with nothing able to speak to the model (live-fired
2026-09-02). This hook is the sensor inside the turn. It never blocks: its
only output is `additionalContext`, never `decision: "block"`.

It is SILENT unless the depth could hard-block at the prompt gate - its
source is in L.BLOCKING_SOURCES (exact, or derived with every input
resolved), so measure() set `block_window`. An inferred depth, an
unresolved or distrusted derived one, is a guess, and the prompt gate
already warns on a guess at the next turn boundary; mid-turn text built on
one could only end an unattended turn early (live-fired 2026-09-16: a 1M
session scored against a guessed 200K).

On a blocking source:
- HARD - printed if and only if L.hard_applies(block_window, tokens), the
  prompt gate's own blocking rule. The body opens with the marker
  "[context-guard context gate] HARD, mid-turn (<source>):", the only text
  the checkpoint skill's unattended section runs on. It says start nothing
  new and checkpoint now in mode `handoff` (a custody skill in charge keeps
  its own mode); under L.CHECKPOINT_MIN_TOKENS left it says a checkpoint no
  longer fits: end the turn with a three-line brief.
- DUE - under the gate window's due line, and not HARD (which covers an
  exact source under an unresolved auto-compact window's hard line: the
  hard stop is measured against the model window there). It says finish the
  step in hand, open no new threads, checkpoint at the turn's natural end.
  Its body carries "DUE: <n> tokens left", as librarian-mode keys on.

Each tier fires on the first crossing in an epoch, on a tier change, and
again after DUE_EVERY_TOKENS of growth; a checkpoint this epoch stands it
down. Skipped on `agent_id` only (a subagent's tool call: its depth is not
this window's); `agent_type` alone is the main thread of an --agent session.

Cost: with the mirror off (CONTEXT_GUARD_DERIVE=off or a window pin) and no
fresh exact record, nothing could be said, so it returns before any
transcript read. Otherwise measure() resumes the transcript scan from the
cache this hook saves (with the sidechain cache and the derived record) in
its one locked state write. Any error prints {}.

A message fires only when its `turn_gate` record ({epoch, tier, tok}) is
read back from the state file after the write. Unwritable state (a
read-only or full config dir) therefore makes the hook silent rather than
repeat the marker on every tool call with no cadence and no record - and
the record is what `--check` needs.

Verification, for the checkpoint skill's unattended section (the marker
text also sits in this file, its tests, the docs and any diff of them, so
text alone proves nothing):
    python3 turn_gate.py --check <session_id>
exits 0 and prints "armed: ..." only when the state's `turn_gate` record is
this epoch's (`epoch`), its `tier` is hard or hard_nofit, and no checkpoint
has run this epoch (`checkpoint_epoch`); otherwise exit 1, "not armed: ...".
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L
import context_warn as CW

DUE_EVERY_TOKENS = CW.DUE_EVERY_TOKENS
MARKER = "[context-guard context gate] HARD, mid-turn"


def tier_of(m):
    """None (silent), "due", "hard" or "hard_nofit" for measure()'s `m`."""
    tok, bw = m["tokens"], m.get("block_window")
    if not tok or not bw or m["source"] not in L.BLOCKING_SOURCES:
        return None
    if L.hard_applies(bw, tok):
        return "hard" if bw - tok >= L.CHECKPOINT_MIN_TOKENS else "hard_nofit"
    if max(m["window"] - tok, 0) <= L.thresholds(m["window"])["due"]:
        return "due"
    return None


def text(tier, m):
    tok, win, src = m["tokens"], m["window"], m["source"]
    extra = f" [{m['note']}]" if m.get("note") else ""
    if tier == "due":
        remaining = max(win - tok, 0)
        hard = L.thresholds(m["block_window"])["hard"]
        return (f"[context-guard context gate] DUE: {remaining:,} tokens left of "
                f"{win:,} ({src}), mid-turn{extra}; a checkpoint has not run this "
                f"epoch. Finish the step in hand and open no new threads of work. "
                f"Run the checkpoint skill when the turn reaches its natural end. "
                f"The hard line is {hard:,} left of {m['block_window']:,}.")
    bw = m["block_window"]
    left = max(bw - tok, 0)
    head = f"{MARKER} ({src}): {left:,} tokens left of {bw:,}{extra}. Start nothing new. "
    if tier == "hard":
        return head + ("Run the checkpoint skill now, in mode `handoff` unless a skill "
                       "in charge of this session names its own mode, then make its "
                       "brief your final message and end the turn.")
    return head + (f"{CW.no_fit(left)}, so do not start one. End the turn now with a "
                   f"three-line brief as your final message (what is in flight, what "
                   f"was decided or refused, the one next action) and tell the "
                   f"operator to run {CW.REMEDY}.")


HARD_TIERS = ("hard", "hard_nofit")


def armed(st):
    """(True, why) when state `st` shows this epoch's mid-turn HARD fired
    and no checkpoint has run since; else (False, why)."""
    tg = st.get("turn_gate")
    if not isinstance(tg, dict):
        return False, "no mid-turn gate record in the state"
    if L.checkpointed_this_epoch(st):
        return False, "a checkpoint already ran this epoch"
    if tg.get("epoch") != L.epoch(st):
        return False, "the mid-turn gate record is from an earlier epoch"
    if tg.get("tier") not in HARD_TIERS:
        return False, f"the mid-turn gate last fired at tier {tg.get('tier')!r}, not HARD"
    return True, f"{tg['tier']} at {tg.get('tok')} tokens, epoch {tg['epoch']}"


def check(argv):
    if len(argv) != 1:
        print("usage: turn_gate.py --check <session_id>"); return 2
    ok, why = armed(L.load_state(argv[0]))
    print(("armed: " if ok else "not armed: ") + why)
    return 0 if ok else 1


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return
    if not isinstance(inp, dict) or inp.get("agent_id"):
        print(json.dumps({})); return
    sid = inp.get("session_id") or "unknown"
    st = L.load_state(sid)
    if L.checkpointed_this_epoch(st):
        print(json.dumps({})); return
    if L.mirror_off() and not L.exact_fresh(L.sensor(sid, st)):
        # The depth would be inferred: nothing to say, so read nothing.
        print(json.dumps({})); return

    m = L.measure(inp.get("transcript_path", ""), sid, cwd=inp.get("cwd"))
    tier = tier_of(m)
    dr = L.derived_record(m)
    fire, rec = [], []

    def apply(s):
        if dr:
            s["derived"] = dr
        if m.get("scan_cache"):
            s["scan"] = m["scan_cache"]
        if m.get("side_cache"):
            s["sidechains"] = m["side_cache"]
        if tier is None or L.checkpointed_this_epoch(s):
            return
        ep = L.epoch(s)
        last = s.get("turn_gate") if isinstance(s.get("turn_gate"), dict) else {}
        try:
            grown = m["tokens"] - int(last.get("tok", 0)) >= DUE_EVERY_TOKENS
        except (TypeError, ValueError):
            grown = True
        if last.get("epoch") != ep or last.get("tier") != tier or grown:
            s["turn_gate"] = {"epoch": ep, "tier": tier, "tok": m["tokens"]}
            fire.append(tier)
            rec.append(dict(s["turn_gate"]))

    if tier is not None or dr or m.get("scan_cache") or m.get("side_cache"):
        L.update_state(sid, apply)
    if not fire or L.load_state(sid).get("turn_gate") != rec[0]:
        # Nothing to say, or the record did not land (unwritable state):
        # silent, never a marker that --check cannot confirm.
        print(json.dumps({})); return
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": text(fire[0], m)}}))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--check"]:
        sys.exit(check(sys.argv[2:]))
    try:
        main()
    except Exception:
        print(json.dumps({}))
