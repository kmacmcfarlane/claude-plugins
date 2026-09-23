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
return: implementer DONE 961d85d
changed: create-repo SKILL.md (Steps 1, 7), references/launch-command.md (series variant), investigate references/investigation-format.md (§ A repo not yet created)
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer aab96e77dfa957a52 round 1
verdict: NEEDS_CHANGES round 1 at 961d85d
findings:
- [medium] launch-command.md:42 — SLUG/OLD "get the same handling below" but the newline-collapse rule is above (:22); an OLD with a newline + an EOF line breaks out of the heredoc and runs a command (reproduced). Pass: validate like NAME/REPO — SLUG kebab-case ^[a-z0-9][a-z0-9-]*$, OLD through Step 2's path-character check; otherwise ask again.
- [medium] investigation-format.md:59 — a dev-flow → sandbox skill reference undeclared in dev-flow's plugin.json and README catalog row (principle 4); two older undeclared pointers too (deep-investigation SKILL.md:242, investigate edge-cases.md:25). Librarian: scope widened to declare sandbox (soft) in dev-flow's plugin.json description and README row.
- [low] :57-70 ask-before-commit vs "under an orchestrator never asked" — one clause on which wins; [low] :60 "the sandbox skill says" widens the SOP — say it follows the same rule.
dispatch: implementer opus — fix round 1 (resume)
agent: implementer a30cdb20435f3ddd1 round 2
return: implementer DONE e430605
changed: + plugins/dev-flow/.claude-plugin/plugin.json (sandbox soft, 1022 chars), README.md (dev-flow row + prose)
dispatch: reviewer opus — review r2 (resume)
agent: reviewer aab96e77dfa957a52 round 2
