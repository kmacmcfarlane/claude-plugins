---
id: librarian-mode-end-the-wait-for-a-forwar-b514
title: "librarian-mode: end the wait for a forward whose live peer never replies"
type: chore
status: todo
priority: 3
created: 2026-09-28
updated: 2026-09-28
refs:
  - 3460 review
---

From the 3460 review 2026-09-28 (residual accepted there): a forward held blocked for a peer that stays live but never replies waits indefinitely. Acceptance: a bound in references/ending-the-session.md (at session end, a forward still waiting is re-blocked naming the operator) or in idle-turn.md, plus a pointer from idle-turn.md to Intake step 4's liveness check.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
folded into policy spike 8dee 2026-09-29: the operator wants an unaccepted forward to land back on the forwarder
2026-09-30 folds into 3460 (8dee F4) under answer 116 b: its session-end bound is replaced by the sooner operator-turn bound and kept as the backstop; closes when 3460 lands.
