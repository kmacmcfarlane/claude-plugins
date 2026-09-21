---
id: wi-ext-requires-appended-again-to-the-bl-b9e8
title: "wi: ext: requires appended again to the blocked/parked reason on each export/import round trip"
type: bug
status: todo
priority: 3
created: 2026-09-21
updated: 2026-09-21
---

Found by the ca20 reviewer, pre-existing on main: a blocked (now also parked) item with an ext: dep gets another '; requires ext:…' appended to its reason on every export → import --update cycle. Acceptance: the round trip is idempotent (test: N cycles leave the item byte-identical).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
