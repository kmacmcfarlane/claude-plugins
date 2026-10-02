---
id: dev-cycle-review-spend-as-a-per-item-cos-f65b
title: "dev-cycle: review spend as a per-item cost budget with justified increases, not a round count"
short_display_name: review spend as a cost budget
type: spike
status: doing
priority: 1
parent: dev-cycle-at-the-review-cap-the-orchestr-5bdd
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-02T16:51Z
created: 2026-10-02
updated: 2026-10-02
refs:
  - operator 2026-10-02, decision 141
---

Operator 2026-10-02 on decision 141 (how many finish rounds before the cap asks), verbatim: '141 - what I REALLY care about is cost, not number of rounds. Investigate how we could frame the threshold that way instead. A spend budget set when the research is created and authorization to increase budget with a justifacation for the budget increase matches the actual problem better'. A dig into on 141, covering 142 (when a finish round may spend unasked) too, since both are about spend. Plan only; the result comes back on 141 and 142 with options.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-02 claimed by Kyle-McFarlane@401123cbad11
dispatch: planner opus high — spike plan (dig into on decisions 141, 142)
target: plan dev-cycle-review-spend-as-a-per-item-cos-f65b /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/f65b-review-cost-budget
agent: planner af46608c4b7a2f7a2 round 1
return: planner PLAN_READY .claude-sandbox/investigations/f65b-review-cost-budget/ (INDEX, 00, evidence/item-costs.md, evidence/item_cost.py)
baseline: a88831aa8df8 00_initial.md 
dispatch: reviewer opus high — plan review round 1
agent: reviewer aa75f970dc65e2c2e round 1
verdict: NEEDS_CHANGES round 1 (plan)
findings:
  1. [high] 00:102,116-119,227-229; INDEX:55-59 — the opus-5-5 → opus-5 price alias overstates cost ~1.73x (cited 5.5 prices: Opus $4/$20/$0.20 cache read; cache reads dominate); every item's dollars ~0.6x; under the proposed defaults no item reaches its budget; "2 of 94", "819f asks at the same three points", the simulation, $38-per-1% and the medians are false; fix: price at cited 5.5 rates, regenerate everything, re-derive defaults (~$4/$6/$18/$18); note in Q2 that share-of-week is price-independent
  2. [medium] 00:193-197,320,323-324,501-514 — (a) loosens two stops 142 asked about (rounds past 4 run with no grant/reading, below the reserve, during a hold) and Q1 does not say so; state how (a) answers 142's three conditions, or a "hold stops rounds past the 4th" sub-choice
  3. [medium] 00:220-221,303,333-339 — the spend window after an increase is undefined; sum since the phase's first budget: line vs the last line's amount; split an id spanning phases
  4. [medium] 00:265-268,347-350 — resume would rebuild the convergence count from free-text findings; store must-fix <n> on the cost: rider at Step 4.5
  5. [medium] 00:246 — defaults miss task/refactor/workflow/epic (wi.py:46); map every type, name a fallback
  6-11,15. [low] skip zero-usage <synthetic> records; transcript cleanup → phase spend = last cost: line + later agents; dev-flow plugin.json description names the new context-guard edge; "Estimated cost: $N" is a parsed tag (api-name); ship the cumulative-series step, flag lost rounds; two budgets per feature is a planner call — offer one per item in Q3; SDK sessions in a worktree not counted
  12-14. [nit] "near the max"; compare like with like for 45x; sonnet ~0.70x opus at cited prices
dispatch: planner opus high — resume (plan fix round 1)
agent: planner af46608c4b7a2f7a2 round 2
return: planner PLAN_READY — serial 01_review-fixes.md (1-15), evidence regenerated at cited prices
baseline: a88831aa8df8 00_initial.md 98c18dec7ccd 01_review-fixes.md 
dispatch: reviewer opus high — resume (plan review round 2)
agent: reviewer aa75f970dc65e2c2e round 2
