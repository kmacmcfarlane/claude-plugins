---
id: checkpoint-rehydration-round-2-lows-from-4a19
title: "checkpoint rehydration: round-2 lows from 5cdb"
type: chore
status: todo
priority: 4
created: 2026-09-18
updated: 2026-09-18
---

From the 5cdb round-2 review (2026-09-18), all low: (1) liveness() label FRESH while Next is withheld when the recorded head is missing locally or HEAD rewound behind it — derive the label from the same ancestry check; (2) 'items: N unparseable' sits under the 'store contradicts' heading — give it its own line; (3) handoff-format.md shows only one withheld-line template — document the not-found / not-an-ancestor variants and '1 commit'; (4) _trim_items regex should match items: only inside frontmatter. Files: plugins/context-guard/hooks/rehydrate.py, tests, checkpoint references/handoff-format.md.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
