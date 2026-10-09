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
updated: 2026-10-09
refs:
  - peer claude-analytics 2026-10-08 (operator request there)
---

Relayed 2026-10-08 by peer claude-analytics from the operator there: a CLAIM.md, when present, sets out a repo's ownership claim and explicit known boundaries with other repos' areas of responsibility, so ownership questions stop recurring (the analytics split prompted it). The operator asks for: (1) a research round on the best shape (sections, how boundaries with other repos are stated, how changes are proposed and approved, how agents read it), with claude-analytics' operator-approved CLAIM.md (repo root, local main 4c2207d, not pushed; rule 'a producer emits; claude-analytics defines, reads and reports') as the worked example; (2) land the skill with the operator in this session, since the shape may need their input; (3) file a low-priority item in every active kmacmcfarlane repo with a work-item store to establish its own CLAIM.md; (4) then tell claude-analytics how to reshape theirs. Placement (which plugin) is a decision. FYI from the approved claim, nothing to change yet: usage-report retires at parity; item_spend.py is replaced by an attribution-event spend report (dev-cycle would emit a dispatch event, schema to come); quota_budget.py stays a listed reader; statusline-hub's record hook stays here.

## Handoff
- doing: plan stopped and carried at review 4; revised cards 186-189 stored and shown
- next: on answers 186-189: build step 2 (the skill) per 00-03; then OQ6 seeding
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
  why ask: precedent — a new plugin and its catalog row are the operator's (principle 6; the operator asked to discuss it)
  impact: Effect → step 2 (the skill build) can start in its home · Wait: blocks step 2 · reach: the marketplace catalog · undo: moving a plugin later renames installs · cost: none
decision 187: What should the plugin and the skill be called? — options: (a) plugin ownership, skill claim-md, file CLAIM.md [recommended] | (b) plugin claims, skill claim | (z) decide later
  raised: 2026-10-08T06:41Z
  why ask: contract — plugin and skill names are what users install and invoke (principle 5)
  impact: Effect → fixes the names the build ships · Wait: blocks step 2 · reach: every repo that installs it · undo: a rename breaks installs · cost: none
decision 188: Approve the proposed CLAIM.md shape (five required parts, optional sections, the defining side holds a boundary's text, every change approved by the operator, the CLAUDE.md pointer)? — options: (a) approve as drafted [recommended] | (b) approve with changes (say which) | (z) decide later
  raised: 2026-10-08T06:41Z
  why ask: your-call — the operator said the shape may need their input
  impact: Effect → the shape the skill writes and checks in every repo · Wait: blocks step 2 · reach: every repo's CLAIM.md · undo: easy before step 3 seeds repos; costly after · cost: none
decision 189: When a repo has both a CLAIM.md "Not ours" list and a librarian "Not owned:" line (from the unlanded scope-interview work), which wins? — options: (a) CLAIM.md is the authority; "Not owned:" must agree, and the check flags a mismatch [recommended] | (b) keep both independent | (z) decide later
  raised: 2026-10-08T06:41Z
  why ask: precedent — it sets which file decides ownership estate-wide
  impact: Effect → one source of truth for "not ours" · Wait: blocks step 2's wording · reach: CLAIM.md and the librarian section in every repo · undo: easy before the scope-interview work lands · cost: none
agent: reviewer a124f7bce7518dd69
verdict: plan review 1 NEEDS_CHANGES (must-fix 11 at medium: per-interface definers, substance-only approval, external owners, seed done-when, MOVED? column, undeclared dev-flow soft dep, unfair framing of 186, 187 and 189, the splitting question unanswered, consult triggers untested; lows 12-16)
correction: decisions 186, 187 and 189 were shown before their plan review and are framed unfairly per the review (dev-flow's best case missing, a safe name option missing, the pointer option for 189 dropped); 188 lacks the substance-only approval option. They are held for revised cards after the fix round; answers given meanwhile are read against the revised cards.
dispatch: planner opus high — plan fix round 1 (resume a73b066060c1a0ca7)
return: DONE series 01_review-fixes.md (F1-F16; R10 splitting rule; OQ4 rec now (b) pointer; four revised cards at the end of 01)
baseline: plan review 2 — a6db4276282b7ffa553a17890ec8d9cd1b3edaf4b42eed59dd73501ce4695e97 .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/00_initial.md; 53ec501c3d2cebabbbcf1d828cbd97af2314cded367a7b9217e08341b00e5af5 .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/01_review-fixes.md; 
dispatch: reviewer opus high — plan review 2 (resume a124f7bce7518dd69)
verdict: plan review 2 NEEDS_CHANGES (must-fix 4, down from 11: card 4 framing, undefined terms on the cards, cards numbered 1-4 not 186-189, Supersedes misses 00 R9 and :306-308; lows: DANGLING for a missing CLAIM.md, card 1 (b) best case)
dispatch: planner opus high — plan fix round 2 (resume a73b066060c1a0ca7)
return: DONE series 02_cards-and-pointers.md (G1-G6; 189 rec back to (a) keep both lists with a widened MISMATCH check; cards numbered 186-189, written for a cold reader)
baseline: plan review 3 — a6db4276282b7ffa553a17890ec8d9cd1b3edaf4b42eed59dd73501ce4695e97 .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/00_initial.md; 53ec501c3d2cebabbbcf1d828cbd97af2314cded367a7b9217e08341b00e5af5 .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/01_review-fixes.md; d80965bd1e7a1abd2938f6b2191f64c45cbaf89908e82a0197659dd918ac6a86 .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/02_cards-and-pointers.md; 
dispatch: reviewer opus high — plan review 3 (resume a124f7bce7518dd69)
verdict: plan review 3 NEEDS_CHANGES (must-fix 2, down from 4: revised-since lines compare against unshown 01 cards; widened MISMATCH omission rule contradicts 188; lows: 189 check cadence, (b) best case, later line; undefined terms)
dispatch: planner opus high — plan fix round 3 (resume a73b066060c1a0ca7)
return: DONE series 03_final-cards.md (H1-H4; shown letters kept: 188 rec moves to a new (c), 189 (a) keeps its letter with a new meaning)
baseline: plan review 4 — a6db4276282b7ffa553a17890ec8d9cd1b3edaf4b42eed59dd73501ce4695e97 .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/00_initial.md; 53ec501c3d2cebabbbcf1d828cbd97af2314cded367a7b9217e08341b00e5af5 .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/01_review-fixes.md; d80965bd1e7a1abd2938f6b2191f64c45cbaf89908e82a0197659dd918ac6a86 .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/02_cards-and-pointers.md; 994dbc898e8171cbadc6876375b33e4c7740528994c4ab9d2ca9c43f6d173a2d .claude-sandbox/investigations/claim-md-convention-research-the-shape-l-53d7/03_final-cards.md; 
dispatch: reviewer opus high — plan review 4 (resume a124f7bce7518dd69)
verdict: plan review 4 NEEDS_CHANGES (must-fix 1, down from 2: the revised-since lines say no impact was shown, but the stored cards carried one; lows: 189 (a) should be re-lettered, 189 (b) best case)
decided: cap — plan stop and carry at the fourth counted review (authority answer 114); if left: the one must-fix and both lows are card wording, which the librarian applies when storing and showing the cards (impact changes named; 189's keep-both option re-lettered (d), (a) withdrawn; (b)'s best case added); a round costs a planner and review pass for wording the store line carries directly
decision 186: Where should the CLAIM.md skill live? — options: (a) a new plugin, ownership [recommended] | (b) inside work-items | (c) inside dev-flow | (d) inside kit-dev | (e) inside sandbox | (z) decide later
  revised: 2026-10-08T07:24:40Z — added (e) sandbox; (a)-(d) keep letters and meaning; each option now states its consequence; (b) now says what work-items already does; rec (a) kept; impact changed: undo is now one edit before release and the rename procedure after (was "moving a plugin later renames installs")
  impact: Effect → a new plugin ownership, one new catalog row; nothing existing changes · Wait: step 2 waits · reach: the catalog and every repo that installs it · undo: one edit before release; the README's rename procedure after (no data moves)
decision 187: What should the plugin and the skill be called? — options: (a) plugin ownership, skill claim-md [recommended] | (b) plugin claims, skill claim | (c) plugin repo-claims, skill claim-md | (z) decide later
  revised: 2026-10-08T07:24:40Z — added (c) repo-claims/claim-md; (a) and (b) keep letters and meaning; rec (a) kept; impact changed: undo is now one edit before release and the rename procedure after (was "a rename breaks installs")
  impact: Effect → plugin ownership, skill claim-md, file CLAIM.md · Wait: step 2 waits · reach: install commands, the catalog, names you type · undo: one edit before release; the rename procedure after
decision 188: Do you approve the CLAIM.md shape, and which changes to a claim must come to you? — options: (a) approve as drafted; every change comes to you | (b) approve with changes (say which part) | (c) approve; only substance changes come to you, upkeep reported [recommended] | (z) decide later
  revised: 2026-10-08T07:24:40Z — shape changed in four places (boundaries per interface, a splitting rule, owners may be a repo, you, or external, the five triggers listed); (a) and (b) keep letters and meaning; added (c); rec moved (a) -> (c); impact changed: undo was "easy before step 3 seeds repos; costly after", now one edit to the format reference, because under (c) a reshape that keeps a claim's meaning is upkeep
  impact: Effect → every repo's CLAIM.md takes this shape; upkeep lands without asking and is reported · Wait: step 2 waits · reach: every repo's CLAIM.md and its readers · undo: one edit to the format reference; claims follow at their next review
decision 189: Where a repo has both a CLAIM.md and a librarian "Not owned" line, should that line keep its own list, or point to CLAIM.md? — options: (a) withdrawn (CLAIM.md as the authority) | (b) keep them independent | (c) point the Not owned line at CLAIM.md | (d) keep both; the claim check compares them by name [recommended] | (z) decide later
  revised: 2026-10-08T07:24:40Z — retitled from "which wins?"; (a) "CLAIM.md is the authority" withdrawn, an answer of (a) is re-asked; (b) keeps letter and meaning; added (c) pointer and (d) keep both and compare; rec moved from (a) to (d); impact changed: effect was "one source of truth", now two lists compared by name
  impact: Effect → both lists stay; the check compares them by name when it runs · Wait: step 2's wording on the librarian list waits · reach: every repo with a librarian and a claim · undo: one edit to the check; nothing in the scope interview
shown 186: 2026-10-08T20:02Z chat
shown 187: 2026-10-08T20:02Z chat
shown 188: 2026-10-08T20:02Z chat
shown 189: 2026-10-08T20:02Z chat
shown 186: 2026-10-09T06:11Z page
shown 187: 2026-10-09T06:11Z page
shown 188: 2026-10-09T06:11Z page
shown 189: 2026-10-09T06:11Z page
answer 186: a (answer page HvKDfFHjrqNtygDKziv7ta, rev 2026-10-09T06:00:00Z, at 2026-10-09T06:31:51.110Z)
answer 187: a (answer page HvKDfFHjrqNtygDKziv7ta, rev 2026-10-09T06:00:00Z, at 2026-10-09T06:33:53.354Z)
answer 188: c (answer page HvKDfFHjrqNtygDKziv7ta, rev 2026-10-09T06:00:00Z, at 2026-10-09T06:34:12.181Z)
answer 189: d — "You aren't necessarily going to use both plugins together, although I do, so they should stay separate" (answer page HvKDfFHjrqNtygDKziv7ta, rev 2026-10-09T06:00:00Z, at 2026-10-09T06:39:15.123Z; read as: (d) keep both lists and compare by name, because the plugins are installed independently)
dispatch: planner opus high — step 2 build plan (04) on answers 186 a, 187 a, 188 c, 189 d; scratch scratchpad/53d7-build-plan/
agent: planner a514507009f7c1aa2
