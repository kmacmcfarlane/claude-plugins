---
id: librarian-mode-round-cap-is-3-review-rou-2b08
title: "librarian-mode: round cap is 3 review rounds; fable on the last fix round"
type: bug
status: done
priority: 1
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator decision 2026-09-16 reversing the librarian's fix-round ruling in 423f: the cap stays at 3 REVIEW rounds (the first review plus two fix rounds). After a third review without CLEAR the librarian blocks the item and asks the operator to weigh in. Consequence for the rules: fix round 1 keeps the tier; fix round 2 is the last before the cap and runs at fable (operator: escalate to fable at that point); rule 2 loses its 'fix round 2 or later' signal; rule 3's round signal becomes 'fix round 2 (the last before the cap)'. Keep 'fix round n = review round n+1' and the verified: line counting fix rounds. Acceptance: every sentence counting rounds in SKILL.md, references/model-routing.md, references/review-brief.md, references/agent-brief.md agrees with this; the escalation says ask the operator.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

model: opus
dispatch: implementer opus — rule 2 (4 files; doctrine of the librarian's own procedure)
dispatch: reviewer opus — rule 4

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
- implementer opus returned DONE, commit a1387b1; reviewer opus round 1 dispatched 2026-09-16 16:45:28
- review round 1: NEEDS_CHANGES — 1 medium (review-brief.md:132 still cites 'Route rules 2–4' as tier-raising; rule 2 has no round signal now), 1 low ('The verified: line counts the same.' has an ambiguous antecedent). Fix round 1 sent 2026-09-16 16:48:04, tier unchanged (opus, resumed).
- fix round 1 returned DONE, new commit 7d49c39, nothing declined; re-review dispatched 2026-09-16 16:49:06 (reviewer opus, resumed)
- 2026-09-16 done: 3466b76
- re-review CLEAR (findings 1,2 FIXED, none new). Landed merge 3466b76 2026-09-16 16:50:47.
