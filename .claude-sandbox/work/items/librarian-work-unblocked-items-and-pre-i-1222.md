---
id: librarian-work-unblocked-items-and-pre-i-1222
title: "librarian: work unblocked items and pre-investigate the rest while idle, without burning quota"
type: spike
status: doing
priority: 0
owner: unknown@360f41058e92
claimed: 2026-09-22T02:36Z
created: 2026-09-22
updated: 2026-09-23
refs:
  - operator 2026-09-22
---

Operator 2026-09-22: an idle librarian should work new items as they arrive when no operator decision is needed (doc-only requests nearly always; skill changes often; implementation or complex skill changes warrant an investigation round). Investigations can run without waiting on the operator, so when the operator returns the decisions are ready to present. Today items queue up waiting for attention when many are unblocked or at least investigable. Question: how to achieve this without accidentally running the operator's quota into the ground. Acceptance: an investigation series with findings and a recommendation (routing rules for what proceeds unattended vs what waits; quota guards; how investigations pre-run and park their decisions), presented to the operator; decisions raised by number.

## Handoff
- doing: session e9bb00fc ran the queue under the quota meter; weekly 42→47%; ~35 landings
- next: after compaction: land the in-flight three (c121, 8519, ba8f); await answers 68-70 for c79e; then the P2/P3 queue: 9197, 0aaa, fc04, 8e14, 6f1c (wi.py, serial), 3c4f, 87fd, 6641, 0d6b (fable), caef (fable), 8ab6 items, 0599, ee7b, 09f1, 3460, d05d, bfd6, b8d6, 5a18, 0900
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
