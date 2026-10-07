---
id: statusline-agent-panel-rows-show-each-su-7f91
title: "statusline agent-panel rows: show each sub-agent's model and effort beside its context fill"
short_display_name: sub-agent rows show model and effort
type: feature
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-07T20:36Z
created: 2026-10-07
updated: 2026-10-07
---

Operator 2026-10-07, verbatim: 'I'd like the status-line entries on sub-agents to show the model and effort too in addition to the context fill'. Acceptance: plugins/statusline/hooks/subagent_statusline.py renders each sub-agent row's model and effort alongside its context fill, from what the subagentStatusLine payload documents or what is observable (CLAUDE.md § Claude Code source material: observed with method and version, or the docs URL); where a field is absent, the row says nothing rather than guessing; tests.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-07 claimed by Kyle-McFarlane@2d49f8460283
target: full statusline-agent-panel-rows-show-each-su-7f91 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/statusline-agent-panel-rows-show-each-su-7f91
budget: 2026-10-07T20:36Z build $22 — default other build
dispatch: implementer opus medium — build (status-line hook code)
agent: implementer a4bd4861771a0bec2 round 1
