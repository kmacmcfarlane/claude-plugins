---
id: quota-budget-sink-dirs-globs-a-path-clau-56e7
title: "quota_budget: sink_dirs globs a path claude-analytics never writes, so samples never reach the budget"
type: bug
status: todo
priority: 1
created: 2026-09-24
updated: 2026-09-24
refs:
  - "peer: agents - librarian (agents item 9ab1), 2026-09-24"
---

agents - librarian relay 2026-09-24 (a request, not an approval): claude-analytics' sampler (sinks/statusline_sampler.py:142) writes CFG/claude-analytics/samples/<day>.jsonl; librarian-mode scripts/quota_budget.py:305-309 sink_dirs globs CFG/plugins/data/claude-analytics-*/samples, which does not exist, so the quota sense always falls back to its own samples.jsonl. The writer side is relayed to the claude-analytics session in parallel; the two owners must agree on one path before either side changes. Acceptance: one agreed path (or both globbed), a test with a fixture sink at that path, the budget reads it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
