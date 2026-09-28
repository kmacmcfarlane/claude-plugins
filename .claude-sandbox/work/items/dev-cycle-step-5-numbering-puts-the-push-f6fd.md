---
id: dev-cycle-step-5-numbering-puts-the-push-f6fd
title: "dev-cycle: Step 5 numbering puts the push (5.3) before landed: (5.5); a run dying between merge and landed: reads STALE"
type: bug
status: todo
priority: 3
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
