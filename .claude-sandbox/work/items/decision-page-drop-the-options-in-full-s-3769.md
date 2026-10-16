---
id: decision-page-drop-the-options-in-full-s-3769
title: "decision-page: drop the Options in full section; hide empty or none sub-sections"
short_display_name: drop full options, hide empty parts
type: feature
status: done
priority: 1
deps:
  - decision-page-progress-bar-sticks-to-the-6d12
created: 2026-10-14
updated: 2026-10-16
closed: 2026-10-16
refs:
  - operator message 2026-10-14
---

Operator 2026-10-14: the 'Options in full' section repeats the inline detail each option already shows, so remove it; any sub-section that is empty or none is not displayed (e.g. Dependencies on a card with none, an Impact cost of none). Acceptance: template renders neither; schema/digest/tests updated; serial after 6d12 (same template).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree off main (352641d7); decision-page template, schema, digest, tests
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — drop Options in full; hide empty or none sub-sections
agent: implementer adb2d16ec86cbf0f8 round 1
result: DONE round 1 at d7e0f453 (Options in full removed, its data in each option's More; one isNone helper hides empty or none parts; four required Impact facets, basis and the rec line's unknown kept; test_none.py; 155 OK)
dispatch: reviewer opus high — fresh (rule 4)
agent: reviewer aea9ab2a707188486 round 1 at d7e0f453
verdict: NEEDS_CHANGES round 1 at d7e0f453 (1 high: a ⚠ option's blocks Undo of 'None.' is hidden; 1 medium: the check passes a blank ⚠ Undo; 2 low: Undo sits low in an open ⚠ More, (z) Wait wording; nit: 'nothing' in the none list)
dispatch: implementer opus medium — resume, fix round 1
agent: implementer adb2d16ec86cbf0f8 round 2
result: DONE round 2 at 5efec89e (Undo always shown; ⚠ rows non-empty; ⚠ More leads with the row; (z) wording; 'nothing' out; 158 OK)
dispatch: reviewer opus high — resume, round 2
agent: reviewer aea9ab2a707188486 round 2 at 5efec89e
verdict: CLEAR round 2 at 5efec89e (nit: cards-schema.md:172 More order lacks the ⚠ exception; declined for now, line 83 states it — folded into aa4e's merge, which edits the same file)
landed: merged 3d93bf47, on origin; closed 2026-10-16 (store drift found by 0a0e's plan: merged and pushed, never closed)

## Notes
- 2026-10-16 done
