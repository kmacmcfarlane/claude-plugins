---
id: statusline-hub-f1-new-plugin-tee-command-bfe2
title: "statusline-hub F1: new plugin + tee command (stdin → sensor record)"
type: feature
status: doing
priority: 1
parent: spike-status-line-multiplexer-dependency-d193
owner: unknown@360f41058e92
claimed: 2026-09-21T18:22Z
created: 2026-09-21
updated: 2026-09-21
---

d193 07 § F1 (.claude-sandbox/investigations/d193-statusline-multiplexer/07_recommendation-dispatcher.md). Operator-approved name statusline-hub (decision 41). New plugin skeleton (plugin.json, catalog row, marketplace.json entry, CLAUDE.md layout); a tee CLI that writes the sensor record v1 exactly as statusline's sensor.py does (vendored copy; no cross-plugin import) with a parity test against statusline's contract tests; docs: ccstatusline Custom Command, Starship custom, shell-wrapper recipes. No SessionStart, no settings writes.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — marketplace shape (new plugin) + executable logic
