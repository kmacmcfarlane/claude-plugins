---
id: quota-budget-py-hardening-f1-review-r2-l-99b4
title: "quota_budget.py hardening: F1 review r2 lows"
type: chore
status: todo
priority: 3
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
