---
id: dev-cycle-review-spend-as-a-per-item-cos-f65b
title: "dev-cycle: review spend as a per-item cost budget with justified increases, not a round count"
short_display_name: review spend as a cost budget
type: spike
status: done
priority: 1
parent: dev-cycle-at-the-review-cap-the-orchestr-5bdd
created: 2026-10-02
updated: 2026-10-02
closed: 2026-10-02
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
verdict: NEEDS_CHANGES round 2 (plan)
findings:
  prior 1-9, 11-15 fixed; 10 partly
  16. [high] evidence/item_cost.py:108,117 — the agent: pattern requires a role before the id; 18 items with transcripts are skipped (plan runs 5140, 6421, a99c, 6d2c, d618, 8dee, a88a at $24.7-30.8; chore dbfc $20.90; feature b3c5 $20.32; caef loses two agents); the per-kind table, simulation, defaults, walkthroughs, Q1/Q3 impacts and INDEX are overturned; fix: every a[0-9a-f]{16} on any agent: line, role from the text; regenerate; Item 2's reader accepts old line shapes
  17. [high] item_cost.py:129-132 (adopted for the real reader, 01:254-259,338) — transcript segments beyond an id's agent: line count are dropped ($39.79 over 29 items; caef reaches ~$19.33 before its sixth planner round); fix: never drop a segment — attribute surplus to the last recorded round or split by timestamp; flag unrecorded_rounds; § 4 states the reader may over-attribute between rounds but never under-read a phase
  18. [low] 01:240-246 — the 142 table's Today column is librarian-only; standalone runs today raise every cap and (a)+Q7 (i) loosens them; add a standalone row to the table and Q1 (a)
  19. [nit] 01:166-169 — leave non-Claude models out of the per-1% rate
dispatch: planner opus high — resume (plan fix round 2)
agent: planner af46608c4b7a2f7a2 round 3
return: planner PLAN_READY — serial 02_review-r2-fixes.md (16-19), evidence regenerated (112 items)
baseline: a88831aa8df8 00_initial.md 98c18dec7ccd 01_review-fixes.md 85fb607d5d9e 02_review-r2-fixes.md 
dispatch: reviewer opus high — resume (plan review round 3)
agent: reviewer aa75f970dc65e2c2e round 3
verdict: NEEDS_CHANGES round 3 (plan)
findings:
  prior 16-19 FIXED (evidence reproduces: 112 items; default tables ask on 12, 4, 3, 2 items); the spike/plan split is readable at phase start from type:
  20. [medium] 02:266,268,315-319,338 — the convergence stop (Q4 (i)) was not simulated: caef's must-fix rose 4 → 5 from r3 to r4, so it asks before round 5 too; "three items ask" and "the spikes finish inside" count budget asks only, and the spikes' convergence asks are unknown; fix: simulate the stop over every phase that reached a 4th review (counts from findings blocks or series review files), state asks as budget plus convergence, or label counts "budget asks only" and add the known ones
  21. [low] 02:228-236, item_cost.py:31-32,156-160 — nested sub-agent spend lands on the parent's first segment; place each by its own start; the cleanup shortcut relies on 00's quiescence rule and only for ids whose transcripts are gone
  22. [nit] caef's spend before planner round 6 is $26.05 (the fable second opinion ran first), not $22.10
  23. [nit] a plan phase with no type: (store-less standalone) takes the $18 plan default
dispatch: planner opus high — resume (plan fix round 3)
agent: planner af46608c4b7a2f7a2 round 4
return: planner PLAN_READY — serial 03_convergence-simulated.md (20-23), new Q8
baseline: a88831aa8df8 00_initial.md 98c18dec7ccd 01_review-fixes.md 85fb607d5d9e 02_review-r2-fixes.md 25a751beac23 03_convergence-simulated.md 
dispatch: reviewer opus high — resume (plan review round 4, the cap)
agent: reviewer aa75f970dc65e2c2e round 4
verdict: CLEAR round 4 (plan)
findings:
  prior 20-23 FIXED (counts spot-checked against item records; 112 items reproduce)
  24. [low] 03:130 — Q8 (i) "stop and carry, as today, decided alone" is true only under a librarian; standalone runs today raise every plan cap; name the standalone case or say standalone follows Q7 (under Q7 (iv) they keep raising)
  25. [nit] 03:159-165 — Q1 (a)'s text should say the round count also stays as the plans' stop at the fourth review under Q8 (i)
findings: carried — 24 [low], 25 [nit] above, verbatim; into the build of decision 145 (a), if chosen
- 2026-10-02 done: closed on its series .claude-sandbox/investigations/f65b-review-cost-budget/ (00-03, plan CLEAR r4); result back as decision 145, replacing 141 and 142
