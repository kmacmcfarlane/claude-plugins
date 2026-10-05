---
id: usage-report-read-an-item-s-spend-by-age-0865
title: "usage-report: read an item's spend by agent id (the cost-budget spend reader)"
short_display_name: spend reader by agent id
type: feature
status: doing
priority: 1
deps:
  - usage-report-price-the-5-5-models-opus-5-ebbe
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-05T17:36Z
created: 2026-10-02
updated: 2026-10-05
refs:
  - decision 145 a
---

Item 2 of the cost-budget build order (series .claude-sandbox/investigations/f65b-review-cost-budget/, serials 00-06, plan CLEAR): a reader in context-guard's usage-report that, given an item's agent: lines, sums list-price spend per phase from local transcripts, by the rules the series settled: every agent-id shape on any agent: line; no segment dropped (surplus flagged unrecorded); nested agents placed by their own start; phases split by time against timestamped budget:/cost: lines; Claude models only, zero-usage <synthetic> skipped, an unknown model with tokens = no reading; transcript cleanup handled via the last cost: line. Acceptance: the series' evidence/item_cost.py results reproduce on the same items through the shipped reader; tests; dev-flow plugin.json description names the context-guard soft edge (README principle 4).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-05 claimed by Kyle-McFarlane@401123cbad11
target: full usage-report-read-an-item-s-spend-by-age-0865 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/usage-report-read-an-item-s-spend-by-age-0865
dispatch: implementer opus medium — build (plan: the cost-budget series f65b 00-06, CLEAR; answer 145 a)
agent: implementer a37cb9fe987c7fcb9 round 1
