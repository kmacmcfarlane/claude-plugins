---
id: handoff-h1-mark-checkpoint-stamps-writte-9852
title: "handoff H1: mark_checkpoint stamps written/head/branch/session; age check handles UTC and future stamps"
type: feature
status: doing
priority: 1
parent: context-guard-compact-and-clear-handoffs-5039
owner: unknown@360f41058e92
claimed: 2026-09-22T16:00Z
created: 2026-09-22
updated: 2026-09-22
---

Machine fields never hand-typed: the mark step rewrites them in the repo manifest; rehydrate ages from file mtime when the stamp is absent/future/garbled and never labels a future stamp FRESH; tests. Opus impl + opus review (fable reviewer if the gate-record code is touched). Plan: .claude-sandbox/investigations/5039-handoff-failures/00_findings.md § fix plan.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — per plan routing (executable hook logic or two-plugin doctrine)
impl r0 DONE_WITH_CONCERNS ab8d2f5 (opus): mark_checkpoint stamps written/head(short)/branch/session atomically before the gate record (body/line endings byte-identical; aborts on a concurrent change); stamps only a manifest modified ≤30 min ago whose session: is empty/placeholder/this session/lineage/adopted author (else warns "not stamped"); warns on >6000-char body and a scratchpad HANDOFF.md. rehydrate reads stamps as UTC, ages by mtime when missing/garbled/future (>10 min), never FRESH for a future stamp. Spec: `<stamped>` placeholders. 19 new tests; two CLI tests now run from temp dirs (they could reach main's real HANDOFF.md). Gate record (L.mark_checkpoint) unchanged.
librarian on OQs: accept the 30-min window and 10-min skew as defaults; keep "copied unknown id → warn, don't stamp" (fails safe; F3b revisits with per-session manifests); `<stamped>` never marked stays foreign (fails safe).
dispatch: reviewer opus — hook logic; gate-record code untouched, so no fable signal
