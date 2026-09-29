---
id: decision-handling-the-pyramid-shaped-dec-69ee
title: "decision handling: the pyramid-shaped decision turn on the decisions skill and its future"
short_display_name: decision-handling pyramid
type: chore
status: todo
priority: 1
deps:
  - present-tonight-s-research-to-the-operat-2081
  - librarian-where-the-line-sits-between-ju-8dee
  - research-light-which-signals-show-how-fr-a99c
created: 2026-09-29
updated: 2026-09-29
refs:
  - operator 2026-09-29
---

Operator 2026-09-29 (.claude-sandbox/investigations/5140-decision-lifecycle/evidence/operator-notes-2026-09-29-stream.md): 'based on these notes, let's continue before making final decisions. When you are ready to present the decisions about the decisions skill and future of decision handling, then build me a pyramid-shaped decision turn I can work through with these thoughts in mind.' Acceptance: one turn, apex first (the direction for decision handling: short term in operator-interaction, long term an attention scheduler in operator-attention and the agents work system), then the layers it decides (what reaches the operator: 8dee; durability and the decision ledger: 98, 99; answerability and freshness: S2; batched replies: 100), each lower decision marked by which apex answer it depends on; sourced from 5140, 6d2c, d618, 8dee, S1, S2.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
agents replied: decision ledger and attention scheduler filed on their 76bc (scheduler as a component for control-plane contract 0a7c); wants pointers to 263c and a99c with the others
operator-attention replied: filed r48-decision-scheduling-decisions-as-a-s-0495 (spec R48, their commit 9ef1ab1; their series decision-collector/06_decision-scheduling.md); adds two requirements: group by what a decision turns on (same fact) across sessions, and arrival-vs-clearance throughput as the scheduler metric; wants pointers to a99c and 263c; flags one decision ledger (in the unified work system) with their collector as a reader, relayed to agents
agents replied: ledger design recorded on 76bc, to be settled with 0a7c (waits on agents decision 10); asked operator-attention (relayed) not to build a private ledger store meanwhile — a request, not a ruling
operator-attention (c4443d7, their 07_ledger-split.md): accepts one ledger, drops private decisions.jsonl; proposes a timestamps-only observation log (shown|answered|deferred|swept) because no store records "shown"; moot if 76bc takes a shown field; will not build until agents or the operator answers — relayed to agents with our 5140 finding (no shown-at time in the store)
agents position (76bc): ledger records timestamped lifecycle events (raised, shown, answered, deferred with wake, swept/dropped); no objection to operator-attention interim ids-and-timestamps log (their call); claude-plugins shown-at item filed as 0999, both peers told
operator-attention: not building the interim log (591a428); 0999 shape requirements recorded on 0999
order: the research briefing (2081) goes first, so the operator is warm when the pyramid decisions arrive
pyramid note (b3c5 review r1): 6421 Q2 (z) impact must read "keeps its trigger but runs at fable high, down from the xhigh it inherits today"
