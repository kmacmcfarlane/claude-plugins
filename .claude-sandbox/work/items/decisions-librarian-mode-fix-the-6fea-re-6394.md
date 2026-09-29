---
id: decisions-librarian-mode-fix-the-6fea-re-6394
title: "decisions + librarian-mode: fix the 6fea render-pass gaps (stored card floor, stakes, grouping, paging)"
type: chore
status: done
priority: 2
created: 2026-09-29
updated: 2026-09-29
closed: 2026-09-29
refs:
  - 6fea
---

From 6fea findings (.claude-sandbox/investigations/6fea-decisions-render-pass/findings.md), 2026-09-29, librarian-noticed. Acceptance: each high and medium finding fixed or declined with a reason; lows taken where one line; LM/SKILL.md edits (findings 10, 11, 23) wait until 3460 lands (same file); nothing reverses a ruled operator decision; provisional rules stay marked.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-29 claimed by Kyle-McFarlane@7696505da8e1

dispatch: implementer opus — rule wording across two plugins (routing rule 2)
agent: ab00e20ebe4f8122b (implementer r1)
r1 DONE ea7e2b9: fixed 1-17,20-22; deferred 18,19,23 (need LM/SKILL.md, after 3460); deviation: finding 12 lets cold re-show beat the deferred-stays-a-line rule (b527) — reviewer to weigh
dispatch: reviewer opus — fresh reviewer, round 1
agent: ab56c44f1a4550941 (reviewer r1)
review r1 NEEDS_CHANGES: 1 medium (open question: line has no close), 6 lows; finding 12 judged a consistent refinement (cold re-show of open decisions was ruled, 84/answer 73), not a reversal; paging reword stays provisional — mention in Report
dispatch: implementer opus — fix round 1 (resume)
r1 fixes a9000b3: all 7 fixed
dispatch: reviewer opus — fresh reviewer, round 2
agent: a73c8e6851379fba5 (reviewer r2)
review r2 NEEDS_CHANGES: 1 medium (revised/backfilled card must keep original raised:), 2 lows (deferred leaves its group, list line too; open-question close form self-matches)
dispatch: implementer opus — fix round 2 (resume)
r2 fixes 890fc2b: all 3 fixed
dispatch: reviewer opus — fresh reviewer, round 3
agent: a250510e2fd4c2a87 (reviewer r3)
review r3 NEEDS_CHANGES: 1 medium (backfill recipe prints %cI with offset; wi _parse_when rejects it -> age None); verified replacement given
dispatch: implementer opus — fix round 3 (resume)
r3 fix 377f706: recipe replaced, verified parses
dispatch: reviewer opus — fresh reviewer, round 4 (cap)
agent: aad16f00a2fdde385 (reviewer r4)
review r4 CLEAR at 377f706
landed: 46ee23b
checks on main 46ee23b: all 8 OK
- 2026-09-29 done
