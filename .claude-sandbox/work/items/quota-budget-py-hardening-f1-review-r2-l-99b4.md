---
id: quota-budget-py-hardening-f1-review-r2-l-99b4
title: "quota_budget.py hardening: F1 review r2 lows"
type: chore
status: done
priority: 3
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
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
verdict: NEEDS_CHANGES round 1 at e1cc057
findings:
- [medium] quota_budget.py:323 — append_sample opens samples.jsonl O_WRONLY|O_APPEND|O_CREAT without O_NOFOLLOW: a planted symlink writes a sample line to a target outside the store, exit 0 (probe A). Same hazard L2 closes, worse (writes content); L2 is moot while this is open. Pass: O_NOFOLLOW there, failing as a store write error; test beside the lock-symlink test; optionally read_jsonl too.
- [low] budget.md:170 — "not a regular file (a symlink…)" is conflict/unusable, but a symlink to a parseable claim is refreshed (link replaced). Pass: wording.
- [low] budget.md:8 — overlong line; reflow.
- [nit] no run_qb test for a parse-callback exception reaching main (rc 1, internal error).
notes: deviations all accepted; F2's idle turn must know unusable:true cannot be cleared by --takeover; FIFO at samples.jsonl blocks open — out of scope.
dispatch: implementer opus — fix round 1 (resume)
return: implementer DONE 60d6d77
dispatch: reviewer opus — review r2 (resume)
verdict: CLEAR round 2 at 60d6d77
landed: a5c7aaa
- 2026-09-22 done: a5c7aaa
