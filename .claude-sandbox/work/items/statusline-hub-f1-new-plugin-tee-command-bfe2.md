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
- doing: in review (opus) at 51707d9
- next: land on CLEAR, then F2
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — marketplace shape (new plugin) + executable logic

## Implementer result
- round 1 DONE_WITH_CONCERNS d72f545 (opus): plugins/statusline-hub (plugin.json, hooks/tee.py vendored writer, tests incl. parity/drift vs statusline, skill statusline-hub with ccstatusline/Starship/wrapper recipes), README/CLAUDE.md/marketplace. Could not: sensor-contract.md "only writer" wording (out of scope).
- scope widened by the librarian before review: that one line in statusline sensor-contract.md; the stale README counts ("three plugins whose aim is harness behavior", "all eight").

## Implementer result (scope widening)
- 51707d9: sensor-contract §2 names both writers (and the "no lock needed" sentence); README counts unstaled. Open: statusline sensor.py docstring still says one writer (follow-up with F3).
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at 51707d9
- byte parity verified (4 payloads, newer-wins cases); drift test catches every mutation that should fail; tee safe (50 MB garbage 22 ms, traversal ids hashed under CFG, modes 0700/0600); ccstatusline and Starship recipes checked against their docs.
- [medium] ccstatusline's global Custom Command Cache TTL (customCommandCacheTtlSeconds) makes the tee run at most once per TTL → record up to 60 s stale silently; recipe must say TTL 0, troubleshooting names the cause.
- lows: sensor-contract §2 overclaims concurrent safety (interleaved writes are last-writer-wins, 5/40 regress with or without the tee); sensor.py:8 and lib_context.py:174 still say one writer; README consumer rows (context-guard/dev-flow) name only statusline as the source (defer to F3); launcher `ls -td` picks newest-modified, not newest version; nits.
- dispatch: implementer opus — fix round 1 (resume)
- round 1 fix df00a29: ccstatusline TTL 0 in recipe + troubleshooting; contract concurrency wording; sensor.py/lib_context docstrings name both writers; launcher wording; README aim. Declined: README consumer rows (F3), allowed-tools nit.
- dispatch: reviewer opus — round 2 (resume)
