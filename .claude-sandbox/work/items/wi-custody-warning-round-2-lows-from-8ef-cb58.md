---
id: wi-custody-warning-round-2-lows-from-8ef-cb58
title: "wi custody warning: round-2 lows from 8efe"
type: chore
status: todo
priority: 4
created: 2026-09-18
updated: 2026-09-18
---

From the 8efe round-2 review (2026-09-18), all low: (1) sidecar store ignoring its own work/ gets host advice (trackInHost) — when sandbox_shape is sidecar, drop trackInHost and name the sidecar repo; (2) 'remove or negate that rule' — git cannot re-include under an excluded parent; for SANDBOX_IGNORES rules say rewrite as /.claude-sandbox/* + !/.claude-sandbox/work/ or remove; (3) check-ignore -v parse splits on the first :N: — use -z output. Files: plugins/work-items/skills/work-items/scripts/wi.py, tests.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
