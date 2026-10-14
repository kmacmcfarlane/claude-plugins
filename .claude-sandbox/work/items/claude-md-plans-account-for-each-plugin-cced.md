---
id: claude-md-plans-account-for-each-plugin-cced
title: "CLAUDE.md: plans account for each plugin standing alone; statusline-hub the named hard dependency"
short_display_name: standalone plugins rule in CLAUDE.md
type: chore
status: todo
priority: 1
created: 2026-10-14
updated: 2026-10-14
refs:
  - answer 214, answer page 2026-10-14
---

Operator 2026-10-14 (answer 214's words): CLAUDE.md needs clear guidance that all architecture and implementation plans account for stand-alone functionality of plugins with graceful degradation where cross-plugin integration is implemented; a notable exception is statusline-hub, a hard dependency for context-guard (and claude-analytics). Acceptance: one rule in CLAUDE.md (README principle 4 holds the doctrine; point, do not restate), naming the planning duty and the hard-dependency exception; dev-cycle's plan review checks it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree off main (f4be55ec); CLAUDE.md, dev-cycle review checklist
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — standalone-plugin planning rule, hard-dependency exception (answer 214's words)
agent: implementer a2a82bfb91a481366 round 1
