---
id: wi-an-archived-done-dep-counts-as-unmet-cc39
title: "wi: an archived done dep counts as unmet in next and claim; show --json disagrees"
type: bug
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - 1d1c implementer
---

1d1c implementer OQ, 2026-09-22: the ready rule resolves deps against items/ only, so once a done dep is archived its dependents vanish from next and claim refuses them, while show --json (blocked_by_unresolved) also reads the archive. Acceptance: one dep-resolution rule reads the archive for next, ready, claim and show alike; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- rider from 1d1c review (2026-09-22): add claim tests for a dep at doing+stage uat (met) and for re-claiming an owned doing item with unmet deps (unchanged).
