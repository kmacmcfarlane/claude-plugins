---
id: review-checklist-3-plugin-shape-changed-775a
title: "review-checklist §3: 'plugin shape changed without README' fires on any .claude-plugin edit"
type: bug
status: done
priority: 3
created: 2026-09-28
updated: 2026-09-28
closed: 2026-09-28
refs:
  - 1a54 implementer
---

Found by the 1a54 implementer 2026-09-28: dev-cycle references/review-checklist.md §3 fails on any change under .claude-plugin/ without a README edit, even a description-only change that leaves the marketplace's shape alone. Acceptance: the check fires only when the set of listed plugins (or their source paths) changes; a test or worked example of both cases.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-review-checklist-3-plugin-shape-changed-775a at .claude/worktrees/review-checklist-3-plugin-shape-changed-775a, base main (49f9420)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — executable checklist commands (rule 2)
agent: implementer ae1c9c8cdf3769714 round 1
return: implementer DONE 4effa0d
changed: plugins/dev-flow/skills/dev-cycle/references/review-checklist.md
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer a0530ba80d27bbf98 round 1 at 4effa0d
verdict: CLEAR round 1 at 4effa0d (4 low: non-ASCII path detail misprinted but still FAILs; object source key-order; bash-only <( ); generic var d — declined for this landing: every failure mode is loud, none lets a shape change through)
landed: a4ef1f4
- 2026-09-28 done: a4ef1f4
