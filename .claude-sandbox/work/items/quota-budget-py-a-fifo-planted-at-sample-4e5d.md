---
id: quota-budget-py-a-fifo-planted-at-sample-4e5d
title: "quota_budget.py: a FIFO planted at samples.jsonl or a sink day-file blocks open indefinitely"
type: bug
status: doing
priority: 4
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:24Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - 99b4 review r2
---

99b4 reviewer note, 2026-09-22: O_NOFOLLOW does not stop a FIFO; append's O_WRONLY open and read_jsonl's open both block with no peer. Acceptance: open non-blocking and refuse a non-regular file (fstat S_ISREG), for both the store and sink paths; test with a FIFO in a temp store.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full quota-budget-py-a-fifo-planted-at-sample-4e5d /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/quota-budget-py-a-fifo-planted-at-sample-4e5d
dispatch: implementer opus — executable logic (quota_budget.py), small local edit
agent: implementer a8e9b1951f050f36b round 1
return: implementer DONE 68bbf4d
changed: quota_budget.py (open_regular), scripts/tests/test_quota_budget.py (TestFifo), references/budget.md
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a9f263fa50130eb00 round 1
