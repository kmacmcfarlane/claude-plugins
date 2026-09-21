---
id: implement-decision-sweep-may-use-a-numbe-0cc6
title: "implement: decision sweep may use a numbered list (same rule as investigate)"
type: chore
status: doing
priority: 3
owner: unknown@360f41058e92
claimed: 2026-09-21T18:55Z
created: 2026-09-21
updated: 2026-09-21
---

From the 183a review: implement/SKILL.md (~l.235) decision-question sweep still mandates AskUserQuestion with the defer option — the pattern the operator objected to. implement usually runs late (scope closed), so the dialog may be right there; apply investigate's 'Asking at a gate' rule by pointer (the investigate skill's § Asking at a gate) rather than restating.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Carried from cbea review
- implement orchestrator Step 9 bullet: "a verification incomplete only by a human-gated step is Step 8's case, committed, not a stop"; implement § Running non-interactively does not say what happens to Step 4 base consent, Step 7 revision prompt / in-scope-issue AskUserQuestion, Step 8 human-action ask.

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer sonnet — default (apply an existing rule by pointer)

## Implementer result
- round 1 DONE 81ecaf6 (sonnet): decision sweep points at investigate § Asking at a gate; orchestrator Step 9 human-gated clause; non-interactive section covers Steps 4/7/8 prompts in its own vocabulary.
- dispatch: reviewer opus — rule 4 floor

## Review round 1 — NEEDS_CHANGES (opus) at 81ecaf6
- [medium] Step 6: "end the turn on the list" then the Proceed/Discuss/Reject menu in the same turn — ambiguous replies; questions first, menu after. [medium] non-interactive Step 8: human-gated step → record manual, deferred; verification incomplete → Gate 2 stop applies. [medium] non-interactive Step 4: base deviation / unresolved repos are blocking Open Questions (no self-consent, never clone silently). [low] Step 7 missed in-scope issue → non-blocking Open Question.
- dispatch: implementer sonnet — fix round 1 (resume)
