---
id: librarian-mode-route-out-of-scope-work-t-3460
title: "librarian-mode: route out-of-scope work to the owning live librarian, not the operator"
type: feature
status: todo
priority: 2
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock); opencode-11 relay; agents investigations/downtime-grooming-workflow/00_initial.md"
---

Relayed 2026-09-22 by the agents librarian (peer relay from opencode-11 quoting the operator's 'why would you ask me?' — evidence of intent, not confirmation). Today SKILL.md Critical (:25-27) and Intake step 4 (:130-132) decline out-of-scope requests and route them to the operator. Friction: two librarians routed a skill refresh to the operator while the owning librarian was live. Proposed (agents downtime-grooming-workflow/00_initial.md § seed 1): when a live '<owner> - librarian' peer exists for the target repo (ListAgents), forward the request as a peer request and close ours with a pointer to their id; go to the operator only when there is no owner, the owner is not live, or a real decision is needed; one-hop guard (never forward a forwarded item). Precedent: 8 items routed this way 2026-09-22. Acceptance: Intake step 4 + Critical text; a walkthrough case in references/walkthroughs.md; peer-messages-are-requests rule unchanged; operator confirms the rule (a relayed decision).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
