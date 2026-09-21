---
id: statusline-hub-f2-owner-mode-hooks-d-reg-b28f
title: "statusline-hub F2: owner mode + hooks.d registry (display/record kinds, health_path)"
type: feature
status: done
priority: 1
deps:
  - statusline-hub-f1-new-plugin-tee-command-bfe2
parent: spike-status-line-multiplexer-dependency-d193
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
---

d193 07 § F2 + consumer requirements recorded in d193 (claude-analytics: record kind gets the raw payload byte-for-byte every render; a crashing/slow record hook leaves gauge and sensor intact; optional health_path glyph; contract doc beside sensor-contract.md; registry path CFG/statusline-hub/hooks.d/<name>.json {name, command, timeout_ms, kind}). Owner/SessionStart logic ported from statusline (states, heal, prune, consent); takeover migration from statusline's owner.json. Wrap consent: decision 40 (b) ask once. Notify agents-61 / claude-analytics session when the contract lands.

## Handoff
- doing: fix round 1 + main merge (conflict round) in progress; reviewer resumes after
- next: review round 2 (opus), then land; then F3 dfa1
- blocked: —
- learned: —

## Carried from F1
- records written only by the hub are not pruned until the hub has its own SessionStart prune (this feature).

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: 53ae9ec

## Dispatch
- dispatch: implementer opus — executable logic, settings writes, executes registered commands (security surface: fable signal; fable unavailable (unknown); fallback)

## Implementer result
- round 1 DONE_WITH_CONCERNS a6e91c4 (opus, fable-signal fallback): hub.py render (sensor first; record hooks detached with exact bytes; display hooks parallel 150/250 ms, last-good 60 s; health ⚠), registry.py (manifest trust: private, user-owned, ≤16 KiB, not in project tree; exec without shell unless "shell": true; output cleaned keeping SGR), owner.py/session_start.py/housekeeping.py ported (vendored-drift test), hook-contract.md, new install-statusline-hub skill. 87 hub tests. Takeover DEFERRED until statusline registers hooks.d/statusline.json (F3).
- scope widening before review: marketplace.json hub description must match plugin.json (F1 text stale).
- widening e9f698d: marketplace description matches plugin.json; contract notes cancelled renders (hook may outlive a killed hub → hooks must be fast and idempotent).
- dispatch: reviewer opus — rule 4 (fable-signal fallback)

## Review round 1 — NEEDS_CHANGES (opus) at e9f698d
- claude-analytics contract verified (byte-for-byte incl. invalid UTF-8/CRLF; crashing/sleeping record hooks don't touch render/sensor); sanitisation holds; SessionStart scenarios: never two owners, no flap.
- [medium] README conflicts with main (catalog rows) — conflict round. [medium] in_project misses a config dir inside the repo when CC starts in a subdir / payload lacks dirs (fails open). [medium] record runners unbounded (31 runners, ~366 MB with one hung hook). [medium] statusline owner.data_dir scan picks statusline-hub-* (F2 created it) — fix in statusline + vendored copy. [medium] hub reads statusline's data → declare statusline (soft) in row + description.
- lows: "shell": true departs from 07 — decision (librarian): accept (an argv array can already name /bin/sh; exec stays the default) and record in 07's successor/contract; hand-written manifests pruned at 14 days; setsid grandchild holding stdout; record spec via argv can exceed MAX_ARG_STRLEN; nits.
- dispatch: implementer opus — fix round 1 (resume; includes a merge-conflict round with main)
- round 1 fix: 3bd6a9b (merge main, default subject → subject-fix at Land), b13fdc1 (git-tree refusal, per-hook lock, pinned manifests, spec on stdin, first-line read, U+2028/9), 0ee1c09 (statusline data-dir scan fix + vendored resync), eafa18d (statusline soft dep declared). 94 hub tests.
- dispatch: reviewer opus — round 2 (resume)
- tell agents-61 on landing: one live copy per record hook (a busy hook skips renders).

## Review round 2 — CLEAR (opus) at eafa18d
- hostile manifests refused incl. git-tree config dirs; hung record hook: 1 runner/12 MB (was 31/366 MB); byte-for-byte; SessionStart scenarios stable.
- lows (to F3): scan still takes statusline-hub-* when it lacks current-hooks → name check; custom config dir inside a git-tracked dir refuses all hooks (fails safe, quiet).
## Landed
- 53ae9ec. 1 fix round + conflict round. agents-61 notified (contract + busy-hook skip rule).
- claude-analytics-8b ack 2026-09-21: contract accepted incl. the single-instance rule; sampler (Phase 2 there) will be a short record hook, argv command, manifest refreshed from SessionStart (not pinned). No action needed.
