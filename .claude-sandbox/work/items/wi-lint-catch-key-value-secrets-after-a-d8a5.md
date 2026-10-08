---
id: wi-lint-catch-key-value-secrets-after-a-d8a5
title: "wi lint: catch KEY=value secrets after a bullet or date prefix"
short_display_name: lint misses prefixed secrets
type: bug
status: todo
priority: 2
created: 2026-10-08
updated: 2026-10-08
refs:
  - checkpoint-before-the-manifest-write-con-6c43 review 1
---

Found by the 6c43 review 1 (finding 7, medium), 2026-10-08: SECRET_ASSIGN_RE in wi.py is anchored at line start, so '- <date> checkpoint: CORRECTION KEY=value' lints clean while the bare line is caught. Acceptance: the assignment is matched after a bullet, date or tag prefix; a test pins both shapes.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
