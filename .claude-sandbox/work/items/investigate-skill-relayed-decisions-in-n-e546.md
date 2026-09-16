---
id: investigate-skill-relayed-decisions-in-n-e546
title: "investigate skill: relayed decisions in non-interactive runs are blocking open questions"
type: feature
status: done
priority: 2
tags: [dev-flow]
deps:
  - checkout-process-convention-9e6d
created: 2026-09-14
updated: 2026-09-14
closed: 2026-09-14
refs:
  - pintail-11 session relaying operator, 2026-09-14
---

Operator process note (2026-09-14, via pintail-11): when an investigation runs non-interactively and a relayed operator decision would change a default for interactive users, record it as an open question that BLOCKS implementation, not as a confirmed assumption. Motivating failure: 'agents should use worktrees' was relayed into 'worktree on by default for everyone', which broke --resume for interactive sessions. Add to the investigate skill's non-interactive section (and its confirmed-assumptions guidance): a relayed decision affecting users not present in the loop is never confirmable in-session. Depends on checkout-process-convention landing first (same file touched).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-14 claimed by librarian
- 2026-09-14 done: 0aa8a29 merged to local main; review CLEAR round 1

## Review
- Round 1 (6f4f3c2): CLEAR — 7-line bullet in Running non-interactively; two-part trigger
  (relayed AND affecting people not present) keeps it from over-blocking; connects to the
  format's blocks-or-not marking; format.md deliberately unchanged (semantics travel in the
  artifact; its header forbids restating). 2 lows + 1 nit accepted: operator-authored work
  items could be read as "relayed" (both routings acceptable, fails safe); the rationale
  sentence proves too much outside its section; bullet 1 lacks a forward reference.
