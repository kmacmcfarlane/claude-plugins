---
id: wi-set-priority-with-a-non-integer-raise-ea51
title: wi set priority with a non-integer raises an uncaught ValueError
type: bug
status: done
priority: 3
created: 2026-09-29
updated: 2026-10-13
closed: 2026-10-13
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
verdict: review round 1 NEEDS_CHANGES (must-fix 3, all docs: format.md:235-237 still says out-of-range priority exits 3; provider-interface title limit is add-only; "as add -p rejects it" implies exit 1 though add -p exits 2; nits: test asserts nothing written, wi.py:2325 comment)
dispatch: implementer sonnet medium — fix round 1 (resume a9d852836275d33ee)
decided: 2026-10-13T20:40Z cap — the fix round applied the reviewer's exact replacement texts plus the two nits (diff read); landed without a second review (authority answer 145)
landed: e734bdf7 (merge of 011b2fdd..45d9e592); Checks 12/12 OK; cc_scan clean
- 2026-10-13 done
