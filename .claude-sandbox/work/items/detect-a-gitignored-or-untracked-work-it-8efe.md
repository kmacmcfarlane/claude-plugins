---
id: detect-a-gitignored-or-untracked-work-it-8efe
title: detect a gitignored or untracked work-item store; one shared ignore-shape helper
type: spike
status: todo
priority: 2
created: 2026-09-18
updated: 2026-09-18
refs:
  - peer Paseo stop-gap (agents repo); operator-attention e5516d2
---

Peer 'Paseo stop-gap' (agents repo), 2026-09-18, retrospective on the 7f00 class. Ask: judge whether it's worth (1) wi lint and the wi prime header warning when the store root is git check-ignore'd or has zero tracked files while holding items; (2) test_wi.py covering private, sidecar and already-ignored shapes, including the 'store exists but ignored' state; (3) one shared shape-classification helper instead of per-tool re-implementations, plus a 'who may write a host .gitignore' rule in agents decision 0002. Siblings: 7772 (wi add recurrence), 37d3 (config.yaml un-ignore), claude-sandbox a7bf. Acceptance: a recommendation per point, then features filed. Held until plugin-factoring merges.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- 2026-09-18: plugin-factoring merged (0d8b4c9); hold released. Paths moved: claude-kit dissolved into kit-dev/context-guard/dev-flow/work-items/chat/sandbox/ralph.
