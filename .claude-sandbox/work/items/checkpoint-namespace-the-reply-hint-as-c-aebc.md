---
id: checkpoint-namespace-the-reply-hint-as-c-aebc
title: "checkpoint: namespace the reply hint as /context-guard:checkpoint so it pastes"
short_display_name: checkpoint reply hint namespaced
type: bug
status: todo
priority: 1
created: 2026-10-09
updated: 2026-10-09
refs:
  - operator message 2026-10-09
---

Operator 2026-10-09: the pasteable reply line the checkpoint skill drafts (Step 0) starts '/checkpoint', which collides with a built-in command of the same name, so it does not run the skill when pasted. Acceptance: every reply line, opener and example the checkpoint skill (and context-guard docs, librarian-mode's references to it) tells an agent to print uses '/context-guard:checkpoint'; a test pins it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
