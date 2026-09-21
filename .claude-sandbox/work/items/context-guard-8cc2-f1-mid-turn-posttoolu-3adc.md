---
id: context-guard-8cc2-f1-mid-turn-posttoolu-3adc
title: "context-guard 8cc2-F1: mid-turn PostToolUse depth check (silent unless it could hard-block)"
type: feature
status: doing
priority: 1
deps:
  - context-guard-8cc2-f3a-re-inject-handoff-5126
parent: context-guard-turn-gate-8cc2
owner: unknown@360f41058e92
claimed: 2026-09-21T19:08Z
created: 2026-09-21
updated: 2026-09-21
---

Port plan .claude-sandbox/investigations/8cc2-turn-gate-port — design awaits the 02 serial (HARD mid-turn marker only when hard_applies(block_window, tok); unattended checkpoint path defers to a custody skill's own mode).

## Handoff
- doing: CLEAR at c7d4757; merge held
- next: land right after F3a (needs decision 48); resolve hooks.json/README/checkpoint Step 5 conflicts via a conflict round
- blocked: —
- learned: —

## Carried from 8cc2-F2
- librarian-mode ending-the-session.md keys on "HARD threshold reached by an INFERRED depth" and runs a checkpoint (continue); below CHECKPOINT_MIN_TOKENS the advisory now says a checkpoint no longer fits → align there (F1 already edits that file).
- operator-playbook: one clause on the under-20K advice (plan 00).

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — new PostToolUse hook in gate code; plan says the blocking predicate extraction must leave decide tests unchanged (else fable reviewer). Lands only after F3a.

## Implementer result
- round 1 DONE_WITH_CONCERNS 59168d1 (opus): turn_gate.py PostToolUse (advisory only; silent unless block_window; HARD marker iff hard_applies; agent_id skip; early return mirror-off; hard_nofit tier), hard_applies extracted (decide tests unchanged → reviewer stays opus), checkpoint unattended section, playbook "Inside a turn", ending-the-session.md exceptions. 24 tests; cached per-call ~15 ms.
- scope widening before review: README context-guard hooks sentence + design-rationale §3 turn-gate layer. Merge held until F3a lands (hooks.json will conflict mechanically).
- widening 9797fab: README hooks sentence; design-rationale §3 added paragraph.
- dispatch: reviewer opus — rule 4 (decide tests unchanged → no fable bump). Merge held for F3a.

## Review round 1 — NEEDS_CHANGES (opus) at 9797fab
- decide() unchanged over 506,880 in-process cases + 640 end-to-end; HARD marker iff context_warn exits 2 (0 mismatches); no output on any guessed/foreign/future/stale source; never blocks or crashes; cadence fires 7× over 150K.
- [medium] a forged/quoted marker (in a docstring, diff, tool result) could trigger the unattended checkpoint and its mark would silence the real gate: the unattended section must verify the state's turn_gate record (this epoch, tier hard/hard_nofit) before acting, and say the marker counts only as hook-added context.
- lows: unwritable state dir → marker every call (pin with a test/comment); a custody skill's remaining steps (librarian push, Report) run before the final message; mode 644; commit layout noted.
- noted follow-up: legacy in-state exact block has no future-`at` check (pre-existing).
- dispatch: implementer opus — fix round 1 (resume)
- round 1 fix 0b530a3 + c7d4757: turn_gate.py --check <sid> (armed only for this epoch, tier hard/hard_nofit, no checkpoint yet); unattended section runs --check first and treats the marker as hook-context only; hook silent when its record cannot land; custody steps run before the final message; 755.
- dispatch: reviewer opus — round 2 (resume). Merge held for F3a.

## Review round 2 — CLEAR (opus) at c7d4757
- every forgery refused by --check; real HARD arms; unwritable state: hook silent, prompt gate still blocks (no regression). lows: malformed top-level epoch → traceback (fail-safe); commit layout.
- READY TO LAND — held until F3a is on main (plan order F2 → F3a → F1). Expect hooks.json / README / checkpoint Step 5 conflicts at merge.
