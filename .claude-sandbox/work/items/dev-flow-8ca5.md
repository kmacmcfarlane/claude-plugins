---
id: dev-flow-8ca5
title: Extract dev-flow plugin (investigate, implement, deep-investigation, cove)
type: refactor
status: done
priority: 2
deps:
  - doctrine-9411
parent: plugin-factoring-924b
created: 2026-09-02
updated: 2026-09-02
closed: 2026-09-02
---

Move the plan-first lifecycle: investigate, implement, deep-investigation, plus chain-of-verification as its verification technique. Retire implement-plan and the three agents (fullstack-developer, plan-architect, plan-reviewer) - only the deprecated skill uses them. The .claude-sandbox/investigations/ path convention stays (directory name only, no sandbox dependency). Pure skill move, no state migration.

## Handoff
- doing: implemented, pending review
- next: fable review, then wi done
- blocked: —
- learned: —

## Notes
- 2026-09-02 claimed by unknown@e7c6135255e0
- 2026-09-02 done: e8f8fd7; fable review APPROVED (should-fix routed to kit-dev-refit-0e21); claude plugin validate PASS
