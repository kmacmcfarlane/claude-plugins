---
id: wi-import-todo-the-heading-strike-re-clo-9197
title: "wi import-todo: the heading STRIKE_RE closes '## ~~T~~ — <any text>', e.g. 'PG16 instead'"
type: bug
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - bf1b review r2
---

bf1b review r2 note, 2026-09-22: STRIKE_RE's \w[\w /]*? after the dash accepts any text, so a struck heading replaced by another ('— PG16 instead') imports as done. Acceptance: the same closure-word/date rule bf1b applies to plain struck list lines; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
