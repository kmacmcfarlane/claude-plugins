---
id: wi-custody-warning-round-2-lows-from-8ef-cb58
title: "wi custody warning: round-2 lows from 8efe"
type: chore
status: doing
priority: 4
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:36Z
created: 2026-09-18
updated: 2026-09-18
---

From the 8efe round-2 review (2026-09-18), all low: (1) sidecar store ignoring its own work/ gets host advice (trackInHost) — when sandbox_shape is sidecar, drop trackInHost and name the sidecar repo; (2) 'remove or negate that rule' — git cannot re-include under an excluded parent; for SANDBOX_IGNORES rules say rewrite as /.claude-sandbox/* + !/.claude-sandbox/work/ or remove; (3) check-ignore -v parse splits on the first :N: — use -z output. Files: plugins/work-items/skills/work-items/scripts/wi.py, tests.

## Handoff
- doing: dispatched in worktree
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — executable logic

impl: DONE 3b3526c (check-ignore -v -z --stdin, one call; sidecar no host advice; rewrite remedy for SANDBOX_IGNORES).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (non-UTF-8 source path under -z -> UnicodeDecodeError escapes _git; prime/lint crash; regression); lows 2 (sidecar branch blames sidecar for an excludesFile rule), 3 (negate advice for dir-level rules outside SANDBOX_IGNORES), 4 (tests for quotePath/non-ASCII/hung stdin).
dispatch: implementer opus fix round 1 — resume
