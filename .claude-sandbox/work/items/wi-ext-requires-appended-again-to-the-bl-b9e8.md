---
id: wi-ext-requires-appended-again-to-the-bl-b9e8
title: "wi: ext: requires appended again to the blocked/parked reason on each export/import round trip"
type: bug
status: dropped
priority: 3
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
---

Found by the ca20 reviewer, pre-existing on main: a blocked (now also parked) item with an ext: dep gets another '; requires ext:…' appended to its reason on every export → import --update cycle. Acceptance: the round trip is idempotent (test: N cycles leave the item byte-identical).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- folded into wi-b020-review-lows-export-round-trip-is-bc6b (librarian 2026-09-21): same wi.py export/write surface; one branch avoids three-way conflicts

## Notes
- 2026-09-21 dropped
