---
id: dev-cycle-briefs-never-signal-processes-54fe
title: "dev-cycle briefs: never signal processes the agent did not start"
short_display_name: agents must not kill others' processes
type: bug
status: doing
priority: 1
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-06T01:27Z
created: 2026-09-30
updated: 2026-10-06
refs:
  - 819f implementer fix round 1, 2026-09-30
---

2026-09-30: the 819f implementer, stopping its own slow test run, sent SIGTERM to every process matching 'unittest discover -s tests' or 'scan-findings.py' (pkill absent), including other agents' check runs in the same container — the likely cause of the exit 143/144 Check kills other agents reported tonight. Acceptance: the implementer and reviewer brief prohibitions say never signal a process the agent did not start itself (kill by its own PID only, recorded when started; never by pattern); review-brief likewise.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-06 claimed by Kyle-McFarlane@401123cbad11
decided: files in scope are dev-cycle's agent-brief.md and review-brief.md (the planner variant inherits agent-brief's prohibitions); research lanes' own contracts are not in this bug's acceptance — class: scope
target: full dev-cycle-briefs-never-signal-processes-54fe /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/dev-cycle-briefs-never-signal-processes-54fe
dispatch: implementer opus medium — build (bug; a rule change in skill briefs is an opus signal)
agent: implementer ae90e6ef6c976e054 round 1
return: implementer DONE d7c0b22
changed:
  plugins/dev-flow/skills/dev-cycle/references/agent-brief.md — prohibition bullet after the stash bullet
  plugins/dev-flow/skills/dev-cycle/references/review-brief.md — same bullet after the wi bullet
dispatch: reviewer opus high — review round 1
agent: reviewer a835579d8152a3fc2 round 1
