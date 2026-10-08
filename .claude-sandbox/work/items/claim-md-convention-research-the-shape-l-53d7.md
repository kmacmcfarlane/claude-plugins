---
id: claim-md-convention-research-the-shape-l-53d7
title: "CLAIM.md convention: research the shape, land a skill, seed one item per repo"
short_display_name: CLAIM.md convention skill
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T06:20Z
created: 2026-10-08
updated: 2026-10-08
refs:
  - peer claude-analytics 2026-10-08 (operator request there)
---

Relayed 2026-10-08 by peer claude-analytics from the operator there: a CLAIM.md, when present, sets out a repo's ownership claim and explicit known boundaries with other repos' areas of responsibility, so ownership questions stop recurring (the analytics split prompted it). The operator asks for: (1) a research round on the best shape (sections, how boundaries with other repos are stated, how changes are proposed and approved, how agents read it), with claude-analytics' operator-approved CLAIM.md (repo root, local main 4c2207d, not pushed; rule 'a producer emits; claude-analytics defines, reads and reports') as the worked example; (2) land the skill with the operator in this session, since the shape may need their input; (3) file a low-priority item in every active kmacmcfarlane repo with a work-item store to establish its own CLAIM.md; (4) then tell claude-analytics how to reshape theirs. Placement (which plugin) is a decision. FYI from the approved claim, nothing to change yet: usage-report retires at parity; item_spend.py is replaced by an attribution-event spend report (dev-cycle would emit a dispatch event, schema to come); quota_budget.py stays a listed reader; statusline-hub's record hook stays here.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: operator 2026-10-08 in this session: "I'm here for when you have decisions around the new claim skill (where should it land in our plugins system? Seems pretty stand-alone so maybe it's own plugin?). We can discuss when the research into how this sort of agentic codebase factoring/claim splitting strategy comes back." Placement lean: its own plugin, not yet decided; discussed after the research.
target: plan main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7
budget: 2026-10-08T06:20Z plan $28 — default plan
dispatch: planner opus high — research round and shape proposal (the research skill run unattended inside the plan)

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: planner a73b066060c1a0ca7
note: 2026-10-08 peer claude-analytics: CLAIM.md stays at their repo root (local main 4c2207d); the attribution/1 event schema follows once their serial 02 clears plan review and their contracts feature lands, with a copyable stdlib emit function
return: DONE_WITH_CONCERNS series 00_initial.md + research report (quick preset by the research skill's rule zero; 25 sources; verifier PASS 4/4); OQ1-4 block step 2, OQ6 blocks step 3
baseline: plan review 1 — a6db4276282b7ffa553a17890ec8d9cd1b3edaf4b42eed59dd73501ce4695e97 .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/00_initial.md; 
dispatch: reviewer opus high — plan review 1
decision 186: Where should the CLAIM.md skill live? — options: (a) a new plugin [recommended] | (b) work-items | (c) dev-flow | (d) kit-dev | (z) decide later
  raised: 2026-10-08T06:41Z
  why ask: placement — a new plugin and its catalog row are the operator's (principle 6; the operator asked to discuss it)
  impact: Effect → step 2 (the skill build) can start in its home · Wait: blocks step 2 · reach: the marketplace catalog · undo: moving a plugin later renames installs · cost: none
decision 187: What should the plugin and the skill be called? — options: (a) plugin ownership, skill claim-md, file CLAIM.md [recommended] | (b) plugin claims, skill claim | (z) decide later
  raised: 2026-10-08T06:41Z
  why ask: api-name — plugin and skill names are what users install and invoke (principle 5)
  impact: Effect → fixes the names the build ships · Wait: blocks step 2 · reach: every repo that installs it · undo: a rename breaks installs · cost: none
decision 188: Approve the proposed CLAIM.md shape (five required parts, optional sections, the defining side holds a boundary's text, every change approved by the operator, the CLAUDE.md pointer)? — options: (a) approve as drafted [recommended] | (b) approve with changes (say which) | (z) decide later
  raised: 2026-10-08T06:41Z
  why ask: your-call — the operator said the shape may need their input
  impact: Effect → the shape the skill writes and checks in every repo · Wait: blocks step 2 · reach: every repo's CLAIM.md · undo: easy before step 3 seeds repos; costly after · cost: none
decision 189: When a repo has both a CLAIM.md "Not ours" list and a librarian "Not owned:" line (from the unlanded scope-interview work), which wins? — options: (a) CLAIM.md is the authority; "Not owned:" must agree, and the check flags a mismatch [recommended] | (b) keep both independent | (z) decide later
  raised: 2026-10-08T06:41Z
  why ask: rule-change — it sets which file decides ownership estate-wide
  impact: Effect → one source of truth for "not ours" · Wait: blocks step 2's wording · reach: CLAIM.md and the librarian section in every repo · undo: easy before the scope-interview work lands · cost: none
agent: reviewer a124f7bce7518dd69
