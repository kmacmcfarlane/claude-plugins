---
id: librarian-mode-idle-turn-read-status-par-de00
title: "librarian-mode idle-turn: read status: parked (not blocked + PARKED reason)"
type: chore
status: done
priority: 3
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
---

ca20 landed a real parked status. librarian-mode/references/idle-turn.md (~l.22, 26, 60-62) still says open items are todo/doing/blocked and 'parked today is blocked with a reason starting PARKED'. Switch to status: parked (wi ls --status parked; next --json counts.parked; prime's PARKED <n> line); decide whether the Groom decision scan should include parked items (an unanswered decision N: on a parked item is now invisible).

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: 79b0bc9

## Dispatch
- dispatch: implementer sonnet — default (reference wording)

## Implementer result
- round 1 DONE 5303406 (sonnet): idle-turn.md uses status: parked; Groom decision scan adds ls --status parked; Work table relies on --ready excluding parked.
- dispatch: reviewer opus — rule 4 floor

## Review round 1 — NEEDS_CHANGES (opus) at 5303406
- every named command verified on a temp store.
- [medium] "(format.md § Parked)" is a bare cross-plugin file pointer → "the `work-items` skill's format reference, § Parked". lows: "closed to ls default" wording; pre-migration PARKED-blocked items note; acceptance command list partially cited.
- dispatch: implementer sonnet — fix round 1 (resume)
- round 1 fix 6a0dc15: owner-named pointer, ls wording, pre-migration clause, prime PARKED line.
- dispatch: reviewer opus — round 2 (resume)

## Review round 2 — CLEAR (opus) at 6a0dc15
- low (landed): pre-migration note sits on the scan loop, better on the blocked line.
## Landed
- 79b0bc9. 1 fix round.
