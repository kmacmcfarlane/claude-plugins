---
id: dev-cycle-xhigh-trial-a-run-whose-first-90e0
title: "dev-cycle xhigh trial: a run whose first late high has passed must not enrol at a later round"
short_display_name: trial enrols after its first late high
type: bug
status: todo
priority: 3
created: 2026-10-13
updated: 2026-10-13
refs:
  - dev-cycle-enrol-the-xhigh-trial-when-a-r-4d27
---

From 4d27 review 2026-10-13 (pre-existing): a unit whose arm was full at its round-1 late high becomes control with no trial: line; at round 2 a high also reads as a late high and the trial step re-runs, so it can enrol if a slot freed. Acceptance: model-routing.md § The xhigh trial's Unit bullet defines L as the run's first late high and says a run past its L writes no trial: line later.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
