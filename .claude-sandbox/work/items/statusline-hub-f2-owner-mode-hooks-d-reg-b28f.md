---
id: statusline-hub-f2-owner-mode-hooks-d-reg-b28f
title: "statusline-hub F2: owner mode + hooks.d registry (display/record kinds, health_path)"
type: feature
status: todo
priority: 1
deps:
  - statusline-hub-f1-new-plugin-tee-command-bfe2
parent: spike-status-line-multiplexer-dependency-d193
created: 2026-09-21
updated: 2026-09-21
---

d193 07 § F2 + consumer requirements recorded in d193 (claude-analytics: record kind gets the raw payload byte-for-byte every render; a crashing/slow record hook leaves gauge and sensor intact; optional health_path glyph; contract doc beside sensor-contract.md; registry path CFG/statusline-hub/hooks.d/<name>.json {name, command, timeout_ms, kind}). Owner/SessionStart logic ported from statusline (states, heal, prune, consent); takeover migration from statusline's owner.json. Wrap consent: decision 40 (b) ask once. Notify agents-61 / claude-analytics session when the contract lands.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
