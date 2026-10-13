---
id: foundation-consult-claim-md-skill-in-pha-286d
title: "foundation: consult CLAIM.md skill in phase 1"
short_display_name: foundation consults claim-md
type: feature
status: done
priority: 3
parent: foundation-follow-ups-build-time-reopens-f3d1
created: 2026-10-09
updated: 2026-10-09
closed: 2026-10-09
refs:
  - spike-a-skill-for-green-field-foundation-5f2d
---

From the 5f2d series 00 § Files to Modify, follow-ups, filed 2026-10-09 (f3d1); 53d7 step 2 (the ownership plugin's claim-md skill) has landed. Acceptance: the foundation skill's phase 1 writes or proposes scope through the ownership:claim-md skill when listed, and G2 checks contracts against its Boundaries and Interfaces; without it, the plain fallback the skill already states, disclosed; edges declared.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
decided: 2026-10-09T15:40Z scope — no separate plan: the 5f2d series (00 § Files to Modify follow-ups, 00:107-110, 00:380) is the plan for this wiring
target: foundation phase 1 writes or proposes scope through ownership:claim-md when listed; G2 checks contracts against its Boundaries and Interfaces; without it the plain fallback, disclosed; edges declared; all Checks green
dispatch: implementer opus medium — build
agent: implementer aac8fa75aac1fadce
return: DONE ec38341; 12/12 Checks OK; judgement: claim approved inside G1, F0 writes it; Scope line drops none; a G3 re-read line added beyond acceptance; hint shaped like claim-md and factor-analysis
dispatch: reviewer opus high — review round 1 of ec38341
agent: reviewer ae00bc0c31c8b8e3e
verdict: review round 1 NEEDS_CHANGES (must-fix 1: medium — F0 writes through claim-md's write mode with no way to use G1's approval, so a build sub-agent blocks or writes proposed; lows: upkeep draft path unstated; Interfaces asked before contracts exist (narrow fix here, the reopen question filed as foundation-is-filling-a-claim-interfaces-8ee2); hint claims "written on your approval" which the fallback also gives; nits: a 121-char line with an ambiguous aside, answer-mode step out of order; G3 re-read line ruled justified)
dispatch: implementer opus medium — fix round 1 (resume aac8fa75aac1fadce)
return: DONE 7ef5ce2 (fix round 1); dev-flow and kit-dev Checks OK
dispatch: reviewer opus high — review round 2 of 7ef5ce2 (resume ae00bc0c31c8b8e3e)
verdict: review round 2 CLEAR (must-fix 0; lows: the no-store case names a decision line that does not exist; SKILL.md restates state.md; nit: "and defining side" redundant)
decided: 2026-10-09T17:00Z cap — a finish round of the three exact fixes (authority answer 145)
dispatch: implementer opus medium — finish round (resume aac8fa75aac1fadce)
verdict: finish round CLEAR — diff read: no-store clause, SKILL.md points at state.md, "and defining side" dropped
landed: c37a3a7 (merge of ec38341..34df253); Checks 12/12 OK; cc_scan clean
- 2026-10-09 done
