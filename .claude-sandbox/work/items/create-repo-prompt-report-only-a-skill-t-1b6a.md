---
id: create-repo-prompt-report-only-a-skill-t-1b6a
title: "create-repo prompt: report only a skill the prompt asked the session to use"
short_display_name: create-repo missing-skill wording
type: chore
status: done
priority: 4
created: 2026-10-12
updated: 2026-10-12
closed: 2026-10-12
refs:
  - create-repo-a-moved-foundation-series-re-7b85
---

From 7b85 review 1, 2026-10-12: launch-command.md lines 25 and 39 say 'if a skill named here is missing … say which one', so a session on an ordinary series reports foundation as missing though it never needed it. Change both to 'if a skill this asks you to use is missing from this session, say which one in one clause of your reply.'

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
target: launch-command.md lines 25 and 39 say "if a skill this asks you to use is missing from this session, say which one in one clause of your reply."
dispatch: implementer sonnet medium — build (two-line wording: canonical kind)
agent: implementer a8276de30316e1fd6
return: DONE c7ee13b; both clauses replaced; substitution phrases intact; no other file quotes it; kit-dev 21 OK
dispatch: reviewer opus high — review round 1 of c7ee13b
agent: reviewer a6f5c269d49772711
verdict: review round 1 CLEAR (must-fix 0; optional: "say which one" singular, pre-existing; a stricter "path you took" wording — both declined: the reviewer expects the wording to read right and it is the item's own)
landed: 67bae4f (merge of c7ee13b); Checks 12/12 OK; cc_scan clean
- 2026-10-12 done
