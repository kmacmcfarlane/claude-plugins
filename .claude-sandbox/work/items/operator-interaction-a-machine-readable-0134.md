---
id: operator-interaction-a-machine-readable-0134
title: "operator-interaction: a machine-readable card under decision N lines for operator-attention's collector (OD-6)"
type: feature
status: todo
priority: 3
deps:
  - dev-flow-a-decision-presentation-skill-d-7113
parent: checkpoint-around-continuation-how-agent-d3ee
created: 2026-09-23
updated: 2026-09-23
refs:
  - operator-attention OD-6; 7113
---

Deferred from 7113. operator-attention's OD-6: optional indented detail lines under 'decision N:' (stakes, reversibility, basis, default, wake, raising session) that today's wi ignores, so the collector reads a conforming card instead of parsing prose. Follows once the operator has used the format. Coordinate with operator-attention (they emit and read whatever schema this fixes).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-23 operator-attention (commit 0c096a4; their decision-collector/05_integration-with-operator-interaction-v1.md):
  - The collector ships as a script with no skill of its own; `decisions` is the operator's single entry point.
  - It supplies warmth and age per decision, and the skill decides line / card / block. Agreed shape: a word, warm | cold (the skill's two states), with the context-distance events underneath for the re-show diff.
  - The card must carry raised-at explicitly (one of the three clocks; git history only gives commit granularity).
  - Until this lands, the collector parses the human `decision N:` form and marks missing fields unknown.
