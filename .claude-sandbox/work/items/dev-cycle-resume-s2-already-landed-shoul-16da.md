---
id: dev-cycle-resume-s2-already-landed-shoul-16da
title: "dev-cycle resume: S2 (already landed) should notice a pending push-rejection merge"
type: chore
status: doing
priority: 3
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:38Z
created: 2026-09-28
updated: 2026-09-28
refs:
  - 5dbf review
---

From the 5dbf review 2026-09-28: resume.md state S2 reports and stops; when MERGE_HEAD is set in the main checkout and equals origin/<base>, it should say a push-rejection merge is pending and point at troubleshooting § Landing. Acceptance: one clause in resume.md S2.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-dev-cycle-resume-s2-already-landed-shoul-16da at .claude/worktrees/dev-cycle-resume-s2-already-landed-shoul-16da, base main (3f1d01c)
dispatch: implementer opus — changes what a skill does on resume (rule 2)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
agent: implementer a913b61dd868620cc round 1
return: implementer DONE 9061d61 (open q: S0b could take the same pointer; a run dying between merge and landed: reads STALE — pre-existing)
changed: plugins/dev-flow/skills/dev-cycle/references/resume.md
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer a2a8c0904d5587680 round 1 at 9061d61
verdict: NEEDS_CHANGES round 1 at 9061d61 (1 high, 1 low)
findings:
  [high] resume.md:112-122,138,139 — unreachable-sink rows never check MERGE_HEAD: a store-less run rejected on push, merged --no-commit and dead reads REMNANT absent → S0 rebuilds landed work, or S0b without the pointer; pass: add a pending main-checkout merge to REMNANT's artefact list so it selects S0b, and give S0b the same pointer (or a MERGE_HEAD precondition ahead of Group P)
  [low] resume.md:137 — "report the landing as not cleanly done" contradicts the bullet ("the local landing merge stands"); pass: "landed <merge sha>; a merge is pending in the main checkout", then follow the bullet
dispatch: implementer opus — resume, fix round 1
agent: implementer a913b61dd868620cc round 2
