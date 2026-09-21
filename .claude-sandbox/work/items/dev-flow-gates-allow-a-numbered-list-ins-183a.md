---
id: dev-flow-gates-allow-a-numbered-list-ins-183a
title: "dev-flow gates: allow a numbered list instead of AskUserQuestion while scope is open"
type: feature
status: todo
priority: 2
created: 2026-09-20
updated: 2026-09-20
refs:
  - "peer: agent-harness-fc (uds 160.sock)"
---

Peer relay 2026-09-19/20 from agent-harness-fc, operator's words: 'all options are open, AskUserQuestion isn't really appropriate for the mode of conversation we are in. It would be easier to use a numbered list that I can respond to free-form.' Three dialog rounds in that session: one worked, one was answered with prose that redefined the project, one was rejected. investigate Steps 2, 9, 11 and deep-investigation Step 1 currently MANDATE AskUserQuestion for blocking gates. Acceptance: gates stay blocking, but each says it may be satisfied by a numbered list in the reply, and prefers that while scope is still open (closed choices late in a task keep the dialog); Step 11's defer option works as prose; librarian-mode/dev-cycle decision channels already use numbered lists - keep them consistent.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
