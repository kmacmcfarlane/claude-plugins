---
id: rewrite-the-12-unsure-claude-code-lines-50c2
title: rewrite the 12 unsure Claude Code lines in three work items to the hint form
short_display_name: unsure internals lines, hint form
type: chore
status: todo
priority: 1
created: 2026-10-13
updated: 2026-10-13
refs:
  - audit-claude-sandbox-on-origin-for-claud-abb8
---

From the abb8 audit, 2026-10-13: 12 current-tree lines in d63e (29,40,59,64,84,87,90,97), 8ab6 (23,29) and e347 (23) state Claude Code facts with no observation method or quote short tool-contract text. Per CLAUDE.md rule 5 when unsure treat as internal: label each with how and on which version it was observed and its doc URL, or replace it with the 'can be derived from Claude Code's internals' hint form, or delete it. Store text only; pushed with the next store push.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree branch off main (832cec4f); store text only (items d63e, 8ab6, e347)
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — rewrite 12 unsure lines to hint or labelled form (CC source rule)
agent: implementer a7b933fa8b09ebdba round 1
