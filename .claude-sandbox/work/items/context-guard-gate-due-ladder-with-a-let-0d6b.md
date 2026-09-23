---
id: context-guard-gate-due-ladder-with-a-let-0d6b
title: "context-guard gate: DUE ladder with a let-it-ride re-arm instead of a one-shot DUE"
type: feature
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock), operator relay"
---

Relayed 2026-09-22 from the agents store (gate-due-ladder-offer-let-it-ride-re-arm-ccb0; operator idea from the 2026-09-01 150k live-fire). Keep autoCompactWindow high and have DUE fire every ~200k of remaining-budget descent with a 'let it ride' re-arm, instead of once. Relates to 8cc2 (turn gate) — check the 8cc2 plan before designing; may fold into it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- see also: agents decision 0007 corrects the compaction facts 0004 stated (item filed for the context-guard text).
- from 8519 review (2026-09-23): precompact_gate re-defers until a checkpoint or HARD, and also stops at unknown depth and resets at a new epoch (PostCompact/clear) — design the DUE ladder against the code, not 0007 alone.
