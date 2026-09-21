---
id: statusline-hub-f2-owner-mode-hooks-d-reg-b28f
title: "statusline-hub F2: owner mode + hooks.d registry (display/record kinds, health_path)"
type: feature
status: doing
priority: 1
deps:
  - statusline-hub-f1-new-plugin-tee-command-bfe2
parent: spike-status-line-multiplexer-dependency-d193
owner: unknown@360f41058e92
claimed: 2026-09-21T18:55Z
created: 2026-09-21
updated: 2026-09-21
---

d193 07 § F2 + consumer requirements recorded in d193 (claude-analytics: record kind gets the raw payload byte-for-byte every render; a crashing/slow record hook leaves gauge and sensor intact; optional health_path glyph; contract doc beside sensor-contract.md; registry path CFG/statusline-hub/hooks.d/<name>.json {name, command, timeout_ms, kind}). Owner/SessionStart logic ported from statusline (states, heal, prune, consent); takeover migration from statusline's owner.json. Wrap consent: decision 40 (b) ask once. Notify agents-61 / claude-analytics session when the contract lands.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Carried from F1
- records written only by the hub are not pruned until the hub has its own SessionStart prune (this feature).

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — executable logic, settings writes, executes registered commands (security surface: fable signal; fable unavailable (unknown); fallback)

## Implementer result
- round 1 DONE_WITH_CONCERNS a6e91c4 (opus, fable-signal fallback): hub.py render (sensor first; record hooks detached with exact bytes; display hooks parallel 150/250 ms, last-good 60 s; health ⚠), registry.py (manifest trust: private, user-owned, ≤16 KiB, not in project tree; exec without shell unless "shell": true; output cleaned keeping SGR), owner.py/session_start.py/housekeeping.py ported (vendored-drift test), hook-contract.md, new install-statusline-hub skill. 87 hub tests. Takeover DEFERRED until statusline registers hooks.d/statusline.json (F3).
- scope widening before review: marketplace.json hub description must match plugin.json (F1 text stale).
- widening e9f698d: marketplace description matches plugin.json; contract notes cancelled renders (hook may outlive a killed hub → hooks must be fast and idempotent).
- dispatch: reviewer opus — rule 4 (fable-signal fallback)
