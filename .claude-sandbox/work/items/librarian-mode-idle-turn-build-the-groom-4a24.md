---
id: librarian-mode-idle-turn-build-the-groom-4a24
title: "librarian-mode idle-turn: build the Groom table from wi needs-input"
type: chore
status: doing
priority: 2
deps:
  - wi-grooming-status-and-a-needs-input-lis-b020
owner: unknown@360f41058e92
claimed: 2026-09-21T22:51Z
created: 2026-09-21
updated: 2026-09-21
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

## Implementer result
- round 1 DONE d652529 (sonnet): Groom table from wi needs-input --plain; hold-scoped items via wi ls --dep; b020 placeholder dropped. SKILL.md Rehydrate grep kept (finds highest N, a different query).
- dispatch: reviewer opus — rule 4
