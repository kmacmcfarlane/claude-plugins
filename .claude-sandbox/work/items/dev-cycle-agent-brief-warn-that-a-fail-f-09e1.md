---
id: dev-cycle-agent-brief-warn-that-a-fail-f-09e1
title: "dev-cycle agent-brief: warn that a fail-first checkout overwrites uncommitted edits"
type: chore
status: doing
priority: 2
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:20Z
created: 2026-09-22
updated: 2026-09-28
refs:
  - librarian observation 2026-09-22
---

2026-09-22: three implementers (H2 d0eb, H6 b6de, H3 2cce) ran 'git checkout HEAD -- <path>' / a main swap before committing and lost their edits (re-applied each time). agent-brief.md's fail-first recipe says commit first, but not loudly. Acceptance: agent-brief.md (and review-checklist if it shows the recipe) states in one bold line: commit before any 'git checkout <ref> -- <path>'; it overwrites uncommitted edits silently.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-dev-cycle-agent-brief-warn-that-a-fail-f-09e1 at .claude/worktrees/dev-cycle-agent-brief-warn-that-a-fail-f-09e1, base main (3d7760d)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — adds a rule line to the brief template (rule 2)
agent: implementer a7730b89c87d8fe2f round 1
