---
id: context-guard-legacy-in-state-exact-bloc-73a6
title: "context-guard: legacy in-state exact block lacks the future-at check"
type: bug
status: doing
priority: 3
owner: unknown@360f41058e92
claimed: 2026-09-21T23:07Z
created: 2026-09-21
updated: 2026-09-21
---

From the 8cc2-F1 review (pre-existing): only the sensor file's exact block is rejected when its at is in the future (lib_context._sensor_exact); a clock-skewed legacy in-state exact block from the deprecated statusline copy counts as fresh for the prompt gate's block and the turn gate. Acceptance: the same future-skew rule for both sources; a test.

## Handoff
- doing: review r1 dispatched (opus)
- next: CLEAR → land after cf95 (statusline suite path artifact)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — executable logic (gate hook)

## Implementer result
- round 1 DONE_WITH_CONCERNS 0a070b6 (opus): shared _future_skewed(at) in lib_context; sensor() drops a skewed or non-finite legacy block before choosing; tests via real hooks (context_warn, precompact_gate, stop_relay) + unit; fail 7 without. Concern: statusline test_session_start_never_leaks fails in any checkout path containing 'context-guard' (worktree path artifact) → filed separately.
- dispatch: reviewer opus — rule 4
