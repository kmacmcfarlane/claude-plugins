---
id: foundation-a-series-moved-after-g3-canno-be6d
title: "foundation: a series moved after G3 cannot see its G3 approval"
short_display_name: moved foundation series G3 status
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-12T21:34Z
created: 2026-10-12
updated: 2026-10-12
refs:
  - create-repo-a-moved-foundation-series-re-7b85
---

From 7b85 review 1, 2026-10-12: state.md says a done foundation item or its G3 approval's answer N: line marks G3 passed; a series moved to a new repo cannot see the old repo's item, so a resumed session may re-run G3. Acceptance: G3's passing is recorded in the series itself (e.g. the Foundation block), so a moved series resumes past it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
target: G3's passing is recorded in the series itself (the Foundation block), so a series moved to a new repo resumes past G3; state.md and gates.md say so; a moved series with no work-item record of its own resumes at the right gate
dispatch: implementer opus medium — build
agent: implementer a6352961bcd58ea3f
return: DONE 0f9ad15; 12/12 OK; ### Gates passed list in the Foundation block, append-only, G<n> passed <date> (<repo>#<N>|reported|no store); orchestrator writes G3's line as step 1 after G3; planner writes G1/G2 lines from the brief; older series keep the old rule; also changed dev-cycle SKILL.md, agent-brief.md, resume.md
dispatch: reviewer opus high — review round 1 of 0f9ad15
agent: reviewer a465df0b41e988bf4
