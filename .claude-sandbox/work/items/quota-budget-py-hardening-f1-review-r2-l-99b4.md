---
id: quota-budget-py-hardening-f1-review-r2-l-99b4
title: "quota_budget.py hardening: F1 review r2 lows"
type: chore
status: doing
priority: 3
owner: unknown@bf9f9839222c
claimed: 2026-09-22T22:26Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - 9882 review r2
---

From 9882 review r2 (CLEAR) lows, 2026-09-22: L1 replaced-unreadable only on a JSON parse failure of a regular file under READ_MAX, else conflict; L2 open samples.lock O_RDWR|O_CREAT|O_NOFOLLOW (fallback O_RDONLY) — a planted symlink currently creates its target outside the store; L3 narrow read_jsonl's except to parse errors or count skipped lines; L4 budget.md:8 cite 'the librarian's decision on R1, recorded on work item 9882'.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@bf9f9839222c

target: full quota-budget-py-hardening-f1-review-r2-l-99b4 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/quota-budget-py-hardening-f1-review-r2-l-99b4
dispatch: implementer opus — executable logic (quota_budget.py), a symlink-containment low; small local edit so not rule 3
agent: implementer afc16f05662a9b76e round 1
return: implementer DONE e1cc057
changed: quota_budget.py, scripts/tests/test_quota_budget.py, references/budget.md
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a6e630e2326326e41 round 1
