---
id: statusline-per-sub-agent-context-fill-vi-c0cc
title: "statusline: per-sub-agent context fill via subagentStatusLine (agent panel rows)"
type: feature
status: doing
priority: 2
owner: unknown@360f41058e92
claimed: 2026-09-21T22:57Z
created: 2026-09-21
updated: 2026-09-21
---

From spike 9f90 (series .claude-sandbox/investigations/9f90-subagent-statusline/00_findings.md). The footer can't follow the focused sub-agent; the agent panel's subagentStatusLine can show every agent's fill. Acceptance: a subagentStatusLine renderer in plugins/statusline (its aim is display) that prints each agent's context fill (exact depth from <session>/subagents/agent-<id>.jsonl, the same sum as context-guard's scan_usage — reuse its incremental read pattern; fall back to tokenCount/contextWindowSize, labelled approximate); shipped via the plugin's settings.json default if the docs allow it (verify precedence vs a user-set subagentStatusLine; never overwrite a user's); latency budget like the footer; tests; README/skill docs; a known-limitation line that the footer can't follow the focused agent (#76863). Check in-process teammates' ids against subagents/agent-<id>.jsonl.

## Handoff
- doing: implementer dispatched (opus, agent a2fc00d5652990edd)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Carried from spike 9f90 (closed)
decision 50: the drafted upstream issue (tell the statusLine which sub-agent is focused; draft in .claude-sandbox/investigations/9f90-subagent-statusline/00_findings.md) — (a) do not post; add the known-limitation line only [recommended: #76863 and #29766 were closed not_planned; subagentStatusLine covers the need]; (b) post the draft as a new issue from the operator's account.

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — executable logic (renderer) + a settings default; decision 50 (upstream issue) does not gate it: the known-limitation line ships either way

## Implementer result
- round 1 DONE_WITH_CONCERNS ff555d2 (opus): subagent_statusline.py renderer (exact from sidechain, incremental 8 MiB/tick, approx fallback labelled); plugin settings.json default subagentStatusLine via current-hooks link (${CLAUDE_PLUGIN_ROOT} not expanded there; user value always wins; no user settings write); prune; 24 tests; docs + #76863 limitation. Verified docs + binary 2.1.278; hand-run on a 10 MB sidechain.
- scope widened (librarian): CLAUDE.md layout line for statusline/hooks gets subagent_statusline + plugin settings.json (same-feature layout rule); catalog row left as is.
- dispatch: implementer opus — widening (same agent resumed), then reviewer opus
- widening DONE c1be970: CLAUDE.md layout lists subagent_statusline + plugin settings.json.
- dispatch: reviewer opus — rule 4
