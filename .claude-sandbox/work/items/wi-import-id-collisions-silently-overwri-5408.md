---
id: wi-import-id-collisions-silently-overwri-5408
title: "wi import: id collisions silently overwrite an item (data loss)"
type: bug
status: todo
priority: 1
created: 2026-09-21
updated: 2026-09-21
refs:
  - 370b reviewer
---

Found by the 370b reviewer 2026-09-21 (pre-existing): make_id uses a 4-hex random suffix; a fresh import of many items whose titles slug alike (e.g. ~44 titles → item-…) can generate the same id twice, and the second write silently replaces the first — one fuzz run lost an item. Acceptance: id generation never returns an id already in the store or earlier in the same batch (check + retry, or widen on collision); import/add refuse to overwrite an existing file they did not read; test forcing a collision (patched RNG) shows both items survive.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
