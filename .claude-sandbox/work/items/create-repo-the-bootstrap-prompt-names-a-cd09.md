---
id: create-repo-the-bootstrap-prompt-names-a-cd09
title: "create-repo: the bootstrap prompt names an existing investigation series to extend"
type: chore
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - fc02 review r1
---

fc02 review r1, 2026-09-22: when an investigation moves to a repo create-repo is making, the launched session's bootstrap prompt (references/launch-command.md) says 'run the thread's first investigation' and starts a fresh series. Acceptance: when the caller hands create-repo an existing series path, the prompt names it and says to extend it (next serial), not start a new 00.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- riders from fc02 review r2 (2026-09-22): investigation-format.md § A repo not yet created — name the sidecar as <new-repo>/.claude-sandbox/'s own git and whether to ask before committing there (sandbox skill sidecar SOP); say whether the old home's INDEX.md Moved-to note is committed alongside.
