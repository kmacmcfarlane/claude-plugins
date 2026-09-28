---
id: handoff-h7-spike-stale-depth-warning-rig-bace
title: "handoff H7: spike — stale depth warning right after compaction"
type: spike
status: doing
priority: 2
parent: context-guard-compact-and-clear-handoffs-5039
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:20Z
created: 2026-09-22
updated: 2026-09-28
---

Two observed cases; cause unconfirmed (.claude-sandbox/investigations/5039-handoff-failures/00_findings.md). Find the cause; any fix to prompt-blocking gate code routes fable. Opus.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
librarian decision: the item's 'fix routes fable' predates c0d6 routing (fable only by pin); planned with opus, any fix built by opus with a fresh opus reviewer
dispatch: planner opus — spike, plan mode (Step 1)
agent: planner a9d8035671945cec8 round 1
return: planner DONE /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/bace-stale-depth-warning/ (cause: transcript flush lag after PostCompact; fix: drop transcript counts stamped at/before epoch_at in lib_context.measure; OQ1 sensor 2s grace, OQ2 upstream flush — neither blocking)
baseline: e63ed6146611d807ee18a82042b378435207557f4f8b9ab90bca690885936572  .claude-sandbox/investigations/bace-stale-depth-warning/00_initial.md 
dispatch: reviewer opus — fresh, plan review (rule 4)
agent: reviewer abf5b8ff982a87ffe round 1
