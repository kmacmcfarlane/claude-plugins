---
id: librarian-mode-secret-committed-in-a-fil-b2ad
title: "librarian-mode: secret committed in a file (not a message) stays in branch history"
type: chore
status: doing
priority: 3
owner: unknown@360f41058e92
claimed: 2026-09-21T18:14Z
created: 2026-09-18
updated: 2026-09-21
---

From the d72e fix round 3 (2026-09-18): the secret-rebuild rule covers a leak in a commit message only. A secret committed in a file and removed in a later commit still sits in the unmerged branch's history and would land with the merge. Acceptance: fix-loop/review-brief treat a secret in any committed content as critical with the same merge-base rebuild (history free of it before Land), name-never-value, rotation as scope change. Lands with or after 07c3 F1 (fix-loop moves to dev-cycle).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — security surface (secret handling procedure): fable signal; fable unavailable (unknown); fallback

## Implementer result
- round 1 DONE a5ff60d (opus): fix-loop § A leaked secret (any committed content; reach check first; merge-base rebuild; name-never-value; rotation to the operator); checklist §1 history scan (shas/files only); review-brief step 7 history review; agent-brief fix-round clause generalised.
- decision (librarian): yes — a secret that reached origin or another branch blocks the item, never lands, and escalates at once.
- dispatch: reviewer opus — rule 4 (fable signal; fallback)
