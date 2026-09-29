---
id: research-light-which-signals-show-how-fr-a99c
title: "research (light): which signals show how fresh a decision's subject is in the operator's mind"
short_display_name: operator-freshness signals
type: spike
status: doing
priority: 1
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-29T06:51Z
created: 2026-09-29
updated: 2026-09-29
refs:
  - operator 2026-09-29
---

Operator 2026-09-29 (.claude-sandbox/investigations/5140-decision-lifecycle/evidence/operator-notes-2026-09-29-stream.md): 'How can we only present decisions in a way that is answerable (depends on how fresh the operator's working memory in their brain is about the subject, may be culled switching between tasks). We have some guidance around recency of response to gauge how interactive the session is. How can we use that better, or are there other signals we should be looking at too?' Acceptance: a light series on signals of operator context freshness (reply latency, task switches across sessions, the subject's last mention, tell-me rounds, answer shape) from transcripts and the store, plus external evidence on task switching and resumption; how the decisions skill's warm/cold reading (worksheet group A) should use them.

## Handoff
- doing: —
- next: planner r1 running; then a fresh plan review; notify agents and operator-attention when it lands
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: planner opus — light research spike, plan mode (series a99c-operator-freshness-signals)
agent: a8307a75146d1df1b (planner r1)
notify: send agents a pointer when this series lands (agents asked)
notify: send operator-attention a pointer when this series lands (their R48 depends on it)
input from operator-attention: no store records that a decision was shown to the operator; their R47 (recency) and shared warm/cold test rest on it — a shown timestamp is a candidate signal source
series 00 written: age >=12h and >=20 operator turns elsewhere each mark 10 of 11 lost-context answers (1 of 31 otherwise); compaction and latency weak; "show me the decisions" is an observable signal; proposal: long-absence event, full re-show on request, stored context line, no re-printing while away; D1-D4 candidates
dispatch: plan reviewer opus — fresh, round 1
agent: a3e0a42b012f2f697 (plan reviewer r1)
plan review r1 NEEDS_CHANGES (1H 3M 1L): H D1 8h rule untested (counted from last show it catches 0); M coding uneven: recoded 8-9 of 20 vs 0-1 of 31 (not 10 of 11 vs 1 of 31); M the 84-86 re-show was three full blocks, not a context line; M D1/D3 change ruled rules unnamed; L shown timestamp input unanswered
CORRECTION owed to the operator: "10 of 11 vs 1 of 31" is the most favourable coding (8-9 of 20 vs 0-1 of 31); the 84-86 re-show was full blocks, not a context line
dispatch: planner opus — resume, serial 01
