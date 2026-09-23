---
id: dev-flow-reconcile-plugin-json-and-marke-0156
title: "dev-flow: reconcile plugin.json and marketplace.json descriptions (pre-existing drift)"
type: chore
status: todo
priority: 3
created: 2026-09-23
updated: 2026-09-23
refs:
  - d44e implementer 2026-09-23
---

Found by the d44e implementer 2026-09-23: dev-flow's plugin.json description and its marketplace.json entry already differed before d44e (the marketplace entry lacks the create-repo and sandbox soft-dependency clauses). d44e added the same operator-interaction clause to both but left the rest. Acceptance: the two descriptions match (house rule: the marketplace entry equals plugin.json's).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
