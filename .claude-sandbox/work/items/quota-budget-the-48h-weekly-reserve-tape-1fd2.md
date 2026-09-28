---
id: quota-budget-the-48h-weekly-reserve-tape-1fd2
title: "quota_budget: the 48h weekly reserve taper from agents decision 0008"
type: feature
status: doing
priority: 3
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:20Z
created: 2026-09-24
updated: 2026-09-28
refs:
  - b112 open question; agents decisions/0008
---

agents decision 0008 ratifies a 5% reserve floor with a 48h weekly taper; quota_budget.py has no taper (budget.md lists 'the decaying weekly reserve' under Not here yet). Acceptance: the taper as 0008 specifies, with tests; waits on the idle-turn work's hold (scheduler) only if the taper depends on it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-quota-budget-the-48h-weekly-reserve-tape-1fd2 at .claude/worktrees/quota-budget-the-48h-weekly-reserve-tape-1fd2, base main (3d7760d)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — script and tests (rule 2)
agent: implementer a0deed94afae4f00d round 1
