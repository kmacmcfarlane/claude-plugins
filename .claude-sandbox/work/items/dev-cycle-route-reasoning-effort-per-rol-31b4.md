---
id: dev-cycle-route-reasoning-effort-per-rol-31b4
title: "dev-cycle: route reasoning effort per role, not only model (agent definitions with effort pins)"
type: feature
status: dropped
priority: 2
created: 2026-09-23
updated: 2026-09-29
closed: 2026-09-29
refs:
  - operator 2026-09-23 (7113 planning)
---

Operator 2026-09-23 asked whether the planner runs at xhigh effort, and wants the right effort chosen for the implementer. Gap: dev-cycle's Step 2 routes only the model. The Agent tool takes no per-call effort, which comes only from an agent definition's frontmatter (the research-lane agent pins medium, research-verifier low); dispatched implementers and reviewers are general-purpose, so their effort is whatever the default is, and a fork inherits the session's. Acceptance: dev-cycle states an effort per role (planner, implementer, reviewer, fixer), and dev-flow ships agent definitions that pin it (or the routing reference says how to get it), with the model-routing table updated.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
closed 2026-09-29 as a duplicate of model-routing-set-reasoning-effort-per-r-2eb7 (same ask, operator 2026-09-29; found by 2eb7 plan review r1); its acceptance is covered by 2eb7 F1/F2

## Notes
- 2026-09-29 dropped
