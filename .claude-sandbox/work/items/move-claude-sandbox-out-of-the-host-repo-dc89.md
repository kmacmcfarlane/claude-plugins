---
id: move-claude-sandbox-out-of-the-host-repo-dc89
title: move .claude-sandbox/ out of the host repo into a sidecar
short_display_name: sandbox files to a sidecar
type: chore
status: blocked
priority: 2
blocked: waits on claude-sandbox fe52 landing, then the operator's go
created: 2026-10-13
updated: 2026-10-13
refs:
  - peer claude-sandbox librarian, 2026-10-13 (its item fe52)
---

Peer notice 2026-10-13: claude-sandbox is re-planning 'track-in-host sidecar' (fe52), which stages git rm --cached in the host repo (never commits there) and inits a sidecar with the current files; this repo is first in line. Running it here is this session's call with the operator. Waits on fe52 landing (the peer messages it). Note: this repo just recorded its store as tracked (store.yaml) and the wi rule reads the layout; a move changes both.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
