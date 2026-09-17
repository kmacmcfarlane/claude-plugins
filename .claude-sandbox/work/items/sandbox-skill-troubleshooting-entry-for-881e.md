---
id: sandbox-skill-troubleshooting-entry-for-881e
title: "sandbox skill: troubleshooting entry for a session that vanishes mid-command (container OOM, exit 137)"
type: chore
status: todo
priority: 3
created: 2026-09-17
updated: 2026-09-17
refs:
  - item session-kappa-3446-implement-in-the-emai-0236
---

From the 0236 diagnosis 2026-09-17: a claude-sandbox container OOM-kill looks like the Claude session dying. Acceptance: one troubleshooting entry in the sandbox skill — symptom (session gone mid-command, relaunch resumes), check (docker events --filter event=oom; exit 137), remedies (raise memoryLimit in .claude-sandbox/config.yaml, cap build/test parallelism, avoid parallel heavy builds across subagents). Lands on the factored layout (plugins/sandbox) after plugin-factoring merges. Also note for the claude-sandbox repo (out of scope here): have the launcher report an OOM kill on exit.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
