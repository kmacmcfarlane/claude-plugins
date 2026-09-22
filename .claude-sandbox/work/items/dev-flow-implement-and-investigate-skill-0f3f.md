---
id: dev-flow-implement-and-investigate-skill-0f3f
title: "dev-flow: implement and investigate SKILL.md over the 5000-token skill guidance"
type: refactor
status: done
priority: 3
created: 2026-09-21
updated: 2026-09-22
closed: 2026-09-22
refs:
  - e08c implementer; 2e7d reviewer
---

Surfaced by e08c (implement ~4.3k words, ~6.6k tokens by proxy) and the 2e7d review (investigate 4751 words) 2026-09-21: both exceed create-skill's 'SKILL.md under 5000 tokens'. Acceptance: each SKILL.md under the guidance by moving detail into references/ (progressive disclosure), no behaviour lost; every moved rule still reachable by a pointer that names it (the be39 lesson: a pointer names the rule, not just the case). Opus: judgement on what stays in the body.

## Handoff
- doing: implementer dispatched (opus, agent a90f854352d818efe)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer opus — judgement on what stays in two skill bodies
- 2026-09-22 done: 5564444

## Implementer result
- round 1 DONE_WITH_CONCERNS bf521e5 (opus): implement 7038→4868, investigate 7622→4903 (chars/4; words 2913/2980); 10 new references (verbatim moves); 72-rule checklist per skill, 0 missing; step numbers and outside citations intact. Concern: chars/4 margin thin (~100-130). Open: retrospective steps disagree (investigate follows update-kit directly, implement asks the user) → follow-up filed.
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at bf521e5
- moved text verbatim; step numbers + outside citations intact; checks green. Sizes (chars/4 Unicode): implement 6972→4818, investigate 7559→4855.
- [medium] investigate § Asking at a gate dropped "and an answer that redefines the problem is one to re-scope from" (main:94-95), in no reference.
- lows: run-modes load cue body vs header; four investigate pointers + implement attestation weakened; implement Step 8 two clauses dropped; <4% headroom on the proxy; two long lines.
- dispatch: implementer opus — fix round 1 (same agent resumed)
- fix round 1 DONE 4e8ab78 (opus): re-scope clause restored; load cues; dropped pointers/attestation/Step 8 clauses restored; rationale-only trims → 4739/4744 chars/4 (Unicode).
- dispatch: reviewer opus — review r2 (same reviewer resumed)

## Review round 2 — CLEAR (opus) at 4e8ab78
- every trim rationale/examples only; nits not taken: ragged rewraps; implement:117 dropped "usually".
- landed 5564444
