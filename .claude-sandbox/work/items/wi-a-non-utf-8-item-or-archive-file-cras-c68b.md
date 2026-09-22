---
id: wi-a-non-utf-8-item-or-archive-file-cras-c68b
title: "wi: a non-UTF-8 item or archive file crashes strict readers with a traceback"
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:47Z
created: 2026-09-22
updated: 2026-09-22
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
