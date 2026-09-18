---
id: rehydrate-chore-only-rewind-reads-0-0-gi-3685
title: "rehydrate: chore-only rewind reads 0/0, 'git unavailable' for non-repo, behind-side drift, systemMessage drops reason"
type: chore
status: done
priority: 4
created: 2026-09-18
updated: 2026-09-18
closed: 2026-09-18
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

impl: DONE 2ef111a (bundle; also fixed latent postcompact "0 tok" ledger header).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (.swept stamp write follows symlinks: empties a file outside the dir; reproduced); lows 2 (sweep unlinks a locked lock path; _acquire never re-checks inode), 3 (mark_checkpoint with a typo sid creates a stray json and reports success), 4 (glob with two data dirs), nit 5.
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE 46cdbd9 (1-5; mark_checkpoint refuses unknown ids; scope grew to mark_checkpoint.py + one test for finding 3).
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR. CORRECTION: the "ledger header always said 0 tok" claim was false — context_warn writes top-level tokens every prompt; the change now prefers exact.tokens. Lows to follow-up.
- 2026-09-18 done: 799cc0b
