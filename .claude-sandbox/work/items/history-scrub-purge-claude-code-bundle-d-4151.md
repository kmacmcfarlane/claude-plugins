---
id: history-scrub-purge-claude-code-bundle-d-4151
title: "History scrub: purge Claude Code bundle-derived content from git history, then force-push"
short_display_name: history scrub of bundle content
type: spike
status: todo
priority: 0
deps:
  - review-claude-code-bundle-derived-conten-e347
created: 2026-10-06
updated: 2026-10-06
refs:
  - operator 2026-10-06, decision 164
---

Operator 2026-10-06 on decision 164: 'I want to perform the history scrub of this content to stay compliant with copyright.' One-way and outward: every sha from 2026-09-19 on changes (the store's recorded landed: shas, parked worktree branches, other clones, peer references); origin needs a force-push, which librarian-mode forbids itself; GitHub may keep unreferenced commits reachable by sha until GC or a support request. Acceptance: a plan (passages to purge, tool such as git filter-repo, pre/post verification, what happens to worktrees, the store and other clones, the GitHub cache step) and a one-way decision before anything runs; runs only after the scrub build (e347) lands.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
