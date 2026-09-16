---
id: librarian-branching-dcf3
title: Decide worktree/branch strategy for librarian-delegated work
type: spike
status: done
priority: 2
tags: [kit-dev]
created: 2026-09-04
updated: 2026-09-04
closed: 2026-09-04
---

Operator is unsure whether feature branches + worktrees fit the librarian workflow (worktree per background feature agent vs. shared checkout; who merges; whether the librarian's own checkout is the integration view). Decide and record in the librarian-mode skill / decision log. Depends on the librarian-mode design conversation.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-04 done: Decided 2026-09-04: feature agents in .claude/worktrees/<name> on worktree-<name> branches off main; librarian reviews, merges into local main, deletes branch+worktree; operator reviews landed changes and decisions; nothing pushed without operator say-so.
