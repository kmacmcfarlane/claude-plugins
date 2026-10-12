---
id: create-repo-prompt-report-only-a-skill-t-1b6a
title: "create-repo prompt: report only a skill the prompt asked the session to use"
short_display_name: create-repo missing-skill wording
type: chore
status: doing
priority: 4
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-12T21:34Z
created: 2026-10-12
updated: 2026-10-12
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
