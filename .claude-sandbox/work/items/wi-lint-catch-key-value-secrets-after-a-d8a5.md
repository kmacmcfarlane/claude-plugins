---
id: wi-lint-catch-key-value-secrets-after-a-d8a5
title: "wi lint: catch KEY=value secrets after a bullet or date prefix"
short_display_name: lint misses prefixed secrets
type: bug
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T04:57Z
created: 2026-10-08
updated: 2026-10-08
refs:
  - checkpoint-before-the-manifest-write-con-6c43 review 1
---

Found by the 6c43 review 1 (finding 7, medium), 2026-10-08: SECRET_ASSIGN_RE in wi.py is anchored at line start, so '- <date> checkpoint: CORRECTION KEY=value' lints clean while the bare line is caught. Acceptance: the assignment is matched after a bullet, date or tag prefix; a test pins both shapes.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: full main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/wi-lint-catch-key-value-secrets-after-a-d8a5
budget: 2026-10-08T04:55Z build $12 — default bug
dispatch: implementer opus medium — bug in a secret guard (security-relevant; not mechanical)
agent: implementer ad8e44c4c16a95bb7

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
return: DONE_WITH_CONCERNS 01a17c1 (SECRET_ASSIGN_RE searched after whitespace, bracket, comma, colon, pipe, quote or backtick; tests both ways; one new real-store hit: a HOME path in item 8a67 line 21, reworded in the store)
changed: wi.py (SECRET_ASSIGN_RE), tests/test_wi.py (two TestLint tests), references/format.md (the rule's wording)
dispatch: reviewer opus high — review round 1
agent: reviewer aed4304ee761faaaf
verdict: review 1 NEEDS_CHANGES at 01a17c1 (must-fix 2: the allowed prefix list misses **bold**, >, #, unspaced em dash and other punctuation; format.md overclaims; low: mid-prose path assignments now flagged)
dispatch: implementer opus medium — fix round 1 (resume ad8e44c4c16a95bb7)
