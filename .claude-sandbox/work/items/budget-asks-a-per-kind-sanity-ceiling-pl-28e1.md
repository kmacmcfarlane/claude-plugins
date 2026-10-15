---
id: budget-asks-a-per-kind-sanity-ceiling-pl-28e1
title: "Budget asks: a per-kind sanity ceiling plus a quota-pressure threshold that moves with the week"
short_display_name: dynamic budget ask thresholds
type: feature
status: todo
priority: 2
created: 2026-10-13
updated: 2026-10-14
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
- doing: F1 (b12bd09f) and F3 (06385bce) landed on local main, unpushed; plan series 00-05 CLEAR at review 6
- next: F2, the rule text, per the series' F2 as composed 00->05 (files: dev-cycle bindings.md, SKILL.md, resume.md, record-lines.md, model-routing.md; librarian-mode cycle-bindings.md, decide-alone.md, idle-turn.md, budget.md one sentence; investigate investigation-format.md; README.md :89 and :360-362; dev-flow plugin.json; marketplace.json; operator-interaction decisions gallery.md :134-136). Carry into F2's brief: F3 review lows 1-2 (--answered-at far-past unpadded, future value accepted -> releases every wait; fix in quota_budget.py), the --repo two-jobs note (say to leave --repo off for the reading), gallery.md:139 $21-of-$20 example (plan nit 29), and keep the wait's '(wait answered <UTC>)' Handoff text as written while a wait holds. Build budget: $46 recorded, ~$17 spent on F1+F3; operator's 2026-10-08 waiver still stands. Landing: local merge, no push (operator answer a). Store commits of this item's edits: operator has not chosen between committing as usual and holding for claude-sandbox part A
- blocked: —
- learned: replay: new rule ~8-10 asks per two weeks vs 3 (+2 estimate asks) today; ~$23-25 per weekly point; plan estimates run 2-3x actual builds

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
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/budget-asks-a-per-kind-sanity-ceiling-pl-28e1/ (02_per-item-wait-take-up.md; 5,13-20 applied; wait per item; estimate $40)
baseline: 1852b6360af117f3b0175427d8c884ee6bbffd89d7370ae00920d3ccca76defb  00_initial.md aaef855cc310cf7742bf12566533056df229bde9670e057937989ccd658c6ede  01_settle-oq1-review-fixes.md 1aeee87fe24208e289091d1698b700b71f9802aff984fdb6b44c07d13727ba08  02_per-item-wait-take-up.md 
dispatch: reviewer opus high — resume (plan review round 3)
agent: reviewer acee424b83620460b round 3
verdict: NEEDS_CHANGES round 3 at 02_per-item-wait-take-up.md
findings: 5,13-20 FIXED; new 21 [medium] no-signal quota ask: go-on promises estate reach it cannot store, wait names no reset (no end); 22 [low] derived answer line quotes a reply quota-answer.json does not store (cross-repo)
cost: 2026-10-13T21:24Z plan $13.19 of $28 after review 3 — must-fix 1 — prices 2
dispatch: planner opus high — resume (fix round 3)
agent: planner aac4ac82dfa759bb0 round 4
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/budget-asks-a-per-kind-sanity-ceiling-pl-28e1/ (03_no-signal-ask-reply-store.md; 21, 22 applied; estimate $41)
baseline: 1852b6360af117f3b0175427d8c884ee6bbffd89d7370ae00920d3ccca76defb  00_initial.md aaef855cc310cf7742bf12566533056df229bde9670e057937989ccd658c6ede  01_settle-oq1-review-fixes.md 1aeee87fe24208e289091d1698b700b71f9802aff984fdb6b44c07d13727ba08  02_per-item-wait-take-up.md 14318e6eeeb0cba8eb93d0a8686f0a72c527b564ce24d9ba2cd78c886df43adf  03_no-signal-ask-reply-store.md 
dispatch: reviewer opus high — resume (plan review round 4)
agent: reviewer acee424b83620460b round 4
verdict: NEEDS_CHANGES round 4 at 03_no-signal-ask-reply-store.md
findings: 21, 22 FIXED; new 23 [high] 03:74-76, :88-91 — 'stop here' uses wi handoff --blocked, which leaves status doing, so the idle turn's Work bullet resumes the stopped item. Fix: 04's replacement for 03:74-76 — "the item is blocked `$WI block <id> "operator: stopped at the no-reading quota ask"` (standalone: the run stops) and stays stopped until you say go on"
cost: 2026-10-13T21:27Z plan $14.1 of $28 after review 4 — must-fix 1 — prices 2
- 2026-10-13 related:  (agents decision 0010 moves budget-value authority here); F1/F2 touch the same constants comments and budget.md ownership paragraph, so fold it in when building
- 2026-10-13 correction to the previous note: the related item is budget-values-claude-plugins-is-the-auth-f0f2
answer: plan decisions 1-4 — operator 2026-10-13 chat, verbatim: "1a 2a 3b 4a" (read as: 1 (a) one more planner round applying finding 23's Fix; 2 (a) publish rounded usage-derived constants with a generic source line; 3 (b) the quota ask recommends go-on until free headroom runs out, wait stays available, and a later stored go-on also releases items held by a wait; 4 (a) build after the plan clears; echoed to the operator)
decided: fold budget-values-claude-plugins-is-the-auth-f0f2 into this plan's F1/F2 (same constants block and budget.md ownership paragraph) — class: scope — reopen: say 'keep f0f2 separate'
dispatch: planner opus high — resume (fix round 4, opened by the operator's answer)
agent: planner aac4ac82dfa759bb0 round 5
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/budget-asks-a-per-kind-sanity-ceiling-pl-28e1/ (04_go-on-recommendation-release-ownership.md; 23 applied; answers 2a/3b folded; f0f2 folded into F1; re-anchored to 60d40295; estimate $45)
baseline: 1852b6360af117f3b0175427d8c884ee6bbffd89d7370ae00920d3ccca76defb  00_initial.md aaef855cc310cf7742bf12566533056df229bde9670e057937989ccd658c6ede  01_settle-oq1-review-fixes.md 1aeee87fe24208e289091d1698b700b71f9802aff984fdb6b44c07d13727ba08  02_per-item-wait-take-up.md 14318e6eeeb0cba8eb93d0a8686f0a72c527b564ce24d9ba2cd78c886df43adf  03_no-signal-ask-reply-store.md 77ec0f2760ec094da65239bf767d386f9a9ec0b2b8f9844cd445d430af762bc8  04_go-on-recommendation-release-ownership.md 
dispatch: reviewer opus high — resume (plan review round 5)
agent: reviewer acee424b83620460b round 5
verdict: NEEDS_CHANGES round 5 at 04_go-on-recommendation-release-ownership.md
findings: 23 FIXED; new 24 [medium] answer 3 (b) 'free headroom' read as headroom above the reserve vs the series' burst-adjusted F; 25 [medium] decisions gallery.md:134-135 restates the retired 50% exemption, not in files (Fix: add it, sentence becoming 'Reaching the budget is the cap the operator set, at any quota level, so the next round is asked for.'); 26 [medium] release test compares times neither on record (librarian go-on stores no answered_at; answer lines carry no time); 27 [low] standalone re-invocation recorded as operator go-on though a parent or loop may relaunch; 28 [nit] 'provisional pending ratification' without naming claude-plugins as ratifier
note (orchestrator, on finding 24): the options as offered in chat 2026-10-13 for decision 3: problem stated 'once every item has to ask (~32% on a Monday) the ask recommends wait'; (a) keep as planned; (b) 'recommend go on until free headroom runs out; wait stays available, and a later go on also releases waiting items'. Read against (a), (b) only differs if 'free headroom' excludes the burst term, so the planner's reading (headroom above the reserve) is the one the option offered; confirmed to the operator in the echo that follows
cost: 2026-10-13T23:04Z plan $19.25 of $28 after review 5 — must-fix 3 — prices 2
decision: plan cap after review 5 (must-fix 1 → 3) — options: (a) one more planner round then review [recommended] | (b) carry 24-28 into the build | (z) decide later
answer: plan cap after review 5 — a — operator 2026-10-13 chat, verbatim: "a - one bore planner pass, then review"
dispatch: planner opus high — resume (fix round 5, opened by the operator's answer)
agent: planner aac4ac82dfa759bb0 round 6
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/budget-asks-a-per-kind-sanity-ceiling-pl-28e1/ (05_record-times-names-gallery.md; 24-28 applied; estimate $46)
baseline: 1852b6360af117f3b0175427d8c884ee6bbffd89d7370ae00920d3ccca76defb  00_initial.md aaef855cc310cf7742bf12566533056df229bde9670e057937989ccd658c6ede  01_settle-oq1-review-fixes.md 1aeee87fe24208e289091d1698b700b71f9802aff984fdb6b44c07d13727ba08  02_per-item-wait-take-up.md 14318e6eeeb0cba8eb93d0a8686f0a72c527b564ce24d9ba2cd78c886df43adf  03_no-signal-ask-reply-store.md 77ec0f2760ec094da65239bf767d386f9a9ec0b2b8f9844cd445d430af762bc8  04_go-on-recommendation-release-ownership.md ad6dec819b20098f2eb878197d066b9d6aeda2c5153540141ff2612313d495e3  05_record-times-names-gallery.md 
dispatch: reviewer opus high — resume (plan review round 6)
agent: reviewer acee424b83620460b round 6
verdict: CLEAR round 6 at 05_record-times-names-gallery.md
findings: 24-28 FIXED; 29 [nit] gallery.md:139 example '$21 of its $20 budget' below every new ceiling (cosmetic; carry to F2); note: a later wi handoff --blocked rewrite would drop '(wait answered <UTC>)' (fails safe; F2 may say the field is left as written while a wait holds)
cost: 2026-10-13T23:11Z plan $23.33 of $28 after review 6 — must-fix 0 — prices 2
decided: no build budget ask — the operator's standing waiver of 2026-10-08 (b9f1 note: no budget stops, asks or decided: spend lines until lifted) holds; plan estimate $46 (F1 ~$8, F3 ~$8, F2 ~$24) shown to the operator — class: spend — reopen: lift the waiver
target: full budget-asks-a-per-kind-sanity-ceiling-pl-28e1 F1 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/budget-asks-a-per-kind-sanity-ceiling-pl-28e1-f1
budget: 2026-10-13T23:11Z build $46 — plan budget-asks-a-per-kind-sanity-ceiling-pl-28e1 estimate (answer: plan decisions 1-4, 4 (a); standing waiver 2026-10-08)
dispatch: implementer opus medium — build F1 (executable logic: quota_budget.py, tests; budget.md)
agent: implementer a3b6744cece0d25ef round 1
return: implementer DONE d2fba8d1 (F1: spend_inputs + quota_pressure in quota_budget.py, 19 new tests, budget.md incl. f0f2 ownership; open: budget.md points at bindings.md § Spend budget which names the keys only after F2)
changed:
  plugins/dev-flow/skills/librarian-mode/scripts/quota_budget.py — spend constants, spend_inputs(), before_reset_share(), quota_pressure(), wired into compute(); f0f2 ownership comments
  plugins/dev-flow/skills/librarian-mode/scripts/tests/test_quota_budget.py — TestSpendInputs, TestQuotaPressure
  plugins/dev-flow/skills/librarian-mode/references/budget.md — Who owns what (decision 0010), spend inputs and quota pressure in The numbers and The result
dispatch: reviewer opus high — review F1 round 1
agent: reviewer ac05463b42cf9315a round 1
verdict: CLEAR round 1 at d2fba8d1
findings: lows/nits for F2 or later: 1 budget.md:15,225-226 point at bindings.md § Spend budget which names the keys only after F2; 2 commit subject shape; 3 budget.md:9 138-col line; 4 budget.md:294,305 example allowed 0.41 vs headroom 44 at 100 h
cost: 2026-10-13T23:25Z build $4.26 of $46 after review 1 — must-fix 0 — prices 2
landed: b12bd09f
checks: on base after b12bd09f, all 10 Librarian Checks OK
target: full budget-asks-a-per-kind-sanity-ceiling-pl-28e1 F3 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/budget-asks-a-per-kind-sanity-ceiling-pl-28e1-f3
budget: 2026-10-14T07:03Z build $46 — plan budget-asks-a-per-kind-sanity-ceiling-pl-28e1 estimate (answer: plan decisions 1-4, 4 (a); standing waiver 2026-10-08)
dispatch: implementer opus medium — build F3 (executable logic: quota_budget.py --quota-answer, store file, tests)
agent: implementer ad90dba4bd9ea6530 round 1
return: implementer DONE_WITH_CONCERNS a85d1c30 (F3: --quota-answer go-on, quota-answer.json, quota_pressure.answer, ref_repo_name, 40 tests; budget.md incl. F1 lows; concern: past-reach answer printed covers:false per series 01, brief said null — series governs, brief was the orchestrator's paraphrase)
changed:
  plugins/dev-flow/skills/librarian-mode/scripts/quota_budget.py — --quota-answer write path and flags, ref_repo_name(), REPLY_MAX, quota_pressure.answer, nofollow read
  plugins/dev-flow/skills/librarian-mode/scripts/tests/test_quota_budget.py — TestQuotaAnswerWrite, TestQuotaAnswerRead, TestRefRepoName
  plugins/dev-flow/skills/librarian-mode/references/budget.md — quota-answer.json, flags, refusals, printed keys; F1 lows (wrap, example allowed)
dispatch: reviewer opus high — review F3 round 1
agent: reviewer a0b9e4a58edd0f87e round 1
verdict: CLEAR round 1 at a85d1c30
findings: lows/nits carried to F2 or a follow-up: 1 [low] quota_budget.py:718 --answered-at far-past year stored unpadded ('1-01-01T00:00Z') then reads null; 2 [low] :717 a future --answered-at accepted (would release every wait); 3 [nit] :717 date-only ISO value refused with a misleading message; 4 [nit] budget.md:145-146 example dates disagree; 5 [nit] budget.md:56-57 ragged wrap; note: --repo does two jobs (claim name and authority repo) — F2 text must say to leave --repo off for the reading or explain the split
cost: 2026-10-14T07:24Z build $8.93 of $46 after review 1 — must-fix 0 — prices 2
landed: 06385bce
checks: on base after 06385bce, all 10 Librarian Checks OK
note: handed off 2026-10-14 by the budget session to the claude-plugins librarian session for F2 (the rule text) in the standard flow; F1 b12bd09f and F3 06385bce landed on local main, not pushed (operator answer a: local merge, no push)
- 2026-10-14 learned: replay: new rule ~8-10 asks per two weeks vs 3 (+2 estimate asks) today; ~$23-25 per weekly point; plan estimates run 2-3x actual builds
decision 216: store commits of the budget session's work-item edits (28e1, b9f1 dropped, f0f2 filed and closed) — options: (a) the librarian commits them as usual [recommended] — quotes and usage figures become public if pushed before claude-sandbox part B, which removes them | (b) hold them uncommitted until claude-sandbox part A moves the store to the sidecar — never in public history, but dirty item files for days — asked 2026-10-14 in the budget session, unanswered
- 2026-10-14 checkpoint: CORRECTION the F3 brief said a past-reach go-on prints null; the series (01) says covers:false and governs; F3 as landed follows the series
- 2026-10-14 checkpoint: OPEN F2 also needs quota_budget.py in its files for the F3 review lows 1-2 (--answered-at far-past unpadded; future value accepted) unless split to a follow-up
decision 218: Should main stay unpushed until you confirm that the budget plan's two landed parts (F1, F3) stay local? The budget session relays your answer (a), local merge, no push, but a relayed answer binds nothing until you confirm it here, and every push of main now carries them — options: (a) confirm: keep main unpushed; everything lands locally until you lift it [recommended] | (b) push as usual: F1 and F3 go to origin with the next push | (z) decide later: main stays unpushed meanwhile
answer 216: a — operator 2026-10-14 in the budget session, verbatim: "commit the store edits as usual"
answer 218: b, in chat 2026-10-15, verbatim: "218b" (read as: push as usual; the budget plan's F1 and F3 go to origin with the next push)
