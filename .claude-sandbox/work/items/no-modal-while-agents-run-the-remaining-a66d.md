---
id: no-modal-while-agents-run-the-remaining-a66d
title: "no modal while agents run: the remaining dialog sites (implement Step 7, dev-cycle push-rejection and resumed Step 0)"
type: chore
status: todo
priority: 3
created: 2026-09-28
updated: 2026-09-28
refs:
  - 09f1 implementer
---

From the 09f1 implementer 2026-09-28: implement Step 7 (and references/edge-cases.md) surfaces a missed in-scope issue via AskUserQuestion during the build while sub-agents may run; dev-cycle troubleshooting.md's standalone push-rejection ask (after landing, probably safe — check); dev-cycle Step 0.2 brief confirmation, checks question and Land's terminal-action question on a resumed run that finds an agent in flight. Acceptance: each either routed to the numbered channel when an agent may be in flight, or recorded as safe with the reason, per answer 58.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-28 from the 09f1 review (low): checkpoint SKILL.md ~211-212 Step 4b next_skill: 'arguments included' — add '(its arguments end before any ` — 2:` answers)'
