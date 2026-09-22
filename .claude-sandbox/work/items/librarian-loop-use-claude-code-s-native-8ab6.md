---
id: librarian-loop-use-claude-code-s-native-8ab6
title: "librarian loop: use Claude Code's native /loop (and CronCreate / ScheduleWakeup) to drive the librarian's idle turn"
type: spike
status: todo
priority: 2
parent: librarian-work-unblocked-items-and-pre-i-1222
created: 2026-09-22
updated: 2026-09-22
refs:
  - operator 2026-09-22
---

Operator 2026-09-22: 'perhaps we should be using the native claude code loop feature to help drive the librarian loop?' Investigate how /loop (dynamic and interval modes), ScheduleWakeup and cron routines relate to 1222's idle-turn design (F2 self-wake, quiet mode, stop), what each can and cannot do (does a loop tick survive compaction? does it re-enter the skill? how does it interact with background agents, peer messages and the context gate?), and what librarian-mode should adopt vs keep. Output: findings + a recommendation, factored items if adopted.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
