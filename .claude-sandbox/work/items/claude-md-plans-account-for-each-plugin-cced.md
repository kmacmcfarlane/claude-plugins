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
result: DONE round 1 at 74f4c1cc (CLAUDE.md Conventions bullet; review-brief plan-review item 5); conflict: README principle 4 forbids a reader being hard and a hard edge outside the marketplace, so the exception is recorded but not declared
decision 217: README principle 4 forbids both hard dependencies you named: context-guard only reads the hub's data, and a plugin that merely reads another's data must keep a fallback; claude-analytics is outside this marketplace, and hard edges must stay within it. How should principle 4 change? — options: (a) amend principle 4: a reader may be declared hard when the operator names the edge, and a hard edge may point at a named external plugin; then declare context-guard → statusline-hub hard [recommended] | (b) keep principle 4; the CLAUDE.md rule records your exception as intent only, and no edge is declared hard | (c) amend for statusline-hub only (inside the marketplace), leave claude-analytics soft until it joins this marketplace | (z) decide later: the rule lands as built (intent recorded, nothing declared)
