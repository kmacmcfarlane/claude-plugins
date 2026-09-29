---
id: operator-interaction-the-plain-names-ski-cad6
title: "operator-interaction: the plain-names skill (0b2d F1)"
type: feature
status: done
priority: 1
deps:
  - decisions-a-b-c-option-order-with-the-re-dbfc
parent: operator-interaction-refer-to-work-items-0b2d
created: 2026-09-29
updated: 2026-09-29
closed: 2026-09-29
refs:
  - 0b2d
---

Build F1 of series .claude-sandbox/investigations/0b2d-plain-item-names (03 + 04, plan review s04-r2 CLEAR). Starts from main after dbfc lands; re-check anchors. Fold lows L3 (Rulings: 'nothing is stored' is the librarian's ruling, 95 was delegated) and L6 (store lines keep full ids; the stored decision card, which the operator reads, names items plainly).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — new skill + catalog/marketplace shape change (routing rule 2)
agent: a0f63f68b3becabab (implementer r1)
r1 DONE e87edfb: plain-names skill + decisions pointers + plugin.json/marketplace/README/CLAUDE.md/repo-map; deviations: examples invented, L3 marked as "the kit maintainers call", added When it goes wrong; answer 90 was given 2026-09-29 so the README date is right
dispatch: reviewer opus — fresh reviewer, round 1
agent: a63441010c68f6094 (reviewer r1)
review r1 CLEAR at e87edfb (4 lows, 1 nit, all wording in the new skill); librarian ruling: take them in one fix round before landing, since the misattributed ruling label matters to the operator
dispatch: implementer opus — resume, fix round 1
review: self
fix round 1 42b99ca: the diff is exactly review r1s "would pass" wording for lows 1-4 and the nit (b7d4 checked unused); verdict CLEAR (self, pure wording)
landed: 016daae
checks on main 016daae: all 8 OK
- 2026-09-29 done
