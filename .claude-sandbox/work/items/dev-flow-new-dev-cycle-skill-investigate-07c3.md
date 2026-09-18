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
