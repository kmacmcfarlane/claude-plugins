---
id: dev-flow-cross-skill-reference-conventio-05bb
title: "dev-flow: cross-skill reference convention + review-checklist lint fix (07c3 F0)"
type: feature
status: doing
priority: 2
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
owner: unknown@e3a28d2cc009
claimed: 2026-09-19T00:29Z
created: 2026-09-18
updated: 2026-09-19
---

07c3 plan §F0. A skill may point into a sibling skill in the same plugin by naming the skill + a bare references/x.md, never ../ and never across plugins; fix review-checklist §2 lint that FAILs the legitimate pointers in implement/deep-investigation; one line each in CLAUDE.md and create-skill. Size S; opus/opus. After d72e lands.

## Handoff
- doing: dispatched
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — doctrine (CLAUDE.md convention, create-skill rule) (rule 2)

impl: DONE 0c1c11c (sibling lint; x.md reserved; 4 -> 1 reference FAIL, remaining is a real cross-plugin pointer in ralph backlog-yaml).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (any backticked sibling in the window rescues the pointer, not the named one), 2 (prefixed paths like beta/references/x.md are silently ignored while the prose says cross-plugin fails); lows 3 (backticks/one-line requirement undocumented); nits 4-6.
dispatch: implementer opus fix round 1 — resume
