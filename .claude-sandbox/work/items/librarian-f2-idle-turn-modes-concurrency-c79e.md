---
id: librarian-f2-idle-turn-modes-concurrency-c79e
title: "librarian F2: idle-turn modes, concurrency from the budget, quiet mode, self-wake, stop"
type: feature
status: doing
priority: 1
deps:
  - librarian-f1-quota-budget-py-and-the-per-9882
parent: librarian-work-unblocked-items-and-pre-i-1222
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:40Z
created: 2026-09-22
updated: 2026-09-22
---

idle-turn.md mode table (full/normal/conservative/stop), N from allowed rate ÷ per-agent rate ÷ active librarians, cap 6, floor 1 for P0; claims on dispatch; quiet mode away; self-wake ≤1 h; walkthrough. Opus (doctrine). Plan: .claude-sandbox/investigations/1222-unattended-librarian/00_initial.md § F2.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- agents librarian 2026-09-22: the registry name-pattern divisor clashes with librarian-mode session-name.md:24-25 (read only your own registry file; never list the directory); prefer a self-written claim/heartbeat file with an expiry in the per-subscription store. Their policy series: agents .claude-sandbox/investigations/librarian-budget-policy/ (in progress) — fold its answer into a 01 serial before dispatching F2.
- agents 8ad9 policy answer 2026-09-22 (reviewed CLEAR; operator ratification pending as agents decision 4; values are defaults), series agents .claude-sandbox/investigations/librarian-budget-policy/ (00-02):
  - active librarians = fresh claim files with demand, claims/<repo>.json (session_id, session_name, pid, pidDomain, procStart from own registry file; heartbeat at; in_flight; demand); stale 2 h idle / 4 h in flight; takeover on pid match or no live same-name session (in_flight reset); two live writers (ListAgents or a claim flip) → E0 hold both; tombstones only for idle claims (>30 min, name absent); non-librarian claims keyed claims/<repo>.<kind>.json.
  - N: ONE estate-wide pool, N_total = floor(share × allowed rate ÷ per-slot rate), share 0.5 present / 1.0 away — replaces this item's per-librarian quotient; estate-wide P0 floor slot when N_total = 0 and mode ≠ stop, E0 if a P0 waits > 30 min; absent signal N_total = 2.
  - self-wake ≤ 1 h while held by the pool AND under a two-writer hold; claims.log.jsonl; optional slot token.
  - OQ14: do background agents survive /clear? If so a same-process /clear keeps in_flight.
  - At today's pace the pool is 0 while the operator is present, 1 away; estate burning ~2× the sustainable weekly pace.
- Before dispatch: write 1222 serial 01 folding this in (supersedes 00 § F2 N formula and divisor).

from 9882 (F1) review, 2026-09-22 — F2 inputs: (1) mode and N are chosen here, not in quota_budget.py (librarian decision on 9882 R1); (2) allowed rate is unbounded just before a reset — cap or ignore a window about to reset; (3) claims refresh-vs-takeover window left open in F1 (budget.md § Claims) — close with the two-writer hold / a lock all writers hold.
decision 55: F2 mode logic (answer to 49's ask) — (a) adopt the librarian's proposal: stop when either window is spent to its reserve; conservative when velocity > allowed rate; full when velocity ≤ half the allowed rate and headroom ≥ 20 points; normal otherwise and on no signal; re-evaluated each idle turn and at next_check; step up one level per check, step down at once [recommended]; (b) the operator adjusts thresholds; (c) leave it to the F2 planner.
answer 55: (c) leave the mode logic to the F2 planner (the librarian's proposal is an input, not a ruling) (operator 2026-09-22)

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: plan librarian-f2-idle-turn-modes-concurrency-c79e /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/1222-unattended-librarian
dispatch: planner opus — plan mode; a plan is judgement (Step 1 minimum opus); doctrine
agent: planner a284b6b14c97d6192 round 1
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/1222-unattended-librarian/01_f2-modes-pool-heartbeat.md (verification sub-agent skipped for quota; B1 gates F2d, B2 gates F2c)
baseline: f1aa0b775916 .claude-sandbox/investigations/1222-unattended-librarian/00_initial.md;1687d7eb5206 .claude-sandbox/investigations/1222-unattended-librarian/01_f2-modes-pool-heartbeat.md;
dispatch: reviewer opus — plan-review variant, plan mode floor
