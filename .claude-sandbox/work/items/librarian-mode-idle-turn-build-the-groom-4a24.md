---
id: librarian-mode-idle-turn-build-the-groom-4a24
title: "librarian-mode idle-turn: build the Groom table from wi needs-input"
type: chore
status: done
priority: 2
deps:
  - wi-grooming-status-and-a-needs-input-lis-b020
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
refs:
  - b020 implementer open question
---

Surfaced by b020's implementer 2026-09-21: plugins/dev-flow/skills/librarian-mode/references/idle-turn.md still says 'once the grooming status exists (wi item b020)' and builds its Groom table from a grep loop. Acceptance: once b020 lands, idle-turn.md points at 'wi needs-input' (and grooming) instead; SKILL.md Rehydrate step 3's decision grep can stay or point at it.

## Handoff
- doing: implementer dispatched (sonnet, agent af321d44e4a7bdf33)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer sonnet — one doc file, no judgement signal
- 2026-09-21 done: 3c9899e

## Implementer result
- round 1 DONE d652529 (sonnet): Groom table from wi needs-input --plain; hold-scoped items via wi ls --dep; b020 placeholder dropped. SKILL.md Rehydrate grep kept (finds highest N, a different query).
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at d652529
- [medium] dropped the legacy PARKED-prefixed blocked → wi migrate-parked --apply hint; restore it.
- lows: open-status sentence contradicts needs-input incl. parked; note every ls here exits 2 on empty; ls --dep default misses parked held items (optional --status); nit 'the scan' → wi needs-input.
- dispatch: implementer sonnet — fix round 1 (same agent resumed)
- fix round 1 DONE cceeae4 (sonnet): PARKED migration hint restored; lows a-d fixed.
- dispatch: reviewer opus — review r2 (same reviewer resumed)

## Review round 2 — CLEAR (opus) at cceeae4
- nit not taken: line 83 ~93 chars.
- landed 3c9899e
