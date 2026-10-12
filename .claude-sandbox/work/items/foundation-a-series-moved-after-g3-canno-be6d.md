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
verdict: review round 1 NEEDS_CHANGES (must-fix 4: high — dev-cycle SKILL.md at 5003 words; medium-high — 'and commit it' conflicts with series tracking (public repo gitignores investigations); medium-high — a crash between the G3 line and filing leaves features never filed; medium — after a reopen an old line still marks the gate passed and the re-run line has no writer; should-fix: mixed-age series fallback per gate; an 'in session' ref for unnumbered approvals; low: investigation-format carry-forward on a move; observation filed as foundation-a-moved-series-with-every-gat-2298)
dispatch: implementer opus medium — fix round 1 (resume a6352961bcd58ea3f)
return: DONE 81198db (fix round 1); 12/12 OK; dev-cycle SKILL.md 4997 words; orchestrator G1/G2 line instruction placed in agent-brief.md
dispatch: reviewer opus high — review round 2 of 81198db (resume a465df0b41e988bf4)
verdict: review round 2 NEEDS_CHANGES (must-fix 2, down from 4: high — a row reading re-run after X can still pass by an earlier line, a later gate's line, an Approved date or the earlier answer, so a cut-short requirements reopen reads as approved; medium — the writers' line formats lack the after <reopen serial> ending and the paragraph is tied to a next dispatch a reopen may not have; low: two lines over width)
dispatch: implementer opus medium — fix round 2 (resume a6352961bcd58ea3f); review 3 next
return: DONE a2dd295 (fix round 2); 12/12 OK; dev-cycle SKILL.md 4997; writer wording mirrored into state.md Who writes, gates.md § 3, foundation SKILL.md
dispatch: reviewer opus high — review round 3 of a2dd295 (resume a465df0b41e988bf4)
