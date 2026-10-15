---
id: work-items-guidance-and-a-guard-so-agent-b2df
title: "work-items: guidance and a guard so agents' git operations cannot destroy or lose a .work-items/ store"
short_display_name: protect work-item stores from git
type: spike
status: todo
priority: 0
created: 2026-10-15
updated: 2026-10-15
refs:
  - operator message 2026-10-15
---

Operator 2026-10-15, after the nested-repo pitfalls: add guidance to the work-items skill that mitigates the named risks (git clean -x/-X/-ff, stash --all, worktrees and clones without the store, commit failures, concurrent writers, embedded-repo surprises, secrets in local history) with examples of safe patterns; investigate, present the plan for review, land before the migration. Also weigh the operator's idea of a guard hook that blocks risky git operations, and how a fix reaches running sessions without /reload-plugins in each. Observed 2026-10-15 (git 2.39.5, scratch repo): git clean -fdx, -fdX and -fxd leave a store that is its own git repo; only -ffdx deletes it. Documented: hook edits in settings files are picked up by the file watcher (https://code.claude.com/docs/en/hooks).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: series .claude-sandbox/investigations/work-items-guidance-and-a-guard-so-agent-b2df/
budget: waived (operator 2026-10-08); spend measured
dispatch: planner opus high — plan the store-safety guidance and guard options
agent: planner a2cdd001d65a75437 round 1
return: planner DONE .claude-sandbox/investigations/work-items-guidance-and-a-guard-so-agent-b2df (00_initial.md; F1 work-items guidance + store-safety.md + tests, F2 dev-flow brief line, F3 new plugin local-data-guard with a PreToolUse deny hook, F4 interim user-settings copy; OQ1-OQ7)
baseline: 4a58600911b3adc583227e7d97a325d7235640b203d290887c3aa6cccde7b2da  00_initial.md c6852e2c818d11b27cd200c86c42991c827bd634ccff84bd17e3abfaa459cb68  INDEX.md 
dispatch: reviewer opus high — plan review round 1 (fresh), in parallel with showing the plan to the operator at their request
decision 233: OQ1 — which guard? — options: (a) a plugin hook only: reaches each session after its next reload | (b) the plugin hook plus an interim copy in your user settings, which running sessions pick up at once; removed by a tracked item once everyone has reloaded [recommended] | (c) guidance only | (z) decide later: guidance lands alone
decision 234: OQ2 — where does the hook live? — options: (a) a new plugin, local-data-guard, whose aim is protecting local-only data from destructive commands [recommended] | (b) inside work-items | (c) inside sandbox, beside its checkout guard | (d) a new plugin under another name | (z) decide later
decision 235: OQ3 — who installs the interim settings hook? — options: (a) the librarian, on your explicit yes at that moment [recommended] | (b) you, by hand, from a printed snippet | (z) decide later
decision 236: OQ4 — does the guard deny or ask? — options: (a) deny, with a message naming the safe alternative: unattended sessions never stall [recommended] | (b) ask | (c) deny only total-loss cases, ask the rest | (z) decide later
decision 237: OQ5 — what does it protect? — options: (a) work-item stores and any folder holding one [recommended] | (b) also every nested repo in a checkout | (c) also a configurable list | (z) decide later
decision 238: OQ6 — backups? — options: (a) a copy inside the repo's .git directory now [recommended] | (b) also an off-machine copy | (c) a wi backup command later | (z) decide later
decision 239: OQ7 — reaching running sessions with the guidance now? — options: (a) a peer message to live sessions plus a relay to claude-sandbox for its container CLAUDE.md [recommended] | (b) the peer message only | (c) neither | (z) decide later
agent: reviewer a465a62b18f0b778d plan round 1
