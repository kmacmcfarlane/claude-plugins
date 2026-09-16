---
id: land-plugin-factoring-fbe8
title: Land plugin-factoring on main (operator review pending)
type: task
status: blocked
priority: 1
blocked: operator review pending; operator holding until spare time (2026-09-08)
created: 2026-09-04
updated: 2026-09-08
---

plugin-factoring (14 commits, 0079d1c..d118f48, epic fully reviewed) now lives in worktree .claude/worktrees/plugin-factoring; the main checkout is on main (dff2449). Operator (2026-09-04) chose NOT to merge it into main yet. Stacked on it: worktree-context-guard-turn-gate, worktree-backstage-disclosure-guard, worktree-librarian-mode. Landing plan: operator reviews plugin-factoring, then it merges to main (fast-forward, main has no commits it lacks), then the stacked branches rebase onto main. Blocks every kit-dev change since plugins/kit-dev exists only on this branch.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-04 operator: librarian-mode lands on `main` FIRST, under main's current layout
  (`plugins/claude-kit/skills/librarian-mode/`, main's CLAUDE.md/README). When this refactor
  lands, migrate it into `plugins/kit-dev/skills/librarian-mode/` with everything else, and
  re-point its catalog row and CLAUDE.md layout line. Anything else that lands on main under
  `claude-kit` before this branch merges gets the same treatment; list them here as they land.
- 2026-09-04: librarian-mode landed on main at `plugins/claude-kit/skills/librarian-mode/`
  (merge of worktree-librarian-mode-main). A kit-dev-layout variant of the same skill sits on
  branch `worktree-librarian-mode` (f1f07ca, stacked on plugin-factoring); the main version's
  layout-agnostic wording is the better base — migrate by moving the directory and dropping
  that branch.
- 2026-09-08: checkpoint-skill-stage-boundary-handoff-0509 lands on main's claude-kit copy of
  the checkpoint skill; the turn-gate branch also edits that SKILL.md (+17) and two
  references. Migration must three-way reconcile: factoring move + turn-gate edits + stage-
  boundary additions. Main's wording is layout-agnostic where possible.
- 2026-09-08: dev-flow-worktrees-1ff9 landed on main's claude-kit implement copy; the
  factoring branch's plugins/dev-flow/skills/implement/references/worktree-orchestration.md
  still mandates the retired .worktrees/<id> convention — reconcile at migration (main's
  version wins). Also sweep update-kit SKILL.md:153's .worktrees/ layout line then.
