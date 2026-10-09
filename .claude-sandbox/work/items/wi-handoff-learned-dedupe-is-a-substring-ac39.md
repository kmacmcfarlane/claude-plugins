---
id: wi-handoff-learned-dedupe-is-a-substring-ac39
title: "wi handoff: learned dedupe is a substring test, so L1 is skipped when L10 exists"
short_display_name: handoff learned dedupe too loose
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T09:47Z
created: 2026-10-08
updated: 2026-10-09
refs:
  - wi-note-append-a-notes-line-under-lock-a-6cfb review 1
---

Found by the 6cfb review 1 notes, 2026-10-08: cmd_handoff skips a learned: line when its text is a substring of an existing one (wi.py ~1654), so 'L1' is dropped when 'L10' exists. Acceptance: compare whole lines; a test pins it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree (bug)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer ab4ffbbabed75ed1b
