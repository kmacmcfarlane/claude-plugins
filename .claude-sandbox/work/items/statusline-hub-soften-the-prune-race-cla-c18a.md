---
id: statusline-hub-soften-the-prune-race-cla-c18a
title: "statusline-hub: soften the prune-race claim in hook-contract § 11; test or drop _dead_segment's read-vs-lstat check"
type: chore
status: todo
priority: 4
created: 2026-09-22
updated: 2026-09-22
refs:
  - 5cde review r1
---

5cde review lows, 2026-09-22: hook-contract.md:391 claims a rewrite during the pass always survives, but lstat→unlink leaves a microsecond window (POSIX cannot unlink by inode) — say so; housekeeping.py:187-189's identity check in _dead_segment is untested and redundant with _unlink_if_same — add a swap test or drop it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
