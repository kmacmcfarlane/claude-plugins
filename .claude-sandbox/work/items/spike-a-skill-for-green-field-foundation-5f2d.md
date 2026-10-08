---
id: spike-a-skill-for-green-field-foundation-5f2d
title: "spike: a skill for green-field foundation sessions (requirements, research, claim, architecture, phased plan)"
short_display_name: green-field foundation session skill
type: spike
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T06:55Z
created: 2026-10-08
updated: 2026-10-08
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
