---
id: statusline-split-f1-context-guard-side-o-7576
title: "statusline split F1: context-guard side of the sensor/gauge contract"
type: feature
status: done
priority: 1
parent: status-line-its-own-independently-instal-3c48
created: 2026-09-18
updated: 2026-09-18
closed: 2026-09-18
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

impl round 0 (fable): FAILED — HTTP 429 out of usage credits (req_011CfBWuzt4pQsJAPpHQ4yJC); reset unknown.
dispatch: implementer opus — fable unavailable (unknown); fallback. Worktree clean, nothing to carry.

impl (opus fallback): DONE_WITH_CONCERNS c982aac (38 tests, 26/26 gate matrix identical; _base_dir empty-var rule; epoch_at demotes legacy race too per plan).
dispatch: reviewer opus — fable unavailable (unknown); fallback

review round 1 (opus, fable fallback): CLEAR. Own matrix 27/28 identical (the 28th = intended _base_dir empty-var move; launcher never exports an empty value). Lows routed: future sensor at / FIFO guard / tokens comment / publish_gauge earlier -> F4; comparison rule in contract -> F2.
- 2026-09-18 done: 69d3283
