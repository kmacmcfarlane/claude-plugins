---
id: wi-half-moved-compare-parent-dirs-by-st-fc04
title: "wi _half_moved: compare parent dirs by (st_dev, st_ino), not realpath"
type: bug
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - 220b review r2
---

From 220b review r2 (CLEAR) low, 2026-09-22: realpath cannot see through a bind mount, so items/ bind-mounted at archive/<year> plus an outside hard link (cp -al / rsnapshot) passes _half_moved and wi archive unlinks the store's only entry (content survives in the backup). Fix: compare the parents' os.stat (st_dev, st_ino); covers symlinks too. Test by patching realpath or stat.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
