---
id: wi-park-groom-reason-with-leading-punctu-370b
title: "wi: park/groom reason with leading punctuation drifts on the first export → import cycle"
type: bug
status: done
priority: 4
created: 2026-09-21
updated: 2026-09-22
closed: 2026-09-22
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
- 2026-09-22 done: e56a257

## Implementer result
- round 1 DONE cfe493f (opus): export quotes a park/groom reason only when the plain form would not read back; import reads the quoted form verbatim; one-line story values not folded; migrate-parked pinned (13 texts, unchanged). Behaviour changes: hand-written blocked 'PARKED: "x"' imports as parked x; one-line values keep space runs/NBSP. Open: blocked reason exactly '—' or starting PARKED/GROOMING still drift.
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at cfe493f
- round trips byte-identical from cycle 0; live-store copy unchanged vs main; backlog.py --strict accepts the quoted form; ralph only checks blocked_reason non-empty.
- [medium] _bridge_decode unwraps PARKED: "" → empty reason, lint fails (main was clean).
- [medium] loose unwrap: hand-written PARKED: "foo" said the vendor, then "bar" loses its outer quotes → unwrap only what export itself would write (reviewer prototyped; 200k round trips 0 failures; restores main's reading of hand-written forms).
- [medium] no test pins how import reads hand-written quoted bridge text.
- lows: _fold_story stops trimming enum/id fields (complexity, ticket_mode, claimed_by) and turns blocked_reason " — " into a literal; format.md:200 overclaims (ext suffix caveat).
- pre-existing, filed separately: make_id 4-hex collisions on fresh import silently overwrite an item.
- dispatch: implementer opus — fix round 1 (same agent resumed)
- fix round 1 DONE e3c52cc (opus): unwrap only export's own form; STORY_TEXT_FIELDS keep as read, enum/id fields folded; padded — is no value; table test of hand-written forms (fails on cfe493f). Seed-4 fuzz failure = the id collision already filed as 5408.
- dispatch: reviewer opus — review r2 (same reviewer resumed)

## Review round 2 — CLEAR (opus) at e3c52cc
- 22 fuzz seeds 0 failures; hand-written forms match main; live-store copy unchanged.
- low carried into 5408: whitespace-only blocked_reason imports as "  " (strip-empty → no value).
- landed e56a257
