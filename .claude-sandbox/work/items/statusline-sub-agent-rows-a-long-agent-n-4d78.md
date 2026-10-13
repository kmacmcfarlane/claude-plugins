---
id: statusline-sub-agent-rows-a-long-agent-n-4d78
title: "statusline sub-agent rows: a long agent name can still crowd out the tag and description"
short_display_name: long agent name crowds the row
type: bug
status: done
priority: 4
created: 2026-10-08
updated: 2026-10-09
closed: 2026-10-09
refs:
  - statusline-sub-agent-rows-cap-an-overlon-8680 review 1
---

From the 8680 review 1 (low 4), 2026-10-08: e.g. dev-flow:implementer-critical with a 40-column model at 80 columns renders name and fill only. Acceptance: decide whether the name is capped or shortened (e.g. the plugin prefix dropped) and pin it with a test; the widening sweep holds.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree (bug)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a5403f5182904c63b
return: DONE worktree-agent-a5403f5182904c63b ca98f84 (long names give way: plugin prefix dropped, then cut with an ellipsis to no less than 8 columns, before the tag goes or the description drops below 10; two tests incl. a 1-140 column sweep; install-statusline doc; 12/12 Checks)
dispatch: reviewer opus high — review round 1 of ca98f84
agent: reviewer a6169790059790f8b
verdict: review round 1 NEEDS_CHANGES (medium 1: the description shrinks as the pane widens when the name's slack is handed to it; lows: cut names collide (implementer-critical/-deep read alike), prefix pattern strips any word:, floor is 7 for wide chars, tests miss the description width)
decided: 2026-10-09T10:07Z design — names cut from the middle keeping both ends (suffixes tell dev-flow's variants apart), prefix stripped only in the plugin-name shape
dispatch: implementer opus medium — fix round 1 (resume a5403f5182904c63b)
return: DONE f926743 (shortened name keeps its whole share, description never narrows, swept; middle cut keeping both ends, pairs tested distinct at 50 and 60; prefix rule must match the whole name in plugin:agent shape; floor wording; 206 tests)
decided: 2026-10-09T10:12Z design — keep dropping a plugin-shaped prefix: a lowercase name like fix:build that has the exact plugin:agent shape loses its prefix only at the 8-column floor, where the full name cannot show anyway
dispatch: reviewer opus high — review round 2 (resume a6169790059790f8b)
verdict: review round 2 CLEAR (0-159 col sweep clean incl. description never narrowing; all 14 dev-flow names distinct at every width; nits accepted)
landed: 1ea5298 (merge of ca98f84, f926743); Checks 12/12 OK
- 2026-10-09 done
