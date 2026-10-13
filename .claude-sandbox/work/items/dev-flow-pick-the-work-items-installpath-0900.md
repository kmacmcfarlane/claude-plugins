---
id: dev-flow-pick-the-work-items-installpath-0900
title: "dev-flow: pick the work-items installPath by scope, not [0]"
type: bug
status: todo
priority: 3
created: 2026-09-21
updated: 2026-09-21
refs:
  - d8f6 implementer
---

Surfaced by d8f6's implementer 2026-09-21: plugins/dev-flow/skills/dev-cycle/references/bindings.md:~154 and librarian-mode/references/troubleshooting.md:~57,62 resolve the installed work-items plugin with [0].installPath; the first entry may be another project's install. Mirror context-guard operator-playbook's scope pick (local/project whose projectPath contains cwd, deepest first, local before project; else user; else the data-dir fallback).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree branch off main (9b5d12b2); dev-cycle references/bindings.md, librarian-mode references/troubleshooting.md
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — work-items installPath by scope
agent: implementer a443ccb5718184cbe round 1
result: DONE round 1 at 356dc506 (scope pick in bindings.md § Store, its kit-dev and context-guard lookups, research intensity-and-routing.md, librarian troubleshooting.md, and the same bug in context-guard checkpoint SKILL.md and ralph backlog-yaml SKILL.md; snippet test picks the user install over another project's; suites OK)
dispatch: reviewer opus high — fresh (rule 4)
