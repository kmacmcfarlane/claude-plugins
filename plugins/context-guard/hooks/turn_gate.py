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

A checkpoint UNDERWAY stands it down too. `checkpointed_this_epoch` only
turns true at the mark (Step 4b), and a checkpoint spends tokens before it
gets there - enough to flip hard to hard_nofit, whose text says to abandon
the checkpoint and end the turn. So the skill writes `checkpoint_started` =
{epoch, at, tok}:
    python3 turn_gate.py --checkpointing <session_id>
and the mark clears it (L.mark_checkpoint). While it stands, this hook says
nothing and `--check` reports it - LAST, after the record's own epoch and
tier tests, so this one command cannot dress a forged or stale marker up as
a checkpoint in progress. It refuses an id with no state file, as
mark_checkpoint.py does: a live session always has one, so a missing file is
a typo, and writing one would stand a phantom session's gate down while the
real session stayed armed.

It lapses on either clock: CHECKPOINT_GRACE_S of wall time, or
L.CHECKPOINT_MIN_TOKENS of growth past the depth it started at (callers that
have measured one pass `tok`). The wall clock alone was not enough - a
stand-down starts at the hard line, where 30 minutes of unconditional
silence can spend what is left of the window, and past that much growth the
checkpoint it was protecting no longer fits anyway. A stamp from the future
(a clock change) does not count either.

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
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L
import context_warn as CW

DUE_EVERY_TOKENS = CW.DUE_EVERY_TOKENS
MARKER = "[context-guard context gate] HARD, mid-turn"
# How long a `--checkpointing` stand-down holds without reaching its mark.
# Long enough for the slowest checkpoint (Step 4's flush can commit several
# repos), short enough that an abandoned one does not silence the rest of
# the epoch.
CHECKPOINT_GRACE_S = 30 * 60


def checkpoint_in_flight(st, now=None, tok=None):
    """True while a checkpoint started this epoch has not reached its mark.
    A record from another epoch, a malformed one, one stamped in the future,
    and one that has lapsed all read as False: the gate speaks by default.

    It lapses two ways. The wall clock caps how long one stand-down can last
    (CHECKPOINT_GRACE_S), and `tok` - the depth now, when the caller has
    measured one - caps how much window it may cost: a stand-down starts at
    the hard line, so 30 minutes of unconditional silence there can spend the
    last of the window. Past CHECKPOINT_MIN_TOKENS of growth the checkpoint
    it was protecting no longer fits anyway, so the gate speaks again."""
    cs = st.get("checkpoint_started")
    if not isinstance(cs, dict):
        return False
    try:
        if cs.get("epoch") != L.epoch(st):
            return False
        since = (time.time() if now is None else now) - float(cs.get("at"))
    except (TypeError, ValueError):
        return False
    if not 0 <= since <= CHECKPOINT_GRACE_S:
        return False
    try:
        if tok is not None and cs.get("tok") is not None:
            return int(tok) - int(cs["tok"]) <= L.CHECKPOINT_MIN_TOKENS
    except (TypeError, ValueError):
        return True     # an unreadable depth is no reason to start speaking
    return True


def depth_now(sid, st):
    """The best depth available without reading the transcript: a fresh exact
    record, else the last depth the prompt gate scored. None when neither is
    there - the token lapse then simply does not apply."""
    try:
        ex = L.sensor(sid, st) or {}
        if L.exact_fresh(ex) and ex.get("tokens"):
            return int(ex["tokens"])
        return int(st.get("tokens") or 0) or None
    except (TypeError, ValueError, AttributeError):
        return None


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
    """(True, why) when state `st` shows this epoch's mid-turn HARD fired,
    no checkpoint has run since and none is underway; else (False, why).
    An unreadable state is never armed: it answers, it does not raise, so a
    hand-edited or half-written file cannot turn `--check` into a traceback
    the caller has to interpret."""
    tg = st.get("turn_gate")
    if not isinstance(tg, dict):
        return False, "no mid-turn gate record in the state"
    try:
        ep = L.epoch(st)
    except (TypeError, ValueError):
        return False, "the gate state is unreadable: its epoch is not a number"
    if L.checkpointed_this_epoch(st):
        return False, "a checkpoint already ran this epoch"
    # The record's own tests come FIRST. `checkpoint_started` is written by
    # whoever runs --checkpointing, so testing it earlier would let that one
    # command turn every real not-armed reason - a forged marker, an earlier
    # epoch, a DUE tier - into "a checkpoint is already underway", whose
    # documented answer is to carry on checkpointing. It is the last test, so
    # it can only ever soften an otherwise ARMED answer.
    if tg.get("epoch") != ep:
        return False, "the mid-turn gate record is from an earlier epoch"
    if tg.get("tier") not in HARD_TIERS:
        return False, f"the mid-turn gate last fired at tier {tg.get('tier')!r}, not HARD"
    if checkpoint_in_flight(st):
        return False, ("a checkpoint is already underway; finish it through "
                       "Step 4b and the mark")
    return True, f"{tg['tier']} at {tg.get('tok')} tokens, epoch {tg['epoch']}"


def check(argv):
    if len(argv) != 1:
        print("usage: turn_gate.py --check <session_id>"); return 2
    ok, why = armed(L.load_state(argv[0]))
    print(("armed: " if ok else "not armed: ") + why)
    return 0 if ok else 1


def checkpointing(argv):
    """Stand the gate down for the checkpoint about to run."""
    if len(argv) != 1:
        print("usage: turn_gate.py --checkpointing <session_id>"); return 2
    sid = argv[0]
    if not os.path.exists(L.state_path(sid)):
        # A live session always has state (every prompt's gate hook writes
        # it), so a missing file is a mistyped id. Writing one would create a
        # phantom session - standing ITS gate down while the real session
        # stays armed - and would also defeat mark_checkpoint.py's refusal on
        # the same id, which exists for exactly that reason.
        print(f"turn_gate.py: no context-gate state for session {sid!r} "
              f"(expected {L.state_path(sid)}); check the session id - "
              f"nothing written, the gate is NOT stood down.")
        return 1
    why = None
    try:
        L.update_state(sid, lambda s: s.__setitem__(
            "checkpoint_started", {"epoch": L.epoch(s), "at": time.time(),
                                   "tok": depth_now(sid, s)}))
    except (TypeError, ValueError):
        why = ("the state's `epoch` is not a number, so the record has no "
               "epoch to sit in")
    except Exception:
        why = "the state could not be written"
    if checkpoint_in_flight(L.load_state(sid)):
        print(f"mid-turn gate stood down for this checkpoint (until the mark, "
              f"or {CHECKPOINT_GRACE_S // 60} min, or "
              f"{L.CHECKPOINT_MIN_TOKENS:,} more tokens)")
    else:
        print(f"mid-turn gate not stood down: {why or 'the record did not land'}. "
              f"Carry on with the checkpoint; if a `HARD, mid-turn` marker "
              f"arrives, it is not a second checkpoint to start.")
    return 0


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return
    if not isinstance(inp, dict) or inp.get("agent_id"):
        print(json.dumps({})); return
    sid = inp.get("session_id") or "unknown"
    st = L.load_state(sid)
    if (L.checkpointed_this_epoch(st)
            or checkpoint_in_flight(st, tok=depth_now(sid, st))):
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
        if (tier is None or L.checkpointed_this_epoch(s)
                or checkpoint_in_flight(s, tok=m["tokens"])):
            # Re-read under the lock: a checkpoint may have started, or
            # reached its mark, since the measurement above.
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
    if sys.argv[1:2] == ["--checkpointing"]:
        sys.exit(checkpointing(sys.argv[2:]))
    try:
        main()
    except Exception:
        print(json.dumps({}))
