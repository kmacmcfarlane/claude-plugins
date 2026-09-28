---
id: review-checklist-bind-6-base-from-landed-533c
title: "review-checklist: bind §6 BASE from landed: <merge sha>^1 with a guard; core.quotePath=false on every diff --name-only"
type: chore
status: done
priority: 4
created: 2026-09-28
updated: 2026-09-28
closed: 2026-09-28
refs:
  - 2364 review
---

From the 2364 review 2026-09-28 (lows): §6's BASE=$(git rev-parse HEAD^1) is right only when HEAD is the landing merge — after a fast-forward or a later commit it silently narrows §2/§4/§5 (guard with HEAD^2, or bind from the recorded landed: <merge sha>^1); §3's first 'CHECK: skill added/changed' line and the §2/§4/§5 loops use git diff --name-only, which quotes non-ASCII paths (add -c core.quotePath=false).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-review-checklist-bind-6-base-from-landed-533c at .claude/worktrees/review-checklist-bind-6-base-from-landed-533c, base main (577d93b)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — checklist commands (rule 2)
agent: implementer a8121c675ddf343db round 1
return: implementer DONE 3932868
changed: plugins/dev-flow/skills/dev-cycle/references/review-checklist.md
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer a65b3f94f74edc90e round 1 at 3932868
verdict: CLEAR round 1 at 3932868 (2 low: BASE still bound after a guard FAIL — matches the checklist's print-FAIL style; §1 git log --name-only quoting — outside acceptance; both declined)
landed: c4d8798
- 2026-09-28 done: c4d8798
