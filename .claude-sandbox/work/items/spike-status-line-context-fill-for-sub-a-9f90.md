---
id: spike-status-line-context-fill-for-sub-a-9f90
title: "spike: status line context fill for sub-agents when switched to in the TUI"
type: spike
status: done
priority: 2
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
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
- 2026-09-21 done: .claude-sandbox/investigations/9f90-subagent-statusline/ (follow-ups filed)

## Dispatch
- dispatch: researcher opus — judgement on harness internals (binary reading); series .claude-sandbox/investigations/9f90-subagent-statusline/

## Result
- research DONE (opus): .claude-sandbox/investigations/9f90-subagent-statusline/00_findings.md. The footer statusLine cannot follow the focused sub-agent: its input is built from the main conversation only (no agent_id), a view switch doesn't re-run it, and no hook or file records which agent is focused (binary 2.1.278 strings + docs; issue #76863 closed not_planned). What works: the separate `subagentStatusLine` setting renders each agent's row in the agent panel (visible while viewing it), with per-agent id/model/contextWindowSize/tokenCount; exact depth from <session>/subagents/agent-<id>.jsonl (tokenCount overstates). A plugin can ship subagentStatusLine in its own settings.json (no user-settings write).
- decision (librarian): the per-agent renderer belongs in `statusline` (its aim is the display), shipped via the plugin's settings.json default — verify precedence against a user-set value first.
decision 50: the drafted upstream issue (tell the statusLine which sub-agent is focused) — (a) don't post; add the known-limitation line only [recommended: #76863/#29766 were closed not_planned; subagentStatusLine covers the need]; (b) post the draft as a new issue from your account.
