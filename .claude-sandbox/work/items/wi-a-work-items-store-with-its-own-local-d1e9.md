---
id: wi-a-work-items-store-with-its-own-local-d1e9
title: "wi: a .work-items/ store with its own local git repo, committed under wi's lock"
short_display_name: wi nested store repo
type: feature
status: todo
priority: 1
created: 2026-10-15
updated: 2026-10-15
refs:
  - answer 232 a
---

Answer 232 a (operator 2026-10-15; claude-sandbox 117 a, 118 a): every .work-items/ store gets its own local git repo with no remote; the host ignores /.work-items/. wi treats such a store as tracked, init sets the repo up, and wi commits each item change into it under its lock; a failed commit never loses the item write (save first, warn), with a fallback identity only when git var GIT_AUTHOR_IDENT fails; lint warns about git clean -ff near a store. Builds on 5f46.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: series .claude-sandbox/investigations/wi-a-work-items-store-with-its-own-local-d1e9/
budget: waived (operator 2026-10-08); spend measured
dispatch: planner opus high — plan the nested store repo (answer 232 a)
agent: planner ac5d8b6d969db2d50 round 1
note: F-R1..F-R5 from b2df handed to the d1e9 planner (F-R5: landed store commits under flock or wi before stores nest)
