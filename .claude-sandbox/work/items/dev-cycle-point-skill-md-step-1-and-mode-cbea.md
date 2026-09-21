---
id: dev-cycle-point-skill-md-step-1-and-mode-cbea
title: "dev-cycle: point SKILL.md Step 1 and model-routing at the orchestrated mode (after F2+F3)"
type: chore
status: todo
priority: 2
deps:
  - librarian-mode-leans-on-dev-cycle-07c3-f-fb09
  - investigate-implement-running-under-an-o-4a6b
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
created: 2026-09-19
updated: 2026-09-19
---

From the F3 (4a6b) implementer, 2026-09-19: dev-cycle/SKILL.md ~l.90 and l.97-98 still describe the dev-flow block as librarian-mode's reused block 'until those skills own an orchestrated mode'; dev-cycle/references/model-routing.md:219 still says 'non-interactively, per the brief's dev-flow block'. Rewrite them to point at each skill's § Running under an orchestrator once both F2 and F3 are on main (F2 owns those files meanwhile). Also: review-checklist §3 catalog CHECK line fires on any SKILL.md edit (low).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Carried from F3 review (lows)
- investigate mode lists inputs as Series home + base only, but its Step 6 bullet relies on "a worktree the orchestrator gave": add "and, when it has one, the worktree".
- implement mode: gate decisions have no home once 10b (outcome file) is off: say they go under DEVIATIONS.
- implement mode: dropping EnterWorktree also drops Step 7's "regenerate stale checked-in artifacts first": restore it for the given worktree.
- implement mode: a human-gated verification — say commit at the planned tier and list the gap under COULD NOT DO.
- implement non-interactive section says "Gates 1 and 6" (likely "1 and 2").

## Carried from F2 review (nits)
- dev-cycle/references/bindings.md:45 librarian Terminal action row: add "an item naming another base merges into that base, never pushed".
- librarian-mode/SKILL.md:158-160 rewrap.
