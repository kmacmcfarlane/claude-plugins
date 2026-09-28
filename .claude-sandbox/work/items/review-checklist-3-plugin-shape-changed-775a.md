---
id: review-checklist-3-plugin-shape-changed-775a
title: "review-checklist §3: 'plugin shape changed without README' fires on any .claude-plugin edit"
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:33Z
created: 2026-09-28
updated: 2026-09-28
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
