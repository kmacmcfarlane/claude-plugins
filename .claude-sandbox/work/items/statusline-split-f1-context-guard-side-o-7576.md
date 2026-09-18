---
id: statusline-split-f1-context-guard-side-o-7576
title: "statusline split F1: context-guard side of the sensor/gauge contract"
type: feature
status: doing
priority: 1
parent: status-line-its-own-independently-instal-3c48
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T20:13Z
created: 2026-09-18
updated: 2026-09-18
---

3c48 plan §F1: ANCHORS refactor; lib_context reads the sensor record at both ~/.claude/statusline/sensor/<sid>.json (v1) and the old claude-kit/context-gate path; epoch-start timestamp demotion after compaction; publish claude-kit/context-gate/gauge.json (v1). Size M. Gate-feeding: fable / opus fallback.

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer fable — rule 3: non-trivial change to HARD-gate inputs; fallback per § Fallback
