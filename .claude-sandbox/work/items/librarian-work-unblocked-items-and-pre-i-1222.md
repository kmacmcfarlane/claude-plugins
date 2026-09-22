---
id: librarian-work-unblocked-items-and-pre-i-1222
title: "librarian: work unblocked items and pre-investigate the rest while idle, without burning quota"
type: spike
status: doing
priority: 0
owner: unknown@360f41058e92
claimed: 2026-09-22T02:36Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - operator 2026-09-22
---

Operator 2026-09-22: an idle librarian should work new items as they arrive when no operator decision is needed (doc-only requests nearly always; skill changes often; implementation or complex skill changes warrant an investigation round). Investigations can run without waiting on the operator, so when the operator returns the decisions are ready to present. Today items queue up waiting for attention when many are unblocked or at least investigable. Question: how to achieve this without accidentally running the operator's quota into the ground. Acceptance: an investigation series with findings and a recommendation (routing rules for what proceeds unattended vs what waits; quota guards; how investigations pre-run and park their decisions), presented to the operator; decisions raised by number.

## Handoff
- doing: answers recorded; running investigate in-session (fable)
- next: present findings + numbered decisions; then prompt for the opus switch
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
