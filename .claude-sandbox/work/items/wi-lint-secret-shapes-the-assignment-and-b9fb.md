---
id: wi-lint-secret-shapes-the-assignment-and-b9fb
title: "wi lint: secret shapes the assignment and key/value rules still miss"
short_display_name: lint misses other secret shapes
type: bug
status: todo
priority: 3
created: 2026-10-08
updated: 2026-10-08
refs:
  - wi-lint-catch-key-value-secrets-after-a-d8a5 review 1
---

From the d8a5 review 1 notes, 2026-10-08: lowercase or mixed-case keys (db_pass=...), spaces around = (KEY = value), KEY: value, JSON "KEY":"value", and --flag=value pass both rules unless the key holds a key/value-rule word. Acceptance: decide per shape with real-store before/after; tests pin each.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
