---
id: librarian-series-home-durable-path-not-t-1dab
title: "librarian Series home: durable path, not the session scratchpad"
type: chore
status: doing
priority: 2
owner: unknown@360f41058e92
claimed: 2026-09-21T18:48Z
created: 2026-09-21
updated: 2026-09-21
---

Noticed by the librarian at the F2 landing (2026-09-21). librarian-mode binds Series home to 'your scratchpad (.claude-sandbox/ is outside every Scope)', preserved from before F2. But the scratchpad is session-scoped: a later session cannot find a spike's series, and F2 now closes a spike with 'wi done --note <series path>' pointing there. In practice this session wrote spike series to $MAIN/.claude-sandbox/investigations/<slug>/ (d193, 7e3b), which is dev-cycle's default and where /implement looks. Acceptance: librarian Series home = $MAIN/.claude-sandbox/investigations/<slug>/ (tooling-owned like the store: written by the cycle, never a custody edit), in librarian-mode's bindings and dev-cycle bindings.md's librarian row; say why it is not a Scope violation (same class as the store).

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Carried from 14bd review (lows) — widen this item to include them (same file set)
- session-name.md: record the operator's "keep the name" decline where Rehydrate reads it (or say it lasts until /clear); scope "Dispatch nothing" to new idle-turn dispatch, not cycles in flight; "show the line once more" → each message until matched or declined.
- SKILL.md § Idle turn: name the rename gate as the second thing that holds dispatch (budget: SKILL.md is at 13,604 chars).

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — librarian behaviour, judgement (Scope vs tooling-owned paths)

## Implementer result
- round 1 DONE 57947df (opus): Series home = $MAIN/.claude-sandbox/investigations/<slug>/ (tooling state like the store, not a custody edit); bindings.md librarian row; session-name.md: gate stops only new dispatch, line shown each message, decline recorded as a closed item with "name kept: <name>" (grep survives /clear); idle-turn.md names the rename gate. SKILL.md 13,644 chars.
- dispatch: reviewer opus — rule 4
