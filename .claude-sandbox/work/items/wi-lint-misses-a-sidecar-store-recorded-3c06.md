---
id: wi-lint-misses-a-sidecar-store-recorded-3c06
title: wi lint misses a sidecar store recorded ignored
short_display_name: lint misses ignored sidecar store
type: bug
status: todo
priority: 2
created: 2026-10-13
updated: 2026-10-13
refs:
  - work-items-wi-init-rule-a-sidecar-store-00fc
---

From 00fc's scratch test, 2026-10-13: wi init --no-track in a sidecar layout records tracking: ignored and writes /work/ into .claude-sandbox/.gitignore, so new items land in no repo, and wi lint stays clean. Acceptance: lint (and prime) warn when a sidecar store is recorded ignored or its sidecar ignores it; wi init --no-track in a sidecar layout refuses or warns, naming --track.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
