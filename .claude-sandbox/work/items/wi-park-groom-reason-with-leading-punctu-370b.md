---
id: wi-park-groom-reason-with-leading-punctu-370b
title: "wi: park/groom reason with leading punctuation drifts on the first export → import cycle"
type: bug
status: doing
priority: 4
owner: unknown@360f41058e92
claimed: 2026-09-21T23:45Z
created: 2026-09-21
updated: 2026-09-21
refs:
  - bc6b reviewer
---

From the bc6b review 2026-09-21 (declined as out of scope): a parked reason '-' / '—' / '...' imports as 'PARKED: -'; grooming '- [ ] x' becomes '[ ] x'; fresh import strips title whitespace and folds NBSP. Stable after cycle 1. Fix must not change how migrate-parked reads hand-written 'PARKED: — reason' text. Acceptance: cycle 0 byte-identical for those shapes; migrate-parked unchanged; tests.

## Handoff
- doing: implementer dispatched (opus, agent a3fc80d9f5e2ba10c)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — wi.py import logic

## Implementer result
- round 1 DONE cfe493f (opus): export quotes a park/groom reason only when the plain form would not read back; import reads the quoted form verbatim; one-line story values not folded; migrate-parked pinned (13 texts, unchanged). Behaviour changes: hand-written blocked 'PARKED: "x"' imports as parked x; one-line values keep space runs/NBSP. Open: blocked reason exactly '—' or starting PARKED/GROOMING still drift.
- dispatch: reviewer opus — rule 4
