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
- doing: plan CLEAR at review 3; build waits on decision 185
- next: on answer 185 (a): dispatch the build from the series with the carried findings
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
verdict: plan review 1 NEEDS_CHANGES (must-fix 5: threads ask open while the next round runs; one-preset and 7d override cards; unparsed word answers in the fallback; decide-later wake contradicts; manifest clause misstates the plain-names edge; lows 6-10, nit 11)
dispatch: planner opus high — plan fix round 1 (resume a01c78fd1feecde49)
return: DONE_WITH_CONCERNS series 01_review-1-fixes.md (findings 1-11; assumptions 13-15; test 8)
baseline: plan review 2 — 5e27a7f129b2ff28a4b30b64c4c0fa28943a4dabae578af750e197e3941808e0 .claude-sandbox/investigations/research-ask-intensity-as-a-decision-car-d49c/00_initial.md; e63e5c5acab50663b437500ccc6ba91ed328cba7f6f2466a0448e32c425f9d07 .claude-sandbox/investigations/research-ask-intensity-as-a-decision-car-d49c/01_review-1-fixes.md; 
dispatch: reviewer opus high — plan review 2 (resume a740e9298c69f0c0b)
verdict: plan review 2 NEEDS_CHANGES (must-fix 2, down from 5: assumptions 13 and 14 clash when the launched round is the last the cap allows; pulled lanes need a stated cost and a fresh quota read at answer time; lows: brief § Lanes and search budget for pulled lanes, Supersedes misses 00 § C research-deep, INDEX numbering)
dispatch: planner opus high — plan fix round 2 (resume a01c78fd1feecde49)
return: DONE_WITH_CONCERNS series 02_review-2-fixes.md (assumptions 16, 17; ledger order on a pull; test 8 five substrings)
baseline: plan review 3 — 5e27a7f129b2ff28a4b30b64c4c0fa28943a4dabae578af750e197e3941808e0 .claude-sandbox/investigations/research-ask-intensity-as-a-decision-car-d49c/00_initial.md; e63e5c5acab50663b437500ccc6ba91ed328cba7f6f2466a0448e32c425f9d07 .claude-sandbox/investigations/research-ask-intensity-as-a-decision-car-d49c/01_review-1-fixes.md; d1e76b5f2bc83acbe7d70628abb62e7174f78f445c9d228e447562df1fcc03ae .claude-sandbox/investigations/research-ask-intensity-as-a-decision-car-d49c/02_review-2-fixes.md; 
dispatch: reviewer opus high — plan review 3 (resume a740e9298c69f0c0b)
verdict: plan review 3 CLEAR (must-fix 0)
findings: carried — (1) research-refine/SKILL.md:51: a T<n> entry marked pulled is not offered as a thread to pull; (2) pull no web lane that would need a search after a SEARCH EXHAUSTED line; local-corpus pulls stay open; keep 00's hand-rendered card and fallback list as the build's check
answer 185: a — "What's the fallback if the decisions plugin isn't installed?" (chat, 2026-10-08T06:28Z; read as: (a) build it; question answered in chat: the plan's fallback is a lettered prose list in text, never a dialog; dependency spike filed separately)
target: full main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/research-ask-intensity-as-a-decision-car-d49c
budget: 2026-10-08T06:28Z build waived — operator waiver 2026-10-08T06:28Z (spend still measured)
dispatch: implementer opus medium — build from the CLEAR series (skill rules and tests)
agent: implementer acfa41296fc254968
