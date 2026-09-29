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
- next: planner r1 running; plan review; build only after a88a 00 reconciles the agent names
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — plan mode for a routing-rule and agent-shape change (runs at the inherited session effort; nothing lower is available until this lands)
agent: aa8a6f616ed8ed9ba (planner r1)
reconcile with a88a (agent-definition factoring, operator 2026-09-29): 2eb7 builds only after its agent names and effort table fit a88a 00
series 00 written: general-purpose sub-agents follow the session effort live; frontmatter effort overrides it; CLAUDE_CODE_EFFORT_LEVEL overrides frontmatter; no per-call effort, no default-subagent-effort setting (maxEffortLevel only caps); the shared host settings.json now saves xhigh for Opus 5.5 (the operator's /effort xhigh, saved as default); proposal: four dev-flow agents (implementer sonnet medium, planner opus high, reviewer opus high, scribe sonnet low), model override per call for tier bumps, fallback general-purpose recorded as inherit; dispatch line gains effort; estimate: -45-56% sub-agent output vs xhigh; three operator questions (reviewers at high; four role agents; per-item effort pin)
librarian ruling: hold the plan review until a88a 00 lands; the planner then reconciles names and table with a88a in serial 01, and one review covers both (saves a review round)
operator 2026-09-29 on the plan: "I like your plan's proposal, but I think there does need to be an opus xhigh tier for really deep, complex work and a fable high/xhigh to use as a critical cross-check for major, cross-cutting, foundational planning and research spaces that have enormous impact on the ecosystem we are building. The next step is for you to carefully consider the criteria for using each in the context of my real usage patterns. This will require a sub-agent to research/investigate and analyze our real conversations to find patterns"
dispatch: planner opus — resume, serial 01: reconcile with a88a 03 (+ review r4 fixes as acceptance, answer 107 a) and 6421 03 (CLEAR); F1 = the ten base agent files, buildable before the pyramid
serial 01 written: F1 ten agent files (name, description, model, effort; tools omitted = all) + pin test + manifests + CLAUDE.md/README; F2 ships now on defaults, waits per 6421 question listed; quota about -40% vs xhigh, +$17-27/week (+3-6%) over the 2eb7 table during the trial; two a88a questions carried (read-only tools later; naming before F1 lands)
dispatch: plan reviewer opus — fresh, round 1
agent: a1db1057941f8460b (plan reviewer r1)
