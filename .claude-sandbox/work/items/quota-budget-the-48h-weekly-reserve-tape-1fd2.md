---
id: quota-budget-the-48h-weekly-reserve-tape-1fd2
title: "quota_budget: the 48h weekly reserve taper from agents decision 0008"
type: feature
status: done
priority: 3
created: 2026-09-24
updated: 2026-09-28
closed: 2026-09-28
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
return: implementer DONE_WITH_CONCERNS 451ae91 (weekly floor 3 per 0008, not the brief's 5; reserves.seven_day now carries the tapered value)
changed: plugins/dev-flow/skills/librarian-mode/scripts/quota_budget.py, scripts/tests/test_quota_budget.py, references/budget.md
librarian decision: weekly floor 3 as 0008 specifies — the brief's '5%' was imprecise (0008's 5% floor and the operator's 5% ruling are the 5h reserve)
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer afb87028a8f73a202 round 1 at 451ae91
verdict: CLEAR round 1 at 451ae91 (2 low: budget.md should say reserves.seven_day is the reserve in effect; one test name claims a binding move it does not show; 1 nit width — declined for this landing, filed as a follow-up chore)
landed: fda88a3
- 2026-09-28 done: fda88a3
