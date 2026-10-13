---
id: spend-reader-split-phases-on-each-target-7421
title: "spend reader: split phases on each target: line, not only the first budget: line per kind"
short_display_name: spend reader phase splits
type: bug
status: todo
priority: 3
created: 2026-10-05
updated: 2026-10-05
refs:
  - dev-cycle-at-the-review-cap-the-orchestr-5bdd
---

From the budget-rule build review (5bdd round 1, finding 4): item_spend.py:404-414 opens each phase at its first budget: line and assigns a segment to the latest-opened phase. A re-plan after a build puts the new plan spend into build; a same-phase pair with a different mode or ref (review <branch> after full; a plan by slug after one by item id) resets the rule's amount and round count but the reader keeps the earlier run's spend (fail-safe: asks early). The budget rule names these as one phase per kind per record for now. Acceptance: phases follow target:/budget: pairs as dev-cycle's bindings.md § Spend budget defines them, with tests for both cases.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
