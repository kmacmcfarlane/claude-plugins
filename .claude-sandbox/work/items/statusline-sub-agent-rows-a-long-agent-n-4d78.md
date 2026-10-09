---
id: statusline-sub-agent-rows-a-long-agent-n-4d78
title: "statusline sub-agent rows: a long agent name can still crowd out the tag and description"
short_display_name: long agent name crowds the row
type: bug
status: doing
priority: 4
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T09:47Z
created: 2026-10-08
updated: 2026-10-09
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
