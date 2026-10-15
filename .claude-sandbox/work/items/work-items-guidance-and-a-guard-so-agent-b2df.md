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
verdict: NEEDS_CHANGES plan round 1 (2 high: the probe never reaches the hook's if-filter; the guard's own git dry run could execute core.fsmonitor from the command's -c or a foreign repo's config before any prompt; 7 medium: bypassPermissions claim not documented for hooks, if-filter misses bash -c/sudo/aliases, aim promises nested repos not built, OQ6 backup question checkable now, two copies both deny the probe, rm -r is beyond the git request, this repo's store is host-tracked not sidecar; 7 low; 3 nits)
dispatch: planner opus high — resume, plan fix round 1 (verbatim report passed)
agent: planner a2cdd001d65a75437 round 2
return: planner DONE .claude-sandbox/investigations/work-items-guidance-and-a-guard-so-agent-b2df (01_review-round-1.md; static guard, no git subprocess; no if filters, every Bash call reaches a fast-exit script; per-copy probes; hooper's restic covers /home/rt/work daily (hooper 9517985); OQ1 and OQ6 reworded)
baseline: 4a58600911b3adc583227e7d97a325d7235640b203d290887c3aa6cccde7b2da  00_initial.md 057d212d0023c838f298c7bded4a9d0bdf5d77c6f91186fe0a9d95941ffa76c4  01_review-round-1.md cf1e94eb8bc83b080e665aecc4f74f65613b0c84495ae6776eb4f9783c616189  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 2
agent: reviewer a465a62b18f0b778d plan round 2
verdict: NEEDS_CHANGES plan round 2 (16 of 18 fixed; 3 must-fix: under -X no -e or :! exclusion keeps the store, so the deny's own safe form deletes it; git clean -f without -d removes untracked items in a host-tracked store; unbounded reads of repo-controlled files (FIFO, /dev/zero) on every Bash call; lows: built-in-named aliases, glob negations, shell aliases, roll-backs out of scope, backups monitor checkable, D4 wording)
dispatch: planner opus high — resume, plan fix round 2
agent: planner a2cdd001d65a75437 round 3
return: planner DONE .claude-sandbox/investigations/work-items-guidance-and-a-guard-so-agent-b2df (02_review-round-2.md; -X never safe with a covered store, positive pathspec safe form; any clean covering a non-ignored store denied; bounded reads; OQ6 narrowed to the operator's backups-alert knowledge)
baseline: 4a58600911b3adc583227e7d97a325d7235640b203d290887c3aa6cccde7b2da  00_initial.md 057d212d0023c838f298c7bded4a9d0bdf5d77c6f91186fe0a9d95941ffa76c4  01_review-round-1.md 4cf41d4b466e84438fb2da508408540967a7942f44095bd1930a22d065eb1387  02_review-round-2.md 5e9c6b2f41d0fb2d72adcb1d1c0b0b8885bd9754b89c8fce4fe5063ad0bc1d13  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 3
agent: reviewer a465a62b18f0b778d plan round 3
verdict: NEEDS_CHANGES plan round 3 (all nine round-2 closed; 2 medium exact: F1 no longer rides the 5f46 push, so push it alone and hold the migration until then; landed store-commit lines need flock or wi's commit before stores nest (F-R5 to d1e9); low: -c alias; nit: provenance)
decided: 2026-10-15T04:48Z cap — only exact text fixes: one plan finish round, read by the librarian (authority answer 145)
dispatch: planner opus high — resume, plan finish round
agent: planner a2cdd001d65a75437 round 4 (finish)
result: DONE plan finish at 03_finish-round.md (27-30 exact; read by the librarian)
verdict: CLEAR plan after 2 fix rounds, 1 finish (series 00-03)
revised: 2026-10-15T04:49Z decision 233 (b) now names that the plugin hook also guards rm -r on a store; 237 tied to the stores-only aim; 238 narrowed: hooper's daily restic already copies /home/rt/work incl. stores (hooper 9517985), the question is whether #backups has been alert-free and a day-old copy is enough — options (a) yes: local copy plus hooper's restic [recommended if no recent alerts] | (b) no: also a wi backup command or a snapshot at each librarian landing in the nested-store build | (c) also other machines | (z) later
decided: 2026-10-15T04:49Z scope — F1 (the work-items guidance) answers no open question, so it builds now; F2-F4 wait on 233-239
target: an agent worktree off main (9cf28cfb); work-items SKILL.md, references/store-safety.md (new), references/format.md, tests/test_store_safety.py
dispatch: implementer opus medium — b2df F1, the store-safety guidance
agent: implementer a1f08393bdfff79d7 F1 round 1
result: DONE F1 round 1 at f02df013 (SKILL.md § Protecting the store, references/store-safety.md, format.md backup clause, tests/test_store_safety.py 25 tests; work-items 440 OK)
dispatch: reviewer opus high — fresh (rule 4), F1
agent: reviewer a5c21442436113174 F1 round 1 at f02df013
verdict: NEEDS_CHANGES F1 round 1 at f02df013 (1 high: 'then -f for -n' reads as a doubled force, and the run deleted a linked worktree in this layout; 4 medium: bundle backup drops uncommitted items, tar restore misplaces a nested-path store, SKILL.md misses the tracked-store rule, the example lint skips SKILL.md and passes unsafe forms; 3 low; 2 nits)
dispatch: implementer opus medium — resume, F1 fix round 1
agent: implementer a1f08393bdfff79d7 F1 round 2
