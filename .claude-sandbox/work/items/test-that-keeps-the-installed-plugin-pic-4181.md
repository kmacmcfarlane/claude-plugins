---
id: test-that-keeps-the-installed-plugin-pic-4181
title: test that keeps the installed-plugin pick snippets identical and runs their edge cases
short_display_name: install pick snippet test
type: chore
status: todo
priority: 3
created: 2026-10-13
updated: 2026-10-13
refs:
  - dev-flow-pick-the-work-items-installpath-0900
---

From 0900 review 2026-10-13: six copies of the scope pick (dev-cycle bindings.md x3, research intensity-and-routing.md, context-guard checkpoint SKILL.md, ralph backlog-yaml SKILL.md) have no test. Acceptance: a dev-flow test extracts each <<'PY' body from the dev-flow copies, asserts they are byte-identical, and runs them against records for path boundary, symlink, trailing slash, several locals, missing projectPath and malformed input; other plugins' copies per the standalone rule.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
