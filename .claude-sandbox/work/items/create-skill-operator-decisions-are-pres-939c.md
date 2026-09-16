---
id: create-skill-operator-decisions-are-pres-939c
title: "create-skill: operator decisions are presented as a numbered list"
type: feature
status: done
priority: 3
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator 2026-09-16 (decision 5, 'both'): the create-skill authoring rules gain a convention — when a skill needs decisions from the operator, it presents them as a numbered list, one decision per number, each with its options and their impact and a recommendation first, so the operator can answer by number; and it never pairs the list with a heavy analysis in the same turn (present, then ask). Acceptance: one bullet in create-skill/SKILL.md's authoring rules (or its references/ style guide if that is where output conventions live), matching the existing bullet register; SKILL.md under 5000 tokens; no other change.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
dispatch: implementer opus — rule 2 (doctrine: authoring rules)
dispatch: reviewer opus — rule 4

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
- implementer opus returned DONE, commit cbdd156; reviewer opus round 1 dispatched 2026-09-16 17:56:16
- 2026-09-16 done: 11b5802
- review CLEAR; 3 lows (bullet length/register; 'operator' vs the file's 'user'; AskUserQuestion vs numbered list mechanism seam with librarian-mode — the 486d review is ruling on that seam). Landed merge 11b5802 2026-09-16 17:59:07.
