---
id: checkpoint-skill-stage-boundary-handoff-0509
title: "checkpoint skill: stage-boundary handoff as a first-class case"
type: feature
status: done
priority: 2
tags: [context-guard]
created: 2026-09-08
updated: 2026-09-08
closed: 2026-09-08
refs:
  - operator, 2026-09-08; evidence sussex/auth/auth-aws/.claude-sandbox/HANDOFF.md and retro_notes.md § Session retro 2026-09-08 (read-only, product repo)
---

Operator (2026-09-08, validated on kappa-3382): skill chains run stages on one ticket (investigate -> implement -> dev-test -> code-review), each stage publishing its result to disk; the next stage reads files, not the conversation, so the stage boundary is the natural fresh-session point regardless of window health. Add to checkpoint skill: (1) Step 0/Step 5 name 'stage boundary in a skill chain' as a handoff trigger in its own right — test: the next skill reads its inputs from files this session already published; (2) manifest shape for stage boundaries: point at the authoritative stage file, carry only what files do not hold (deploy state, fixtures/accounts, cross-ticket blocks, model/agent rules, CORRECTION/REFUSED lines) — one sentence in Step 4b, keep under budget; (3) Step 5 prints a ready-to-paste opener for the next session: manifest path + mode, Read-in-full instruction, next skill to invoke, 'do not re-run the previous stage — its gate label is set'; (4) Step 0 shortcut: argument naming mode + next skill asks only the inventory question; (5) word for any adjacent stage pair, never a specific chain (kappa skills are downstream, not named here). Wording must stay generic to any skill chain.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-08 claimed by librarian
- 2026-09-08 done: 1c48b8f merged to local main; review CLEAR round 2

## Review
- Round 1 (e4f25bc): NEEDS_CHANGES — 1 high: the opener's "its gate label is set" asserted
  state nothing generic establishes (phrase occurred nowhere else repo-wide) and leaked the
  operator's downstream chain vocabulary against the item's own point 5; 2 lows (shortcut had
  no argument syntax; Step 4b duplicated handoff-format's carry-only list).
- Round 2 (ba608fd): CLEAR — opener now conditional and self-established; argument-hint gains
  [then next-skill]; Step 4b deduped to a gist + pointer; description gains the stage-boundary
  trigger with the boundary test inline (over-trigger attack failed: scoped to skill chains,
  misfire cost is one declinable question). 2 nits accepted. Net +197 words in SKILL.md.
- Note for the operator: the committed opener line differs from the requested phrasing —
  "do not re-run the previous stage — its outputs are published and complete; read them as
  your inputs (if your chain records a per-stage gate or label, it is already set)" — because
  the literal "gate label" wording asserted state the generic skill never writes.
