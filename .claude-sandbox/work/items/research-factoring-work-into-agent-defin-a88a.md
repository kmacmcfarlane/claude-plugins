---
id: research-factoring-work-into-agent-defin-a88a
title: "research: factoring work into agent definitions vs skills (investigate, research stages, implementation profiles)"
short_display_name: agent-definition factoring
type: spike
status: doing
priority: 0
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-29T07:05Z
created: 2026-09-29
updated: 2026-09-29
refs:
  - operator 2026-09-29
---

Operator 2026-09-29: 'this is a good point to dip more into using agent definitions instead of just skills. We should consider how that factoring works for investigations, research (at different stages and different intensity skill invocations), implementation (different agent profiles for different effort/use-case scenarios in broad strokes). Do a research spike on how that factoring should work as well, that'll be foundational to the rest of the week's progress if we can use resources more effectively.'
Acceptance: a sourced series on (1) what agent definitions can pin in Claude Code (model, effort, tools, permission mode, skills preloaded, hooks, isolation, memory) versus what a skill carries, and how each is dispatched and overridden; (2) today's kit: every dispatch site in plugins/ (investigate, implement, dev-cycle, librarian-mode, research family at each stage and intensity, checkpoint, review) with the role, model and effort it gets today; (3) a proposed factoring: a small set of agent profiles by role and effort/use case, which skills load them, the contract each agent body holds (CLAUDE.md: role, tools, model; task context via the prompt), naming, and where each lives (placement rules); (4) the quota effect, estimated from the store's dispatch lines; (5) landable features. Reconcile with 2eb7 (effort routing, in planning): 2eb7's agent names and table must fit this factoring before 2eb7 builds.

## Handoff
- doing: —
- next: planner r1 running (research lanes for web evidence); then a fresh plan review
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — research spike, plan mode (series a88a-agent-factoring); instructed to gather web evidence through dev-flow:research-lane agents (sonnet, medium) to save quota
agent: a1f0aa368080b709e (planner r1)
