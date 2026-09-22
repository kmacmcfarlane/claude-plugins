---
id: wi-claimant-falls-back-to-unknown-host-w-59ce
title: wi claimant falls back to unknown@<host> when USER is unset
type: bug
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock), operator relay"
---

Relayed 2026-09-22 from the agents store (wi-claimant-falls-back-to-unknown-host-i-59d4). default_owner() uses $USER, unset in claude-sandbox, so claims read unknown@<container-id> (this store's claims show unknown@360f41058e92 too). Acceptance: fall back to git config user.name, then getpass; document WI_OWNER as the explicit override in format.md; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
