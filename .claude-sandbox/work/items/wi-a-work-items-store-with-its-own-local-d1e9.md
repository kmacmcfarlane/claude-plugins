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
return: planner DONE .claude-sandbox/investigations/wi-a-work-items-store-with-its-own-local-d1e9 (00_initial.md; store.yaml repo: own; hardened store git runner with ceiling and hooksPath=/dev/null; new wi commit verb replacing every landed store-commit site (closes b2df F-R5, two more sites found); init creates or adopts; per-change commits; F1-F5 with F4 a relay; OQ1 names, OQ2 migration waiting)
baseline: 57b8bc4b87f6de3a6edf8c70a9c585107fbef27fd98b87bdf3eb1699e0848210  00_initial.md f5a5db2660075459e4f2c7aa95a894cef89add67fbdc66632a789305b90c0724  INDEX.md 
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer a3b8f5b2c3a80ea24 plan round 1
verdict: NEEDS_CHANGES plan round 1 (7 must-fix: fixed pathspec list fails on a store with no archive/; custody reads run unpinned git (fsmonitor); attribute-selected clean filters run under every pin; own-but-unrecorded store gets unhardened commits; uncommitted as a lint problem breaks the lint-then-commit rule; the plan ignores claude-sandbox's agreed hold; A9 notes and Q1 (iii) also need relaying; 6 low incl. lock deadline, journal sources, idempotent rerun, cc_scan before wi commit; 1 nit)
dispatch: planner opus high — resume, plan fix round 1
agent: planner ac5d8b6d969db2d50 round 2
return: planner DONE .claude-sandbox/investigations/wi-a-work-items-store-with-its-own-local-d1e9 (01_review-round-1.md; all 14 applied plus blast-radius line; OQ1 names (rec keep --no-track), OQ2 rec keep the hold)
baseline: 57b8bc4b87f6de3a6edf8c70a9c585107fbef27fd98b87bdf3eb1699e0848210  00_initial.md 069ab639f391e5af8d26b3aaed83087b9a48f9a86b5496f88e4ef25177cf4de4  01_review-round-1.md 641b4a26479a6d2f7d836b60a4df2d18e71f7cbb67b85d31cc19cf908d3b4d98  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 2
agent: reviewer a3b8f5b2c3a80ea24 plan round 2
verdict: NEEDS_CHANGES plan round 2 (12 of 14 closed; 2 medium exact: attribute files deeper than the store shape or index-only still run a filter; check-ignore refuses GIT_LITERAL_PATHSPECS so custody goes silent; 3 low exact: validation before the lock with a 2 s timeout, a dedicated top-of-repo store keeps attributes, relay the lift only at the push; nit; note: scrub GIT_ATTR_SOURCE, check attr.tree on newer git)
dispatch: planner opus high — resume, plan fix round 2
agent: planner ac5d8b6d969db2d50 round 3
return: planner DONE .claude-sandbox/investigations/wi-a-work-items-store-with-its-own-local-d1e9 (02_review-round-2.md; six exact fixes; attr.tree risk recorded)
baseline: 57b8bc4b87f6de3a6edf8c70a9c585107fbef27fd98b87bdf3eb1699e0848210  00_initial.md 069ab639f391e5af8d26b3aaed83087b9a48f9a86b5496f88e4ef25177cf4de4  01_review-round-1.md 5e7df59960dcfc76f565fa0c23bb8b99f5943f1b3ec2c9ab9d194cd6a2af1fee  02_review-round-2.md daa906d3241f6821b3948939c3bc2cd272cc222dd5a03fa24becd258b2b38666  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 3
agent: reviewer a3b8f5b2c3a80ea24 plan round 3
verdict: CLEAR plan round 3 (low: pin -c attr.tree=<empty tree> in the runner, no version check needed; nit: skip the GIT_ATTR_SOURCE test below the git that reads it — both carried into F1's brief)
findings: carried — D2 pins add -c attr.tree=4b825dc642cb6eb9a060e54bf8d69288fbee4904 (https://github.com/git/git/blob/master/Documentation/config/attr.adoc); the GIT_ATTR_SOURCE test is skipped below the git that reads it
decision 240: OQ1 — names for a store with its own repo — options: (a) keep --no-track; store.yaml records tracking: tracked plus repo: own (the flag describes the host, the record the store's own repo) [recommended] | (b) a new --own-repo flag | (c) a third value, tracking: own-repo | (z) decide later: F3 builds (a)
decision 241: OQ2 — lift claude-sandbox's hold (no nested store repo before d1e9 lands)? — options: (a) lift it now: claude-sandbox creates the repos by hand, adopted later with history kept | (b) keep it: only history between a store's move and d1e9's push is lost [recommended] | (z) decide later: the hold stands
