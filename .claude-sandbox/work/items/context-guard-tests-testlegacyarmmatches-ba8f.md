---
id: context-guard-tests-testlegacyarmmatches-ba8f
title: "context-guard tests: TestLegacyArmMatchesMain compares against the moving main ref, false red in any older worktree"
type: bug
status: todo
priority: 2
created: 2026-09-22
updated: 2026-09-22
refs:
  - 9ec9 review r2
---

9ec9 reviewer, 2026-09-22: tests/test_rehydrate.py:286-293 builds its expected output from git show main:…, so any worktree cut before a context-guard change lands on main fails 30 tests though it touches no context-guard file; every parallel dev-cycle review hits it. Acceptance: compare against the merge-base of HEAD and main (or HEAD's own parent tree for the legacy hooks), so the test judges this branch's change only; test that it stays green in a worktree behind main.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
