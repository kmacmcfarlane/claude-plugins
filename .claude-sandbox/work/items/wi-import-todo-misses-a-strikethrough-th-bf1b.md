---
id: wi-import-todo-misses-a-strikethrough-th-bf1b
title: wi import-todo misses a strikethrough that wraps only the bold title
type: bug
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock), operator relay"
---

Relayed 2026-09-22 from the agents store (wi-import-todo-misses-strikethrough-wrap-1b1b). '- [ ] ~~**Title**~~ rest' imports as open with literal ~~**…**~~ in the title; closed-entry detection expects the strike to wrap the whole entry. Acceptance: a strike wrapping the title counts as closed and the markers are stripped; test with both wrap shapes.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
