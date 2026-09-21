---
id: work-items-first-class-parked-status-wi-ca20
title: "work-items: first-class parked status (wi park / unpark)"
type: feature
status: done
priority: 2
created: 2026-09-19
updated: 2026-09-21
closed: 2026-09-21
refs:
  - "peer: implement headless paseo support (uds 242.sock), for claude-sandbox librarian"
---

Peer request 2026-09-19 (claude-sandbox librarian, relayed via session 'implement headless paseo support', operator's ask). Deliberate deferral currently abuses 'wi block "PARKED: ..."'. Acceptance: status 'parked' valid in lint with a reason field; 'wi park <id> <reason>' / 'wi unpark <id>' (back to todo, or recorded previous status); excluded from ready/next; prime shows a one-line count or collapsed section, not under BLOCKED; ls filters on parked; archive via done --drop + archive; backlog-yaml bridge maps it (deferred-like) or documents it doesn't; SKILL.md table + references/format.md updated. Migration: optional step converting 'status: blocked' items whose reason starts with 'PARKED' to parked. The claude-sandbox store's own migration (b090, 2dd5) is outside this repo's Scope: message the claude-sandbox librarian when it ships; it migrates its store.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: d6ba6da

## Dispatch
- dispatch: implementer opus — executable logic (wi.py)

## Implementer result
- round 1 DONE a7d7969 (opus): parked status + parked: reason; park/unpark (unpark → todo, or blocked if a blocked: reason remains); migrate-parked (dry run unless --apply); excluded from next and default ls; prime PARKED <n>; claim refuses parked; bridge exports blocked "PARKED: …" and imports it back as parked. 108 tests; 57 fail on main.
- follow-ups after landing: idle-turn.md to read status: parked; message the claude-sandbox librarian (it runs migrate-parked); b020 follows the same pattern; wi release on a parked item.
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at a7d7969
- temp copy of all 140 live items + the two real claude-sandbox PARKED items: migrate dry run writes nothing; --apply diffs limited to owned lines; parked never surfaces in next/ls/claim; bridge validates --strict.
- [medium] wi release on a parked item forces todo and leaves parked: (concurrent-session path un-parks silently). [medium] export/import --update loses a parked item's blocked: reason (doc says round trip is exact).
- lows: "PARKED (operator 2026-09-19): …" strips only "PARKED " (and the text says "unblock"); lint does not flag leftover parked: on other statuses; `wi set status parked` bypasses _park; idle-turn.md goes stale (follow-up).
- pre-existing bugs found (filed separately): front-matter escape amplification (data loss); ext: requires appended again each round trip.
- dispatch: implementer opus — fix round 1 (resume)
- round 1 fix 8dd4d35: release never unparks; import --update keeps blocked:; provenance "(…)" stripped, whole text in the Notes line; lint flags stray parked:; set status parked refuses. 113 tests.
- dispatch: reviewer opus — round 2 (resume)

## Review round 2 — CLEAR (opus) at 8dd4d35
- concurrent release, bridge round trips, migrate on the real claude-sandbox reasons all hold. lows: nested "(…)" provenance leaves a fragment (full text in Notes); idle-turn.md goes stale (filed).
## Landed
- d6ba6da. 1 fix round. claude-sandbox librarian notified.
- claude-sandbox librarian ack: filed its migration as claude-sandbox item migrate-the-parked-paseo-items-to-wi-s-f-51d0; runs after its plugins update.
