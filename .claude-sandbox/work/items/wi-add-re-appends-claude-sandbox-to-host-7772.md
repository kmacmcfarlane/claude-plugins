---
id: wi-add-re-appends-claude-sandbox-to-host-7772
title: wi add re-appends /.claude-sandbox/ to host .gitignore (7f00 recurrence)
type: bug
status: todo
priority: 2
created: 2026-09-18
updated: 2026-09-18
refs:
  - recurrence note in 7f00 body, 2026-09-18
---

Noticed at rehydrate 2026-09-18: an uncommitted recurrence note was appended to closed item 7f00 by another session. In operator-attention, after the ignore line was removed and committed (e5516d2), a later 'wi add' re-appended /.claude-sandbox/ to the working-tree .gitignore, silently ignoring the new item. Acceptance: wi add (and every store-creating path, not only wi init) leaves a host .gitignore that already tracks the store alone. Held until plugin-factoring merges (wi.py moves to the work-items plugin).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- 2026-09-18: plugin-factoring merged (0d8b4c9); hold released. Paths moved: claude-kit dissolved into kit-dev/context-guard/dev-flow/work-items/chat/sandbox/ralph.
