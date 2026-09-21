---
id: wi-park-groom-reason-with-leading-punctu-370b
title: "wi: park/groom reason with leading punctuation drifts on the first export → import cycle"
type: bug
status: todo
priority: 4
created: 2026-09-21
updated: 2026-09-21
refs:
  - bc6b reviewer
---

From the bc6b review 2026-09-21 (declined as out of scope): a parked reason '-' / '—' / '...' imports as 'PARKED: -'; grooming '- [ ] x' becomes '[ ] x'; fresh import strips title whitespace and folds NBSP. Stable after cycle 1. Fix must not change how migrate-parked reads hand-written 'PARKED: — reason' text. Acceptance: cycle 0 byte-identical for those shapes; migrate-parked unchanged; tests.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
