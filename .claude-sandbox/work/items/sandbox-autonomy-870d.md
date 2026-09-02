---
id: sandbox-autonomy-870d
title: Split sandbox (standalone) and autonomy (ralph + backlog skills)
type: refactor
status: done
priority: 2
deps:
  - doctrine-9411
  - work-plugin-36f5
parent: plugin-factoring-924b
created: 2026-09-02
updated: 2026-09-02
closed: 2026-09-02
---

sandbox plugin stands alone (always the goal - usable without ralph or any backlog). autonomy plugin = ralph loop conventions + backlog-yaml/entry/grooming skills, consuming a work source through the work plugin's provider interface via a thin shim over backlog.py (which stays canonical in the claude-sandbox repo, seeded by init-ralph). Dependencies declared and directional: autonomy -> sandbox (hard), autonomy -> work interface (soft, degrades).

## Handoff
- doing: implemented, pending review
- next: fable review, then wi done
- blocked: —
- learned: —

## Notes
- 2026-09-02 claimed by unknown@e7c6135255e0
- 2026-09-02 done: 6c6ede2 + 6df885c; fable review APPROVED; marketplace coherent at 7 plugins
