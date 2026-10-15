---
id: decisions-skill-gallery-update-the-revie-341a
title: "decisions skill gallery: update the review-cap example card for the spend budget"
short_display_name: gallery cap example update
type: chore
status: done
priority: 3
created: 2026-10-05
updated: 2026-10-13
closed: 2026-10-13
refs:
  - dev-cycle-at-the-review-cap-the-orchestr-5bdd
---

plugins/operator-interaction/skills/decisions/references/gallery.md:126-135's example card still reads 'four review rounds — the cap'; once the budget rule (5bdd) lands, the cap is spend-based (decision 145 a). Update the illustration (invented, per the skill) so it does not teach the old rule.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree branch off main (3d839b5c); operator-interaction decisions references/gallery.md
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — example card to the spend-based cap
agent: implementer ab4b79c648f196843 round 1
result: DONE round 1 at 5c504eb5 (gallery example 5 to a budget-cap round ask; 138 OK; flagged decisions SKILL.md:91,108 still says review-round cap waiver)
dispatch: reviewer opus high — fresh (rule 4)
agent: reviewer ab756b260ea63feb2 round 1 at 5c504eb5
verdict: NEEDS_CHANGES round 1 at 5c504eb5 (2 medium: the example is a case dev-flow would finish-round without asking — make the leftover not exact-fix; list line lost quota from a round's cost; lows: 'above the reserve' ambiguous, Undo understates spend; nits: asked-for rule reads unconditional, (a) label differs card vs line; SKILL.md:91,108 acceptable)
dispatch: implementer opus medium — resume, fix round 1
agent: implementer ab4b79c648f196843 round 2
result: DONE round 2 at 175dc146 (all 6 applied; 138 OK)
dispatch: reviewer opus high — resume, round 2
agent: reviewer ab756b260ea63feb2 round 2 at 175dc146
verdict: CLEAR round 2 at 175dc146 (all 6 exact; SKILL.md:91,108 wording optional, declined)

## Notes
- 2026-10-13 done
