---
id: dev-cycle-briefs-never-signal-processes-54fe
title: "dev-cycle briefs: never signal processes the agent did not start"
short_display_name: agents must not kill others' processes
type: bug
status: todo
priority: 1
created: 2026-09-30
updated: 2026-09-30
refs:
  - 819f implementer fix round 1, 2026-09-30
---

2026-09-30: the 819f implementer, stopping its own slow test run, sent SIGTERM to every process matching 'unittest discover -s tests' or 'scan-findings.py' (pkill absent), including other agents' check runs in the same container — the likely cause of the exit 143/144 Check kills other agents reported tonight. Acceptance: the implementer and reviewer brief prohibitions say never signal a process the agent did not start itself (kill by its own PID only, recorded when started; never by pattern); review-brief likewise.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
