---
id: wi-owner-token-keep-unicode-letters-and-0aaa
title: "wi owner token: keep Unicode letters and cap the length"
type: chore
status: todo
priority: 4
created: 2026-09-22
updated: 2026-09-22
refs:
  - 59ce review r1
---

59ce review lows, 2026-09-22: _owner_token keeps ASCII only (José Núñez -> Jos-N-ez; all-CJK falls to getpass) and has no length cap (a 400-char user.name feeds status columns). Acceptance: allow Unicode letters/digits with no whitespace or @, truncate ~64 chars; claim's 'held by' refusal names --steal; tests.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
