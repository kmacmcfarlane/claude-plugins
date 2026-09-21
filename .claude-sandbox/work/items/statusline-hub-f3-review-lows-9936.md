---
id: statusline-hub-f3-review-lows-9936
title: statusline-hub F3 review lows
type: bug
status: todo
priority: 3
created: 2026-09-21
updated: 2026-09-21
refs:
  - dfa1 reviewer
---

From dfa1 review r2 2026-09-21 (CLEAR with lows). (1) hub session_start.py:320-326 fresh machine where the hub runs first: use the footer wording when _statusline_installs_only_hooks(); (2) session_start.py:182-184 heal waits silently forever on a footer entry after statusline was uninstalled — wait only while a statusline@ install record exists, else yield with the message; (3) README team enabledPlugins snippet: list statusline-hub@ beside statusline@ (auto-install from enabledPlugins unverified).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
