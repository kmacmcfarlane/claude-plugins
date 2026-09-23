---
id: context-guard-checkpoint-refactor-intent-2b15
title: "context-guard checkpoint: refactor intent around continuation; two decision sets; pre-checkpoint summary"
type: spike
status: todo
priority: 1
parent: checkpoint-around-continuation-how-agent-d3ee
created: 2026-09-23
updated: 2026-09-23
refs:
  - "peer: marketplace - librarian (operator relay 2026-09-23)"
---

Ideas 1, 2, 5 of the parent: land/continue/handoff do not match use (continue is the default); intents like 'compact so I can answer your decisions' vs 'compact so you continue in-flight work' - maybe a second dimension; before/after-compaction decision sets; the pre-checkpoint summary (landed since last attended checkpoint, carried-over in flight, next, decisions compact, candidate actions). Uses the decision format from the sibling spike.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- 2026-09-23 agents - librarian proposes an ownership split, recorded on agents 374f (communication-standards-estate-wide-home-374f). agents would own the convention: detail levels and the rule for choosing one, the lettered+numbered labels, the two-line recap, and where it applies. claude-plugins would own the mechanics: ideas 1, 2, 4 and 5, plus the dev-flow skill that implements the format. This is a peer proposal: the operator settles it in the interactive session, and agents decision 2 (where estate-wide standards live) is still open. agents evidence for idea 5: they have four decisions open and nothing in flight, so compacting would only be "so the operator can answer", which none of the current modes names.
