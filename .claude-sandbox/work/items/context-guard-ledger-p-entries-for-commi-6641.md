---
id: context-guard-ledger-p-entries-for-commi-6641
title: "context-guard ledger: P-entries for commits in other repos name the session cwd"
type: bug
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock), operator relay"
---

Relayed 2026-09-22 from the agents store (ledger-pointer-attributes-cross-repo-com-03b8). Ledger P-entries for a commit made in another repo say '-> .../<session cwd>': the hook uses the payload cwd, not the repo the commit landed in. Acceptance: derive the repo from the command's git -C / cd context (or the commit's own repo), fall back to cwd; test with a git -C <other> commit.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
