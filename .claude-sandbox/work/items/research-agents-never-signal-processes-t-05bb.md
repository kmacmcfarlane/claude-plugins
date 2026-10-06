---
id: research-agents-never-signal-processes-t-05bb
title: "research agents: never signal processes the agent did not start (lane and verifier contracts)"
short_display_name: research agents must not kill others
type: bug
status: todo
priority: 2
deps:
  - research-skills-effort-based-routing-par-e184
created: 2026-10-06
updated: 2026-10-06
refs:
  - dev-cycle-briefs-never-signal-processes-54fe
---

Noticed 2026-10-06 by the librarian from the 54fe implementer's open question: research-lane, research-lane-deep (e184) and research-verifier contracts in plugins/dev-flow/agents/ lack the never-signal-others prohibition 54fe adds to dev-cycle's briefs; they run checks/scripts in the same shared container. Acceptance: the same bullet in each research agent contract; after e184 lands (it adds research-lane-deep and edits the verifier).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
