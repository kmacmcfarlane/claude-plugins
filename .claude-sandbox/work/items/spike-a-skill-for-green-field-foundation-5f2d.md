---
id: spike-a-skill-for-green-field-foundation-5f2d
title: "spike: a skill for green-field foundation sessions (requirements, research, claim, architecture, phased plan)"
short_display_name: green-field foundation session skill
type: spike
status: done
priority: 1
created: 2026-10-08
updated: 2026-10-09
closed: 2026-10-08
refs:
  - peer claude-analytics 2026-10-08T06:55Z (operator request there)
---

Relayed 2026-10-08T06:55Z by peer claude-analytics from the operator there, verbatim: 'what's the type of artifacts typically used to establish the requirements and architecture of a green-field piece of software? Have the claude-plugins agent do a research spike on this with the goal of defining a skill for this sort of foundationaly requirements/research/scope/claim/architecture/planning type session to define the sort of procedure and artifacts that should happen. For instance, not much requirement gathering has occured, you are just going off what I already knew I wanted. The skill should cycle through initial requirement gathering, architecture planning, and phased execution planning with optional research and required review gates to move to the next phase. We should also be careful to not get TOO waterfall about it and have logical paths to move ahead and backward in an intuitive way (holding items for later requirement gathering, factoring out aspects for follow-up, asking new questions throughout later stages as new requirement gaps are identified, etc).' Acceptance: (1) sourced survey of green-field artifacts (vision, goals/non-goals, PRD or Shape Up pitch, functional requirements and quality-attribute scenarios, constraints, glossary, scope/charter and context diagram incl. CLAIM.md 53d7, design doc/RFC, C4, arc42, ADRs, data contracts, threat/privacy model, risk register, roadmap, feature breakdown, test strategy, spikes) and which earn their keep for agent-run sessions in minimal form; (2) the procedure: phases with optional research and a required review gate to advance, plus explicit non-waterfall paths (back a phase, hold a question, factor out, raise questions anywhere); (3) composition with dev-flow investigate/deep-investigation/research/dev-cycle, operator-interaction decisions, CLAIM.md, work items: overlap and gaps; (4) placement options as an operator decision. Case study, read-only: claude-analytics .claude-sandbox/investigations/agent-telemetry/ (INDEX, 00-08), docs/architecture.md, CLAIM.md (requirements inferred, claim mid-stream, harness-agnosticism at serial 05, 7 plan review rounds). The operator may run it retroactively over claude-analytics.

## Handoff
- doing: plan review 2 running (reviewer ae5914d0eefb54dbc)
- next: on CLEAR: store cards 193-195 from 01's end and show them; close the spike on its series
- blocked: —
- learned: —
target: plan main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d
budget: 2026-10-08T06:55Z plan waived — operator waiver (spend still measured)
dispatch: planner opus high — research spike (research skill run unattended inside the plan)

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: planner a5d2c918ad5eec7bd
return: DONE_WITH_CONCERNS series 00_initial.md + research report (quick; verifier PASS 4/4; the lane's findings file held by the scanner, not used, left in scratchpad/5f2d-plan/research/…/findings/); OQ1 placement (rec dev-flow skill), OQ2 name (rec foundation), OQ3 gate approvals, blocking the build
baseline: plan review 1 — 54fd015edc5f38b5e2facbb12b12880884397cabefa057e87198a4683d798abf .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/00_initial.md; 
dispatch: reviewer opus high — plan review 1
agent: reviewer ae5914d0eefb54dbc
verdict: plan review 1 NEEDS_CHANGES (must-fix 7: BMAD correct-course refutes the stated gap (high); no architecture reopen path; dev-cycle wiring missing; card 1 (b) best case; card 3 undefined G1-G3/ADR; cards 1-2 undefined rule labels; card 2 unfair on 'green-field'; lows 8-14)
dispatch: planner opus high — plan fix round 1 (resume a5d2c918ad5eec7bd)
return: DONE series 01_review-fixes.md (all 15; BMAD correct-course confirmed and adapted; three reopen tiers; dev-cycle wiring entries; cards as decisions 193-195)
baseline: plan review 2 — 54fd015edc5f38b5e2facbb12b12880884397cabefa057e87198a4683d798abf .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/00_initial.md; 770aadcdc767bfc34aea3d0ca3faa27ff3991aa9e57f3c0a1e4ea506b6b98400 .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/01_review-fixes.md; 
dispatch: reviewer opus high — plan review 2 (resume ae5914d0eefb54dbc)
verdict: plan review 2 NEEDS_CHANGES (must-fix 1, down from 7: answer rows leave other phase-2 artifacts unrouted; lows 2-8, nit 9)
dispatch: planner opus high — plan fix round 2 (resume a5d2c918ad5eec7bd)
return: DONE series 02_review-2-fixes.md (all 9; any phase-2 artifact reopens architecture; resume.md entry; build-time reopens a follow-up)
baseline: plan review 3 — 54fd015edc5f38b5e2facbb12b12880884397cabefa057e87198a4683d798abf .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/00_initial.md; 770aadcdc767bfc34aea3d0ca3faa27ff3991aa9e57f3c0a1e4ea506b6b98400 .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/01_review-fixes.md; 182c8f334c5d2a80ed6054c059480aba93589d5bf57aa8a2c0d1b797e13f4882 .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/02_review-2-fixes.md; 
dispatch: reviewer opus high — plan review 3 (resume ae5914d0eefb54dbc)
verdict: plan review 3 NEEDS_CHANGES (must-fix 1: intent and the neighbours table have no reopen path; low: dev-cycle files G3's features; nit provenance); cards 193-195 graded clean
dispatch: planner opus high — plan fix round 3 (resume a5d2c918ad5eec7bd)
return: DONE series 03_review-3-fixes.md (phase-1 reopen covers intent and the neighbours table; dev-cycle files G3 features)
baseline: plan review 4 — 54fd015edc5f38b5e2facbb12b12880884397cabefa057e87198a4683d798abf .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/00_initial.md; 770aadcdc767bfc34aea3d0ca3faa27ff3991aa9e57f3c0a1e4ea506b6b98400 .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/01_review-fixes.md; 182c8f334c5d2a80ed6054c059480aba93589d5bf57aa8a2c0d1b797e13f4882 .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/02_review-2-fixes.md; 4fc5355352c6559cb4ea31428e47bc16e575def63fefdc0aca3effe56ab018f6 .claude-sandbox/investigations/spike-a-skill-for-green-field-foundation-5f2d/03_review-3-fixes.md; 
dispatch: reviewer opus high — plan review 4 (resume ae5914d0eefb54dbc)
verdict: plan review 4 CLEAR (must-fix 0; low: 03 has no Risk Assessment section, 02's risks stand)
note: spike closed on its series (00-03); build filed as foundation-skill-build-the-green-field-f-cc8a, waiting on decisions 193-195
decision 193: Where should the foundation skill live? — options: (a) a new skill in dev-flow [recommended] | (b) a new plugin, foundation | (c) a mode of investigate | (d) inside create-repo | (e) inside kit-dev | (z) decide later
  raised: 2026-10-08T07:50Z
  why ask: precedent — dev-flow's aim fits, but you may see a project's foundation as an aim of its own (a new plugin, a permanent name)
  impact: Effect → a new skill inside dev-flow, one line in its tables · Wait: blocks the build · reach: everyone who installs dev-flow · undo: one edit before release; a cheap skill move after · cost: none now
decision 194: What should the skill be called? — options: (a) foundation [recommended] | (b) greenfield | (c) project-foundation | (z) decide later
  raised: 2026-10-08T07:50Z
  why ask: contract — both main candidates are your words
  impact: Effect → /dev-flow:foundation · Wait: blocks the build · reach: README, install notes, what you type · undo: one edit before release; a cheap skill rename after, or a costly plugin rename if 193 is (b) · cost: none
decision 195: At which phase gates must you approve before the next phase starts? — options: (a) requirements and the plan always; architecture only for hard-to-reverse decisions (ADRs) and CLAIM.md changes, the rest reported [recommended] | (b) all three always | (c) requirements only | (z) decide later
  raised: 2026-10-08T07:50Z
  why ask: precedent — it sets how often every foundation run stops for you
  impact: Effect → you approve requirements and plan every run; architecture only when hard to reverse · Wait: blocks the build · reach: every foundation run in every repo · undo: one rule edit · cost: usually two stops per run, three with a hard-to-reverse decision
- 2026-10-08 done
shown 193: 2026-10-08T20:02Z chat
shown 194: 2026-10-08T20:02Z chat
shown 195: 2026-10-08T20:02Z chat
shown 193: 2026-10-09T06:11Z page
shown 194: 2026-10-09T06:11Z page
shown 195: 2026-10-09T06:11Z page
answer 193: a (answer page HvKDfFHjrqNtygDKziv7ta, rev 2026-10-09T06:00:00Z, at 2026-10-09T06:43:30.480Z)
answer 194: a (answer page HvKDfFHjrqNtygDKziv7ta, rev 2026-10-09T06:00:00Z, at 2026-10-09T06:44:09.683Z)
answer 195: a (answer page HvKDfFHjrqNtygDKziv7ta, rev 2026-10-09T06:00:00Z, at 2026-10-09T06:45:19.096Z)
