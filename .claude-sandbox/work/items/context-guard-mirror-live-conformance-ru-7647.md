---
id: context-guard-mirror-live-conformance-ru-7647
title: "context-guard mirror: live conformance run + playbook note on hand-run hooks"
type: chore
status: todo
priority: 3
created: 2026-09-19
updated: 2026-09-22
---

From the d63e final review (2026-09-19): never verified live — (1) the plan's claude -p conformance run (derived window vs the status line's context_window_size across opus-5, opus-5[1m], haiku-4-5, DISABLE_1M), (2) interactive /model switching firing PostModelSwitch, (3) whether the documented usage-credits error for 1M context is written to the transcript as an API-error line. Also add one playbook line: a hook script hand-run from a session's Bash tool against the real config dir is verified as that session and can write its latch — use a scratch CLAUDE_CONFIG_DIR.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Groom 2026-09-21
decision 46: live conformance needs real `claude -p` runs (opus-5, opus-5[1m], haiku-4-5, DISABLE_1M) on the operator's credentials and quota — (a) an agent runs ~8 short -p calls from a scratch project dir (their own sessions; hooks write only their own session state), then adds the playbook line [recommended]; (b) the agent writes a script, the operator runs it with `!`; (c) skip the live run, add only the playbook line. Interactive /model switching (part 2) needs the operator either way.
answer 46: (c) too expensive to verify live now — keep as a P3 item and dogfood meanwhile (operator 2026-09-22)
note: 2026-10-07T19:02Z from the e347 scrub build (landed fbe2c0f): answer 169 (a)'s condition — confirm the credits message text against a real transcript line — is still unmet; no such line exists on this machine; the gate matches the documented title, and a miss only under-warns. Confirm when one appears.
