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
