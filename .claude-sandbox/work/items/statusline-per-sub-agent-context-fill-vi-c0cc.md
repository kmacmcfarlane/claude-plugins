---
id: statusline-per-sub-agent-context-fill-vi-c0cc
title: "statusline: per-sub-agent context fill via subagentStatusLine (agent panel rows)"
type: feature
status: todo
priority: 2
created: 2026-09-21
updated: 2026-09-21
---

From spike 9f90 (series .claude-sandbox/investigations/9f90-subagent-statusline/00_findings.md). The footer can't follow the focused sub-agent; the agent panel's subagentStatusLine can show every agent's fill. Acceptance: a subagentStatusLine renderer in plugins/statusline (its aim is display) that prints each agent's context fill (exact depth from <session>/subagents/agent-<id>.jsonl, the same sum as context-guard's scan_usage — reuse its incremental read pattern; fall back to tokenCount/contextWindowSize, labelled approximate); shipped via the plugin's settings.json default if the docs allow it (verify precedence vs a user-set subagentStatusLine; never overwrite a user's); latency budget like the footer; tests; README/skill docs; a known-limitation line that the footer can't follow the focused agent (#76863). Check in-process teammates' ids against subagents/agent-<id>.jsonl.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
