---
id: statusline-hub-end-the-silent-wait-behin-7dd3
title: "statusline-hub: end the silent wait behind an older footer copy; name the footer"
short_display_name: hub silent wait behind old footer
type: bug
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T07:26Z
created: 2026-10-08
updated: 2026-10-08
refs:
  - spike-how-much-inter-plugin-dependency-i-72ef
---

Follow-up F2 from the plugin-dependency spike (72ef), 2026-10-08. Acceptance: as .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md § R3 F2 states, with 01_review-1-fixes.md and 02_review-2-fixes.md applied (Supersedes in order). Rank 1. Must land before the statusline compat removal (a95a).

## Handoff
- doing: review round 1 running (reviewer a0d68362569272315) on 0354d97
- next: on CLEAR: land and push; weigh the a95a open case
- blocked: —
- learned: —
target: full main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/statusline-hub-end-the-silent-wait-behin-7dd3
budget: 2026-10-08T07:26Z build waived — operator waiver (spend still measured)
findings: carried — reviewer nit: when the install records cannot be read, keep the hub's existing "cannot tell, do nothing" rule (session_start.py:370-378)
dispatch: implementer opus medium — hook code fix with tests

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a6b6507ff123a6363
return: DONE_WITH_CONCERNS 0354d97 (older-copy rule: dead copy taken, live copy said once, dangling link with record left alone, cannot-tell does nothing; SH-1 names statusline; 228 hub tests; open: recorded plugin, link resolves, script removed (the a95a removal) still waits silently)
changed: statusline-hub hooks session_start.py, owner.py, tests (handover, session_start, owner), skills/statusline-hub/references/hook-contract.md
dispatch: reviewer opus high — review round 1
agent: reviewer a0d68362569272315
