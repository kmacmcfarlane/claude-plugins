---
id: investigate-skill-md-over-size-guidance-be39
title: "investigate SKILL.md over size guidance (5659 words): move detail into references/"
type: refactor
status: done
priority: 3
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
---

Noted in the 183a and F3 reviews: investigate/SKILL.md is ~5.7k words, over the ~5000 guidance (create-skill). Move long step detail into references/ without losing rules (preservation sweep). Contended file: land after b43e and 4ca4.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Carried from 4ca4 review (lows)
- README dev-flow table: investigate row restates the escalation test (say "broad landscape (deep-investigation)"); chain-of-verification Not-when should be its own boundary (no falsifiable content / speed over accuracy); implement row: also fans out to worktrees; investigate description: comma after "feature".

## Carried from b43e review (lows)
- investigate Step 15 options: use the typeable form with a leading slash (/dev-flow:implement, /context-guard:checkpoint, /dev-flow:dev-cycle); plainer skill-list sentence; README:87 dev-flow row "rehydrates from its manifest and ledger" → "weighs its manifest and ledger when it rehydrates".

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- 2026-09-21 done: c302e7f

## Dispatch
- dispatch: implementer opus — >3 files; preservation sweep required

## Implementer result
- round 1 DONE 2207670 (opus): investigate 5,761 → 4,737 words; headings identical; Step 3a detail → references/branch-survey.md, Step 11 → open-question-sweep.md, Edge Cases → edge-cases.md, Quality Criteria → quality-criteria.md (verbatim); Step 15 slash commands; README table rows + catalog row lows. Inventory: .claude-sandbox/investigations/be39-investigate-preservation.md.
- dispatch: reviewer opus — rule 4, line-level preservation sweep

## Review round 1 — CLEAR (opus) at 2207670
- line-level sweep: no rule lost (13 unmatched sentences all explained); inbound pointers resolve; every new reference reached from SKILL.md.
- lows (landed; filed as 4a3c-style follow-up below): edge-cases.md:27 path rewrite; quality-criteria pointer better at Step 12; name the several-problems rule in the Edge Cases pointer.
## Landed
- c302e7f.
