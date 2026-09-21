---
id: wi-grooming-status-and-a-needs-input-lis-b020
title: "wi: grooming status and a needs-input listing"
type: feature
status: todo
priority: 1
deps:
  - work-items-first-class-parked-status-wi-ca20
created: 2026-09-20
updated: 2026-09-20
refs:
  - operator 2026-09-20
---

Operator 2026-09-20: an item with open questions should sit in a 'grooming' status with the questions recorded in the item, and wi should list what needs operator input. Acceptance: status 'grooming' valid in lint, set with a reason/questions (like block/park); grooming items are NOT in the ready queue; 'wi needs-input' (or ls --needs-input) lists every item awaiting the operator - grooming items, and any item whose body carries an unanswered 'decision N:' line; prime shows a grooming count beside blocked/parked; format.md and SKILL.md table updated; the decision-N convention (librarian-mode Report) is the canonical marker for an unanswered question, so document it in references/format.md. Sits beside ca20 (parked); same lint/table surface.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
