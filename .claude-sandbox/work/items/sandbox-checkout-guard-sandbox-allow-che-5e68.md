---
id: sandbox-checkout-guard-sandbox-allow-che-5e68
title: "sandbox checkout guard: SANDBOX_ALLOW_CHECKOUT_EDITS, with CLAUDE_KIT_ alias kept"
type: chore
status: doing
priority: 2
owner: unknown@e3a28d2cc009
claimed: 2026-09-19T00:27Z
created: 2026-09-19
updated: 2026-09-19
refs:
  - operator decision 10
---

Operator decision 10 (2026-09-19): consistency and cohesion. The checkout-guard opt-out env var is CLAUDE_KIT_ALLOW_CHECKOUT_EDITS (legacy brand; claude-kit dissolved). Acceptance: plugins/sandbox/hooks/checkout_guard.py accepts SANDBOX_ALLOW_CHECKOUT_EDITS as canonical and still honours CLAUDE_KIT_ALLOW_CHECKOUT_EDITS (documented deprecated alias, same semantics); docs (sandbox SKILL.md, README, CLAUDE.md, any hint text the guard prints) name the new var first; tests for both names. Note other CLAUDE_KIT_* vars (context-guard CLAUDE_KIT_CONTEXT_WINDOW etc.) in OPEN QUESTIONS for a follow-up, do not rename them here.

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — gating hook, trivial change (rule 3 exclusion)

impl: DONE 1199590 (alias tuple; 21 tests; 29/31 matrix identical, 2 intended allows).
dispatch: reviewer opus — rule 4
