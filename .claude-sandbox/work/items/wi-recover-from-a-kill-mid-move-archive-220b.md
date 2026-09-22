---
id: wi-recover-from-a-kill-mid-move-archive-220b
title: "wi: recover from a kill mid-move (archive duplicate, 0-byte reservation); bound the exhaustion test"
type: bug
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - 5408 reviewer
---

From 5408 review r2 (lows): (1) archive hard-link path — a kill between link and unlink leaves the item in items/ and archive/; archive then refuses forever: when dest has src's dev/inode, finish the move (unlink src). (2) no-hard-link path — a kill between the O_EXCL reservation and os.replace leaves a 0-byte item file and every command exits 3 'missing front matter': treat a 0-byte item file as a stale reservation, name it and the fix (lint) rather than blocking all loads. (3) test_exhausted_retries_fail_loudly_and_write_nothing hangs on main's code — bound it (counting urandom that raises after N).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
