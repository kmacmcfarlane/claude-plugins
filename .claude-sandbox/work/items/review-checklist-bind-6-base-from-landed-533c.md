---
id: review-checklist-bind-6-base-from-landed-533c
title: "review-checklist: bind §6 BASE from landed: <merge sha>^1 with a guard; core.quotePath=false on every diff --name-only"
type: chore
status: todo
priority: 4
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
