---
id: sandbox-skill-troubleshooting-entry-for-881e
title: "sandbox skill: troubleshooting entry for a session that vanishes mid-command (container OOM, exit 137)"
type: chore
status: done
priority: 3
created: 2026-09-17
updated: 2026-09-18
closed: 2026-09-18
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

fix round 1 (sonnet): DONE_WITH_CONCERNS dabadf0 (single commit on a426bf1). LESSON (librarian brief error): my "git reset --soft main" rule for fixing a commit subject was unsafe once main had advanced — the stale index produced a commit reverting ~27 unrelated files; the implementer caught it, reset --hard to main and reapplied. Never brief reset --soft onto a moved main; use a new commit, or reset --soft to the merge-base.
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR. Low 1 (--since 1h window, no note to widen; daemon backlog limited) not addressed — carried as a note, author not re-dispatched for a low.
- 2026-09-18 done: 8f8da39
