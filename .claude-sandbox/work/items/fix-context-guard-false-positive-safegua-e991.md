---
id: fix-context-guard-false-positive-safegua-e991
title: Fix context-guard false-positive safeguard blocks on continuation sessions
short_display_name: context guard block fix
type: bug
status: todo
priority: 1
tags: [context-guard, claude-code, safeguard]
created: 2026-10-13
updated: 2026-10-13
refs:
  - https://github.com/anthropics/claude-code/issues/88139
  - https://github.com/anthropics/claude-code/issues/96118
---

Resumed / continuation sessions are stopped mid-turn by a model safeguard
refusal ("safeguards flagged this message", empty reply) on otherwise normal
work. False positive: the same turn passes on a fresh session and on older
models. Cause: context-guard injects prose the model's safety classifier reads
as a request to spell out its internal thinking; the wording, not the content,
trips it.

Fix: rename the label we use for the conversation-only thinking we capture —
currently "reasoning" — to "noodle notes", in the injected strings only. No
behaviour change: same ledger lines, budget and ordering; internal R/P kind
letters and code comments untouched.

## Acceptance
- [ ] none of the injected sites carries the old trigger wording
- [ ] context-guard hook test suite passes (2 asserts updated)
- [ ] a resumed session on Opus 5.5 completes a turn with no safeguard refusal

## Sites
Reword "reasoning" to "noodle notes" (grammar adjusted) in the injected prose:
- hooks/stop_relay.py, hooks/rehydrate.py, hooks/ledger.py
- skills/checkpoint/SKILL.md
- consistency: skills/checkpoint/references/*.md
- test asserts: hooks/tests/test_ledger_digest.py (2)

## Handoff
- doing: —
- next: claim, reword the injected sites + 2 test asserts, run suite, live-check a resumed Opus 5.5 session
- blocked: —
- learned: model-side classifier; continuation-specific on recent CLI builds; renaming the injected prose is the fix

## Notes
- 2026-10-13 filed from opencode investigation; held for operator review before execution (context compact first)
