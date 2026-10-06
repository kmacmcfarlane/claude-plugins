---
id: dev-cycle-briefs-name-the-harness-s-own-02f8
title: "dev-cycle briefs: name the harness's own background-task stop as a way to stop your own process"
short_display_name: allow stopping own background tasks
type: chore
status: todo
priority: 2
created: 2026-10-06
updated: 2026-10-06
refs:
  - dev-cycle-briefs-never-signal-processes-54fe
---

54fe review low 1, 2026-10-06: the briefs allow stopping your own process only by recorded PID ($! after a background start); a check started with the Bash tool's run_in_background gets a task id, and the harness stop (TaskStop) is not named, so read literally an agent has no permitted way to stop its own hung run and may reach for ps|grep. Acceptance: agent-brief.md and review-brief.md prohibitions name the harness's stop for a task the agent started as permitted, alongside the PID route; also say the rule holds with or without a container (54fe nit 2).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
