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

## Implementer result
- round 1 DONE_WITH_CONCERNS d72f545 (opus): plugins/statusline-hub (plugin.json, hooks/tee.py vendored writer, tests incl. parity/drift vs statusline, skill statusline-hub with ccstatusline/Starship/wrapper recipes), README/CLAUDE.md/marketplace. Could not: sensor-contract.md "only writer" wording (out of scope).
- scope widened by the librarian before review: that one line in statusline sensor-contract.md; the stale README counts ("three plugins whose aim is harness behavior", "all eight").
