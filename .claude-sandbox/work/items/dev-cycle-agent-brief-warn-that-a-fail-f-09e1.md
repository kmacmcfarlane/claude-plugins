---
id: dev-cycle-agent-brief-warn-that-a-fail-f-09e1
title: "dev-cycle agent-brief: warn that a fail-first checkout overwrites uncommitted edits"
type: chore
status: todo
priority: 2
created: 2026-09-22
updated: 2026-09-22
refs:
  - librarian observation 2026-09-22
---

2026-09-22: three implementers (H2 d0eb, H6 b6de, H3 2cce) ran 'git checkout HEAD -- <path>' / a main swap before committing and lost their edits (re-applied each time). agent-brief.md's fail-first recipe says commit first, but not loudly. Acceptance: agent-brief.md (and review-checklist if it shows the recipe) states in one bold line: commit before any 'git checkout <ref> -- <path>'; it overwrites uncommitted edits silently.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
