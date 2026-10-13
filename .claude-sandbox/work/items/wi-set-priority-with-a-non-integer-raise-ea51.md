---
id: wi-set-priority-with-a-non-integer-raise-ea51
title: wi set priority with a non-integer raises an uncaught ValueError
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-13T19:34Z
created: 2026-09-29
updated: 2026-10-13
refs:
  - 928d
---

Found by the 928d implementer 2026-09-29: 'wi set <id> priority abc' prints a traceback (exit 1) instead of a clean error. Acceptance: a clean exit-1 message naming the field, added to provider-interface.md's exit-1 list, with a test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
widened 2026-09-29 (928d review r1): provider-interface.md:92 exit-1 list is not exact — "title longer than its limit or empty" is true only of add (set title "" exits 3, set accepts 200 chars); the missing-root error (exit 1) is not listed; fix the list with this bug

## Notes
- 2026-10-13 claimed by Kyle-McFarlane@2d49f8460283
dispatch: implementer sonnet medium — build (input validation bug: canonical kind) (triage d2aa)
agent: implementer a9d852836275d33ee
return: DONE 011b2fdd; set priority exits 1 on a non-integer or out-of-range value (was a traceback, or exit 3 for out of range); provider-interface exit-1 list updated; work-items 366, kit-dev 21 OK
dispatch: reviewer opus high — review round 1 of 011b2fdd
agent: reviewer a9c0cd51371ff55de
