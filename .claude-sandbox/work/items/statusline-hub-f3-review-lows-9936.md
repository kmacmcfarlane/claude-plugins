---
id: statusline-hub-f3-review-lows-9936
title: statusline-hub F3 review lows
type: bug
status: doing
priority: 3
owner: unknown@360f41058e92
claimed: 2026-09-21T23:07Z
created: 2026-09-21
updated: 2026-09-21
refs:
  - dfa1 reviewer
---

From dfa1 review r2 2026-09-21 (CLEAR with lows). (1) hub session_start.py:320-326 fresh machine where the hub runs first: use the footer wording when _statusline_installs_only_hooks(); (2) session_start.py:182-184 heal waits silently forever on a footer entry after statusline was uninstalled — wait only while a statusline@ install record exists, else yield with the message; (3) README team enabledPlugins snippet: list statusline-hub@ beside statusline@ (auto-install from enabledPlugins unverified).

## Handoff
- doing: implementer dispatched (opus, agent ad4c93ef652d4ecc3)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — hub session_start owns the statusLine slot (fable signal: settings ownership; fable unavailable, fallback)
