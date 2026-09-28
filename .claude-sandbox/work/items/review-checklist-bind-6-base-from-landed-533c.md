---
id: review-checklist-bind-6-base-from-landed-533c
title: "review-checklist: bind §6 BASE from landed: <merge sha>^1 with a guard; core.quotePath=false on every diff --name-only"
type: chore
status: doing
priority: 4
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T23:43Z
created: 2026-09-28
updated: 2026-09-28
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
