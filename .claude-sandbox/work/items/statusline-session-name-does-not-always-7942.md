---
id: statusline-session-name-does-not-always-7942
title: "statusline: session name does not always match /rename or an agent-set name"
type: bug
status: doing
priority: 3
deps:
  - statusline-progress-bars-for-session-fab-28ad
owner: unknown@4d338747396e
claimed: 2026-09-16T18:04Z
created: 2026-09-16
updated: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator 2026-09-16: the session name shown by hooks/statusline.py does not always match what /rename set, or a name the agent set itself. Investigate first: which payload key(s) Claude Code sends (session_name? a nested session object? does it change after /rename without a re-render? is the agent-set name a different field?), read the statusline docs and check a live payload capture; then fix statusline.py to prefer the current name with a fallback chain, and add tests. Depends on 28ad (same file). Harness file -> fable (rule 3).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
dispatch: implementer fable — rule 3 (harness file hooks/statusline.py); research step included in the brief
dispatch: reviewer fable — rule 4
