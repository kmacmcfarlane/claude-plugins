---
id: checkpoint-rehydration-round-2-lows-from-4a19
title: "checkpoint rehydration: round-2 lows from 5cdb"
type: chore
status: doing
priority: 4
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:36Z
created: 2026-09-18
updated: 2026-09-18
---

From the 5cdb round-2 review (2026-09-18), all low: (1) liveness() label FRESH while Next is withheld when the recorded head is missing locally or HEAD rewound behind it — derive the label from the same ancestry check; (2) 'items: N unparseable' sits under the 'store contradicts' heading — give it its own line; (3) handoff-format.md shows only one withheld-line template — document the not-found / not-an-ancestor variants and '1 commit'; (4) _trim_items regex should match items: only inside frontmatter. Files: plugins/context-guard/hooks/rehydrate.py, tests, checkpoint references/handoff-format.md.

## Handoff
- doing: dispatched in worktree
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — executable logic

impl: DONE ebd501d (head_state() single ancestry check; AGED(reason); separate unparseable block; frontmatter-only trim; handoff-format variants). Note: implementer used bare git stash/pop in its worktree (shared stash stack) — restored; stash list checked.
dispatch: reviewer opus — rule 4
