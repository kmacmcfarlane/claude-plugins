---
id: claude-md-conventions-add-a-hooks-entry-e01a
title: "CLAUDE.md conventions: add a hooks entry"
type: chore
status: done
priority: 4
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - reviewer report, item readme-structure-tree-lists-only-part-of-b85e
---

Reviewer of b85e 2026-09-16: CLAUDE.md's layout block now shows plugins/claude-kit/hooks/ but the Conventions list has entries only for skills, agents and the plugin registry. Acceptance: one convention bullet for hooks (location plugins/claude-kit/hooks/, registered via hooks/hooks.json, tests under hooks/tests/), same shape as the agent bullet.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
dispatch: implementer opus — rule 2 (CLAUDE.md conventions / doctrine)
dispatch: reviewer opus — rule 4
- implementer opus returned DONE, commit df32a49; reviewer opus round 1 dispatched 2026-09-16 17:01:34
- review round 1: CLEAR with 2 lows (bullet omits that every hooks.json command interpolates ${CLAUDE_PLUGIN_ROOT}; one SessionStart command is a shell one-liner, not a script). Librarian: low 1 has a real silent-failure scenario — offered to the implementer as fix round 1 (author's call), tier unchanged (opus, resumed) 2026-09-16 17:03:33. Reviewer also flagged: the checklist's '^[-+][-+]' grep drops Markdown bullet lines (false negative); README has no doctrine section though review-checklist.md § 3 says 'when present' — cross-reference may be stale.
- fix round 1 returned DONE, new commit 260b0b8, both lows fixed; re-review dispatched 2026-09-16 17:04:24 (reviewer opus, resumed)
- 2026-09-16 done: 69f555a
- re-review CLEAR (1 FIXED, 2 fixed in substance); 1 new low (bullet is 687 chars, ~3x the longest sibling) — not blocking, left as is. Landed merge 69f555a 2026-09-16 17:06:06.
