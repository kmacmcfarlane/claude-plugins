---
id: spend-budgets-raise-the-defaults-so-only-b9f1
title: "Spend budgets: raise the defaults so only big spends ask, from real usage data"
short_display_name: budgets flag only big spends
type: spike
status: todo
priority: 2
created: 2026-10-07
updated: 2026-10-07
---

Operator 2026-10-07 on 151: 'I'm getting a lot of budget decisions coming in, we should bump up the budget to really only flag big spends (based on real data).' Acceptance: from measured item spend (usage-report item reader over this and sibling stores) propose defaults so that an ask fires only on unusually large spends (e.g. above the p95 of each kind), and say how many asks the last two weeks would have produced; note which recent asks were budget asks versus convergence stops.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: operator 2026-10-08T06:28Z in the claude-plugins librarian session: "waive the budgets for plan/implement/review/research for now, those thresholds are under review and the strategy doesn't feel right as it is." Standing waiver: no budget stops, asks or decided: spend lines until the operator lifts it; spend is still measured and reported.
