---
id: trim-librarian-mode-skill-md-back-under-b176
title: trim librarian-mode SKILL.md back under its size line
short_display_name: trim librarian-mode SKILL.md
type: chore
status: todo
priority: 3
created: 2026-10-13
updated: 2026-10-13
refs:
  - librarian-mode-route-out-of-scope-work-t-3460
---

From 3460 review 2, 2026-10-13: librarian-mode SKILL.md is 26,933 chars (~6.7k tokens) after 3460 against the review checklist's ~5000-token line; main was already over (25,261) and the earlier trim item 1420 is closed. Acceptance: move procedure detail into references behind pointers until SKILL.md is near the line, no rule dropped, every pointer resolving.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree branch off main (832cec4f); plugins/dev-flow/skills/librarian-mode/{SKILL.md,references/*}
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — move procedure detail from SKILL.md into references, no rule dropped
agent: implementer a593c50487cfe0983 round 1
result: DONE round 1 at 7387a873 (SKILL.md 26,836 → 14,887 chars; new references rehydrate, intake, cycle-bindings, report; dev-flow 78, kit-dev 21, context-guard hooks 731 OK)
dispatch: reviewer opus high — fresh (rule 4), review 7387a873 against main: no rule dropped, pointers resolve
agent: reviewer a1a195df2772e8418 round 1 at 7387a873
verdict: NEEDS_CHANGES round 1 at 7387a873 (1 medium: Critical push bullet lost the abort-and-no-other-commit-to-main rule; lows: incoming: timing in two homes, dev-cycle bindings.md:34,651 pointers lack the sibling name, Ground/Terminal lines drop the other-base exception; nits: rehydrate.md restates, Intake 3 line-form pointer, rewraps; no rule dropped, pointers resolve, tests green)
dispatch: implementer opus medium — resume, fix round 1
agent: implementer a593c50487cfe0983 round 2
