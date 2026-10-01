---
id: decisions-a-general-shape-for-decision-c-90bc
title: "decisions: a general shape for decision classes, not tags fitted to the cases analyzed so far"
short_display_name: general shape for decision classes
type: spike
status: doing
priority: 1
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-01T07:13Z
created: 2026-10-01
updated: 2026-10-01
refs:
  - operator 2026-10-01, decision 134
---

Operator 2026-10-01 on decision 134 (keep the 19 class-tag spellings?), verbatim: '134 - these seem pretty specific to the data you happen to have analyzed. Investigate a better shape for this'. A dig into on 134: investigate a shape for the decided-alone / raised classes (decide-alone.md § The line, § Class names) that generalizes beyond the cases the 19 tags were drawn from — e.g. a few orthogonal axes (reversibility, reach, authority, what kind of thing changes) instead of a flat list — and how stored lines would carry it and migrate. Result comes back on decision 134 with options. Plan only, nothing lands.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-01 claimed by Kyle-McFarlane@401123cbad11
dispatch: planner opus high — spike plan (dig into on decision 134)
agent: planner a8587db799d0fa021 round 1
return: planner PLAN_READY .claude-sandbox/investigations/90bc-decision-classes/ (00-02)
dispatch: reviewer opus high — plan review round 1
agent: reviewer af72c7119ecda3329 round 1
verdict: NEEDS_CHANGES round 1 (plan)
findings:
  1. [high] 02:76-78,82,87 — closes the trade-off list (reasons 2-7 only) and drops minor-design's fourth term; UI-layout and perf-vs-memory choices become decided alone; fix: an open last reason (trade-off/weighable), restore the term, add both cases
  2. [medium] 02:110,119,211-213 — cap record → spend breaks resume.md:226's key; the store's decided cap round is under answer 137 not 114; 5bdd will make such rounds default; stop-and-carry spends nothing; fix: keep a dedicated cap/round kind or key resume on something tag-independent; note 5bdd
  3. [medium] 02:191-193 — row conditions dropped (ruled-rule-case's narrowing/policy rule, table-placement's no-table, rule-change's undo exception, relay's batchable ok N-M; relayed answers homeless); fix: a table of all 19 rows' conditions and their new homes; a relayed: marker
  4. [medium] 02:69 — contract lacks interface/behaviour (reply 112); library default changes and webhook timing fall to design; fix: "a name, format, interface or behaviour something else relies on"; test cases not used in design
  5. [medium] 02:72 vs 88 — an existing kind with no placement rule matches no reason; fix: precedent covers where something lives unless one standing rule settles it
  6. [medium] 02:190-202,240; INDEX:97 — file list misses decide-alone § Trivial documentation (dabd rewriting it) and § The Report; section count; residue grep can never be empty and misses tags; fix accordingly
  7. [medium] 02:27-33,142-161 — operator-level changes hidden in planner calls (promotion key, scope merge, design widening, trade-off closing); state them in (a)'s impact or OQ3
  8-11. [low/nit] authority word collides with authority: field (offer "yours"); fallback: doubt raises; name the migration trigger (86e1 gap); word count 14 and provenance
dispatch: planner opus high — resume (plan fix round 1)
agent: planner a8587db799d0fa021 round 2
return: planner PLAN_READY — serial 03_review-fixes.md (all 11 findings), INDEX rewritten
dispatch: reviewer opus high — resume (plan review round 2)
agent: reviewer af72c7119ecda3329 round 2
