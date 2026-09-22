---
id: context-guard-rehydration-should-the-cle-44a4
title: "context-guard rehydration: should the clear tier inject the ledger tail?"
type: spike
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock); agents investigations/circadian-epochs"
---

Relayed 2026-09-22 by the agents librarian (design question, operator decides). rehydrate.py:19-24 gives startup/clear a header only, so after /clear the previous epoch's ledger tail ('naps') is not re-injected. The agents circadian-epochs study (agents .claude-sandbox/investigations/circadian-epochs/, INDEX + 01 § OQ6) asks whether it should be, since naps only pay off if they survive the next sleep. Heads-up: the same study will likely recommend a telemetry-only 'epoch journal' in context-guard as the first harness change (agents decision 3, pending). Acceptance: a decision with the trade-off (clear = fresh start vs ledger continuity; budget cost of the tail) recorded; if yes, the tier table and tests change.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
