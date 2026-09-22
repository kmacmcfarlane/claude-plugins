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
review r1 (opus) at daf57d2: NEEDS_CHANGES. Seven Checks OK; probes: multibyte counted in chars, CRLF normalized, garbled input safe, 15 MB ledger in 0.2 s, other tiers byte-identical, acceptance met.
- [medium] no test pins the half-budget R/C cap (mutating room//2 → room passes all 9 tests). Pass: a test with R/C over half the budget plus D lines asserting D kept, R/C ≤ ~room/2, newest R/C kept.
- lows: handoff-format.md:133-135 omits the half cap and "newest within a kind" is wrong (D/X/U/Q ranked together); an R/C line longer than the room dropped whole; closing line can exceed a small budget (H5 reuses digest); nits: closing wording, uncounted `# ` lines (H5's successor line), tail() uncalled.
dispatch: implementer opus — fix round 1 (resume)
fix r1 DONE c21f67c (opus): half-cap test fails under the room//2 → room mutation; long lines cut with [cut]; output clamped to budget (0–1000 tested); closing wording; non-title `# ` lines counted as reasoning; doc gives the real order; (f) declined — tail() is the test's baseline. Note: implementer's first mutation undo (git checkout) wiped uncommitted edits; re-applied and re-tested before commit.
dispatch: reviewer opus — review r2 (resume)
