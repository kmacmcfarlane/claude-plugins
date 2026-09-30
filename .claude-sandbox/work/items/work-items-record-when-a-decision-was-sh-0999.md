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
operator-attention requirements for the shape (their commit 591a428; they will not build their interim log):
  - ISO-8601 UTC timestamp, never relative or human text
  - per decision number, not per item
  - last-write-wins on a re-show (same rule as wake N:)
  - distinct from raised: (two of the three clocks)
  - optional, cheap if possible: a reason on swept/dropped — "dropped by the operator" (a decision) vs "swept as stale" (a miss) — so arrival-vs-clearance is not pooled; if absent they treat all sweeps as misses
input from a99c 01 (2026-09-29): a stored shown time alone does not make the cold test work (re-prints overwrite it); it needs a seen N: time beside shown N:, plus the operator turn times in other sessions
2026-09-30 shape per the pyramid answers: 98 a (one counter; shown N:/seen N: are per decision number, <repo>#N for another repo's), 99 c (closed N: rides 5140 C1/C2, filed as decisions-record-one-counter-for-every-q-b6f7 and wi-parse-closed-n-list-decisions-by-stat-728a), 118 b (the away test needs shown N: — decisions-while-the-operator-is-away-sho-602b depends on this item), 120 z (wakes when this item stores seen N: and 76bc or R48 publishes turn times). Acceptance adds: a seen N: line beside shown N: (a99c 01: a re-print overwrites shown, so the cold test needs seen), both ISO-8601 UTC, last-write-wins, per decision number; the operator-attention requirements above stand.
