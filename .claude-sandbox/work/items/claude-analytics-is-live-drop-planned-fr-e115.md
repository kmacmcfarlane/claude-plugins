---
id: claude-analytics-is-live-drop-planned-fr-e115
title: "claude-analytics is live: drop 'planned' from README, plugin.json, marketplace.json; refresh parse_sink_sample docstring"
type: chore
status: todo
priority: 3
created: 2026-09-24
updated: 2026-09-24
refs:
  - 56e7 review lows
---

From the 56e7 review (CLEAR): README.md:82, plugins/dev-flow/.claude-plugin/plugin.json:3 and .claude-plugin/marketplace.json:31 still call claude-analytics 'external, planned', but its sampler is live; quota_budget.py:263-266 parse_sink_sample docstring cites the design doc and the payload's rate_limits, while the code reads the top-level rate_limits per the writer's contract. Optional: tests pinning a symlinked and an empty samples dir. Mechanical (sonnet).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
