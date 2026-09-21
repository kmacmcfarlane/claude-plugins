---
id: spike-status-line-context-fill-for-sub-a-9f90
title: "spike: status line context fill for sub-agents when switched to in the TUI"
type: spike
status: doing
priority: 2
owner: unknown@360f41058e92
claimed: 2026-09-21T19:43Z
created: 2026-09-21
updated: 2026-09-21
refs:
  - operator 2026-09-21
---

Operator 2026-09-21: our status line does not show the context fill for sub-agents when the operator switches to them in the Claude Code TUI. Is it possible? Acceptance: sourced findings (docs, changelog, issues, and read-only strings in the 2.1.27x binary) on (1) whether the statusLine command runs, and with what stdin, while a sub-agent / teammate view is focused; (2) whether the payload identifies the viewed agent (agent_id, transcript path, context_window) or only the main session; (3) any other source for a sub-agent's live depth (sidechain transcript usage lines — context-guard already scans sidechains); (4) a recommendation: feasible now (and how, in statusline / statusline-hub), feasible by deriving from the sidechain transcript, or not possible (known limitation + upstream issue).

## Handoff
- doing: research agent (opus) running
- next: report the answer; file follow-ups
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: researcher opus — judgement on harness internals (binary reading); series .claude-sandbox/investigations/9f90-subagent-statusline/
