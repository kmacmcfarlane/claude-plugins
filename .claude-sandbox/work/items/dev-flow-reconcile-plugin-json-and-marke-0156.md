---
id: dev-flow-reconcile-plugin-json-and-marke-0156
title: "dev-flow: reconcile plugin.json and marketplace.json descriptions (pre-existing drift)"
type: chore
status: doing
priority: 3
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T21:55Z
created: 2026-09-23
updated: 2026-09-28
refs:
  - d44e implementer 2026-09-23
---

Found by the d44e implementer 2026-09-23: dev-flow's plugin.json description and its marketplace.json entry already differed before d44e (the marketplace entry lacks the create-repo and sandbox soft-dependency clauses). d44e added the same operator-interaction clause to both but left the rest. Acceptance: the two descriptions match (house rule: the marketplace entry equals plugin.json's).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
librarian decision: built with e115 on worktree-claude-analytics-is-live-drop-planned-fr-e115 (same files); recorded there
