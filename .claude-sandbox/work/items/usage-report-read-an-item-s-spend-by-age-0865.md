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
return: implementer DONE 3ef7190 (218 of 220 items match the prototype to the cent; judgement calls: role from the first word, non-Claude left out and flagged, deleted transcripts by line order, a 10% floor for the week rate)
dispatch: reviewer opus high — review round 1
agent: reviewer af1fce518a42ec2c1 round 1
verdict: NEEDS_CHANGES round 1 at 3ef7190
findings:
  judgement calls checked and sound; type-checker warnings not crash paths; fixtures clean (no conversation text); memory bounded (18 MB RSS)
  1. [medium] item_spend.py:643-646,683 — text output crashes (KeyError 'why') when the week rate is $0 with >=10% used; week_rate returns per_percent=None with a why when spend <= 0; test
  2. [medium] item_spend.py:213-215 — one agent id with transcripts in two session dirs: only the first is read (real case a363290b7595fc80f, nearly disjoint files), dropping spend; map ids to all paths, read all into one deduped kept; test
  3-6. [low] week_spend: no upper time bound on a stale sensor reading, unknown Claude models skipped silently; a deleted transcript before any budget: line falls back to build, should be UNBUDGETED; covered phases' cumulative series contradicts usd; context-guard plugin.json and README soft-dependency paragraph should name the statusline-hub weekly reading (principle 4)
  7-9. [nit] README dev-flow row clause order and "(the coming spend budget)"; unused name at 719, --week-used without --week-resets-at; anchor AGENT/BUDGET/COST regexes at column 0
dispatch: implementer opus medium — resume (fix round 1)
agent: implementer a37cb9fe987c7fcb9 round 2
