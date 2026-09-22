---
id: librarian-work-unblocked-items-and-pre-i-1222
title: "librarian: work unblocked items and pre-investigate the rest while idle, without burning quota"
type: spike
status: todo
priority: 0
created: 2026-09-22
updated: 2026-09-22
refs:
  - operator 2026-09-22
---

Operator 2026-09-22: an idle librarian should work new items as they arrive when no operator decision is needed (doc-only requests nearly always; skill changes often; implementation or complex skill changes warrant an investigation round). Investigations can run without waiting on the operator, so when the operator returns the decisions are ready to present. Today items queue up waiting for attention when many are unblocked or at least investigable. Question: how to achieve this without accidentally running the operator's quota into the ground. Acceptance: an investigation series with findings and a recommendation (routing rules for what proceeds unattended vs what waits; quota guards; how investigations pre-run and park their decisions), presented to the operator; decisions raised by number.

## Handoff
- doing: filed; follow-up questions to the operator
- next: answers → run investigate (this session, fable) → present findings + decisions
- blocked: —
- learned: —

## Librarian notes
- Subsumes the design question of d05d (auto-investigation per item; decision 49 open) and builds on 693a (idle turn), b020 (grooming/needs-input), 810f (holds). d05d's peer tensions 1-7 are input.
- Investigation run in the librarian session itself on fable at the operator's request (2026-09-22); series home .claude-sandbox/investigations/1222-unattended-librarian/.
- Model note: operator switched this session to fable for the investigation; prompt to switch back to opus 5 before resuming other items.
