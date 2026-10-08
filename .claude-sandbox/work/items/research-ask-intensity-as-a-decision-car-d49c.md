---
id: research-ask-intensity-as-a-decision-car-d49c
title: "research: ask intensity as a decision card with each preset's cost and benefit, not a dialog"
short_display_name: research intensity as a decision card
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T05:43Z
created: 2026-10-08
updated: 2026-10-08
refs:
  - peer claude-analytics 2026-10-08 (operator request there)
---

Relayed 2026-10-08 by peer claude-analytics from the operator there, verbatim: 'When deciding about the intensity of research, it would be better to have some understanding of the costs and benefits. The research skill should present those costs and benefits for each option instead of using AskUserQuestion for that.' Today research Step 3 (references/intensity-and-routing.md § When to ask) asks one AskUserQuestion with only cost lines. Acceptance: the intensity ask is rendered per the operator-interaction decisions skill when loaded (a card, one option per preset, each with its cost line and its benefit for this question: sub-question coverage, round-2 gap closing, verifier sample, what stays thin; recommendation, basis, unknown, decide later), with a plain-prose fallback when that skill is absent; research-deep's round-3 ask moves off the dialog form too.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: plan main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/research-ask-intensity-as-a-decision-car-d49c
budget: 2026-10-08T05:43Z plan $28 — default plan
dispatch: planner opus high — plan

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: planner a01c78fd1feecde49
return: DONE_WITH_CONCERNS series 00_initial.md (one owner section in intensity-and-routing.md for every research-family ask; decisions-skill card when loaded, lettered prose fallback, never a dialog; run waits while asked; AskUserQuestion off allowed-tools; ledger ASKED/ANSWERED; test_research_asks.py; open: confirm the relayed request, blocking)
baseline: plan review 1 — 5e27a7f129b2ff28a4b30b64c4c0fa28943a4dabae578af750e197e3941808e0 .claude-sandbox/investigations/research-ask-intensity-as-a-decision-car-d49c/00_initial.md; 
dispatch: reviewer opus high — plan review 1
decision 185: Do you want the research skills to put their intensity and round questions to you as decision cards (each preset's cost and what it buys, in text) instead of a pop-up dialog, in every interactive session? — options: (a) yes, as the claude-analytics session relayed [recommended] | (b) no, keep the dialog | (z) decide later
  raised: 2026-10-08T06:00Z
  why ask: trust — a relayed request changes an interactive default, and relayed answers bind nothing until you confirm here
  impact: Effect → the research build can start; research asks show cost and benefit per preset and wait for your reply · Wait: blocks the build · reach: research, research-deep, research-refine, research-prune, deep-investigation in every repo · undo: easy, restore the dialog · cost: none
agent: reviewer a740e9298c69f0c0b
