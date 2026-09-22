---
id: handoff-h2-ledger-digest-keeps-reasoning-d0eb
title: "handoff H2: ledger digest keeps reasoning lines ahead of commit pointers"
type: feature
status: doing
priority: 1
parent: context-guard-compact-and-clear-handoffs-5039
owner: unknown@360f41058e92
claimed: 2026-09-22T16:00Z
created: 2026-09-22
updated: 2026-09-22
---

Compaction-time ledger injection keeps D/X/C/U/R/Q lines from every epoch before free commit pointers; budget unchanged; tests. Opus/opus. Plan: .claude-sandbox/investigations/5039-handoff-failures/00_findings.md § fix plan.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — per plan routing (executable hook logic or two-plugin doctrine)
impl r0 DONE daf57d2 (opus): ledger.digest(sid, budget) — R/C first (all epochs, up to half), then D/X/U/Q newest, rest of R/C, then P pointers; file order; headers only above kept lines; closing line counts drops and names the ledger file; compact tier calls it; 9 tests (fail on main); handoff-format wording. Overlap with H1 in rehydrate.py docstring + compact ledger block only.
dispatch: reviewer opus — rule 4
