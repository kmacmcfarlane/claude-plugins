---
id: librarian-mode-start-gate-asks-the-opera-14bd
title: "librarian-mode: start gate asks the operator to /rename the session '<repo> - librarian'"
type: feature
status: doing
priority: 2
deps:
  - librarian-mode-leans-on-dev-cycle-07c3-f-fb09
owner: unknown@360f41058e92
claimed: 2026-09-21T18:37Z
created: 2026-09-19
updated: 2026-09-21
refs:
  - "peer: mcfacehead-plugins librarian (uds 324.sock)"
---

Peer idea 2026-09-19 from the mcfacehead-plugins operator via the mcfacehead-plugins librarian (their item relay-idea-to-claude-kit-librarian-libra-b440). Peers identify a repo's librarian by session name (ListAgents, /peers). Acceptance: librarian-mode start carries a hard gate telling the operator to rename the session to one canonical form, '<repo name> - librarian', with an example (/rename mcfacehead-plugins - librarian); /rename is a built-in Claude Code slash command the skill cannot run, only instruct. Settle: one canonical form (names today are inconsistent: 'mcfacehead-plugins librarian', 'claude-kit librarian'); check the current name against it where the session name is observable (e.g. peer registry / statusline session name) and skip the gate when it already matches. Lands after 07c3 F2 (fb09) - same file.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — librarian behaviour; judgement (canonical name form)
