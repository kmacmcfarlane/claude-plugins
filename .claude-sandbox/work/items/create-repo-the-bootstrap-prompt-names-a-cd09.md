---
id: create-repo-the-bootstrap-prompt-names-a-cd09
title: "create-repo: the bootstrap prompt names an existing investigation series to extend"
type: chore
status: doing
priority: 3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:52Z
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

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full create-repo-the-bootstrap-prompt-names-a-cd09 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/create-repo-the-bootstrap-prompt-names-a-cd09
dispatch: implementer opus — more than one plugin (create-repo + dev-flow investigate reference), rule 2
agent: implementer a30cdb20435f3ddd1 round 1
