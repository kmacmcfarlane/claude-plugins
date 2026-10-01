---
id: dev-cycle-at-the-review-cap-the-orchestr-5bdd
title: "dev-cycle: at the review cap, the orchestrator finishes trivial leftover fixes by default instead of raising a decision"
short_display_name: finish trivial fixes at the cap
type: feature
status: todo
priority: 1
deps:
  - review-caps-and-spend-plans-raise-only-o-5579
created: 2026-10-01
updated: 2026-10-01
refs:
  - operator 2026-10-01, answer 137
---

Operator 2026-10-01 on decision 137, verbatim: 'I think the orchestrator should just finish trivial changes when the cap is reached. Make a work-item to make that the default behavior'. Acceptance: when a review hits the round cap and every leftover finding is trivial (to be defined: e.g. one-sentence or one-line fixes the reviewer states exactly, no design choice), the orchestrator (librarian or standalone dev-cycle) finishes them without a cap decision — whether by one more implementer round or its own edit is a plan question, as is the trivial test and the review it gets afterwards; non-trivial leftovers still raise the cap decision. Depends on review caps and spend (5579), which rewrites the same cap rules. Authority: answer 137 (rule-change, operator-requested).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
