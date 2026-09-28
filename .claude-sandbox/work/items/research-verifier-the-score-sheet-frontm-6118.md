---
id: research-verifier-the-score-sheet-frontm-6118
title: "research-verifier: the score-sheet frontmatter puts five counts on one line, so strict YAML rejects it"
type: bug
status: doing
priority: 2
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:46Z
created: 2026-09-23
updated: 2026-09-28
refs:
  - "peer: agent-research - librarian (item 7e28)"
---

Reported by agent-research - librarian (from its lint build, item 7e28), 2026-09-23, against dev-flow 7f80e306a424: in plugins/dev-flow/agents/research-verifier.md the verification.md frontmatter template reads 'supported: <n>   partial: <n>   contradicted: <n>   not_found: <n>   unreachable: <n>' on one line. A strict YAML loader (ruamel safe) rejects it with 'mapping values are not allowed here', so every verification.md copied from the template fails strict parsing (this session's two 7113 runs show it). Acceptance: one count per line (or a flow mapping) in the template, plus any reference that repeats it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-research-verifier-the-score-sheet-frontm-6118 at .claude/worktrees/research-verifier-the-score-sheet-frontm-6118, base main (b29422b)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer sonnet — template format fix, no behaviour change (rule 1)
agent: implementer aef8403cde4873f81 round 1
