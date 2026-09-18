---
id: relay-to-claude-sandbox-librarian-init-s-5b76
title: "relay to claude-sandbox librarian: init seeds env.example only; warn when project env shadows upstream"
type: chore
status: todo
priority: 1
created: 2026-09-18
updated: 2026-09-18
refs:
  - peer kappa-3446 implement
---

Peer 'kappa-3446 implement', 2026-09-18. A claude-sandbox change (product code there, NOT custody here), so this item only relays it to the claude-sandbox librarian, which is offline. Ask: (1) claude-sandbox init writes .claude-sandbox/env.example, never a real env; (2) a project-level .claude-sandbox/env stays supported but is never auto-created; (3) on startup, print one line when a project env shadows an upstream one (the silent precedence is the defect); (4) fix the env header comment, which names .env.claude-sandbox in the project root instead of .claude-sandbox/env. Cost observed: an upstream GitLab token (path and key only) was refreshed 4 times with no effect because a project env dated 2026-06-23 shadowed it. Verification: init in a fresh project leaves no env; a token set only upstream reaches the container. Full write-up: /home/rt/work/src/git.sussexdirectories.com/sussex/communications/email/.claude/scratch/KAPPA-3446/librarian_request_sandbox_env.md. Close when delivered, or when the operator files it there.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
