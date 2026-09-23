---
id: wi-a-non-utf-8-item-or-archive-file-cras-c68b
title: "wi: a non-UTF-8 item or archive file crashes strict readers with a traceback"
type: bug
status: done
priority: 3
created: 2026-09-22
updated: 2026-09-23
closed: 2026-09-23
refs:
  - cc39 implementer
---

cc39 implementer OQ, 2026-09-22 (pre-existing on main): claim, show, lint and every load_all(archived=True) caller raise an uncaught UnicodeDecodeError on a non-UTF-8 file in items/ or archive/. Acceptance: strict readers turn it into a WiError naming the file (clean exit code); lint reports it; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full wi-a-non-utf-8-item-or-archive-file-cras-c68b /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/wi-a-non-utf-8-item-or-archive-file-cras-c68b
dispatch: implementer opus — executable logic (wi.py), rule 2
return: implementer DONE 87e4d23
changed: wi.py (read_raw decode → WiError 3; lint via read_raw), tests/test_wi.py
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer ae37871f87893f897 round 1
verdict: NEEDS_CHANGES round 1 at 87e4d23 (CRLF lint identical main vs HEAD; locale not a regression)
findings:
- [medium] wi.py:1847 cmd_ls --dep swallows every WiError (bare except → dep = args.dep): a bad archive file gives rc 2, no rows, no message. Pass: re-raise unless the no-match case (code 2), keep AmbiguousId; test ls --dep <prefix> with a bad archive file → rc 3 naming it.
- [low] wi.py:970-975 read_raw decodes with the locale encoding; librarian decision: force encoding="utf-8" in read_raw and atomic_write (symmetric, the one decode point).
- [low] :2755 lint on a CR-only file now reports only missing front matter — accepted as an extreme edge (note only).
dispatch: implementer opus — fix round 1 (resume)
agent: implementer acf6981e295ee076f round 2
return: implementer DONE 1b5c7cd
dispatch: reviewer opus — review r2 (resume)
agent: reviewer ae37871f87893f897 round 2
verdict: CLEAR round 2 at 1b5c7cd
landed: 4dcaba3
- 2026-09-23 done: 4dcaba3
