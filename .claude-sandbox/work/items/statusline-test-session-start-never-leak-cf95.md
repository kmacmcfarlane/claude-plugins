---
id: statusline-test-session-start-never-leak-cf95
title: statusline test_session_start_never_leaks false-fails when the checkout path contains 'context-guard'
type: bug
status: doing
priority: 2
owner: unknown@360f41058e92
claimed: 2026-09-21T23:12Z
created: 2026-09-21
updated: 2026-09-21
refs:
  - 73a6 implementer
---

Found by 73a6's implementer 2026-09-21: plugins/statusline/hooks/tests/test_standalone.py test_session_start_never_leaks asserts the written manifest never contains 'context-guard', but the manifest records an absolute path, so any worktree named after a context-guard item (.claude/worktrees/context-guard-…) fails the statusline suite — blocks the librarian's Checks on those branches. Acceptance: the assertion ignores the checkout/plugin-root path (e.g. strip the test's own root before matching, or match references to the context-guard plugin rather than the substring); test passes under a path containing 'context-guard'.

## Handoff
- doing: implementer dispatched (sonnet, agent abe03223a8ae1a8f5)
- next: on DONE: review r1 (opus); land before 73a6 so its Checks run green
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer sonnet — one test file, mechanical

## Implementer result
- round 1 DONE 1756f50 (sonnet): scrubs the checkout root before the leak check; proved old fails under a context-guard path, new passes; still fails on a real leak.
- dispatch: reviewer opus — rule 4
