---
id: dev-flow-worktrees-1ff9
title: Align dev-flow worktree-orchestration with harness-native .claude/worktrees convention
type: chore
status: done
priority: 3
tags: [dev-flow]
created: 2026-09-04
updated: 2026-09-08
closed: 2026-09-08
---

Operator decision (2026-09-04): the estate standardizes on the harness-native worktree convention, .claude/worktrees/<name> on branch worktree-<name>, with single-writer enforcement from the harness. dev-flow's implement reference (plugins/dev-flow/skills/implement/references/worktree-orchestration.md) still mandates .worktrees/<id>/ and slug-<n> branches. Align it: paths, branch names, gitignore guidance (.claude/worktrees/ must be ignored), and prefer the harness tools (EnterWorktree / Agent isolation) over manual git worktree add where available. Also note ralph's worktree.py helper targets the old path.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-08 claimed by librarian
- 2026-09-08 done: de15d0c merged to local main; review CLEAR round 2

## Review
- Round 1 (b059772): NEEDS_CHANGES — 1 medium: naming/consolidation/cleanup written only in
  manual worktree-<slug>-<n> terms, ignoring harness-assigned branch names on the doc's own
  preferred dispatch path; 1 low (invariant false for worktree-less branches; bare-slug
  collision) and 1 nit (helper convention was story/<id>), both taken. CAID doctrine verified
  byte-untouched; MIGRATION.md facts confirmed.
- Round 2 (15c06aa): CLEAR — both dispatch paths walk coherently; retired tokens survive only
  in the Retired section. 1 informational nit accepted.
- Path mapping: item named plugins/dev-flow/... (unlanded layout); landed on main's copy at
  plugins/claude-kit/skills/implement/. Migration reconcile note: land-plugin-factoring-fbe8.
- Reviewer follow-up suggestion not filed as an item: update-kit SKILL.md:153 still lists
  .worktrees/ in a layout listing — fold into the factoring migration sweep.
