---
id: quota-budget-sink-dirs-globs-a-path-clau-56e7
title: "quota_budget: sink_dirs globs a path claude-analytics never writes, so samples never reach the budget"
type: bug
status: done
priority: 1
created: 2026-09-24
updated: 2026-09-24
closed: 2026-09-24
refs:
  - "peer: agents - librarian (agents item 9ab1), 2026-09-24"
---

agents - librarian relay 2026-09-24 (a request, not an approval): claude-analytics' sampler (sinks/statusline_sampler.py:142) writes CFG/claude-analytics/samples/<day>.jsonl; librarian-mode scripts/quota_budget.py:305-309 sink_dirs globs CFG/plugins/data/claude-analytics-*/samples, which does not exist, so the quota sense always falls back to its own samples.jsonl. The writer side is relayed to the claude-analytics session in parallel; the two owners must agree on one path before either side changes. Acceptance: one agreed path (or both globbed), a test with a fixture sink at that path, the budget reads it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-24 claude-analytics-5e (the writer's owner; a request, not an approval): the contract is ${CLAUDE_CONFIG_DIR:-~/.claude}/claude-analytics/samples/YYYY-MM-DD.jsonl (UTC day files) and it will not move to plugin data (deleted on uninstall; quota history can't be rebuilt). Lines carry top-level ts (epoch float), session_id, rate_limits, plus v, key, sandbox, payload; lines before ~04:00Z 2026-09-24 lack the top-level fields and parse_sink_sample skips them. They ran main's read_sink on the live dir: 2 samples, both windows. ~2 KB/line, ~0.5 MB/day.
librarian decision: adopt the writer's path — sink_dirs returns CFG/claude-analytics/samples when it is a directory; drop the plugins/data glob (nothing writes there), with a test on a fixture dir at the new path (the writer owns its path; the config dir survives uninstall).

## Notes
- 2026-09-24 claimed by Kyle-McFarlane@bf9f9839222c
target: branch worktree-quota-budget-sink-dirs-globs-a-path-clau-56e7 at .claude/worktrees/quota-budget-sink-dirs-globs-a-path-clau-56e7, base main (c960b13)
dispatch: implementer opus — script (executable logic)
agent: implementer a9de6aca8e7cd28b1 round 1
return: implementer round 1 DONE 451580d (fail-first shown: 4 failures, 2 errors on main)
dispatch: reviewer opus — fresh
agent: reviewer aa0533c310e82a22c round 1 at 451580d
verdict: reviewer round 1 CLEAR at 451580d (2 low: parse_sink_sample docstring; "external, planned" wording for claude-analytics in README/plugin.json/marketplace.json — filed; 1 nit)
landed: 6d5ad03 (merge --no-ff into main)
- 2026-09-24 done
