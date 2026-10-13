---
id: declaration-sweep-declare-every-soft-cro-eef5
title: "declaration sweep: declare every soft cross-plugin edge"
short_display_name: declaration sweep of soft edges
type: chore
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-12T23:38Z
created: 2026-10-08
updated: 2026-10-12
refs:
  - spike-how-much-inter-plugin-dependency-i-72ef
---

Follow-up F7 from the plugin-dependency spike (72ef), 2026-10-08. Acceptance: as .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md § R3 F7 states, with 01_review-1-fixes.md and 02_review-2-fixes.md applied (Supersedes in order).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
target: as 72ef F7 (with 01, 02 applied): every soft edge in the inventory agrees across source plugin.json, catalog cell and README section, marketplace.json matches plugin.json; DF-7 pointer to the hub's hook-contract.md and statusline-hub owner labels; SH-4 and WI-4 as F7 says; test_declared_edges excuses shrink only; all Checks green
dispatch: implementer opus medium — build, run alone (wide README edits)
agent: implementer a561dcc2863a9c6b3
return: DONE 942a05e; 12/12 OK; CR-4 already done; CG-7 and SH-3 declared, WI-4 inlined (edge gone), DF-7/SH-4/KD-4/KD-5/WI-5 done; ALLOWED 20 → 11, UNDECLARED 4 → 0
dispatch: reviewer opus high — review round 1 of 942a05e
agent: reviewer a6043ac544148d699
verdict: review round 1 CLEAR (must-fix 0; lows: L1 hook-contract § 12 is a hand copy of sensor-contract with nothing keeping them in step, and omits unknown-keys; L2 WI-4 reason incomplete (a tracked store is a stale copy); L3 the agent: lines are also written by the research skills; nits: repo-map test lines, CG-8 not named; 41 edges re-measured, 3 mutations caught, code files docstring-only)
decided: 2026-10-13T03:00Z cap — a finish round of L1 (the sensor-contract cross-note and the unknown-keys line), L2, L3 and nit 2 (authority answer 145)
dispatch: implementer opus medium — finish round (resume a561dcc2863a9c6b3)
