---
id: work-items-record-when-a-decision-was-sh-0999
title: "work-items: record when a decision was shown to the operator (a shown timestamp on decision lines)"
short_display_name: decision shown-at record
type: feature
status: todo
priority: 2
created: 2026-09-29
updated: 2026-09-29
refs:
  - agents 76bc
  - operator-attention R47
---

Relayed 2026-09-29 from the agents librarian (76bc: the decision ledger records timestamped lifecycle events: raised, shown, answered, deferred with wake, swept/dropped) and operator-attention (R47 recency, warm/cold test, arrival-vs-clearance throughput; their 07_ledger-split.md). Our 5140 found the same gap: no shown-at time, so 'while it waited' has no source. Acceptance: a store line or field recording each showing of decision N (shown N: <UTC time>), written by the raising session when it renders the decision, read by wi needs-input/estate; shaped by the pyramid decision turn (69ee) together with decisions 98/99 (one counter, closed N: lines), and by 76bc's ledger when it lands. Peer relays are requests, not approvals.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
