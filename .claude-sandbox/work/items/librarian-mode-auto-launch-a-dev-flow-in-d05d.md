---
id: librarian-mode-auto-launch-a-dev-flow-in-d05d
title: "librarian-mode: auto-launch a dev-flow investigation per new item; pointer + decision block in the item"
type: feature
status: todo
priority: 2
created: 2026-09-21
updated: 2026-09-21
refs:
  - "peer: hooper librarian (uds 155.sock), operator relay"
---

Operator request 2026-09-21 via the hooper librarian (their item route-to-claude-kit-librarian-librarian-bf80). Goal (operator's words): 'use the investigation to help the operator understand the issue and select the preferred path forward with the work-item'. Each new item gets a dev-flow investigation launched in a sub-agent (investigate in its orchestrated mode, Series home .claude-sandbox/investigations/<slug>/), and a block appended to the item when it returns: series path + latest serial + INDEX.md + provenance SHAs; one-line problem statement as understood; recommended path in one line; alternatives as a numbered decision N (recommended first) the operator answers with answer N:; blocking open questions with owners; blast radius; Route tier + signal; status (draft — awaiting operator).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Peer's tensions (input for the design)
1. A sub-agent can't ask: investigate's gates become Confirmed Assumptions / Open Questions, so an auto-run series is a DRAFT; the operator's review becomes the real requirements gate — the item must say so.
2. Non-interactive treats the review gate as Save: needs a visible status (INDEX.md status column value, e.g. "draft — awaiting operator").
3. Cost/noise: skip typo/path bypasses, routing-only items, chores with an obvious best way — gate on type or a "no investigation: <reason>" line.
4. No doubling: dev-cycle's plan step / implementer must consume an existing series instead of re-investigating.
5. Writes to .claude-sandbox/investigations/ in the main checkout (outside Scope, tooling state — now the librarian Series home per 1dab; tolerated dirt).
6. Host-only evidence: sandboxed investigators can't see the host; an "evidence requested from <where>" state on the item.
7. Routing: opus for code exploration, sonnet for web research.
## Librarian notes
- Relates: dev-cycle Step 1 plan mode (spikes already get a plan agent); 693a idle turn (auto-investigation is dispatch — holds apply); b020 grooming status (an item awaiting the operator's pick is "grooming"); decision/answer N convention (693a).
decision 49: which new items get an automatic investigation — (a) features and spikes only, and any item the librarian can't decide in one line (Intake step 3), with "no investigation: <reason>" recorded otherwise [recommended: bounds cost; bugs/chores with a clear fix skip it]; (b) every new item except typo/path bypasses; (c) only on request (operator says "investigate").
answer 49: operator likes the per-mode breakdown; wants a brief explanation per mode of how the mode is determined and what the transition events are — owed by 1222 F2 (serial 01) and summarized to the operator (operator 2026-09-22)
