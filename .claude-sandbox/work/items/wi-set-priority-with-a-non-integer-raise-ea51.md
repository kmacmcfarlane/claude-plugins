---
id: wi-set-priority-with-a-non-integer-raise-ea51
title: wi set priority with a non-integer raises an uncaught ValueError
type: bug
status: todo
priority: 3
created: 2026-09-29
updated: 2026-09-29
refs:
  - 928d
---

Found by the 928d implementer 2026-09-29: 'wi set <id> priority abc' prints a traceback (exit 1) instead of a clean error. Acceptance: a clean exit-1 message naming the field, added to provider-interface.md's exit-1 list, with a test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
