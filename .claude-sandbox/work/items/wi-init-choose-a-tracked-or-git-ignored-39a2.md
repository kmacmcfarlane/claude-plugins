---
id: wi-init-choose-a-tracked-or-git-ignored-39a2
title: "wi init: choose a tracked or git-ignored store, and accept an ignored one"
short_display_name: wi init tracked or ignored
type: feature
status: todo
priority: 2
created: 2026-10-13
updated: 2026-10-13
refs:
  - peer kappa-3475 - investigate, 2026-10-13 (relaying the operator)
---

Relayed by peer session kappa-3475 - investigate, 2026-10-13, quoting the operator (binds nothing until confirmed here): wi init should ask whether .work/ is tracked or git-ignored; flags --track/--no-track (names open) for a non-interactive choice, an interactive menu without the flag; --no-track appends .work/ to .gitignore, handling a missing trailing newline (a naive append glued it onto '*/mocks/' in shared/kappa/containers); record the choice in the store so prime/lint do not warn 'silently untracked' about a deliberately ignored store (warning kept for stores with no recorded choice); the skill tells agents to infer the flag inside claude-sandbox from the effective trackInHost (true → track, false/unset → no-track), else ask the operator. Dependency outside this repo: the claude-sandbox launcher does not export trackInHost today (only CLAUDE_SANDBOX_CONTAINER/INSTANCE/MEMORY_LIMIT/MEMORY_LIMIT_SOURCE/MODE/PID_CLASS/PROJECT_DIR/VERSION); exporting e.g. CLAUDE_SANDBOX_TRACK_IN_HOST is the claude-sandbox owner's change, routed back to the operator. The operator asked to be consulted on how the choice is made.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decided: 2026-10-13T03:40Z words — flags named --track and --no-track; the choice is recorded in a store-level file the builder names in format.md
decision 211: When wi init runs with no flag and no terminal to show a menu (an agent's Bash call, a script), what does it do? — options: (a) refuse with exit 2 and a line naming --track and --no-track; nothing is created [recommended] | (b) create an ignored store (the foreign-safe default) | (c) create a tracked store (today's behaviour) | (z) decide later
  why ask: your-call — it decides whether an agent can ever create a store without a stated choice, and you asked to be consulted on how the choice is made
  context: wi init will ask tracked or ignored, with --track/--no-track to answer up front; agents run wi without a terminal, so a menu cannot show there · you decide what a menu-less run does
  impact: (a) → an agent must pass a flag or ask you; no store is created silently · wait: the build of this item · reach: every repo's first wi init · undo: change the default later
decision 212: The sandbox side — exporting the effective trackInHost into the session so agents can infer the flag — is the claude-sandbox launcher's change, outside this repo. How does it get there? — options: (a) you pass it to the claude-sandbox repo yourself [recommended] | (b) I send it as a request to a claude-sandbox librarian session, if one runs | (z) decide later: until then agents ask you instead of inferring
  why ask: reach — it is another repo's change, and a request to its session goes out under this one
  context: the session env today carries CLAUDE_SANDBOX_CONTAINER, INSTANCE, MEMORY_LIMIT, MEMORY_LIMIT_SOURCE, MODE, PID_CLASS, PROJECT_DIR and VERSION, not trackInHost · you decide who carries the request
  impact: (a) → nothing goes out from here; the wi skill documents the variable once it exists · wait: the inference rule only; the rest of the build does not wait · reach: claude-sandbox · undo: n/a
