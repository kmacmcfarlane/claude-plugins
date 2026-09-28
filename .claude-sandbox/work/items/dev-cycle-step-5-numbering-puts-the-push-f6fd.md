---
id: dev-cycle-step-5-numbering-puts-the-push-f6fd
title: "dev-cycle: Step 5 numbering puts the push (5.3) before landed: (5.5); a run dying between merge and landed: reads STALE"
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T23:02Z
created: 2026-09-28
updated: 2026-09-28
refs:
  - 16da review
---

From the 16da review 2026-09-28: SKILL.md Step 5 numbering puts the push at 5.3 and landed: at 5.5; only 'the moment the merge succeeds' says landed: comes first — an executor following the numbers pushes before recording; Step 5 never runs the MERGE_HEAD check the troubleshooting bullet says happens at Land; and a run that dies between merge and landed: (worktree already cleaned) reads STALE and may re-land merged work. Acceptance: the order made explicit in Step 5; Land checks MERGE_HEAD; the STALE case handled or documented.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-28 from the 16da review (lows): S0b's report reads 'not resumable' even when the pending MERGE_HEAD may be the operator's own — say 'a merge is pending in the main checkout (one this run may not have made)'; troubleshooting.md:60-62 S0b symptom bullet still says the orphan-worktree rule decides, but a pending merge now routes to the merge bullet
target: branch worktree-dev-cycle-step-5-numbering-puts-the-push-f6fd at .claude/worktrees/dev-cycle-step-5-numbering-puts-the-push-f6fd, base main (4dcf3de)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — changes Step 5's order and Land's checks (rule 2)
agent: implementer ad34ddcd4498110e0 round 1
