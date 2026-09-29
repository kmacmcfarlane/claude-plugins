---
id: model-routing-set-reasoning-effort-per-r-2eb7
title: "model routing: set reasoning effort per role, so sub-agents stop inheriting the session's xhigh"
short_display_name: sub-agent effort routing
type: feature
status: doing
priority: 0
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-29T07:00Z
created: 2026-09-29
updated: 2026-09-29
refs:
  - operator 2026-09-29
---

Operator 2026-09-29: 'all of these sub-agents are xhigh effort. It seems excessive to have the plain-names sub-agent running at xhigh effort? That seems like a model-routing failure? work-item to fix that (high priority, this will slow progress if we waste resources and run out of quota).'
Found: every librarian dispatch uses subagent_type general-purpose with only a model, so each inherits the session's effort (the operator set /effort xhigh as default this session). The dev-cycle skill's references/model-routing.md, routing's one home, never mentions effort. Agent frontmatter does support it: dev-flow's research-lane pins model sonnet, effort medium; research-verifier pins haiku, low. The Agent tool takes no effort parameter.
Acceptance: routing names an effort for every role and signal (implementer mechanical vs rule-bearing, reviewer, planner, plan reviewer, brief/render agents, second opinion) with the reason; dispatches can actually get that effort (e.g. dev-flow ships role agents with pinned model and effort, dispatched by subagent_type), with the fallback when a pinned agent is unavailable; the librarian's dispatch lines record model and effort; quota impact estimated; no role runs above high unless routing says why.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — plan mode for a routing-rule and agent-shape change (runs at the inherited session effort; nothing lower is available until this lands)
agent: aa8a6f616ed8ed9ba (planner r1)
reconcile with a88a (agent-definition factoring, operator 2026-09-29): 2eb7 builds only after its agent names and effort table fit a88a 00
