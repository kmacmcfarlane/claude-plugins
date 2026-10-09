---
id: wi-note-stray-refusal-names-the-wrong-te-98b1
title: "wi note: stray -- refusal names the wrong text number in two odd argv shapes"
short_display_name: wi note stray -- text number
type: bug
status: done
priority: 4
created: 2026-10-08
updated: 2026-10-09
closed: 2026-10-09
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
return: DONE worktree-agent-a9822fcef7cddd25f 8de11d9 (refusal counts texts as argparse does: --root in any accepted prefix or =value, note's own options excluded; test with four cases, three fail on old code; reported 10 Checks)
dispatch: reviewer opus high — review round 1 of 8de11d9
agent: reviewer a73be5f650ca9e7b2
verdict: review round 1 CLEAR (fuzzed 69,038 accepted argv shapes: 0 mismatches vs 1,756 on old code; lows: id-is-'--' disables the refusal (harmless, resolve fails); missing id-after-separator subtest; nit: _abbrev docstring and hand-typed option names); all 12 Checks pass
decided: 2026-10-09T10:48Z cap — finish round of lows 1-2 and the nit's comment (authority answer 145)
dispatch: implementer opus medium — finish round (resume a9822fcef7cddd25f)
return: DONE b2cf9a8 (id-is-'--' searched past; two subtests; docstring and comment)
review: self
verdict: finish round CLEAR — diff read: the snippet as given, the comment names build_parser not line numbers
landed: c4873ef (merge of 8de11d9, b2cf9a8); Checks 12/12 OK
- 2026-10-09 done
