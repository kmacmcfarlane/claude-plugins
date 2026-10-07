---
id: checkpoint-before-the-manifest-write-con-6c43
title: "checkpoint: before the manifest, write conversation-only residue into every open item the session touched"
short_display_name: checkpoint writes residue to items
type: feature
status: todo
priority: 1
created: 2026-10-07
updated: 2026-10-07
refs:
  - peer kappa-3567 2026-10-07
---

Relayed 2026-10-07 by peer kappa-3567 (sussex/communications/email), feedback from the operator there: 'it should be SOP to add details like this to open work-items before checkpointing.' At their checkpoint an open item lacked six conversation-only points (an unconfirmed operator rule, an alternative proposal, a ticket refinement, an unanswered question about another team's ticket, a bug file:line, a product design question). Suggested: in checkpoint Steps 2/3/4a, for every open or doing item the session touched (the manifest's items: set), audit that its file holds the conversation-only residue (open questions, unconfirmed operator statements, proposals and alternatives, refinements, file:line pointers) and append what is missing (dated section or wi handoff) before writing the manifest. Relayed: confirm with the operator here before building.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
