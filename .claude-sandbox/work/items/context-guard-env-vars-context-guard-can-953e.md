---
id: context-guard-env-vars-context-guard-can-953e
title: "context-guard env vars: CONTEXT_GUARD_* canonical names, CLAUDE_KIT_* aliases kept"
type: chore
status: doing
priority: 3
deps:
  - context-guard-get-exact-depth-from-its-o-d63e
owner: unknown@e3a28d2cc009
claimed: 2026-09-19T05:58Z
created: 2026-09-19
updated: 2026-09-19
---

From 5e68 (decision 10 consistency, 2026-09-19): CLAUDE_KIT_CONTEXT_WINDOW (lib_context, context_warn, stop_relay, tests, operator-playbook, statusline tests/helpers.py:24) and CLAUDE_KIT_LEDGER_EVERY still carry the dissolved claude-kit brand. Acceptance: canonical CONTEXT_GUARD_CONTEXT_WINDOW / CONTEXT_GUARD_LEDGER_EVERY, old names honoured as deprecated aliases (same semantics), docs name the new first, tests for both. Lands after d63e (same files).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

## Dispatch
- dispatch: implementer opus — executable logic (hooks); gate-code fable signal: fable unavailable (unknown); fallback

## Implementer result
- round 1 DONE b3bfc9f (opus): canonical+alias via lib_context.env_setting; empty canonical falls to alias; invalid canonical wins (no pin). All 5 check suites green; revert-to-verify 7 failures/2 errors.
- held: operator paused new dispatches 2026-09-19 until bedtime; next is reviewer opus.
- dispatch: reviewer opus — rule 4 (impl opus)

## Review round 1 — NEEDS_CHANGES (opus) at b3bfc9f
- [high] invalid canonical (e.g. "1m") beside a valid alias disables the pin → mirror on → can hard-block where base could not (false-block class). Fix: first VALID name wins (validator in env_setting); flip test_invalid_canonical_pin... to pinned/rc 0; document in operator-playbook; same for LEDGER_EVERY (no ValueError).
- [medium] test_window_mirror leaks a host pin / CONTEXT_GUARD_DERIVE=off (window() reads os.environ): 3 failures with either pin exported. Fix: scrub os.environ in Base setUp (or pass environ into window()); re-run suite with both pin names and DERIVE=off exported.
- dispatch: implementer opus — fix round 1 (resume, same tier)
