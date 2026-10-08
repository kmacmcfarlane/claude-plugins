---
id: spike-how-much-inter-plugin-dependency-i-72ef
title: "spike: how much inter-plugin dependency is baked in, graceful degradation, and a non-naggy hint at better functionality"
short_display_name: plugin dependencies and degradation
type: spike
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T06:28Z
created: 2026-10-08
updated: 2026-10-08
refs:
  - operator 2026-10-08
---

Operator 2026-10-08T06:28Z, in this session: 'We should probably have a work-item spike to investigate how much inter-dependencies are baked into these plugins, because generally they should work independently and have graceful degradation when the other plugin isn't available. We should also make the user aware that there's improved functionality they COULD be utilizing with the other plugin without being too naggy. What's the best way to do that?' Acceptance: an inventory of every cross-plugin reference (prose and code) with its declared or undeclared status and what happens when the other plugin is absent; gaps against README principle 4; a recommended pattern for a once-only, non-naggy notice of the richer behaviour available with the other plugin (when shown, how often, where recorded, how dismissed); follow-up items per gap.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: plan main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef
budget: 2026-10-08T06:28Z plan waived — operator waiver 2026-10-08T06:28Z (spend still measured)
dispatch: planner opus high — spike plan

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: planner af420e468ce5cb8bb
