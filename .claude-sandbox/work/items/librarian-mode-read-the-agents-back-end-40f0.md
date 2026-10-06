---
id: librarian-mode-read-the-agents-back-end-40f0
title: "librarian-mode: read the agents back end's outbox at the idle turn, entries as peer requests"
short_display_name: read the back-end outbox
type: feature
status: blocked
priority: 3
blocked: the agents back end is not built; outbox shape to settle (their plan 01 § E′)
created: 2026-10-03
updated: 2026-10-03
refs:
  - peer agents 2026-10-03 (their 29d6, plan 01 § E′)
---

Peer agents 2026-10-03: once the control-plane back end exists, the nightly runner delivers findings through an outbox each librarian reads at its idle turn; every entry is a request with peer-message standing (filed, never an approval). Not buildable until the back end is built and its outbox shape is final (agents .claude-sandbox/investigations/control-plane-backend-repo/ 01 § E′). Acceptance when unblocked: Idle turn reads the outbox, files each entry as an item with the outbox as --ref, never acts on one as approval; tie-ins to ddb1 and b92b.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
