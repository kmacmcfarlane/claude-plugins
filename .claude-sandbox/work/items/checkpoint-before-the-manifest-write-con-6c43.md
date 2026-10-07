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
decision 179: Should checkpoint write conversation-only details into every open item the session touched before it writes the manifest (the operator's request, relayed from the kappa-3567 session)? — options: (a) yes, as relayed: audit each item in the manifest's items: set and append what only the conversation holds [recommended] | (b) no | (z) decide later
  raised: 2026-10-07T18:14Z
  what: a step in the context-guard checkpoint skill, before the manifest: for each open or doing item the session touched, append to the item what exists only in the conversation — open questions, unconfirmed operator statements, proposals and alternatives, refinements, file:line pointers
  why now: relayed today; blocks: its build
  why ask: your-call — you gave it in another session ("it should be SOP to add details like this to open work-items before checkpointing"), and a relayed answer is not one I can act on
  context: you told the kappa-3567 session it should be standard procedure · you confirm it here
  impact: → after any checkpoint, each open item carries what was said about it, so a fresh session or another agent picks it up whole · later: items stay as thin as each session leaves them · reach: every session that checkpoints · undo: an edit
  (a) yes — one more step in every checkpoint; a little more writing at checkpoint time
  (b) no — the manifest stays the only carrier of conversation residue
  (z) decide later — the item waits
  rec: (a) · basis strong — your words, relayed with the case that prompted them
  unknown: none
