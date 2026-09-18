---
id: statusline-split-f4-context-guard-hands-77b1
title: "statusline split F4: context-guard hands over; dev-flow Fallback path"
type: feature
status: done
priority: 1
deps:
  - statusline-split-f2-the-statusline-plugi-a67f
parent: status-line-its-own-independently-instal-3c48
created: 2026-09-18
updated: 2026-09-18
closed: 2026-09-18
---

3c48 plan §F4: remove context-guard's settings-writing heal, add notice, docs; dev-flow model-routing.md § Fallback reads the new sensor path; declare soft deps. Size M; opus.

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — settings writes / hook code (rule 2); fable not needed: not a gate

impl: DONE 562b047 (no settings writes; notice once/7d; FIFO + future-at guards; 22/22 gate matrix identical; dev-flow fallback reads the sensor).
dispatch: reviewer opus — rule 4

review round 1 (opus): CLEAR. Gate matrix 23/25 identical; the 2 differences intended (future at rejected; FIFO sensor no longer hangs the gate). Operator path unchanged (claude-kit cache still maintains its current-hooks link). Lows -> F5.
- 2026-09-18 done: ad71f30
