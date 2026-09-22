---
id: wi-import-todo-a-struck-plain-title-with-6f1c
title: "wi import-todo: a struck plain title with a STATUS suffix, and a top-level struck bold bullet, import as done"
type: chore
status: todo
priority: 4
created: 2026-09-22
updated: 2026-09-22
refs:
  - bf1b implementer
---

bf1b implementer OQs, 2026-09-22: '- [ ] ~~Title~~ — DONE <date>' stays open (no bold, so the strike reads partial) and '- ~~**T**~~ rest' outside a section is dropped (_parse_bold_bullets matches only '- **'). Acceptance: mirror the heading rule's '~~T~~ — STATUS date' shape for list entries; a top-level struck bold bullet imports as done; tests.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
