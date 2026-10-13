---
id: statusline-agent-panel-rows-show-the-age-edec
title: "statusline: agent-panel rows show the agent profile, model and effort after the title, before the (id)"
short_display_name: agent profile on panel rows
type: feature
status: todo
priority: 2
created: 2026-09-30
updated: 2026-09-30
refs:
  - operator 2026-09-30 chat
---

Operator 2026-09-30: 'the status line for sub-agents includes the agent profile, model, and effort after the title (but before the id in parans)'. Acceptance: each sub-agent row (plugins/statusline/hooks/subagent_statusline.py, the subagentStatusLine setting) renders <title> <profile> <model> <effort> (<id>) — profile being the role agent (e.g. dev-flow:reviewer), model and effort as the agent runs; a field the payload lacks is left out, never guessed; tests in plugins/statusline/hooks/tests.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
