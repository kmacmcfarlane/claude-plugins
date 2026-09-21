---
id: librarian-mode-start-gate-asks-the-opera-14bd
title: "librarian-mode: start gate asks the operator to /rename the session '<repo> - librarian'"
type: feature
status: done
priority: 2
deps:
  - librarian-mode-leans-on-dev-cycle-07c3-f-fb09
created: 2026-09-19
updated: 2026-09-21
closed: 2026-09-21
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
- 2026-09-21 done: 3e0d977

## Dispatch
- dispatch: implementer opus — librarian behaviour; judgement (canonical name form)

## Implementer result
- round 1 DONE 946c533 (opus): references/session-name.md (canonical `<repo> - librarian`, repo = basename of MAIN; reads only this session's registry file by CLAUDE_PID, trusted when sessionId matches); start = Rehydrate → name gate (hard on mismatch, soft when unobservable) → idle turn; status prints the name; idle-turn.md ordering. SKILL.md 13,604 chars.
- dispatch: reviewer opus — rule 4

## Review round 1 — CLEAR (opus) at 946c533
- registry read + trust check verified in this sandbox (mismatch: "claude-kit librarian"); basename(MAIN) right from worktrees; no rule lost in the three cuts.
- lows carried to 1dab: decline of the rename lasts only for the conversation (record it, or say until /clear); "Dispatch nothing" should not stall cycles in flight; SKILL.md Idle turn "Only an operator hold" now has a second stopper (the gate); "show the line once more" → each message until matched or declined.
## Landed
- 3e0d977.
