---
id: sandbox-skill-verify-and-document-whethe-cb11
title: "sandbox skill: verify and document whether a worktree session can run git -C on the main checkout"
type: spike
status: todo
priority: 3
created: 2026-09-24
updated: 2026-09-24
refs:
  - "peer: mcfacehead-plugins - librarian (session clustertool-c3)"
---

Reported 2026-09-24 by mcfacehead-plugins - librarian, relaying session clustertool-c3's live observation (2026-09-22/23). UNVERIFIED: (1) the checkout guard ('Enter a worktree first') blocks Edit/Write on tracked files in a main checkout while git via Bash in that checkout still works; the mcfacehead reviewer confirmed this against plugins/sandbox/hooks/checkout_guard.py (only Edit, Write, MultiEdit and NotebookEdit, when cwd is a main checkout; it skips .claude-sandbox/ and .claude/). (2) From inside a worktree session, 'git -C <main checkout>' is refused. Neither checkout_guard.py nor the sandbox skill's § The Worktree Convention documents (2), and the claude-sandbox docs suggest Bash into the main checkout works from a worktree, so the report and the docs may disagree. Acceptance: reproduce (2) in a worktree session and identify which layer refuses it (the harness's own worktree guard, a permission rule, or this plugin); then record the true behaviour in the sandbox skill's § The Worktree Convention, with its source. The mcfacehead clustertool skill already points at that section.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
