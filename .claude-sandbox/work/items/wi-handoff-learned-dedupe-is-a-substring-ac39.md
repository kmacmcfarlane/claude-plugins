---
id: wi-handoff-learned-dedupe-is-a-substring-ac39
title: "wi handoff: learned dedupe is a substring test, so L1 is skipped when L10 exists"
short_display_name: handoff learned dedupe too loose
type: bug
status: done
priority: 3
created: 2026-10-08
updated: 2026-10-09
closed: 2026-10-09
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
return: DONE worktree-agent-ab4ffbbabed75ed1b 67d7774 (cmd_handoff dedupes learned lines by whole line, CR tolerated; regression test fails without the fix; Checks OK)
dispatch: reviewer opus high — review round 1 of 67d7774
agent: reviewer aa487b8cabddd063c
verdict: review round 1 CLEAR (low 1: a --learned value with trailing whitespace is re-added every call — pre-existing, same class of bug; low 2: same text on a later day re-added, by design; info 3-4)
decided: 2026-10-09T09:59Z cap — finish round of low 1 (strip the value; compare stripped), authority answer 145; low 2 is by design
dispatch: implementer opus medium — finish round (resume ab4ffbbabed75ed1b)
return: DONE 931c198 (learned value stripped for the note line, compare rstripped; test)
review: self
verdict: finish round CLEAR — diff read: the strip and compare, one test
landed: 9b6728b (merge of 67d7774, 931c198); Checks 12/12 OK
- 2026-10-09 done
