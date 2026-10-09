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
- next: build waits on decision 207 (probe runs with the operator present); OQ1 blocks only if O5 can't separate -p runs
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
verdict: plan review 2 NEEDS_CHANGES (must-fix 2: --setting-sources project,local doesn't keep installed plugins out — defaultEnabled defaults to true, so set enabledPlugins false for every installed key plus syncClaudeAiPlugins false in the --settings file, and back up settings.json first; OQ4's default removes F2's reviewed first-run clause ahead of the operator — default to keeping it behind the switch; nits: tip duplicates the disclosure, attended runs before shown)
dispatch: planner opus high — plan fix round 2 (resume a6717d91dad7541ab)
return: DONE 02_review-2-fixes.md (probe --settings disables every installed plugin and synced plugins, enables only the scratch one; settings.json backed up with cp -p; hash guard kept; OQ4 default keeps F2's clause behind the switch; nits)
baseline: plan review 3 — ec847eb9f594e10188c8675004f9966805b9a4b6910c6fea4928d6750f225711 .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/00_initial.md; 1ce9e10e8da5d1fa459acf64a0946e21fb5072e338e38483340e25f05ac9340a .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/01_review-fixes.md; dd00bcda844b497fee643c1114e0e8918fe695082edee03a8680e3d3d6ef6ace .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/02_review-2-fixes.md; 4daa288604c1953561bc03305c6f3e461d5f9f65945c2d5cd93f740e5f5f8a76 .claude-sandbox/investigations/peer-hint-helper-and-first-adopters-4bd4/INDEX.md;
dispatch: reviewer opus high — plan review 3 (resume a9c964d98c306d46e)
verdict: plan review 3 CLEAR (low 1: positive guard — system/init plugins list holds only the scratch plugin and every hook_started names a probe hook, else stop; nit 2: unset CLAUDE_CODE_PLUGIN_DIRS on each probe)
findings: carried — plan review 3 low 1 and nit 2, into the build's acceptance
decided: 2026-10-09T08:34Z trust — the build waits for the operator: it runs nested headless sessions against this host (its global config and a backed-up settings.json), which is theirs to allow and best done with them present; raised as decision 207
decided: 2026-10-09T08:34Z scope — OQ2: the factor-analysis and librarian-mode hint steps (KD-2, DF-9) move onto F3 (d0b0) and F4 (64c7), which are not landed; written on those items
decision 207: May the peer-hint build run its five probe sessions (nested headless Claude Code runs in a scratch folder) against this host? — options: (a) yes, with the planned isolation, while you are around to see the result [recommended] | (b) yes, unattended | (c) no: ship the helper without the probes, hook hints off until a documented signal exists | (z) decide later (the build waits)
  raised: 2026-10-09T08:34Z
  why ask: trust — the runs use your account, write the global config's entry for the scratch folder, and could touch the shared settings.json if isolation failed
  what: each run starts from an empty folder, turns off every installed plugin in a one-off settings file, enables only a scratch test plugin, checks afterwards that nothing else loaded, and hashes your settings.json before and after (a backup is taken first); the runs confirm what the docs say and find how a headless run can be told apart from you
  impact: Effect → the helper ships with observed facts, hints fire only in sessions you attend · Wait: blocks the peer-hint build · reach: this host's config, briefly · undo: restore the backup if the guard fires · cost: five short runs on your plan
decision 208: The hub's first-run message names the statusline plugin and its install command once, just because statusline is absent — which the new principle 4 forbids. Keep it or remove it? — options: (a) remove it; hint statusline only when its absence actually costs you something [recommended] | (b) keep it, behind the hint switch (the build's default) | (z) decide later (it stays, behind the switch)
  raised: 2026-10-09T08:34Z
  why ask: precedent — an earlier reviewed change (F2) required the message; the doctrine you adopted with 190 now forbids it; only you resolve the two
  impact: Effect → no install pitch at install time · Wait: none, the build keeps it behind the switch · reach: every new statusline-hub user · undo: one message edit · cost: none
shown 207: 2026-10-09T08:34Z chat
shown 208: 2026-10-09T08:34Z chat
shown 207: 2026-10-09T08:57Z page
shown 208: 2026-10-09T08:57Z page
note: 2026-10-09T08:59Z DF-9 returns to this item's stage 2 (not 64c7): the librarian-mode hint points at dev-cycle references/bindings.md § Peer hint, which this item adds; text per 00 § DF-9 ('context-guard adds the context gate and checkpoints'). KD-2 stays with d0b0 (inline, no pointer needed)
