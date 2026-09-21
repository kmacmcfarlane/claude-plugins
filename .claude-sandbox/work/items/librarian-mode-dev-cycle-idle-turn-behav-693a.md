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

## Review round 1 — NEEDS_CHANGES (opus) at 3524c7b
- wi behaviour for holds verified on a temp store; no dispatch loop.
- [high] a limiting hold (no fable / at most N / sonnet only) binds only the idle turn, not The cycle (Intake, fix rounds); precedence vs a model pin unstated.
- [medium] status (read-only) and start ("wait for requests") now contradict the idle turn; [medium] --on-held items are invisible in every view; [medium] decision-answer form undefined, live store uses several forms, grep includes closed items; [medium] rate-limited items already claimed (doing) never re-enter the Work table.
- lows: lift with done --note alone (unblock exposes the hold as a P0 ready item); PARKED convention vs free-text holds here; "after reset <time>" next value.
- dispatch: implementer opus — fix round 1 (resume)
- round 1 fix f393376: Hold binding in The cycle (limits cap every dispatch; limit below a pin → decision), start runs the idle turn, status exempt; held items via ls --json filter; canonical `answer N:` reply form; own doing items resume; lift = done only; after reset <time>.
- dispatch: reviewer opus — round 2 (resume)
- note for b020: adopt `answer N:` as the reply marker; wish: wi ls --dep <id>, HOLD line in prime.

## Review round 2 — NEEDS_CHANGES (opus) at f393376
- 6 of 8 round-1 findings fixed; wi mechanics re-verified on a temp store.
- [medium] Groom grep only shows lines starting decision/answer: misses legacy replies; decision 43 (answered "- 43 → (a)" in 2c77) shows open. [medium] a "sonnet only" hold vs the opus reviewer floor — unresolved clash. [low] "at most N agents": does implementer+reviewer count as two?
- dispatch: implementer opus — fix round 2 (resume)
- round 2 fix 5b3b860: Groom reads only `answer N:`; one-time librarian migration of legacy replies; limit below pin or reviewer opus floor → held + decision; N counts every agent.
- dispatch: reviewer opus — round 3 (resume)
