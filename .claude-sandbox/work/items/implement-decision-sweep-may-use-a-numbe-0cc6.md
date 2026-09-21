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
