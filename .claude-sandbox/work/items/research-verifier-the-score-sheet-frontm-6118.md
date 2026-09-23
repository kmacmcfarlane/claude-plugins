---
id: research-verifier-the-score-sheet-frontm-6118
title: "research-verifier: the score-sheet frontmatter puts five counts on one line, so strict YAML rejects it"
type: bug
status: todo
priority: 2
created: 2026-09-23
updated: 2026-09-23
refs:
  - "peer: agent-research - librarian (item 7e28)"
---

Reported by agent-research - librarian (from its lint build, item 7e28), 2026-09-23, against dev-flow 7f80e306a424: in plugins/dev-flow/agents/research-verifier.md the verification.md frontmatter template reads 'supported: <n>   partial: <n>   contradicted: <n>   not_found: <n>   unreachable: <n>' on one line. A strict YAML loader (ruamel safe) rejects it with 'mapping values are not allowed here', so every verification.md copied from the template fails strict parsing (this session's two 7113 runs show it). Acceptance: one count per line (or a flow mapping) in the template, plus any reference that repeats it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
