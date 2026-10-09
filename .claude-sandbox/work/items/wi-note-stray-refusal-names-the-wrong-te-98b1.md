---
id: wi-note-stray-refusal-names-the-wrong-te-98b1
title: "wi note: stray -- refusal names the wrong text number in two odd argv shapes"
short_display_name: wi note stray -- text number
type: bug
status: doing
priority: 4
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T10:30Z
created: 2026-10-08
updated: 2026-10-09
refs:
  - wi-note-append-a-notes-line-under-lock-a-6cfb review 2
---

From the 6cfb review 2 (low 1), 2026-10-08: _stray_separator reports text 3 for 'wi --roo note note <id> -- a -- b' and text 2 for 'wi note <id> -5 -- a -- b'. Refusal is still correct; only n is off, and checkpoint 4a½ never builds these shapes. Acceptance: count texts as argparse does (drop --raw/-h/--help and the id only); a test pins both shapes.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a9822fcef7cddd25f
