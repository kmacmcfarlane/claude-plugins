---
id: work-items-typed-cross-repo-edges-repo-i-375e
title: "work-items: typed cross-repo edges (repo:id) that wi estate reads and shows"
short_display_name: cross-repo edges
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-09-30T22:27Z
created: 2026-09-30
updated: 2026-09-30
refs:
  - "peer: agents librarian (uds 135.sock), 2026-09-30; their item relay-to-claude-plugins-wi-deps-must-accept-*"
  - agents .claude-sandbox/investigations/initiative-layer/01-synthesis.md § 1c, § 6, OQ5
---

Requested 2026-09-30 by the agents librarian (peer request, not an approval) for the first landable slice of their initiative layer. Their research (12/12 claims verified) found 167 wi deps edges estate-wide, all local; wi validates deps and parent against its own store, so a cross-repo edge cannot be written. Asked: typed edges from one item to another repo's item in repo:id form, types blocks, rolls-out-after, derived-from, interface; wi estate reads and displays them. Shape, storage and validation are ours to decide; the plan settles (1) whether deps takes repo:id or a new field is added, (2) an unreadable store or item shows as unavailable, never silently dropped. Related: agents 76bc (work-system requirements; its 4-char tag lookup is on the same path). Acceptance: the plan's answers to (1) and (2); wi add/set/ls/show/lint and wi estate handle the edges with tests; format.md documents them.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-30 claimed by Kyle-McFarlane@401123cbad11
target: plan work-items-typed-cross-repo-edges-repo-i-375e /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/375e-cross-repo-edges
dispatch: planner opus high — plan-only in wave 1 (132 a); spike-style plan for a feature
agent: planner ad19358f9a90c2117 round 1
return: planner DONE_WITH_CONCERNS /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/375e-cross-repo-edges
baseline: 4e1be3b1f4f3cc3dafc905bc62e779bd487dba52d8de118e9e98bc59e1f97fb3  00_initial.md 
dispatch: reviewer opus high — plan review round 1 (rule 4)
agent: reviewer a5869445e366eb4e6 round 1
verdict: NEEDS_CHANGES round 1 at .claude-sandbox/investigations/375e-cross-repo-edges
findings:
  1. [high] 00:174-179,254-260,291 — unreadable store dir / .claude-sandbox / repo dir: Path.is_dir() raises EACCES on py3.11, wi estate crashes (reproduced); estate_scan and _repo_candidates/git_common_dir must catch OSError → PROBLEM + store unreadable, with tests
  2. [medium] 00:280 vs 302-304 — "do not cap edges" contradicts adding edges to ESTATE_LISTS (_estate_cap caps every key; early-return rec lacks key → KeyError)
  3. [medium] 00:254-257,443-445 — an unreadable archive year takes the whole-store failure path, hiding live items/decisions; make it a problem entry that keeps the live summary
  4. [medium] 00:129-131 vs 290 — skipped alias (symlinked repo, linked worktree) resolves to not found, not repo not scanned as documented
  5. [medium] 00:72-79,201,572-574 — blocked-by beyond acceptance (four kinds asked); new stored API needs the requester's or operator's yes
  6. [low] 00:291-292 — no store before repo ambiguous ordering
  7. [low] 00:13,230-232 — deps refuses repo:id only without --force; consider refusing edge-shaped values under --force
  8. [low] 00:37-38 — wi next prints "1 waiting on deps"; "no message" overstated
  9. [nit] 00:534 — "estate gains no I/O" vs the listdir calls; resolution needs the scan-dir listing kept
librarian ruling on 5: the build ships the four requested kinds; blocked-by moves to Open Questions (owner: agents librarian and the operator; not blocking) and is asked of them with the plan, not added now — a new stored name is theirs (111 b raises API names)
dispatch: planner opus high — resume, fix round 1 (serial 01)
agent: planner ad19358f9a90c2117 round 2
