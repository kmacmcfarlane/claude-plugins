---
id: librarian-mode-leans-on-dev-cycle-07c3-f-fb09
title: librarian-mode leans on dev-cycle (07c3 F2)
type: feature
status: doing
priority: 2
deps:
  - dev-flow-add-the-dev-cycle-skill-07c3-f1-325d
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
owner: unknown@e3a28d2cc009
claimed: 2026-09-19T05:57Z
created: 2026-09-18
updated: 2026-09-19
---

07c3 plan §F2: 'The cycle' section with librarian bindings; moved references tombstoned; SKILL.md drops to ~11-12k chars. Reviewer gets a line-level preservation sweep. Size M-L; opus/opus.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Carried to F2
- librarian-mode troubleshooting.md merge-conflict entry has the same hand-resolve wording; fix when librarian-mode leans on dev-cycle.
- Standalone /dev-cycle in a librarian-custody repo ignores ## Librarian Scope/Exclude: decide whether dev-cycle must refuse or honour a declared Scope.

## Carried from F1 review
- plan-mode re-review: paste "none" for the changed: list; fix-loop.md:33 long line; conflict-round CHANGED may list base-brought files (drop them against the three-dot diff).

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

## Dispatch
- decision (librarian): standalone /dev-cycle in a repo with a ## Librarian section honours its Scope/Exclude as the Ground binding (never refuses; never widens). Least surprise, keeps custody; no operator trade-off.
- dispatch: implementer opus — >3 files; judgement (preservation, reconcile); README text (plan §6)

## Implementer result
- round 1 DONE_WITH_CONCERNS f88d128 (opus): The cycle section (dev-cycle Steps 1–5 with librarian bindings), Route/Delegate/Review/Land removed, 5 tombstones, walkthroughs.md, opt-in checks table → dev-cycle bindings.md § Checks, troubleshooting split (merge conflict → implementer fix round), README sentence; carried notes a–d in dev-cycle bindings/fix-loop/review-brief. SKILL.md 19918 → 12691 bytes (concern: above 11–12k target). 5 suites green; pointer sweep 77 checked, 0 real misses.
- named changes to judge in review: a spike now runs dev-cycle plan mode (no worktree) instead of /investigate in a worktree; no explicit `git checkout main` before merge (dev-cycle stops and asks instead); cycle red flags condensed to one bullet; opt-in option list only in opt-in.md.
- preservation inventory: .claude-sandbox/investigations/07c3-dev-cycle/f2-preservation.md (copied from the session scratchpad).
- held: operator paused 2026-09-19; next is reviewer opus with the line-level preservation sweep (plan §5 Risks, verbatim).
- dispatch: reviewer opus — rule 4 (impl opus)
