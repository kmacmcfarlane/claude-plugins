---
id: research-agents-never-signal-processes-t-05bb
title: "research agents: never signal processes the agent did not start (lane and verifier contracts)"
short_display_name: research agents must not kill others
type: bug
status: doing
priority: 2
deps:
  - research-skills-effort-based-routing-par-e184
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-13T19:35Z
created: 2026-10-06
updated: 2026-10-13
refs:
  - dev-cycle-briefs-never-signal-processes-54fe
---

Noticed 2026-10-06 by the librarian from the 54fe implementer's open question: research-lane, research-lane-deep (e184) and research-verifier contracts in plugins/dev-flow/agents/ lack the never-signal-others prohibition 54fe adds to dev-cycle's briefs; they run checks/scripts in the same shared container. Acceptance: the same bullet in each research agent contract; after e184 lands (it adds research-lane-deep and edits the verifier).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-13 claimed by Kyle-McFarlane@2d49f8460283
dispatch: implementer sonnet medium — build (one rule into three agent files: canonical kind) (triage d2aa)
agent: implementer a35c15d51db64350c
return: DONE 0fe941ec; rule copied verbatim from dev-cycle agent-brief's never-send-a-signal bullet; lane item 10, verifier Rules bullet; dev-flow 78, kit-dev 21 OK
dispatch: reviewer opus high — review round 1 of 0fe941ec
agent: reviewer a4464969693f44b90
