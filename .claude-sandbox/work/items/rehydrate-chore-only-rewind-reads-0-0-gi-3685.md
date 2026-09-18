---
id: rehydrate-chore-only-rewind-reads-0-0-gi-3685
title: "rehydrate: chore-only rewind reads 0/0, 'git unavailable' for non-repo, behind-side drift, systemMessage drops reason"
type: chore
status: todo
priority: 4
created: 2026-09-18
updated: 2026-09-18
---

From the b02c review (2026-09-18), all low: (1) HEAD rewound over store-only commits -> 'not an ancestor' + '0 commits ahead, 0 behind' — treat a store-only rewind as FRESH or word it; (2) '(git unavailable)' also shows for a non-repo / empty repo — use 'head unverified' or document; (3) STALE drift ignores the behind side (50 behind reads AGED); (4) user-facing systemMessage prints the bare label without the reason. File: plugins/context-guard/hooks/rehydrate.py, tests, handoff-format.md.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
