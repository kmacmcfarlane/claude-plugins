---
id: librarian-work-unblocked-items-and-pre-i-1222
title: "librarian: work unblocked items and pre-investigate the rest while idle, without burning quota"
type: spike
status: doing
priority: 0
owner: unknown@360f41058e92
claimed: 2026-09-22T02:36Z
created: 2026-09-22
updated: 2026-10-06
refs:
  - operator 2026-09-22
---

Operator 2026-09-22: an idle librarian should work new items as they arrive when no operator decision is needed (doc-only requests nearly always; skill changes often; implementation or complex skill changes warrant an investigation round). Investigations can run without waiting on the operator, so when the operator returns the decisions are ready to present. Today items queue up waiting for attention when many are unblocked or at least investigable. Question: how to achieve this without accidentally running the operator's quota into the ground. Acceptance: an investigation series with findings and a recommendation (routing rules for what proceeds unattended vs what waits; quota guards; how investigations pre-run and park their decisions), presented to the operator; decisions raised by number.

## Handoff
- doing: nothing in flight; landed since the last checkpoint: ebbe 614b738, 819f 66cc7ff, 0865 e959ae2, 5bdd e92f0e3, 48a8 12de6eb (+ earlier 5579, dabd); all pushed
- next: answers 134, 147-156; e184 lands on 147/148 after merging main + short re-review; 5925 builds on 153-155; 2bbe on 149; 0999/3e8e on 150/151; 1ffd after e184
- blocked: —
- learned: —

## Librarian notes
- Subsumes the design question of d05d (auto-investigation per item; decision 49 open) and builds on 693a (idle turn), b020 (grooming/needs-input), 810f (holds). d05d's peer tensions 1-7 are input.
- Investigation run in the librarian session itself on fable at the operator's request (2026-09-22); series home .claude-sandbox/investigations/1222-unattended-librarian/.
- Model note: operator switched this session to fable for the investigation; prompt to switch back to opus 5 before resuming other items.

## Operator answers 2026-09-22 (to the six follow-ups)
1. Protect the 5-hour window. Operator will say when they are nearly done for the day; then the librarian may run up to the limit and let Claude Code auto-resume (auto-resume is flaky — investigate).
2. If the quota-consumption velocity outpaces what the window/weekly limit allows, switch to a more conservative auto-investigation policy. Operator asks: what are the priority options — how big is the P0–P4 scale?
3. Tier: sonnet for simple investigations; opus for medium/high complexity; for very complex ones, PROMPT the operator to switch to fable (overriding auto-investigate in that case).
4. Concurrency limit derived from quota velocity vs amount used vs time left; less conservative while the operator is asleep/away.
5. Yes: establish guidelines for reversible, low-impact, high-probability decisions the librarian runs with (and makes sure the operator sees) without blocking.
6. On a guard trip: finish in-flight, stop dispatching; a short turn to tell the operator is fine.

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
decision 52: push of main rejected — origin/main has eda3422 (operator, GitHub web: 'Update README.md', removes the 5-line claude-kit refactor paragraph) that local main lacks; local main has one store commit past it. Rules forbid pull/rebase/force — (a) allow a one-time `git merge origin/main` on main (a merge commit, no history rewrite; the two change disjoint files), then push [recommended]; (b) you rebase/push locally yourself; (c) hold pushes until told.

## Operator answers 2026-09-22 (requirements gate)
- Several semi-autonomous "librarian" agents share one subscription: the design needs shared state (budget samples, schedule, intent) and coordination; the agents repo owns the big-picture workflow; involve the agents and operator-attention librarians (messaged the agents librarian).
- G3: interactive for the strong model in almost all cases; ask when the problem warrants it — define "warrants".
- G4: a per-subscription state store, location codified in the skill.
- G5: name the decide-alone class; refine from conversations on disk (item b8d6).
- G6: phase 1 simple with expectations of the operator's own quota need; later phases e.g. vacation mode at the top end.
- G1, G2, decision 52: deferred — operator wants more thinking from me first. Context at ~50%: no deep research.
- New standard: every message ends with a two-line recap (recap; operator's next steps). Lettered+numbered lists stay.
- agents librarian filed 374f (comms standards) and 8ad9 (multi-agent budget coordination, blocked on this series path); points at claude-analytics investigations/agent-telemetry: a status-line quota sampler (record hook on statusline-hub) is already designed there — F1 must read its sink when present rather than sample twice.

## Factored 2026-09-22
- F1 librarian-f1-quota-budget-py-and-the-per-9882 → F2 librarian-f2-idle-turn-modes-concurrency-c79e → F3 librarian-f3-pre-investigation-per-item-a9be ∥ F4 librarian-f4-librarian-calls-call-n-mark-ef9f ∥ F5 librarian-f5-operator-intent-phrases-and-4f7d (see the series). d05d closes into F3 once F3 lands.
decision 53: interim cap until F2 lands — (a) open a hold `limit: 4 agents in flight, no fable` now [recommended]; (b) no cap; (c) a different N.
- 2026-09-22: agents librarian's view on the active-librarian divisor recorded on F2 (c79e); a 01 serial follows their librarian-budget-policy series.
- agents 8ad9 policy answer recorded on F2 (c79e); 01 serial pending (supersedes 00 § F2 N formula/divisor; F1 claims → claims/<repo>.json).
- CORRECTION 00 contradicts itself on the away 5-hour reserve (F1: 5%, F5: 10%); the agents policy picks 10% — 01 will say so.
answer 53: (b) no interim limit — the real feature (F2) is being delivered (operator 2026-09-22)
answer 52: (a) — operator: 'Why would we forbid doing a pull? That seems like a weird policy'; librarian merges origin/main (merge, never rebase/force), runs Checks, pushes; rule revision filed (operator 2026-09-22)
answer G1: the quota reserve plan as written (F1 constants: 5h 25/10/0/5 present/away/done/vacation, weekly 15/15/15/10 — away 10 per the agents-policy correction) (operator 2026-09-22)
answer G2: operator asks whether P0 should mean parked/don't-schedule, with a separate blocked+reason. Librarian: wi already has both — `wi park <id> <reason>` (status parked, never scheduled) and `wi block <id> <reason|item>` (schedulable at its priority once unblocked); P0 is the highest priority and priorities gate scheduling only through F2's mode table. No change needed; confirm in F2 serial 01 (operator 2026-09-22)
- 2026-09-22 held for the next wave (quota: weekly 32%, ~2× the sustainable pace): caef (fable), 8cc2 F3b planner (serial 04), dev-cycle-design-resume-whole-split-from-e770 planner, 3adc conflict round.
decision 62: weekly quota burn — 32% → 34% in ~35 min (~3.4 %/h vs the sustainable 0.37 %/h; at this pace the week runs out in ~1 day, reset in 5.7 days). Held wave: caef (fable security hardening), 8cc2 F3b planner, e770 resume planner, 3adc conflict round. (a) hold new dispatch until the 5-hour window resets and then run one item at a time, most valuable first (F3b planner) [recommended: keeps the week usable; in-flight H3/H5 finish]; (b) dispatch the held four now (answer 53 stands); (c) pause everything but reviews of in-flight work until you say go.
answer 62: superseded — operator 2026-09-22: 'continue with the work queue'; dispatch resumes (no cap), the librarian keeps reporting the burn rate (operator 2026-09-22)

## Queue plan under the quota meter (session e9bb00fc, 2026-09-22, operator: "see how much you can get done without overrunning the reserve")
Meter at start (quota_budget.py, intent present): 5h used 22 (reserve 25, resets 1.3h); weekly used 42 (reserve 15, resets 132.8h), headroom 43 pts, allowed 0.32 pts/h; binding weekly.
Rules: HARD STOP of new dispatch at weekly used >= 85 (the reserve) or 5h used >= 75; in-flight cycles finish. SOFT CHECKPOINT at weekly 64 (half the headroom): report the burn and keep going unless the operator stops it. Meter re-read before every wave; per-wave cost recorded here to calibrate. Cheapest tier the routing rules allow; fable only where rule 3 demands it.
Waves (disjoint files within a wave; a later wave waits on its deps):
W1: F3b-4 0426 (opus/opus); e770 F2 1709 (opus/opus); 1f7f team-summary (sonnet/opus)
W2: F3b-3 c3e1 (opus/opus, carries 3a8f's docstring rider); e770 F3 acdd (opus/opus); d978 team-summary nits (sonnet/opus, after 1f7f)
W3: F3b-5 b495 (sonnet/opus); e770 F4 d81c (sonnet/opus); 09e1 + 5dbf dev-cycle docs (sonnet/opus, after F3); 4b6a, 5cde, 99b4 review lows (sonnet/opus)
W4: wi fixes one at a time (same script): 1d1c, 59ce, fc04, bf1b, then 8e14 (opus); read_list c121; lineage 87fd; ledger 6641; docs 8519, 0900, 5a18
W5 (judgement, planner first, most expensive): c79e librarian F2 (opus plan), 8ab6 loop items, bace H7 spike, 0599, ee7b, 3460, 09f1, d05d, bfd6, b8d6, 0d6b (gate code: fable), caef (fable) last
Held for the operator/peers, not dispatched: e466 (iterate with operator), 4b0e (peer coordination), 32cc/380c (blocked), e5a7/7e8f (another session's claim), 680a/919c/d3a8/8189/segment 40ed/8c2c/7647/a95a/8482/8605/fa54/9ec9/bb7e taken after W5 as budget allows.
- 2026-09-24 via agents - librarian: the operator is hitting subscription limits (weekly 60% with 4 days left) and worries that overnight work depletes the quota they need during the day. They asked for research into routing a "free" class of tasks to the local RTX PRO 6000 before any overnight model use (agents repo; results to be shared). Until then the librarian does not dispatch queue work overnight or unattended.
- 2026-09-28 post-compaction status (session e9bb00fc): quota weekly 0% used (reset ~6.6 d), 5h 2%; recommended first batch A-D, second wave, interactive 2b15, waiting list; housekeeping: ask claude-analytics re usage-report retirement, release stale claims 5039/e5a7, orphan check of two old worktrees
decision 87: first batch to dispatch now, attended — (a) all four: flake fix d1e3, security-hardening plan caef, plain-language item names 0b2d, sonnet wording batch e115/0156/6bff [recommended] | (b) only A-C | (c) you pick | (z) decide later
  raised: 2026-09-28
  what: which items I start on now while you are here
  why now: quota is back (weekly 0% used); nothing is in flight
  (a): three builders plus reviewers at once; about a day of wall time for caef's plan, the rest within hours — undo: stop any item before it lands — who: this repo only
  (b): the wording fixes wait for the second wave
  (z): I start nothing and stay idle
  rec: (a) · basis: strong — queue read from the store; quota from quota_budget --read-only
  unknown: how much of caef's plan will need your ruling
decision 88: the no-unattended-dispatch hold (set 2026-09-24) — (a) keep it: I dispatch only while you are taking turns [recommended] | (b) lift it for this week: I keep working the queue between your turns and while you are away, stopping at the 15% weekly reserve | (z) decide later
  raised: 2026-09-28
  what: whether I may keep dispatching while you are away
  why now: weekly quota is 0% used with ~6.6 days to reset, and you want the backlog caught up; your 68 answer tied librarian quota use to the agents scheduler
  (a): slower catch-up; nothing spends quota unseen — undo: lift any time — who: you
  (b): faster catch-up; landings and pushes happen while you are away, reviewed by opus but not seen by you until you return — undo: say stop; reinstated at once — who: you, and peers that pull the marketplace
  rec: (a) · basis: partial — your 68 answer; no scheduler yet
  unknown: whether the agents scheduler lands this week
answer 87: (a) A-D, "work in whatever order makes sense to you" (operator 2026-09-28)
answer 88: (b) the no-unattended-dispatch hold is lifted for this week: keep working the queue between turns and while the operator is away, stopping at the 15% weekly reserve (operator 2026-09-28)
decision 132: Which waves of tonight's plan may run unattended (plan shown 2026-09-30 in chat; weekly 41% used, stop at 85%)? — options: (a) waves 1-3, stopping at the reserve; waves 4-5 wait for your review [recommended] | (b) all five waves, stopping at the reserve | (c) wave 1 only | (z) decide later
  raised: 2026-09-30
  rec: (a) · basis partial — per-item cost from past rounds (~0.5-1% weekly per planner or review round), not measured per feature
answer 132: a — "wave 1 approved, continue on up through wave 3 and I'll check on your progress later" (2026-09-30T22:17Z, chat)
answer 133: a — "133a" (2026-09-30T22:22Z, chat; operator relaunches; the new session runs waves 1-3 per 132 a)
decision 146: Weekly usage is at 82%, 3 points from your 85% stop on new dispatch, and climbing about 1 point an hour; the reset is 2026-10-05 11:00 UTC. What should happen to the work you just approved? — options: (a) keep the 85% stop: finish what is running (the scan floor's last round, the prices fix, the research-routing plan), and queue the spend reader, the budget rule and the research-routing build until the reset [recommended] | (b) raise the stop to 90% for these items only, so the spend reader and the research-routing build can land before the reset | (c) stop new dispatch now, at 82% | (z) decide later
  raised: 2026-10-02T22:09Z
  what: whether your 85% weekly stop holds for the work approved today (answers 144 a, 145 a, and the research routing go-ahead)
  why now: the reading crosses 85% in about three hours at today's rate, mid-way through that work; blocks: the spend reader (0865), the budget rule (5bdd) and the research-routing build (e184) past their current step
  why ask: spend — your threshold (answer 132 a / 133 a); moving it is yours
  context: you set the 85% weekly stop for the unattended run; today you approved 144, 145 and the research routing to land · you decide whether the stop holds for that work — then: none
  stakes: reversible, narrow — this week's quota
  (a) keep 85% — running work finishes (each step is about $4-30 list price, roughly 0.2-1.4% of a week); new steps after the line wait about 2.5 days; nothing is lost, each item keeps its handoff — undo: lift it later — who: the queued items
  (b) 90% for these items — the spend reader and research routing likely land this week; about 5 more points of the week go to them, leaving 10% for everything else until the reset — undo: n/a once spent — who: your other sessions' headroom this week
  (c) stop now — the running agents finish; nothing new starts until the reset
  (z) decide later — as (a) by default: the 85% stop is the rule in force
  rec: (a) · basis strong — the rule is yours and the queued work loses nothing by waiting; this week's spend is already high
  unknown: how much the research-routing plan and its reviews will cost (planner runs this week were $13-40 each)
decision 152: How should the agent-scope protocol you just described start? — options: (a) a plan-only spike here after Sunday's weekly reset, with the agents librarian asked now which parts its control plane already covers [recommended] | (b) the same spike now, past the weekly stop if needed | (c) hand it to the agents repo to own, with this repo implementing the librarian-mode side | (z) decide later
  raised: 2026-10-03T05:05Z
  what: the first step on agent scope of responsibility (agent-scope-protocol-declared-scope-the-51df): declared scope, the observability and credentialed access that come with it, advertising it, and escalating overlaps to you
  why now: you just asked for it; blocks: nothing
  why ask: placement — it spans this repo's librarian-mode (Scope, claims, forwarding 3460) and the agents repo's control plane (claims, ledger), and credentialed access is a trust question; where it is owned is yours
  context: you described the protocol just now, after a day of peers relaying consent and stepping on blurry lines · you decide where it starts and when — then: none
  stakes: reversible, narrow — planning only
  (a) plan here after the reset, agents asked now — a cheap peer question now avoids planning what their back end already does; the plan comes back with placement and the credential questions for you — undo: n/a — who: this repo and agents
  (b) plan now — starts today; a planner run is about 1-2% of a week, with weekly at 83% of your 85% stop
  (c) the agents repo owns it — fits its control-plane role; this repo builds the librarian-mode half when their spec lands
  (z) decide later — the item waits
  rec: (a) · basis partial — the agents back end already has claims and a ledger, so asking first avoids duplicate design; quota is tight until Sunday
  unknown: how much of this the agents control-plane plan already covers
answer 152: 152a - I'm imagining a simple skill change in the librarian skill in the short term (interview scope for the Librarian CLAUDE.md section, ask to fill it for repos that don't have it filled yet). Good to consider the long-term solution for this with the `agents` librarian too (read as: (a), shaped — short term, a librarian-mode skill change: the opt-in interviews the repo's scope of responsibility into the ## Librarian section, and a librarian whose repo's section lacks it asks to fill it at start; long term, worked out with the agents librarian, asked now)
note: 2026-10-05 17:36Z — moot: the weekly window reset (2026-10-05 11:00 UTC) before any queued work crossed 85%; the librarian withdraws decision 146 unless the operator objects; the queued work (spend reader 0865, the scope interview plan 5925) starts under the 85% stop as it stands
decision 176: When the weekly quota is plentiful, should reaching an item's spend budget still stop and ask you, or just be noted while the rounds go on? — options: (a) below 50% weekly use, a reached budget is noted in the Report and rounds continue; at or above 50% it asks as today [recommended] | (b) double every default budget, asks unchanged | (c) keep the budgets as they are | (z) decide later
  raised: 2026-10-06T19:10Z
  what: how the per-item spend budget (answer 145 a) behaves while your subscription quota is cheap; the dollar figures are list-price equivalents, not money you pay
  why now: you said you don't want good work cut off early to save quota that is cheap right now; blocks: nothing
  why ask: rule-change — the budget rule is yours (145 a)
  context: you replaced the round cap with a spend budget per item (145 a) · you decide whether plentiful quota should loosen it
  impact: → while the week is under half used, no item stops to ask you about its budget; you see the overrun in the Report · later: budgets keep asking at today's amounts · reach: every dev-cycle item the librarian runs · undo: an edit
  (a) quota-aware — the convergence stop (a review whose must-fix count stops falling) and the reserve guards stay; only the budget ask is waived under 50% weekly
  (b) double the defaults — fewer asks at any quota level; still asks at the new amounts
  (c) keep as is — asks at $10 chore, $12 bug, $22 build, $28 plan, $40 spike
  (z) decide later — budgets stay as they are
  rec: (a) · basis partial — it ties the ask to what is actually scarce, your quota, and keeps the stop that catches work going in circles
  unknown: whether 50% is the right line for you
answer 176: 176a (2026-10-06T19:28Z, chat; read as: (a) quota-aware — below 50% weekly use a reached budget is noted in the Report and rounds continue; at or above 50% it asks as today; the convergence stop and the reserve guards stay)
helper: scribe sonnet low — cards.json for the decision page (15 open decisions) — agent ae38c041c289219b5
