---
id: spike-how-much-inter-plugin-dependency-i-72ef
title: "spike: how much inter-plugin dependency is baked in, graceful degradation, and a non-naggy hint at better functionality"
short_display_name: plugin dependencies and degradation
type: spike
status: doing
priority: 1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T06:28Z
created: 2026-10-08
updated: 2026-10-08
refs:
  - operator 2026-10-08
---

Operator 2026-10-08T06:28Z, in this session: 'We should probably have a work-item spike to investigate how much inter-dependencies are baked into these plugins, because generally they should work independently and have graceful degradation when the other plugin isn't available. We should also make the user aware that there's improved functionality they COULD be utilizing with the other plugin without being too naggy. What's the best way to do that?' Acceptance: an inventory of every cross-plugin reference (prose and code) with its declared or undeclared status and what happens when the other plugin is absent; gaps against README principle 4; a recommended pattern for a once-only, non-naggy notice of the richer behaviour available with the other plugin (when shown, how often, where recorded, how dismissed); follow-up items per gap.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: plan main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef
budget: 2026-10-08T06:28Z plan waived — operator waiver 2026-10-08T06:28Z (spend still measured)
dispatch: planner opus high — spike plan

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: planner af420e468ce5cb8bb
correction: pushed a store-only commit (answers 184/185, waiver, dispatches) before the Report again; store pushes now wait for the next Report
return: DONE_WITH_CONCERNS series 00_initial.md (inventory; worst gap statusline-hub waits silently, must precede a95a; two-form hint pattern since ~/.claude writes prompt; 11 follow-ups F1-F11; OQ1 adopt pattern + amend principle 4, OQ2 hide-all switch, OQ3 statusline silent, OQ4 checks in kit-dev/tests)
baseline: plan review 1 — 4ff51f7372ea1c4a687e75e2fbf697d655aeac46578655c28a47cd01fb817520 .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md; 
dispatch: reviewer opus high — plan review 1
agent: reviewer a86526c62ee89cf6b
verdict: plan review 1 NEEDS_CHANGES (must-fix 3: hub-wait gap overstated for the live copy and missed for a dead copy; F2 conflates take and yield; prose hints can read the off-switch with echo; lows 4-8, nits 9-11)
dispatch: planner opus high — plan fix round 1 (resume af420e468ce5cb8bb)
return: DONE series 01_review-1-fixes.md (all ten; dead-copy wait now rank 1 high; F2 take vs yield; prose off-switch via echo; CG-5, DF-16 updated)
baseline: plan review 2 — 4ff51f7372ea1c4a687e75e2fbf697d655aeac46578655c28a47cd01fb817520 .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md; eead84f940de0073a99b1a699970aaf1f450595264aa9ee4c0bd9f79db87e339 .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/01_review-1-fixes.md; 
dispatch: reviewer opus high — plan review 2 (resume a86526c62ee89cf6b)
verdict: plan review 2 NEEDS_CHANGES (must-fix 1, down from 3: the dead-copy signal is backwards — a dangling current-hooks link is what an update leaves; nits)
dispatch: planner opus high — plan fix round 2 (resume af420e468ce5cb8bb)
return: DONE series 02_review-2-fixes.md (dead-copy signal is the owning plugin's absence; F10 echo check; DF line numbers)
baseline: plan review 3 — 4ff51f7372ea1c4a687e75e2fbf697d655aeac46578655c28a47cd01fb817520 .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md; eead84f940de0073a99b1a699970aaf1f450595264aa9ee4c0bd9f79db87e339 .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/01_review-1-fixes.md; e3535bf42c099a88de4a3580e0a5749f1b38ea1eb4d367f22b351457e82af572 .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/02_review-2-fixes.md; 
dispatch: reviewer opus high — plan review 3 (resume a86526c62ee89cf6b)
