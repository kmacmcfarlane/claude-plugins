---
id: context-guard-rehydrate-py-module-docstr-3a8f
title: "context-guard: rehydrate.py module docstring still calls the own arm 'ours by the path, no comparison'"
type: chore
status: todo
priority: 4
created: 2026-09-22
updated: 2026-09-22
refs:
  - 0836 review round 1
---

0836 reviewer low, 2026-09-22: rehydrate.py:46 module docstring predates the realpath ownership test in read_store_manifest. Acceptance: the module docstring carries the same qualifier as resolve_manifest's own line, or points at read_store_manifest.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
