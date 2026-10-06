---
id: work-item-summary-tables-an-index-number-f568
title: "work-item summary tables: an index-number column so several rows can be answered in one reply"
short_display_name: index column on item tables
type: feature
status: todo
priority: 2
created: 2026-10-05
updated: 2026-10-05
refs:
  - peer marketplace 2026-10-05, relaying its operator
---

Peer marketplace (librarian) 2026-10-05, relaying its operator: every work-item summary table gets an index-number column, including librarian-mode's Groom and Work tables (references/idle-turn.md) and wi's summary output, so the operator can answer several items in one reply ('3 go, 5 drop, 7 hold'). Settled in the request: the index column comes first; numbering runs 1..N across all tables in one message, not restarted per table; the numbers hold for that message only and are never stored, so they don't clash with durable decision numbers. Plan questions: how a reply tells a row index from a decision number ('3 go' vs '147: a') — e.g. a distinct form or prefix; which wi commands print summaries (ls, next, prime, estate) and whether their JSON changes (the agents back end pins estate/ls/needs-input/show JSON, item 8c42 — announce if so); the reply forms a row accepts (go, drop, hold, …) and how they map to wi actions; relation to the scribe feedback on addressable rows (9535, 21b4). Relayed operator request: confirm with the operator before a build acts on it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
