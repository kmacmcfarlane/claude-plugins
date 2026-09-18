---
id: sandbox-skill-troubleshooting-entry-for-881e
title: "sandbox skill: troubleshooting entry for a session that vanishes mid-command (container OOM, exit 137)"
type: chore
status: doing
priority: 3
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:16Z
created: 2026-09-17
updated: 2026-09-18
refs:
  - item session-kappa-3446-implement-in-the-emai-0236
---

From the 0236 diagnosis 2026-09-17: a claude-sandbox container OOM-kill looks like the Claude session dying. Acceptance: one troubleshooting entry in the sandbox skill — symptom (session gone mid-command, relaunch resumes), check (docker events --filter event=oom; exit 137), remedies (raise memoryLimit in .claude-sandbox/config.yaml, cap build/test parallelism, avoid parallel heavy builds across subagents). Lands on the factored layout (plugins/sandbox) after plugin-factoring merges. Also note for the claude-sandbox repo (out of scope here): have the launcher report an OOM kill on exit.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer sonnet — default (one doc entry)

impl: DONE 5dd2511 (entry inline in SKILL.md Troubleshooting)
dispatch: reviewer opus — rule 4 (implementer sonnet)

review round 1 (opus): NEEDS_CHANGES — high 1 (--rm: docker ps -a / inspect cannot see the dead container), medium 2 (use after-the-fact docker events --since/--until with oom+die exit code), 3 (say where to run: host or sandbox with docker socket), 4 (commit verb docs:), lows 5-7, nit 8.
dispatch: implementer sonnet fix round 1 — resume, tier unchanged
