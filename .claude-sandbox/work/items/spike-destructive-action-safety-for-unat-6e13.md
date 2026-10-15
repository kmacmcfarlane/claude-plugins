---
id: spike-destructive-action-safety-for-unat-6e13
title: "spike: destructive-action safety for unattended agents (dangerous-rm sub-agent stalls, recoverable deletes)"
short_display_name: permission pop-up and delete safety
type: spike
status: todo
priority: 1
created: 2026-10-15
updated: 2026-10-15
refs:
  - operator message 2026-10-15; .claude-sandbox/temp/spike-agent-deletion-safety.md
---

Operator 2026-10-15: dropped .claude-sandbox/temp/spike-agent-deletion-safety.md to file as a work item for the tool permission pop-ups (dangerous-rm prompts stalling sub-agents with no auto-deny) and recoverable deletes. Workstreams E1-E7; E1 (stop the stall, deny hook) highest. Acceptance per the doc section 7. Overlaps b2df's guard hook (decisions 233-239). Launcher snapshots (E2) and OpenCode parity (E7) likely belong to claude-sandbox.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
brief: the operator's spike doc copied to .claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13/brief-operator-spike.md (temp/ is scratch)
decided: plan mode first (spike); experiments that need nested claude runs (E1 steps 1, 3, 5) wait for the operator, per the standing rule; desk research, design and harmless local probes proceed
dispatch: planner opus high — spike plan, E1 first; fold b2df guard-hook overlap; placement of the hook
agent: planner a17fe67421b5a97f3 plan round 1
return: planner DONE .claude-sandbox/investigations/spike-destructive-action-safety-for-unat-6e13 (00_initial.md; E1 = L1 PermissionRequest backstop + L2 PreToolUse predictor R1-R6; home: new hook plugin shell-guard; merge b2df guard as a second rule pack (234 moot); OQ1-OQ9; unverified: L1 firing in sub-agents, hook deny under bypass, agent_id in input)
baseline: 77165043a85c70a4e8c46e5edaa7bf1b318815c5e8f2cd655220d19f0c4f8f56  00_initial.md 793399525965e9c1965ca5dce53cb3ecc4f7dae72a200064d547b3ab2450e126  INDEX.md 
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer afdc46fe247e2b56b plan round 1
