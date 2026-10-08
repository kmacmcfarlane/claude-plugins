---
id: statusline-hub-end-the-silent-wait-behin-7dd3
title: "statusline-hub: end the silent wait behind an older footer copy; name the footer"
short_display_name: hub silent wait behind old footer
type: bug
status: done
priority: 1
created: 2026-10-08
updated: 2026-10-08
closed: 2026-10-08
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
verdict: review 1 NEEDS_CHANGES at 0354d97 (must-fix 1: a recorded plugin whose current-hooks resolves to a dir with no statusline.py still waits — the a95a state; lows: tracked .claude/settings.json can be written (follow-up), README soft-dep paragraph understates; nits)
decided: wording — finding 1 is in scope: the series lands F2 before a95a precisely so a95a's state is not a silent wait; a resolving link with no script is not the mid-update state 02 guards (a dangling link)
dispatch: implementer opus medium — fix round 1 (resume a6b6507ff123a6363)
return: DONE 7cf366d fix round 1 (recorded plugin whose resolving link lacks statusline.py is taken; test; hook-contract; README :537)
changed: README.md (:537, soft-dep sentence)
dispatch: reviewer opus high — review round 2 (resume a0d68362569272315)
verdict: review 2 CLEAR at 7cf366d (must-fix 0; lows: a local-path git rewrite window, a recorded-but-disabled context-guard still waits once its orphaned folder is pruned — noted on a95a)
landed: ea740bd (merge --no-ff into main; Checks 10/10 OK; push scan read, clean)
- 2026-10-08 done
