---
id: dev-flow-snippet-robustness-ur-py-df-8-d-9385
title: dev-flow snippet robustness (UR_PY, DF-8, DF-13)
short_display_name: dev-flow snippet robustness
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T10:30Z
created: 2026-10-08
updated: 2026-10-09
refs:
  - spike-how-much-inter-plugin-dependency-i-72ef
---

Follow-up F9 from the plugin-dependency spike (72ef), 2026-10-08. Acceptance: as .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md § R3 F9 states, with 01_review-1-fixes.md and 02_review-2-fixes.md applied (Supersedes in order).
verdict: review round 1 CLEAR (must-fix 0; lows: 1 README dev-flow section omits the create-skill edge; 2 the context-guard tip repeats the disclosure instead of folding into it (CLAUDE.md Peer hints); 3 SKILL.md:420 pointer wording, and no word that a tip line may follow the four; nits: 4 parity test assertIn dumps 25 KB, 5 bindings.md:546 sentence dangles after the tip block, 6 brief templates' no-create-skill line reads as an addition); 12/12 Checks green in the worktree; snippets exercised against a planted __main__.py
decided: 2026-10-09T13:15Z cap — a finish round of the six exact-fix leftovers (authority answer 145)
dispatch: implementer opus medium — finish round (resume a2612a58ec3e235a7)

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a2612a58ec3e235a7
return: DONE worktree-agent-a2612a58ec3e235a7 11236a6 (DF-8: spend reader no longer runs python3 "", 'no reader found' plus the context-guard tip under the hint rules; DF-13: create-skill lookup worktree → installed → cache, else a fallback line; checklist key-list parity test; declarations synced; 12/12 Checks)
dispatch: reviewer opus high — review round 1 of 11236a6
agent: reviewer a000d96456cf992b3
