---
id: checkpoint-skill-handoff-md-trips-the-no-bc3e
title: "checkpoint skill: './HANDOFF.md' trips the non-bare-path lint"
type: chore
status: done
priority: 4
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - implementer report, item checkpoint-skill-describe-the-gate-s-inf-80ab
---

Pre-existing: checkpoint/SKILL.md and references/handoff-format.md say './HANDOFF.md' (a cwd write target), which the librarian review checklist's non-bare-path grep flags. Acceptance: reword to 'HANDOFF.md in the working directory' (or equivalent) so the checkpoint folder passes the lint with no behaviour change; do not narrow the lint.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
dispatch: implementer sonnet — default (two prose files, no opus signal)
dispatch: reviewer opus — rule 4 floor
- implementer sonnet returned DONE, commit 520e795; reviewer opus round 1 dispatched 2026-09-16 16:52:20
- review round 1: NEEDS_CHANGES — 1 medium (the new wording says 'in the working directory'; hooks/rehydrate.py
  manifest_path() resolves against the git repo root, cwd only as a fallback outside a repo — the librarian's own
  acceptance parenthetical was wrong), 2 nits (unwrapped lines; stacked 'in' phrases).
- librarian correction: acceptance is now 'HANDOFF.md at the repo root' (the code is authoritative; handoff-format.md
  already says one per repo). Fix round 1 sent 2026-09-16 16:54:01, tier unchanged (sonnet, resumed).
- fix round 1 returned DONE, new commit 0d568a4, nothing declined; re-review dispatched 2026-09-16 16:55:16 (reviewer opus, resumed)
- 2026-09-16 done: 3d050db
- re-review CLEAR (all 3 FIXED, none new). Landed merge 3d050db 2026-09-16 16:56:43.
