---
id: dev-cycle-point-skill-md-step-1-and-mode-cbea
title: "dev-cycle: point SKILL.md Step 1 and model-routing at the orchestrated mode (after F2+F3)"
type: chore
status: done
priority: 2
deps:
  - librarian-mode-leans-on-dev-cycle-07c3-f-fb09
  - investigate-implement-running-under-an-o-4a6b
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
created: 2026-09-19
updated: 2026-09-21
closed: 2026-09-21
---

From the F3 (4a6b) implementer, 2026-09-19: dev-cycle/SKILL.md ~l.90 and l.97-98 still describe the dev-flow block as librarian-mode's reused block 'until those skills own an orchestrated mode'; dev-cycle/references/model-routing.md:219 still says 'non-interactively, per the brief's dev-flow block'. Rewrite them to point at each skill's § Running under an orchestrator once both F2 and F3 are on main (F2 owns those files meanwhile). Also: review-checklist §3 catalog CHECK line fires on any SKILL.md edit (low).

## Handoff
- doing: dispatched
- next: review
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

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: f1de676

## Dispatch
- dispatch: implementer opus — >3 files across 3 skills; judgement (F3 lows)

## Implementer result
- round 1 DONE 9fd75e2 (opus): dev-cycle Step 1 + model-routing point at the orchestrated modes; bindings.md librarian Terminal action non-main base clause; implement/investigate orchestrator-mode lows (gate decisions → DEVIATIONS; regenerate stale artifacts; human-gated verification → commit + COULD NOT DO; worktree input); "Gates 1 and 6" → "Gate 1 (Step 6, the plan)".
- dispatch: reviewer opus — rule 4

## Review round 1 — CLEAR (opus) at 9fd75e2
- lows (landed): implement orchestrator Step 9 bullet should defer "incomplete" to Step 8 human-gated case; "Gate 1 (Step 6, the plan)" confirmed right. Out of scope noted: implement non-interactive mode silent on several prompts.
## Landed
- f1de676.
