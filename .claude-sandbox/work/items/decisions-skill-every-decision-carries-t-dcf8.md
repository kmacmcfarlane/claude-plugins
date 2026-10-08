---
id: decisions-skill-every-decision-carries-t-dcf8
title: "decisions skill: every decision carries the inputs needed to act on it where shown"
short_display_name: decisions carry every needed input
type: spike
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T04:57Z
created: 2026-10-06
updated: 2026-10-08
refs:
  - operator 2026-10-06, decision 160
---

Operator 2026-10-06 on decision 160, verbatim: 'decision skill feedback: you gave me a decision I can't act on. You haven't specified the location of paste.txt. That blocks me from doing the test now and makes me ask you where the file is in another turn. This is inefficient. A decision should have all the MUST-HAVE inputs the decider needs to make the decision. Make a work-item to look into the research we have already collected to see if there's a model we can follow around this?' Acceptance: a read of the decision research already collected (pyramid 69ee, 0c4d delta, operator-attention R-series, the decisions skill's rationale) for a model of 'actionable from where it is shown'; a proposal for the decisions skill's floor (e.g. every artifact the operator must touch named by absolute path, any text to paste shown inline).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
note: 2026-10-07 operator on 172 (answer page): "This decision mentions details not in the decision card, so I'm blocked from answering. Before this decision was shown, it should have included what the tiers were and what 'plus wording' means. How can the skill be updated to achieve this?" — the same class as 160's missing paste.txt: a card names terms or artifacts it does not define or show; acceptance gains: every term a card's options use is defined on the card (or the card links what it summarises with the definitions inline)
target: plan main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/decisions-skill-every-decision-carries-t-dcf8
budget: 2026-10-08T04:55Z plan $40 — default spike plan
dispatch: planner opus high — spike plan (operator feedback on 160 and 172)
agent: planner aa442cae2c2859ccd

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
return: DONE series 00_initial.md (floor widens to terms; new 'what it takes to act' floor item; worksheet group F cold read; To act on card part; gallery 27-28; page act field + test_act.py; open: scanner not now, re-check stored cards at next re-show)
baseline: plan review 1 — 67c3fb20872d5c39b02a284c7e7fc91643db3702dd75cbb64e32b7a9c1d3fabd .claude-sandbox/investigations/decisions-skill-every-decision-carries-t-dcf8/00_initial.md; 
dispatch: reviewer opus high — plan review 1
agent: reviewer a40143babb8d3fe90
