---
id: wi-claim-allows-a-dependency-blocked-ite-1d1c
title: wi claim allows a dependency-blocked item
type: bug
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock), operator relay"
---

Relayed 2026-09-22 from the agents store (wi-claim-allows-dependency-blocked-items-77f7). wi claim refuses status:blocked but claims an item hidden from the ready queue by an unmet --on dependency (live-fired 2026-09-01 on brainboy). Acceptance: claim refuses an item whose deps are not all done/dropped (same rule as next/ready), with a message naming the dep; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
