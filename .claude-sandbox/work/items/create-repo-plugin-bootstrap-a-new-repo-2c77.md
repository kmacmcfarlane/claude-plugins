---
id: create-repo-plugin-bootstrap-a-new-repo-2c77
title: "create-repo plugin: bootstrap a new repo and launch an attachable agent session on it"
type: feature
status: todo
priority: 2
created: 2026-09-19
updated: 2026-09-19
refs:
  - "peer: claude-sandbox-93 (uds 91.sock), operator relay"
---

Operator request 2026-09-19, relayed by peer claude-sandbox-93. New plugin create-repo with a skill: mkdir + git init -b main + seed README naming the purpose; claude-sandbox init --yes (inherits workspace config); initial commit; launch a session with a bootstrap prompt (write CLAUDE.md /init-style, then the thread's first investigation); tell the user the copy-paste attach command (cd <repo> && claude-sandbox --attach). Ecosystem support where needed. Rough edges (claude-sandbox side, tracked in its store, e.g. detached launch f9dc): no detached mode yet, so a launch under the agent's pty dies with the launching session; until --detach, prefer one copy-paste command that launches AND attaches in the user's terminal; in-sandbox launch needs host-visible TMPDIR; launch lock is per-container. Principle notes: marketplace shape (catalog row, CLAUDE.md layout, marketplace.json in the same feature); overlaps kit-dev new-project-from-template; claude-sandbox is a soft dependency (degrade to plain claude).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

decision 43: placement — (a) new plugin create-repo as asked, with new-project-from-template (kit-dev) left as is and cross-noted [recommended: the operator named it; catalog row first]; (b) new plugin create-repo that also absorbs kit-dev new-project-from-template (one aim: start a new repo); (c) a skill in the sandbox plugin instead of a new plugin.

## Operator answer 2026-09-19
- 43 → (a) new plugin create-repo; kit-dev new-project-from-template stays, cross-pointed. PLUS: an optional arg lets the user name a claude-templates template as the goal (via new-project-from-template), gated on a check that kit-dev is installed; if not, offer to install it with instructions (soft dependency, principle 4).
