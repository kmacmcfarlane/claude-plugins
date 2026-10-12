---
id: foundation-a-moved-series-with-every-gat-2298
title: "foundation: a moved series with every gate passed has no next step"
short_display_name: moved series past G3, next step
type: bug
status: doing
priority: 4
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-12T22:50Z
created: 2026-10-12
updated: 2026-10-12
refs:
  - foundation-a-series-moved-after-g3-canno-be6d
---

From be6d review 1 observation, 2026-10-13: a resumed moved series with every gate passed has no defined next step; its features were filed in the old repo's store or listed for filing by hand. Acceptance: foundation says what a resume after G3 does in a new repo (refile the listed features here, or point at the old repo's items).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: foundation says what a resume does when every gate passed, in a new repo: the features listed in the series are filed here (wi present) or listed for filing (no store), and the old repo's items are named when known; no re-filing in the old repo
dispatch: implementer opus medium — build

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a456e958153f73c9a
correction: 2026-10-13 I named this follow-up 63c4 to the operator twice; its tag is 2298. A dispatch record I wrote with an empty id landed in a stray items/.md file and was folded back into this item.
return: DONE e903e68; 12/12 OK; new bullet "A moved series past G3" in state.md § The work item, SKILL.md § Usage pointer; keys on a Moved from note and no item ref-ing the series path; new item --ref series path, first note carries the G3 line from the old repo
dispatch: reviewer opus high — review round 1 of e903e68
agent: reviewer a224d4b920c6f7d94
verdict: review round 1 NEEDS_CHANGES (must-fix 2: medium-high — trigger fires on a series moved before G3 whose gates passed here (Frame adds the item without --ref), re-filing every feature; medium — the ref search is unnamed and the default wi ls misses done and archived items; should-fix: Item: (was …) not in the template, readers taking the field whole fail; lows: never-re-files wording, no wi found, resume S7 moved case, crash between add and regeneration)
dispatch: implementer opus medium — fix round 1 (resume a456e958153f73c9a)
return: DONE 084bac8 (fix round 1); 12/12 OK; note: wi show exits 2 for an ambiguous id too
dispatch: reviewer opus high — review round 2 of 084bac8 (resume a224d4b920c6f7d94)
