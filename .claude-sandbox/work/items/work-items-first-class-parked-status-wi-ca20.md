---
id: work-items-first-class-parked-status-wi-ca20
title: "work-items: first-class parked status (wi park / unpark)"
type: feature
status: todo
priority: 2
created: 2026-09-19
updated: 2026-09-19
refs:
  - "peer: implement headless paseo support (uds 242.sock), for claude-sandbox librarian"
---

Peer request 2026-09-19 (claude-sandbox librarian, relayed via session 'implement headless paseo support', operator's ask). Deliberate deferral currently abuses 'wi block "PARKED: ..."'. Acceptance: status 'parked' valid in lint with a reason field; 'wi park <id> <reason>' / 'wi unpark <id>' (back to todo, or recorded previous status); excluded from ready/next; prime shows a one-line count or collapsed section, not under BLOCKED; ls filters on parked; archive via done --drop + archive; backlog-yaml bridge maps it (deferred-like) or documents it doesn't; SKILL.md table + references/format.md updated. Migration: optional step converting 'status: blocked' items whose reason starts with 'PARKED' to parked. The claude-sandbox store's own migration (b090, 2dd5) is outside this repo's Scope: message the claude-sandbox librarian when it ships; it migrates its store.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
