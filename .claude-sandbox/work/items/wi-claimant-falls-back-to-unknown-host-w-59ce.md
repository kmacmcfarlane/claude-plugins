---
id: wi-claimant-falls-back-to-unknown-host-w-59ce
title: wi claimant falls back to unknown@<host> when USER is unset
type: bug
status: doing
priority: 3
owner: unknown@bf9f9839222c
claimed: 2026-09-22T22:36Z
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

## Notes
- 2026-09-22 claimed by unknown@bf9f9839222c

target: full wi-claimant-falls-back-to-unknown-host-w-59ce /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/wi-claimant-falls-back-to-unknown-host-w-59ce
dispatch: implementer opus — executable logic (scripts/wi.py), rule 2
agent: implementer a94dc4899be9d4077 round 1
