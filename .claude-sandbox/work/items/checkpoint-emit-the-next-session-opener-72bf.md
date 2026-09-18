---
id: checkpoint-emit-the-next-session-opener-72bf
title: "checkpoint: emit the next-session opener on the lean path too"
type: chore
status: done
priority: 3
created: 2026-09-16
updated: 2026-09-18
closed: 2026-09-18
refs:
  - reviewer report, item checkpoint-end-continue-handoff-output-w-2a88
---

Raised twice by the 2a88 reviewer 2026-09-16: the Lean path (<60K tokens left) runs Steps 0, 2, 4b only, so the new Step 7 opener is skipped exactly when a handoff is likeliest and the next session has the least to go on. Acceptance: the lean path emits the one-line opener (Step 7) after 4b; also restore the conditional wording '(if your chain records a per-stage gate or label, it is already set)' in Step 7; SKILL.md under 5000 tokens.

## Handoff
- doing: in review/fix loop in worktree (see item body)
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — bundled into worktree 5cdb with 5cdb (same SKILL.md)

impl: in worktree 5cdb as e2680e3; reviewed with 5cdb
- 2026-09-18 done: c78cb50
