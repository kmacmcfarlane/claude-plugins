---
id: sandbox-autonomy-870d
title: Split sandbox (standalone) and autonomy (ralph + backlog skills)
type: refactor
status: todo
priority: 2
deps:
  - doctrine-9411
  - work-plugin-36f5
parent: plugin-factoring-924b
created: 2026-09-02
updated: 2026-09-02
---

sandbox plugin stands alone (always the goal - usable without ralph or any backlog). autonomy plugin = ralph loop conventions + backlog-yaml/entry/grooming skills, consuming a work source through the work plugin's provider interface via a thin shim over backlog.py (which stays canonical in the claude-sandbox repo, seeded by init-ralph). Dependencies declared and directional: autonomy -> sandbox (hard), autonomy -> work interface (soft, degrades).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
