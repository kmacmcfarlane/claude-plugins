---
id: librarian-mode-secret-committed-in-a-fil-b2ad
title: "librarian-mode: secret committed in a file (not a message) stays in branch history"
type: chore
status: done
priority: 3
created: 2026-09-18
updated: 2026-09-21
closed: 2026-09-21
---

From the d72e fix round 3 (2026-09-18): the secret-rebuild rule covers a leak in a commit message only. A secret committed in a file and removed in a later commit still sits in the unmerged branch's history and would land with the merge. Acceptance: fix-loop/review-brief treat a secret in any committed content as critical with the same merge-base rebuild (history free of it before Land), name-never-value, rotation as scope change. Lands with or after 07c3 F1 (fix-loop moves to dev-cycle).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: 583e6d0

## Dispatch
- dispatch: implementer opus — security surface (secret handling procedure): fable signal; fable unavailable (unknown); fallback

## Implementer result
- round 1 DONE a5ff60d (opus): fix-loop § A leaked secret (any committed content; reach check first; merge-base rebuild; name-never-value; rotation to the operator); checklist §1 history scan (shas/files only); review-brief step 7 history review; agent-brief fix-round clause generalised.
- decision (librarian): yes — a secret that reached origin or another branch blocks the item, never lands, and escalates at once.
- dispatch: reviewer opus — rule 4 (fable signal; fallback)

## Review round 1 — NEEDS_CHANGES (opus) at a5ff60d
- procedure walk-through works (history clean after rebuild; value never printed by the scan or reach check).
- [medium] scan pattern misses github_pat_, bare sk-ant-/sk-proj-, ASIA ids, AGE-SECRET-KEY-1, passwords in URLs, PASS=, := assignments.
- [medium] merge commits invisible: git log -G / -p without --cc shows nothing added in a merge (conflict-round merge could land a secret).
- [low] dev-cycle SKILL.md:169-170 still frames it as a commit-subject exception (out of scope; fold in: one clause).
- dispatch: implementer opus — fix round 1 (resume)
- round 1 fix 5febe4e: pattern widened (all 8 shapes caught in a scratch repo); -G scan uses --remerge-diff (--cc flagged every merge); log -p reads use --cc; SKILL.md wording. Noise main~50: 4 commits.
- dispatch: reviewer opus — round 2 (resume)

## Review round 2 — CLEAR (opus) at 5febe4e
- --remerge-diff judged correct (catches conflict-resolution and hand-edited clean-merge secrets; no base-side noise); 27/29 fixture shapes caught; main~50 noise 4 harmless hits.
- lows (landed as CLEAR): Bearer tokens not matched (optional); review-brief:92-93 uneven wrap. Note: system grep is ugrep; the pattern exceeds its -o limit (checklist uses git -G, unaffected).
## Landed
- 583e6d0. 1 fix round. Fable-signal item run on opus as recorded fallback.
