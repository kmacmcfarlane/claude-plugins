---
id: librarian-mode-secret-committed-in-a-fil-b2ad
title: "librarian-mode: secret committed in a file (not a message) stays in branch history"
type: chore
status: todo
priority: 3
created: 2026-09-18
updated: 2026-09-18
---

From the d72e fix round 3 (2026-09-18): the secret-rebuild rule covers a leak in a commit message only. A secret committed in a file and removed in a later commit still sits in the unmerged branch's history and would land with the merge. Acceptance: fix-loop/review-brief treat a secret in any committed content as critical with the same merge-base rebuild (history free of it before Land), name-never-value, rotation as scope change. Lands with or after 07c3 F1 (fix-loop moves to dev-cycle).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
