---
id: rehydrate-chore-only-rewind-reads-0-0-gi-3685
title: "rehydrate: chore-only rewind reads 0/0, 'git unavailable' for non-repo, behind-side drift, systemMessage drops reason"
type: chore
status: doing
priority: 4
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:59Z
created: 2026-09-18
updated: 2026-09-18
---

From the b02c review (2026-09-18), all low: (1) HEAD rewound over store-only commits -> 'not an ancestor' + '0 commits ahead, 0 behind' — treat a store-only rewind as FRESH or word it; (2) '(git unavailable)' also shows for a non-repo / empty repo — use 'head unverified' or document; (3) STALE drift ignores the behind side (50 behind reads AGED); (4) user-facing systemMessage prints the bare label without the reason. File: plugins/context-guard/hooks/rehydrate.py, tests, handoff-format.md.

## Handoff
- doing: bundled in worktree 3685
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — executable logic; bundled 3685+fe33 (both touch rehydrate.py)
