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
