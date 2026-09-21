---
id: context-guard-8cc2-f2-hard-advice-fits-t-1f9d
title: "context-guard 8cc2-F2: HARD advice fits the space left (CHECKPOINT_MIN_TOKENS)"
type: feature
status: done
priority: 1
parent: context-guard-turn-gate-8cc2
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
---

Port plan .claude-sandbox/investigations/8cc2-turn-gate-port (00 + 01; plan review round 2 cleared F2 to go). context_warn advises /clear or /compact instead of /checkpoint when too little is left to afford a checkpoint; CHECKPOINT_MIN_TOKENS in lib_context derived from the thresholds() docstring (lib_context.py ~520, lean-path floor ~16K + margin); measured against block_window; also the inferred-not-blocked message. Verify whether /compact still works at ~1K left (plan OQ3) or keep /clear first.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: 747af46

## Dispatch
- dispatch: implementer opus — executable logic in a gating hook (advice text only; the blocking predicate is untouched) — fable signal not met

## Implementer result
- round 1 DONE_WITH_CONCERNS 0c89988 (opus): CHECKPOINT_MIN_TOKENS = 16K lean cost + 4K margin (traced to thresholds() docstring); fit_left/no_fit/COMPACT_GUIDANCE in context_warn; advice below 20K: /clear first, /compact <guidance> second (binary read suggests /compact retries on prompt-too-long, not verified live). decide() unchanged; existing tests unedited.
- follow-ups to F1: ending-the-session.md still runs a checkpoint on the inferred-HARD advisory even when it now says a checkpoint no longer fits; operator-playbook clause for the under-20K advice.
- dispatch: reviewer opus — rule 4 (gate code; blocking predicate untouched)

## Review round 1 — NEEDS_CHANGES (opus) at 0c89988
- blocking decision byte-identical; 1,152-case matrix base vs head: 0 exit-code differences.
- [medium] operator-playbook clause for the under-20K advice missing (planned in F2). lows: "guidance is all that survives" overstates; model-facing text should put "end the turn and tell the operator" first.
- dispatch: implementer opus — fix round 1 (resume)
- round 1 fix 7604b35: playbook clause; REMEDY wording (guidance steers what the summary keeps); model told to end the turn and tell the operator.
- dispatch: reviewer opus — round 2 (resume)

## Review round 2 — CLEAR (opus) at 7604b35
- full 1,152-case matrix re-run: blocking decision unchanged.
## Landed
- 747af46. 1 fix round.
