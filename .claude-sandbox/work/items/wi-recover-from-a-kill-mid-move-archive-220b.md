---
id: wi-recover-from-a-kill-mid-move-archive-220b
title: "wi: recover from a kill mid-move (archive duplicate, 0-byte reservation); bound the exhaustion test"
type: bug
status: doing
priority: 3
owner: unknown@360f41058e92
claimed: 2026-09-22T00:50Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - 5408 reviewer
---

From 5408 review r2 (lows): (1) archive hard-link path — a kill between link and unlink leaves the item in items/ and archive/; archive then refuses forever: when dest has src's dev/inode, finish the move (unlink src). (2) no-hard-link path — a kill between the O_EXCL reservation and os.replace leaves a 0-byte item file and every command exits 3 'missing front matter': treat a 0-byte item file as a stale reservation, name it and the fix (lint) rather than blocking all loads. (3) test_exhausted_retries_fail_loudly_and_write_nothing hangs on main's code — bound it (counting urandom that raises after N).

## Handoff
- doing: worktree ready, not yet dispatched (paused for 1222)
- next: dispatch implementer (opus) after 1222's investigation and the model switch back to opus
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
- dispatch: implementer opus — wi.py store integrity
- 2026-09-22: worktree fast-forwarded to main; answer 53 lifts the hold. dispatch: implementer opus — wi.py store integrity
- impl r0 DONE a70f389 (opus): _same_file (lstat dev/inode), move/archive finish a linked move, load_all skips a 0-byte item with a warning naming lint, lint names both kill states and fixes; bounded exhaustion test (fails in 0.04s vs hang on an unbounded loop); 2 new tests fail on main. OQs: empty file never auto-removed (add writes outside the lock); stray .tmp<pid> after a create-path kill.
- dispatch: reviewer opus — rule 4
- review r1 (opus) at a70f389: NEEDS_CHANGES. Seven Checks OK; new tests fail on main; bounded test meaningful.
  - [medium] wi.py:991-998, 2648-2652 — _same_file true for one entry reached by two paths (archive/<year> symlinked to items/) → archive unlinks the only copy (reproduced: items/ emptied by a default `wi archive`). Pass: half-done only when same dev/inode AND st_nlink >= 2 AND parent dirs resolve to different real paths; test the symlinked-dir case.
  - [low] lint mv/rm fixes print unquoted paths → shlex.quote.
  - [low] a write to the item before the next archive breaks the link → refuses forever again; follow-up or format.md line.
  - [low] unlocked ls/show/lint can report a live reservation as killed (microsecond window, message only).
  - note: implementer's OQ "add writes outside the lock" is mistaken — cmd_add holds Lock.
- dispatch: implementer opus — fix round 1 (resume, tier kept)
- fix r1 DONE b157e01 (opus): _half_moved (same dev/inode, nlink >= 2, parents realpath-distinct); 3 new tests (symlinked dir refuses, item survives; fail on a70f389); lows a/b/c fixed (b as a format.md line: items/ copy is current).
- dispatch: reviewer opus — review r2 (resume)
