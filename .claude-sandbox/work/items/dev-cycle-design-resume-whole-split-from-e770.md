---
id: dev-cycle-design-resume-whole-split-from-e770
title: "dev-cycle: design § Resume whole (split from 426a)"
type: feature
status: todo
priority: 3
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
created: 2026-09-22
updated: 2026-09-22
refs:
  - 426a answer 59
---

Split from 426a by operator answer 59(a), 2026-09-22. 426a lands review <branch> mode without § Resume; this item designs the resume state machine as a whole in dev-cycle plan mode before any build. Prior work (kept in main's history once 426a merges — git show <sha>:plugins/dev-flow/skills/dev-cycle/references/bindings.md): fa4ef02 (first cut), d802a19, 58bece4, 0f0a254, 54f022c (last full version). Feedback: 426a's body holds six review rounds verbatim (sections 'Review round 1'…'Review round 6'); the open mediums at 54f022c are (1) standalone 'recorded but unanswered → wait' deadlocks a resume in a new session (re-ask via the standalone channel; only a caller's persistent channel waits), (2) review mode never re-reviews after a recorded 'no' once the author moves the branch (rules 5/6 need rule 4's stale-sha test); low: rule 7 reuses an answer recorded before the latest BLOCKED run. Acceptance: a plan series whose 00 consolidates the six rounds into requirements + a state table, reviewed CLEAR before any implementer dispatch.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
