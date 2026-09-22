---
id: quota-budget-py-4e5d-review-lows-claim-p-f381
title: "quota_budget.py 4e5d review lows: claim-path FIFO test, budget.md wording, O_NOCTTY"
type: chore
status: todo
priority: 4
created: 2026-09-22
updated: 2026-09-22
refs:
  - 4e5d review r1
---

4e5d review lows, 2026-09-22: test_quota_budget.py:1034's claim-path FIFO test passes on the old code — split the mocked-lstat claim_file_state assertion into its own SIGALRM-guarded test; budget.md:64-65 'reads as absent' is wrong for a claim path (an unusable conflict) and the line is not reflowed; add os.O_NOCTTY to open_regular (a symlink to a tty on a follow path).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
