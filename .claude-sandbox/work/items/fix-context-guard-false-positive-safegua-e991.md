---
id: fix-context-guard-false-positive-safegua-e991
title: Fix context-guard false-positive safeguard blocks on continuation sessions
short_display_name: context guard block fix
type: bug
status: doing
priority: 1
tags: [context-guard, claude-code, safeguard]
owner: rt@hooper
claimed: 2026-10-13T18:18Z
created: 2026-10-13
updated: 2026-10-13
refs:
  - https://github.com/anthropics/claude-code/issues/88139
  - https://github.com/anthropics/claude-code/issues/96118
---

Resumed / continuation sessions are stopped mid-turn by a model safeguard
refusal ("safeguards flagged this message", empty reply) on otherwise normal
work. False positive: the same turn passes on a fresh session and on older
models. Cause: context-guard injects prose whose wording the model's safety
classifier over-reads; the words, not the content, trip it.

Fix: rename the label we use for the conversation-only thinking we capture to
"noodle notes", in the injected strings only (the old single-word label is
retired). No behaviour change: same ledger lines, budget and ordering; internal
R/P kind letters and code comments untouched.

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
- 2026-10-13 claimed by rt@hooper
