---
id: dev-cycle-briefs-name-the-harness-s-own-02f8
title: "dev-cycle briefs: name the harness's own background-task stop as a way to stop your own process"
short_display_name: allow stopping own background tasks
type: chore
status: done
priority: 2
created: 2026-10-06
updated: 2026-10-13
closed: 2026-10-13
refs:
  - dev-cycle-briefs-never-signal-processes-54fe
---

54fe review low 1, 2026-10-06: the briefs allow stopping your own process only by recorded PID ($! after a background start); a check started with the Bash tool's run_in_background gets a task id, and the harness stop (TaskStop) is not named, so read literally an agent has no permitted way to stop its own hung run and may reach for ps|grep. Acceptance: agent-brief.md and review-brief.md prohibitions name the harness's stop for a task the agent started as permitted, alongside the PID route; also say the rule holds with or without a container (54fe nit 2).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree branch off main (9b5d12b2); dev-cycle references (brief templates)
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — name the harness background-task stop in the briefs
agent: implementer afb8e096c07e9f442 round 1
result: DONE round 1 at f4556ea8 (TaskStop documented at tools-reference; rule in agent-brief.md, copies in review-brief.md and the three research agents kept identical by new test_stop_rule.py; CLAUDE.md layout; 82 OK)
dispatch: reviewer opus high — fresh (rule 4)
agent: reviewer a6951ae94aef48795 round 1 at f4556ea8
verdict: CLEAR round 1 at f4556ea8 (low 1: widen the ban to agents and teammates and to listings in /tasks or an error; low 2 no fix needed; nits: test every copy across the plugin, backticked names)
decided: 2026-10-13T22:29Z cap — low 1 and nits 3-4 with exact wording: one finish round, read by the librarian (authority answer 145)
dispatch: implementer opus medium — resume, finish round
agent: implementer afb8e096c07e9f442 round 2 (finish)
result: DONE finish at a31fed02 (exact; test_no_unlisted_copy added; diff read by the librarian)
verdict: CLEAR after 1 finish at a31fed02

## Notes
- 2026-10-13 done
