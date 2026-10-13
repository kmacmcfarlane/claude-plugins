---
id: budget-asks-a-per-kind-sanity-ceiling-pl-28e1
title: "Budget asks: a per-kind sanity ceiling plus a quota-pressure threshold that moves with the week"
short_display_name: dynamic budget ask thresholds
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@0f4d9af15968
claimed: 2026-10-13T20:19Z
created: 2026-10-13
updated: 2026-10-13
refs:
  - operator 2026-10-08 budget session
  - operator 2026-10-13 approval
---

Operator, 2026-10-08 (budget session), verbatim: "these budget decisions befor starting work are getting annoying. I only want budget decisions for true outlier research and implementation." and "if we are above 50% on Monday, that's very different than above 50% on Sunday ... We should establish some high threshold to catch the sort of spending that's outside anything I've ever seen or approved (or in the p99 range maybe). And I want a proposal to deal with time decay on the impact of larger work we can factor in. I don't want to target limiting the work to a linear spread throughout the week (my time/attention is bursty). The never ask under 50% is a good start, but we need a sanity ceiling even under 50% quota." Operator approved the proposal below as "a good plan" (2026-10-13) and asked to see the plan before the build.

## Evidence (measured 2026-10-08, this machine only; prototype readers, not claude-analytics)
- item_spend.py over 262 items with agent: lines, 16 repos, 2026-09-22..10-08, list price: build chore p50 $1.7 / p95 $7.6 / max $21; bug 2.4 / 12.0 / 26; feature 7.3 / 19.2 / 45; plan feature 11.6 / 26.9 / 30; plan spike 12.9 / 31.9 / 34 (bunched under the old $28 cap: censored). 23 budgeted phases, 2 over budget.
- Pre-build asks come from plan `Estimated cost:` lines ($35-50) above the build default; actual builds ran far lower (e807: est $50, actual $18.4). The estimate ask ignores quota.
- usage_report summary: ~$23 list per weekly percentage point (week to 10-05: $2,195 / 96 pts; week to 10-12: $838 / 35 pts by 10-08). One item is 0.1-2 pts; burst days are 20-30 pts (max 24 h rise 53) from many concurrent items.
- Weekly samples (claude-analytics sampler): daily rises 25,12,29,7,20,1,2 in the week to 10-05: bursty.
- Gaps: work-project (non-kmacmcfarlane) usage absent; research-skill runs and orchestrator turns not attributed to items; ~16 days of history. Operator is skeptical of p95 as a threshold until data improves.

## Design (approved shape; values are defaults to retune)
Two independent ask triggers; ask when either fires. They replace the default-budget-as-ask and the pre-build estimate ask; answer 176's flat 50% line is subsumed by rule 2.
1. **Sanity ceiling (anomaly)**, any quota level: per kind ~1.5x the largest completed/approved item of that kind (or p99 once data allows). Starting values: feature build $65, spike plan $60, other plan $45, bug build $35, chore build $30. An amount the operator approved before counts as in range for its kind. Quota-independent.
2. **Quota pressure**, from the weekly window: d = days to reset; burst(d) = b * sqrt(d), b = 20 pts (a typical big day; sqrt because bursts do not add linearly); reserve(d) = the existing weekly reserve with its 48 h taper; free headroom F = 100 - used - reserve(d) - burst(d). Ask when an item's expected remaining spend (in points) > alpha * F, alpha = 0.25; ask on every item when F <= 0. The effective "asks start" line moves ~27% used at 7 days left, ~40% at 4, ~52% at 2, ~67% at 1, ~86% at 2 h.
- **Expected spend** = the kind's historical p75, not the plan's estimate; an estimate counts only when it exceeds the sanity ceiling.
- **Time decay of large work**: only the share expected to land before the reset counts against this week; burst(d) shrinks toward the reset because unused quota is lost there.
- Dollars-to-points via a configured $/pt (default ~$23) until claude-analytics publishes it.
- The concurrency sum (apply F to everything in flight) is the librarian F2 idle turn's (c79e), not this item: note it there.

## Acceptance
- quota_budget.py prints the inputs rule 2 needs (burst(d), F, and the ask threshold in points and dollars) with tests; values as constants at the top, sourced like the reserves.
- dev-cycle bindings.md § Spend budget (and SKILL.md, resume.md, librarian-mode budget.md/decide-alone.md where they restate it) state the two triggers, replacing the defaults-as-ask, the pre-build estimate ask and the flat 50% line; convergence stop and quota-reserve guards unchanged; never named in a brief.
- A replay over the last two weeks' items says how many asks the new rule would have produced vs the old.
- Ownership: claude-analytics owns the inputs ($/pt, b, per-kind p75/p99) once its reports exist (CLAIM.md 2026-10-08); this repo owns the ask rule. The agents repo owns the reserve values until its decision record 0010 moves them.

Supersedes spend-budgets-raise-the-defaults-so-only-b9f1. Related: budget-rule-quota-aware-asks-answer-176-20f5 (answer 176), librarian-f2-idle-turn-modes-concurrency-c79e, spend-reader-split-phases-on-each-target-7421.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-13 claimed by Kyle-McFarlane@0f4d9af15968
target: plan budget-asks-a-per-kind-sanity-ceiling-pl-28e1 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/budget-asks-a-per-kind-sanity-ceiling-pl-28e1
budget: 2026-10-13T20:19Z plan $28 — default other plan
checks: CLAUDE.md ## Librarian Checks (read only)
dispatch: planner opus high — plan (doctrine change to dev-cycle's budget rule plus quota_budget.py logic; operator asked to review the plan before the build)
agent: planner aac4ac82dfa759bb0 round 1
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/budget-asks-a-per-kind-sanity-ceiling-pl-28e1/ (OQ1 blocking F2/F3: approved values replay to 77 asks in two weeks vs 3 today)
answer: OQ1 (c) — operator 2026-10-13 chat, verbatim: "77c" (read as: option (c), b=20 with one go-on covering all work for the next 10 weekly points; F3 in; OQ2-OQ5 take the plan's recommendations, echoed to the operator)
baseline: 1852b6360af117f3b0175427d8c884ee6bbffd89d7370ae00920d3ccca76defb  00_initial.md 
dispatch: reviewer opus high — plan review round 1
agent: reviewer acee424b83620460b round 1
verdict: NEEDS_CHANGES round 1 at 00_initial.md
findings: 9 must-fix (all medium) + 2 low + 1 nit; verbatim in the reviewer's report, pasted into the planner's fix brief: 1 OQ1 still open in series/menus; 2 go-on option omits its estate-wide reach; 3 grant authority 'answer N' is per-store; 4 no outcome for a failed --grant write or post-reset answer; 5 pending quota asks when a grant starts covering; 6 replay of (c) is 7 at phase start only, 10 at all check points; 7 resumed phases with old default/estimate/fable sources; 8 README row, dev-flow plugin.json and marketplace.json descriptions for the new reader; 9 quota pressure vs step 3 finish round; 10 low --grant 10 hardcoded; 11 low verification grep vs legacy text; 12 nit 'grant' overloaded
cost: 2026-10-13T21:09Z plan $7.09 of $28 after review 1 — must-fix 9 — prices 2
dispatch: planner opus high — resume (fix round 1)
agent: planner aac4ac82dfa759bb0 round 2
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/budget-asks-a-per-kind-sanity-ceiling-pl-28e1/ (01_settle-oq1-review-fixes.md; findings 1-12 applied, none declined; OQ6-8 non-blocking; estimate $39)
baseline: 1852b6360af117f3b0175427d8c884ee6bbffd89d7370ae00920d3ccca76defb  00_initial.md aaef855cc310cf7742bf12566533056df229bde9670e057937989ccd658c6ede  01_settle-oq1-review-fixes.md 
dispatch: reviewer opus high — resume (plan review round 2)
agent: reviewer acee424b83620460b round 2
verdict: NEEDS_CHANGES round 2 at 01_settle-oq1-review-fixes.md
findings: prior 1-4,6-12 FIXED; 5 PARTIAL (idle turn never takes up an item blocked on a quota ask; idle-turn.md not in files); new 13 [medium] estate-wide wait built ahead of OQ6, no lift path; 14 [medium] option (b) text wrong under ask_all; 15 [medium] nothing resumes a wait-held item after the reset (idle-turn.md); 16 [medium] floor overrides an answer-sourced tighter amount; 17 [low] resume S8/S10 dispatch during a wait; 18 [low] <repo> basename vs origin rule; 19 [low] closed-superseded form for unnumbered answers, needs-input still shows; 20 [nit] fable ceiling source words
cost: 2026-10-13T21:18Z plan $11.73 of $28 after review 2 — must-fix 5 — prices 2
decided: "wait" stays per item, as the operator's answer (c) covered only go-on; the estate-wide wait (OQ6) is offered to the operator as a later option, not built — class: scope — reopen: say 'make wait estate-wide' and the planner adds it with a lift path
dispatch: planner opus high — resume (fix round 2)
agent: planner aac4ac82dfa759bb0 round 3
