---
id: usage-report-price-the-5-5-models-opus-5-ebbe
title: "usage-report: price the 5.5 models (opus-5-5, sonnet-5-5) and fable-5-1 from a cited source"
short_display_name: price the 5.5 models
type: bug
status: todo
priority: 2
created: 2026-10-02
updated: 2026-10-02
refs:
  - dev-cycle-review-spend-as-a-per-item-cos-f65b
---

Found by the cost-budget investigation (f65b, 00-01): plugins/context-guard/skills/usage-report/scripts/prices.json has no entry for claude-opus-5-5 or claude-sonnet-5-5, so usage_report.py prices opus-5-5 as sonnet-5 (14-day opus-5-5 spend reads $749 vs $1,079 at cited prices, ~1.44x under). Cited (claude-api skill model table, cached 2026-09-25): Opus 5.5 $4/$20/$0.20 cache read, Sonnet 5.5 $2/$10/$0.20, Fable 5.1 $10/$50/$0.25; cache-write rates derived (1.25x / 2x input) unless a source gives them. Evidence: .claude-sandbox/investigations/f65b-review-cost-budget/evidence/prices_cited.json. Acceptance: entries with their source cited; a test that the 5.5 models price at those rates; an unknown model is reported, not silently priced as another. Independent of decisions 141/142.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
