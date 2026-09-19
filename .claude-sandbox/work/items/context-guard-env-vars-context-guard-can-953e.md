---
id: context-guard-env-vars-context-guard-can-953e
title: "context-guard env vars: CONTEXT_GUARD_* canonical names, CLAUDE_KIT_* aliases kept"
type: chore
status: todo
priority: 3
deps:
  - context-guard-get-exact-depth-from-its-o-d63e
created: 2026-09-19
updated: 2026-09-19
---

From 5e68 (decision 10 consistency, 2026-09-19): CLAUDE_KIT_CONTEXT_WINDOW (lib_context, context_warn, stop_relay, tests, operator-playbook, statusline tests/helpers.py:24) and CLAUDE_KIT_LEDGER_EVERY still carry the dissolved claude-kit brand. Acceptance: canonical CONTEXT_GUARD_CONTEXT_WINDOW / CONTEXT_GUARD_LEDGER_EVERY, old names honoured as deprecated aliases (same semantics), docs name the new first, tests for both. Lands after d63e (same files).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
