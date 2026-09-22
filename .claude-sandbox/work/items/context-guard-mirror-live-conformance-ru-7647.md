---
id: context-guard-mirror-live-conformance-ru-7647
title: "context-guard mirror: live conformance run + playbook note on hand-run hooks"
type: chore
status: todo
priority: 3
created: 2026-09-19
updated: 2026-09-22
---

From the d63e final review (2026-09-19): never verified live — (1) the plan's claude -p conformance run (derived window vs the status line's context_window_size across opus-5, opus-5[1m], haiku-4-5, DISABLE_1M), (2) interactive /model switching firing PostModelSwitch, (3) whether a long_context_credits_required api error is written to the transcript. Also add one playbook line: a hook script hand-run from a session's Bash tool against the real config dir is verified as that session and can write its latch — use a scratch CLAUDE_CONFIG_DIR.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Groom 2026-09-21
decision 46: live conformance needs real `claude -p` runs (opus-5, opus-5[1m], haiku-4-5, DISABLE_1M) on the operator's credentials and quota — (a) an agent runs ~8 short -p calls from a scratch project dir (their own sessions; hooks write only their own session state), then adds the playbook line [recommended]; (b) the agent writes a script, the operator runs it with `!`; (c) skip the live run, add only the playbook line. Interactive /model switching (part 2) needs the operator either way.
answer 46: (c) too expensive to verify live now — keep as a P3 item and dogfood meanwhile (operator 2026-09-22)
