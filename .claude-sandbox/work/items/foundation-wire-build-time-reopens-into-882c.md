---
id: foundation-wire-build-time-reopens-into-882c
title: "foundation: wire build-time reopens into dev-cycle's build"
short_display_name: foundation build-time reopens
type: feature
status: doing
priority: 3
parent: foundation-follow-ups-build-time-reopens-f3d1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-12T19:47Z
created: 2026-10-09
updated: 2026-10-12
refs:
  - spike-a-skill-for-green-field-foundation-5f2d
---

From the 5f2d series 02 § G4 and its Files to Modify, filed by the librarian 2026-10-09 (f3d1). A finding during a feature's build that changes a phase-1 or phase-2 foundation artifact is today raised by hand only; wire dev-cycle's implementer and reviewer briefs to raise it (the foundation skill's moves table, Reopen requirements / Reopen architecture). Acceptance: the briefs name the reopen and where it goes; the foundation skill's moves table points at it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
target: dev-cycle's implementer and reviewer briefs raise a build-time reopen (a finding that changes a phase-1 or phase-2 foundation artifact) to the foundation moves table, Reopen requirements or Reopen architecture; the moves table points back
dispatch: implementer opus medium — build
agent: implementer a0145b26351bddd68
return: DONE ce34197; 12/12 OK; REOPEN: line in agent-brief (OPEN QUESTIONS) and review-brief (NOTES, step 9); bindings § Decisions "A foundation reopen" (a stop / b carry / c answer locally); reopen: carried record line, separate from findings: carried because resume.md Group D reads that as Step 4.3 done; moves.md, state.md, foundation SKILL.md table row
dispatch: reviewer opus high — review round 1 of ce34197
agent: reviewer a0abf135be56981e0
verdict: review round 1 NEEDS_CHANGES (must-fix 4: high 1 — dev-cycle SKILL.md never tells the orchestrator to act on a REOPEN: line (Step 4.4 lists what escalates, NOTES are not recorded), so a build lands with the reopen surfacing only after the merge; high 2 — resume reads no reopen decision at S4/S7, so a build the operator stopped lands on resume; medium 3 — artifact list incomplete and no phase-1/phase-2 split in the brief; medium 4 — the step fires on F0, whose job is writing the artifacts; lows: how the filler decides the condition, option (c) undefined for an implementer line, why ask + (z) not named; nit: reopen: missing from resume rider list)
decided: 2026-10-12T21:00Z design — an item stopped under (a) is re-dispatched from its record once the reopen passes its gates, with the changed artifact named in its acceptance, through a full review; noted in bindings beside option (a)
dispatch: implementer opus medium — fix round 1 (resume a0145b26351bddd68)
return: DONE c91512e (fix round 1); 12/12 OK; dev-cycle SKILL.md 4996 words
dispatch: reviewer opus high — review round 2 of c91512e (resume a0abf135be56981e0)
