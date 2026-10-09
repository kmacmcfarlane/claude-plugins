---
id: peer-hint-helper-and-first-adopters-4bd4
title: peer-hint helper and first adopters
short_display_name: peer-hint helper
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T07:47Z
created: 2026-10-08
updated: 2026-10-09
refs:
  - spike-how-much-inter-plugin-dependency-i-72ef
---

Follow-up F10 from the plugin-dependency spike (72ef), 2026-10-08. Acceptance: as .claude-sandbox/investigations/spike-how-much-inter-plugin-dependency-i-72ef/00_initial.md § R3 F10 states, with 01_review-1-fixes.md and 02_review-2-fixes.md applied (Supersedes in order). After F1. Waits on decisions 190 and 191.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: planner opus high — plan (feature; F10 of the 72ef spike; answers 190 a, 191 a; doctrine landed with bdff), scratch scratchpad/4bd4-plan/
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: planner a6717d91dad7541ab
return: DONE series 00_initial.md (peer_hint.py copied byte-identical into context-guard and statusline-hub with a kit-dev identity test; sync SessionStart/UserPromptSubmit only; first adopters; probes O1-O5 owed, 2.1.293; lands after 193f; OQs: entrypoint as the -p signal (observed, undocumented), F3/F4 hint steps, per-peer switch wording)
baseline: plan review 1 — ec847eb9f594e10188c8675004f9966805b9a4b6910c6fea4928d6750f225711 .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/00_initial.md; 0a2999b15fdafb1cc8d0b437a63718026aac8672b18b411ef4d1d89fbb880104 .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/INDEX.md;
dispatch: reviewer opus high — plan review 1, scratch scratchpad/4bd4-review/
agent: reviewer a9c964d98c306d46e
verdict: plan review 1 NEEDS_CHANGES (high 1: probes load the host's settings and plugins, which can rewrite the host settings.json; medium 2-7: nested -p inherits the session's env, the entrypoint vocabulary is documented on the monitoring page and labels lack versions, OQ1's fallback contradicts the acceptance, WI-2 hint shape off spec, the hub's first-run install clause breaks principle 4, the kit-dev tripwire is beyond acceptance and fails; lows 8-14, nit 15)
dispatch: planner opus high — plan fix round 1 (resume a6717d91dad7541ab)
return: DONE 01_review-fixes.md (probes isolated: --setting-sources project,local, host settings.json hashed before/after; O5 three ways; entrypoint labels documented/observed with versions; OQ1 three options, build stops if O5 can't separate -p; WI-2 shape; hub first-run tip OQ4, default remove; tripwire dropped; shown pre-check; 193f constraints; tests)
baseline: plan review 2 — ec847eb9f594e10188c8675004f9966805b9a4b6910c6fea4928d6750f225711 .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/00_initial.md; 1ce9e10e8da5d1fa459acf64a0946e21fb5072e338e38483340e25f05ac9340a .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/01_review-fixes.md; d5b2449950336c17288779470f8aaf25122e48fc168f61a382b4bd9d95d2503d .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/INDEX.md;
dispatch: reviewer opus high — plan review 2 (resume a9c964d98c306d46e)
