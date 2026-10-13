---
id: wi-symlink-edge-cases-left-after-39a2-af-d4ae
title: "wi: symlink edge cases left after 39a2 (.. after a link, enclosing-repo links, temp dir, items/ symlink)"
short_display_name: wi symlink edge cases
type: bug
status: todo
priority: 3
created: 2026-10-13
updated: 2026-10-13
refs:
  - wi-init-choose-a-tracked-or-git-ignored-39a2
---

From 39a2 review 3, 2026-10-13, all low and none reachable from repo content with a default store path: (1) WI_ROOT=sub/../.work with sub linked outside passes _store_outside_repo because abspath cancels .. — walk the unnormalised path or refuse a .. whose realpath differs; (2) false refusal for a project reached through a symlink inside an enclosing repo (dotfiles ~/.git) — count only links the enclosing repo tracks (ls-files mode 120000); (3) mkstemp normalises .. so the temp dir and the rename target can differ — use realpath(path.parent) for both; (4) items/ as a symlink outside the repo is written through by add and every command (predates 39a2).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
