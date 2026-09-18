---
id: dev-flow-new-dev-cycle-skill-investigate-07c3
title: "dev-flow: new dev-cycle skill (investigate → implement → verify via sub-agents); librarian-mode leans on it"
type: feature
status: todo
priority: 2
created: 2026-09-18
updated: 2026-09-18
refs:
  - peer claude-sandbox librarian; claude-sandbox 8b2d
---

Peer claude-sandbox librarian (its 8b2d), relaying its operator, 2026-09-18. Factor the sub-agent dev cycle out of librarian-mode into dev-flow as dev-cycle: callable ad hoc on a work item or a conversation, no librarian needed; librarian-mode references its spec (implementer brief, review brief + severity, fix loop + cap, checks, model routing) instead of carrying a copy; compose/replace/wrap dev-flow investigate/implement (librarian's call). Overlaps ed88: product-repo opt-in and repo-specific checks would live in dev-cycle. Lands after ed88 (which moves librarian-mode into dev-flow) and after the two routing items, or absorbs them — decide at factoring.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

dispatch: plan-writer opus — design plan for operator/librarian review (.claude-sandbox/investigations/07c3-dev-cycle/plan.md)

## Plan and factoring (2026-09-18; plan: .claude-sandbox/investigations/07c3-dev-cycle/plan.md)
Librarian adopts the plan's recommendations (operator delegated; listed in the Report for review, not blocking): wrap investigate/implement with an orchestrator mode; standalone checks = reuse ## Librarian Checks else detect + ask once, never write CLAUDE.md; standalone land = ask once, local merge first, never push unasked; tombstones for one release; conversation runs file a work item when a store exists; no land-only mode. Migration = copy -> cut over -> tombstone. None of it reaches fable (prose procedure).
Precondition: d72e bundle lands first.
Features (children): F0 cross-skill reference convention + lint fix; F1 add dev-cycle (+catalog same commit); F2 librarian-mode leans on dev-cycle (dep F1); F3 orchestrator mode in investigate/implement (dep F1, parallel with F2); F4 review mode + resume (dep F1); F5 remove tombstones one release after F2.
