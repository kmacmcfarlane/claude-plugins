---
id: decisions-adopt-the-two-word-class-shape-bb44
title: "decisions: adopt the two-word class shape (answer 134 a) and migrate stored tags"
short_display_name: two-word decision classes
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T06:55Z
created: 2026-10-09
updated: 2026-10-09
refs:
  - decisions-a-general-shape-for-decision-c-90bc
---

Answer 134 (a), 2026-10-09: adopt the two-word class shape from the 90bc series (.claude-sandbox/investigations/90bc-decision-classes/ 00-04, plan CLEAR r3): a raised line says why it is the operator's (blocker, one-way, trust, contract, reach, spend, precedent, your-call, trade-off, unclassed), a decided line says what changed (words, design, place, scope, reading, cap); migrate this store's tags via the retired-spellings table. Carried findings 18-21 from the 90bc item apply. OQ2 (reasons in librarian-mode vs the decisions skill) stays open, blocks nothing.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree (budget waived; spend measured)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a69db72a9e3f61139
return: DONE worktree-agent-a69db72a9e3f61139 b88938f (two-word tags in decide-alone.md etc.; findings 18-21 applied; new test_decision_tags.py; migration scratchpad/bb44-migrate/ dry run 59 lines in 19 files, 10 ruled-rule-case hand-ruled; 10/10 Checks; first commit message clobbered by the shared msg.txt, amended on its own unmerged branch)
dispatch: reviewer opus high — review round 1 of b88938f, and the migration script
agent: reviewer afb07a4dafaa4fa03
verdict: review round 1 CLEAR (lows: 1 migration must run with --owner, 53 lines/17 files; 2 ten untimed decided: lines, seven with retired spellings, fix by hand in the store step; 3 walkthroughs.md:19 tags a same-item dependency contract, should be precedent; nits 4 residue test misses fenced record lines, 5 'nothing moves the other way' overclaims, 6 migrate.py should stop on relay lines)
correction: the librarian's own decided: lines this session (2ff6, eda1, and others) omit the UTC time the record-lines format carries; from now on decided: lines carry the time and the new two-word kinds
decided: 2026-10-09T07:22Z cap — finish round of exact-fix leftovers 3-6 (authority answer 145); 1-2 are the store step at landing
dispatch: implementer opus medium — finish round (resume a69db72a9e3f61139)
return: DONE da4ed4f (finish round: precedent in walkthroughs; fenced-tag test with mutation proof; 'moves the other way' corrected; relay stops; untimed decided: lines matched, two decided rows added; dry run 65 lines with --owner)
review: self
verdict: finish round CLEAR — diff read: the five fixes, three files
landed: 2b59dba (merge of b88938f, da4ed4f); Checks 10/10 OK
