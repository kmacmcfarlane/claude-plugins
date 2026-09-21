---
id: wi-grooming-status-and-a-needs-input-lis-b020
title: "wi: grooming status and a needs-input listing"
type: feature
status: done
priority: 1
deps:
  - work-items-first-class-parked-status-wi-ca20
created: 2026-09-20
updated: 2026-09-21
closed: 2026-09-21
refs:
  - operator 2026-09-20
---

Operator 2026-09-20: an item with open questions should sit in a 'grooming' status with the questions recorded in the item, and wi should list what needs operator input. Acceptance: status 'grooming' valid in lint, set with a reason/questions (like block/park); grooming items are NOT in the ready queue; 'wi needs-input' (or ls --needs-input) lists every item awaiting the operator - grooming items, and any item whose body carries an unanswered 'decision N:' line; prime shows a grooming count beside blocked/parked; format.md and SKILL.md table updated; the decision-N convention (librarian-mode Report) is the canonical marker for an unanswered question, so document it in references/format.md. Sits beside ca20 (parked); same lint/table surface.

## Handoff
- doing: implementer dispatched (opus, agent a9aead350ab6aa1df)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Carried from 693a
- adopt `answer N:` (librarian-mode Report) as the canonical reply marker for needs-input; add `wi ls --dep <id>` (items depending on an id) and a HOLD line in prime for hold-tagged items.

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — executable logic (wi.py) + format doctrine
- 2026-09-21 done: 750a2a1

## Implementer result
- round 1 DONE 55249bb (opus): grooming status + groom/ungroom, needs-input (decision N without answer N, line-start only, fences ignored; includes parked), ls --dep, prime GROOMING count + HOLD line; backlog-yaml bridge maps GROOMING both ways. Deviations: default ls includes grooming; groom supersedes park and keeps a blocked reason. 146 tests; TestGrooming fails 17 without the change.
- open: librarian-mode idle-turn.md still greps for decisions → follow-up item filed.
- dispatch: reviewer opus — rule 4

## Review round 1 — CLEAR (opus) at 55249bb
- deviations judged sound. Lows (not fixed; carried to follow-up): lint hint grooming+stray parked; duplicate decision N keeps first text; no decision 4 / answer 40 test; ls --dep swallows ambiguity; SKILL.md lacks HOLD mention. Inherited (park too): U+2028 breaks export YAML; '; requires ext:' suffix grows in blocked reason over export/import.
- landed 750a2a1
