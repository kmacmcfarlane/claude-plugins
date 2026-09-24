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
updated: 2026-09-23
---

idle-turn.md mode table (full/normal/conservative/stop), N from allowed rate ÷ per-agent rate ÷ active librarians, cap 6, floor 1 for P0; claims on dispatch; quiet mode away; self-wake ≤1 h; walkthrough. Opus (doctrine). Plan: .claude-sandbox/investigations/1222-unattended-librarian/00_initial.md § F2.

## Handoff
- doing: —
- next: on 68(a): planner writes 1222 serial 05 with the two rulings + the Esc low; close the plan; file F2a-F2d as children
- blocked: awaiting decisions 68 (plan cap ruling), 69 (B1), 70 (B2)
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
agent: reviewer afb3f69db46fcf792 round 1
verdict: NEEDS_CHANGES plan round 1 (1 high, 11 medium) — findings verbatim at /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/e9bb00fc-c89f-4c8e-a7ca-b4c1e9ccbc73/scratchpad/c79e/plan-review-r1.md (scratchpad; summary: re-arm unconditionally after Rehydrate; duplicate-loop dedupe; post-checkpoint gap; allowed-tools; one owner per admission rule; P0 floor stated once; floor vs U; sprint semantics; hysteresis on new readings; slot-leak reconcile; calibration under-count; two-writer hold keep-alive)
dispatch: planner opus — plan fix round 1 (resume), revises by a new serial 02
agent: planner a284b6b14c97d6192 round 2
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/1222-unattended-librarian/02_review-round-1.md (all 23 findings fixed, none declined)
baseline: f1aa0b775916 .claude-sandbox/investigations/1222-unattended-librarian/00_initial.md;1687d7eb5206 .claude-sandbox/investigations/1222-unattended-librarian/01_f2-modes-pool-heartbeat.md;fe767a12a5d6 .claude-sandbox/investigations/1222-unattended-librarian/02_review-round-1.md;
dispatch: reviewer opus — plan re-review r2 (resume)
agent: reviewer afb3f69db46fcf792 round 2
verdict: NEEDS_CHANGES plan round 2 (1 high, 3 medium, 4 low) — findings at /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/e9bb00fc-c89f-4c8e-a7ca-b4c1e9ccbc73/scratchpad/c79e/plan-review-r2.md (high: the dedupe kills a fresh arm after compaction; floor cap; tier-bump bypass; re-arm triggers in two places)
dispatch: planner opus — plan fix round 2 (resume), new serial 03
agent: planner a284b6b14c97d6192 round 3
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/1222-unattended-librarian/03_review-round-2.md (all 8 fixed, none declined)
baseline: f1aa0b775916 .claude-sandbox/investigations/1222-unattended-librarian/00_initial.md;1687d7eb5206 .claude-sandbox/investigations/1222-unattended-librarian/01_f2-modes-pool-heartbeat.md;fe767a12a5d6 .claude-sandbox/investigations/1222-unattended-librarian/02_review-round-1.md;0eba08865ae3 .claude-sandbox/investigations/1222-unattended-librarian/03_review-round-2.md;
dispatch: reviewer opus — plan re-review r3 (resume); round 3 of the cap of 4
agent: reviewer afb3f69db46fcf792 round 3
verdict: NEEDS_CHANGES plan round 3 (1H 3M MUST-CHANGE, all local textual; 3 low) — /home/rt/.claude/tmp/claude-1000/-home-rt-work-src-github-com-kmacmcfarlane-claude-plugins/e9bb00fc-c89f-4c8e-a7ca-b4c1e9ccbc73/scratchpad/c79e/plan-review-r3.md
dispatch: planner opus — plan fix round 3 (resume), serial 04; review round 4 is the last under the cap
agent: planner a284b6b14c97d6192 round 4
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/1222-unattended-librarian/04_review-round-3.md (4 must-change fixed per Pass, 2 declared extensions; 3 lows taken)
baseline: f1aa0b775916 .claude-sandbox/investigations/1222-unattended-librarian/00_initial.md;1687d7eb5206 .claude-sandbox/investigations/1222-unattended-librarian/01_f2-modes-pool-heartbeat.md;fe767a12a5d6 .claude-sandbox/investigations/1222-unattended-librarian/02_review-round-1.md;0eba08865ae3 .claude-sandbox/investigations/1222-unattended-librarian/03_review-round-2.md;f80f8166014f .claude-sandbox/investigations/1222-unattended-librarian/04_review-round-3.md;
dispatch: reviewer opus — plan re-review r4 (resume), the LAST under the cap
agent: reviewer afb3f69db46fcf792 round 4
verdict: NEEDS_CHANGES plan round 4 at 04 f80f8166014f — the CAP (4 plan-review rounds) reached. Round-3 fixes verified; two MUST-CHANGE left, each a one-sentence edit to 04 § A.1 and § B.1 (reviewer: adoptable verbatim as the operator's ruling, no re-plan):
- [medium] 04:47-57 — a checkpoint crossing an all-dispatch hold deadlocks dispatch: Rehydrate skips trigger 1 under the hold, so checkpoint_pending stays; after the hold lifts, trigger 2 and every slot take refuse "checkpoint" until a later Rehydrate. Pass: every Rehydrate clears checkpoint_pending and the due time; only the ARM is skipped under the hold; test "checkpoint, compaction under an all-dispatch hold, then lift: re-arms and takes admit".
- [medium] 04:117,122-128 — a planned item's implementer dispatch after its planner slot is a "tier change" and bypasses stop, the two-writer hold and the checkpoint (same/down tier: no checks; up: only 1, 2, 9). Pass: the implementer's first dispatch after a planner runs the full order 1-10 with r_old (floor rules per B.1); the reduced check only for fix-round rises; test "planner slot held, raw stop, implementer take refused stop".
- [low] 04:87-89 — Esc is re-armed by trigger 2; say in heartbeat.md a durable stop is a hold, not Esc.
decision 68: c79e plan hit the 4-round review cap with two one-sentence must-change fixes left (a checkpoint crossing a hold deadlocks dispatch; a planned item's implementer dispatch skips stop/hold/checkpoint) — (a) rule both fixes in as the reviewer's Pass text says, the planner writes serial 05 with only those two edits plus the low, and the plan closes with the fixes recorded as operator rulings (no fifth review) [recommended]; (b) allow one more review round after 05; (c) park F2 as is.
decision 69: B1 (gates F2d only) — how to settle whether the librarian can arm /loop itself, whether a dynamic loop survives compaction, whether a second ScheduleWakeup replaces the pending one, whether arming prompts, and whether the arm runs at once — (a) run the five-step probe in the librarian's own session before F2d, the operator doing the /compact step [recommended]; (b) ship F2d with the operator-typed /loop line as primary; (c) defer F2d.
decision 70: B2 (gates F2c's switch-on sentence) — when F2c lands, before the agents repo ratifies its budget policy, is the estate-wide pool enforced? — (a) enforce, with the sprint grant available for present bursts like today's [recommended]; (b) report-only until agents ratifies; (c) enforce only when away. Note: at today's burn the pool allows the P0 floor plus one sonnet agent while you are present; this session ran 3-7 under your "run to the reserve", which the plan records as a sprint grant.
note: plan-review findings r1-r3 copied to .claude-sandbox/investigations/1222-unattended-librarian/reviews/ (the scratchpad paths above are session-scoped)
- 2026-09-24 agents - librarian, first-hand from the operator: agents decision 4 answered "(a) sure, let's start with that and refine". The 8ad9 budget policy is ratified as DEFAULTS: pool share 0.5 present / 1.0 away; one estate-wide P0 floor slot; a 5% reserve floor, with the weekly reserve tapering over its last 48 h; never spill into extra usage; claim-file liveness (series agents .claude-sandbox/investigations/librarian-budget-policy/). This changes decision 70's premise ("before agents ratifies"): the pool is ratified. OQ6 (pool + P0 floor) is buildable; OQ7 stands as sent.
