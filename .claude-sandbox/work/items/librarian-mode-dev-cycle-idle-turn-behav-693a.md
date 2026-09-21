---
id: librarian-mode-dev-cycle-idle-turn-behav-693a
title: "librarian-mode/dev-cycle: idle-turn behaviour - show groom/work tables, then work the queue"
type: feature
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-21T18:13Z
created: 2026-09-20
updated: 2026-09-21
refs:
  - operator 2026-09-20
---

Operator 2026-09-20: 'work-items that are ready and not parked should be worked instead of landing an idle turn whenever possible, unless there is some quota-preserving behaviour specified at the time by the operator.' Acceptance: librarian-mode gains an 'Idle turn' rule - when a turn would otherwise end with nothing in flight, print two short status tables (items to groom: grooming/blocked/unanswered decision N; items to work: ready, not parked) and then immediately claim and dispatch the top ready item(s) rather than waiting; an operator hold (a stated pause, a quota-preserving instruction) is the only thing that stops it, is recorded in the store, and is named in the idle-turn output so it is visible why nothing is moving; the hold's end condition is recorded too. Mirror the rule in dev-cycle where it applies (a standalone run has no standing queue). Depends in spirit on the wi grooming/needs-input work and on ca20 (parked) for the table's inputs, but can land with the fields that exist today.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Hold record
- 2026-09-19: operator paused new dispatches ("until I am ready to go to bed"). 2026-09-21: lifted - "work through any items in the work-item queue that you can" (decision 45 -> a). The hold lived only in the transcript; this item makes it visible.

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — judgement (librarian behaviour rule; where a hold lives)

## Implementer result
- round 1 DONE 3524c7b (opus): ## Idle turn in librarian-mode (Groom/Work tables, then dispatch; only a hold stops it; rate limit is not a hold); references/idle-turn.md; a hold = a work item tagged hold, kept blocked, held items --on it; Rehydrate lists `wi ls --tag hold`; dev-cycle: one clause (standalone ends at its Report). SKILL.md 13.4k.
- implementer wish (not filed yet): wi prime shows hold-tagged items on their own line.
- dispatch: reviewer opus — rule 4
