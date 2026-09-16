---
id: readme-structure-tree-lists-only-part-of-b85e
title: README Structure tree lists only part of claude-kit's skills
type: chore
status: done
priority: 4
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - implementer report, item readme-catalog-missing-the-chat-plugin-a13d
---

Noticed by the a13d implementer 2026-09-16: README.md's Structure tree omits work-items, checkpoint, install-statusline, implement, investigate (and any other skill on disk). Acceptance: the tree lists every plugins/*/skills/* directory on disk, or is replaced by a shorter form that cannot go stale, e.g. plugins/<plugin>/skills/<skill>/ with a pointer to the tables above.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
Also (a13d reviewer): the tree omits the agents/ directory CLAUDE.md documents; cover it too. And CLAUDE.md's layout block now mixes a literal skill dir (chat) with <skill-name> placeholders — pick one idiom.

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
Scope: README.md (Structure block) and CLAUDE.md (layout block) only.
dispatch: implementer opus — rule 2 (doctrine / catalog)
dispatch: reviewer opus — rule 4
- implementer opus returned DONE, commit c779549 (kept a literal tree; placeholders everywhere in CLAUDE.md); reviewer opus round 1 dispatched 2026-09-16 16:53:24
- 2026-09-16 done: 23f2840
- review CLEAR; 2 lows not sent back (a 'One directory per skill' comment only on claude-kit's skills/; hooks/ comments enumerate different subsets in README vs CLAUDE.md) — recorded, author's call, loop already CLEAR. Reviewer flagged the librarian's sed-based tree->disk loop as vacuous (stops at the opening fence); replaced with an awk range at Land. Landed merge 23f2840 2026-09-16 16:56:12.
- Land note: the librarian's awk tree->disk loop printed STALE for every name because 'ls -d a b c' exits nonzero when any arg is missing; the merge had already run. Re-verified on main with a per-path [ -d ] test: no STALE, disk->README clean. Landing stands; the loop in the review brief needs the per-path form next time.
