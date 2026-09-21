---
id: statusline-hub-f3-statusline-becomes-a-d-dfa1
title: "statusline-hub F3: statusline becomes a display hook (hard dependency on the hub)"
type: feature
status: todo
priority: 2
deps:
  - statusline-hub-f2-owner-mode-hooks-d-reg-b28f
parent: spike-status-line-multiplexer-dependency-d193
created: 2026-09-21
updated: 2026-09-21
---

d193 07 § F3. statusline declares statusline-hub in plugin.json dependencies (principle 4 as amended by 5343: statusline has no function without the hub), catalog (hard); stops writing settings; the hub owns the sensor write. context-guard/analytics/dev-flow stay soft readers.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
