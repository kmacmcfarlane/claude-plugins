---
id: checkpoint-around-continuation-how-agent-d3ee
title: checkpoint around continuation + how agents present decisions (relayed operator request)
type: spike
status: todo
priority: 1
created: 2026-09-23
updated: 2026-09-23
refs:
  - "peer: marketplace - librarian (operator relay 2026-09-23)"
---

Relayed 2026-09-23 by peer 'marketplace - librarian' at the operator's instruction (a request, not an approval). Five ideas: (1) two decision sets at a checkpoint: answer-before-compaction to wrap loose ends vs deal-with-after; (2) a pre-checkpoint summary for continue: landed since the last attended checkpoint, in-flight carried over, next up, open decisions compact, candidate actions to make the checkpoint; (3) a decision communication format with detail levels (one line / options+impact / block per option) and when to use each, probably a new dev-flow skill (decisions, more later); (4) re-present open decisions at medium/high detail after rehydration, compact list in the manifest; (5) refactor checkpoint intent: continue is the default use, land/handoff rarely used; operator intents vary on another axis (compact so I can answer decisions and unblock you / compact so you can continue in-flight work) - maybe a second dimension. Test case: marketplace HANDOFF.md stamped 2026-09-23T01:12Z (DECISIONS OPEN list + closing Report decisions needed block), decision context in the marketplace store (read-only). Acceptance: investigation series with findings + recommendation, decisions by number; features filed as children. Operator plans an interactive session on this first.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- 2026-09-23 relayed: replied ids to marketplace - librarian; summaries sent to agents - librarian and operator-attention requirements gathering and research (asked the latter to reconcile its decision-UI work). Held for the operator's interactive session before any dispatch.

- 2026-09-23 agents - librarian proposes an ownership split, recorded on agents 374f (communication-standards-estate-wide-home-374f). agents would own the convention: detail levels and the rule for choosing one, the lettered+numbered labels, the two-line recap, and where it applies. claude-plugins would own the mechanics: ideas 1, 2, 4 and 5, plus the dev-flow skill that implements the format. This is a peer proposal: the operator settles it in the interactive session, and agents decision 2 (where estate-wide standards live) is still open. agents evidence for idea 5: they have four decisions open and nothing in flight, so compacting would only be "so the operator can answer", which none of the current modes names.

- 2026-09-23 operator-attention answered: the decision-UI work is theirs; see 7113 for their paths and gist, and the ownership conflict with agents 374f.
