---
id: wi-claimant-falls-back-to-unknown-host-w-59ce
title: wi claimant falls back to unknown@<host> when USER is unset
type: bug
status: done
priority: 3
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
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
return: implementer DONE 4a3a190
changed: wi.py (default_owner order), tests/test_wi.py, references/format.md (Claimant), SKILL.md (claim row)
librarian on OQ: no sweep; old unknown@<host> claims are released or --steal-ed by the librarian as items move — release never checks owner, and container ids already orphaned them.
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a81b9403aba1aa4a2 round 1
verdict: CLEAR round 1 at 4a3a190
landed: ea92599
- 2026-09-22 done: ea92599
