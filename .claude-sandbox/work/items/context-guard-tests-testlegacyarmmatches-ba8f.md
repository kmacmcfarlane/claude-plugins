---
id: context-guard-tests-testlegacyarmmatches-ba8f
title: "context-guard tests: TestLegacyArmMatchesMain compares against the moving main ref, false red in any older worktree"
type: bug
status: doing
priority: 2
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:40Z
created: 2026-09-22
updated: 2026-09-23
refs:
  - 9ec9 review r2
---

9ec9 reviewer, 2026-09-22: tests/test_rehydrate.py:286-293 builds its expected output from git show main:…, so any worktree cut before a context-guard change lands on main fails 30 tests though it touches no context-guard file; every parallel dev-cycle review hits it. Acceptance: compare against the merge-base of HEAD and main (or HEAD's own parent tree for the legacy hooks), so the test judges this branch's change only; test that it stays green in a worktree behind main.

## Handoff
- doing: implementer DONE at 42ecd0d, not yet reviewed
- next: after Rehydrate: dispatch an opus reviewer (common-review brief): judge the pinned-baseline choice vs merge-base, that a real legacy-arm regression still fails, the shallow/tarball skips, and whether the notice tests should run without git
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full context-guard-tests-testlegacyarmmatches-ba8f /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/context-guard-tests-testlegacyarmmatches-ba8f
dispatch: implementer opus — executable logic (context-guard tests)
agent: implementer afaf2a529d1566917 round 1
return: implementer DONE 42ecd0d (pinned baseline e8ff7fd = 92c9738^1, the last pre-store tree; skips on no git / shallow; class renamed TestLegacyArmMatchesPreStore)
dispatch: reviewer opus — implementer tier opus (executable logic: context-guard tests)
agent: reviewer aa775351c71a2503c round 1
verdict: NEEDS_CHANGES round 1 at 42ecd0d (1 medium: the documented re-pin remedy is unworkable and contradicts the meta-test, and inject() writes the ledger with the current module for both sides; 3 low, 1 nit). Pinned-baseline choice judged right; all 8 legacy-arm mutations fail the guard.
dispatch: implementer opus — resume, fix round 1
agent: implementer afaf2a529d1566917 round 2
