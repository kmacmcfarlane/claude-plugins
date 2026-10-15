---
id: wi-default-store-work-items-git-ignored-5f46
title: "wi: default store .work-items/, git-ignored on init; env vars renamed to WORK_ITEMS_"
short_display_name: wi store .work-items, WORK_ITEMS_ env
type: feature
status: todo
priority: 1
created: 2026-10-15
updated: 2026-10-15
refs:
  - answer 227, operator 2026-10-15
---

Answer 227 b (operator 2026-10-15): the default work-item store is .work-items/ at the repo root, git-ignored when established, because it matches the plugin's name and works without claude-sandbox. Also rename wi's env vars to the WORK_ITEMS_ prefix (WI_ROOT -> WORK_ITEMS_ROOT, WI_OWNER -> WORK_ITEMS_OWNER, ...). Decided alone: the old WI_* names and the .work/ and .claude-sandbox/work/ stores keep working as deprecated fallbacks with a one-line warning, so no repo breaks mid-migration. Acceptance: wi finds .work-items/ first; the estate sweep includes it; every skill and reference naming WI_ROOT or the old store paths is updated; tests; README/CLAUDE.md layout. Coordinate with claude-sandbox decision 115.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: series .claude-sandbox/investigations/wi-default-store-work-items-git-ignored-5f46/
budget: waived (operator 2026-10-08); spend measured
dispatch: planner opus high — plan the store default and env-var rename (answer 227 b)
agent: planner ac82427bf27ca5eb5 round 1
return: planner DONE .claude-sandbox/investigations/wi-default-store-work-items-git-ignored-5f46 (00_initial.md; F1 env rename, F2 .work-items default and lookup order, F3 dev-flow, F4 context-guard, F5 ralph and ownership; 3c06 lands first as built; OQ1 this repo's store, OQ2 nested .git store)
baseline: 66828c2369cb833c7af58dcba081aea7c108e92be6a81ff72a80796921933e6e  00_initial.md 476e811190bfe5bd27743d53602dfd56b507ed898043c06bfb8475446754e878  INDEX.md 
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer ada90b0ef30b65b3c plan round 1
verdict: NEEDS_CHANGES plan round 1 (8 medium: two-store check never runs with an exported root; a worktree init creates a stray store; test harness leaks old names; first-start sets only the new name; librarian's store-and-git premise is a doctrine question (new OQ3); OQ1 misses a private versioned option and the decision-numbering reset; 3c06 must be a hard prerequisite; the move recipe empties other clones' stores; 6 low; 1 nit)
dispatch: planner opus high — resume, plan fix round 1
agent: planner ac82427bf27ca5eb5 round 2
return: planner DONE .claude-sandbox/investigations/wi-default-store-work-items-git-ignored-5f46 (01_review-round-1.md; all 15 applied; OQ1 gains (d) private versioned and the numbering-reset cost, rec (c) then (d) else (b); new OQ3 librarian first-start --track, rec (b))
baseline: 66828c2369cb833c7af58dcba081aea7c108e92be6a81ff72a80796921933e6e  00_initial.md 08359e578cb99edc80ad839405eb030487c67eb013c04e71e2a0257d6c226260  01_review-round-1.md 7c6651b0e5029a28a47c78cb9d1772df46c7236d42a8ece9c90a802f5e202db2  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 2
agent: reviewer ada90b0ef30b65b3c plan round 2
verdict: CLEAR plan round 2 (low: the claimant helper strips first, then sets the new root; nits: _race_claim name, (z) on OQ2 and OQ3; carried into the build briefs)
findings: carried — build F1 after 3c06 lands (same files); the round-2 low and nits go into F1's brief
decision 229: OQ1 — this repo's own store: when does it move, and in what form? — options: (a) move to .work-items/ and git-ignore it: no off-machine copy, and a lost store restarts decision numbering, which collides with numbers already cited | (b) move it and keep it tracked | (c) stay at .claude-sandbox/work/ until claude-sandbox's decision 115 is settled, then (d) if 115 provides it, else (b) [recommended] | (d) a private versioned store (its own git repo, or a sidecar), only if 115 picks that shape | (z) decide later: it stays where it is
decision 230: OQ2 — a .work-items/ that is its own git repo: should wi support it? — options: (a) leave it as is; wi already refuses to record such a store as ignored [recommended] | (b) make init add it to the host .gitignore and treat it as tracked by default, as a follow-up if 229 picks (d) | (z) decide later: (a) holds meanwhile
decision 231: OQ3 — does the librarian's first start create a tracked store, or follow the new git-ignored default? — options: (a) follow the ignored default: its decision records stay on this machine | (b) pass --track: the store is the librarian's memory and the source of decision numbers other repos cite [recommended] | (c) ask once per repo at opt-in | (z) decide later: the ignored default holds meanwhile
findings: carried from 3c06 review 2 — keep the sidecar refusal and its format.md bullet when the default moves; test that a .claude-sandbox/work/ sidecar store is still refused git-ignored; fix choose_tracking's docstring opening
note: 2026-10-15T02:50Z claude-sandbox's amended migration plan (04) gates on F1-F4 and relies on: init --no-track on a moved existing store records ignored and keeps items; .work-items/ found first, two stores warned; --no-track's host .gitignore line; F3/F4 shipped with F1/F2; a probe for the new wi (wi --help names WORK_ITEMS_ROOT). The push waits until F1-F4 all land, so they ship together
target: an agent worktree off main (d39e0e7c); work-items wi.py, SKILL.md, format.md, provider-interface.md, test_wi.py, test_estate.py
dispatch: implementer opus medium — F1, the WORK_ITEMS_ env rename, per the series
agent: implementer a308b4bc437e8e143 F1 round 1
result: DONE F1 round 1 at aa37b2e9 (_env helper, notices only from prime/lint/init, help names WORK_ITEMS_ROOT, harness scrub, EnvNamesTest and HelpNamesEnvTest; 391 OK)
dispatch: reviewer opus high — fresh (rule 4), F1
agent: reviewer af7353ff071081892 F1 round 1 at aa37b2e9
verdict: CLEAR F1 round 1 at aa37b2e9 (nits: 'old name is set' wording in format.md:237-244 and SKILL.md:70; test_estate.py:469 env scrub — carried into F2's brief)
landed: F1 locally bb9add15 (Checks 12/12 OK); push held until F1-F4 land (told claude-sandbox)
target: an agent worktree off main (bb9add15); work-items wi.py, SKILL.md, format.md, work-review SKILL.md, README.md, tests
dispatch: implementer opus medium — F2, .work-items/ default, lookup order, two-store check, init default, worktree guard, moving-a-store recipe
agent: implementer aeaab9c573ce82b95 F2 round 1
relayed: 2026-10-15T03:37Z from claude-sandbox (its decisions 117 a, 118 a, operator answers given there): every .work-items/ store gets its own local git repo with no remote, the host ignores /.work-items/; wi treats such a store as tracked, commits item changes there under wi's lock, and init sets it up; librarian stores follow the same rule. Binds nothing until the operator confirms here; bears on 229 (d), 230 (b) and 231
decision 232: Confirm the relayed rule that every .work-items/ store has its own local git repo (no remote), which wi treats as tracked and commits each item change into, under its lock, and which init sets up; and when it lands — options: (a) confirm, built as a follow-up feature after the four parts claude-sandbox waits on, which ship as planned; the migration creates the nested repo itself meanwhile [recommended] | (b) confirm, folded into the store-default part now: everything waits for it, the migration included | (c) do not confirm: stores stay plain git-ignored folders | (z) decide later: the four parts ship; the nested repo waits
result: DONE F2 round 1 at aa6a228e (lookup order, old-location and two-store notices by real path, worktree guard, estate, init default .work-items, docs incl. § Moving a store; claude-sandbox's three behaviours tested; 413 OK)
dispatch: reviewer opus high — fresh (rule 4), F2
agent: reviewer a0fba032061992e48 F2 round 1 at aa6a228e
answer 232: a, in chat 2026-10-15 after the pitfalls were shown, verbatim (excerpt): "So, let's just stay the course and let the change land to create the embedded origin-free repo for .work-items and run the migration." (read as: (a) confirmed; claude-sandbox's 117 a and 118 a are confirmed here; the nested-repo support lands as a follow-up after F1-F4; this settles 229 (d), 230 (b) and 231)
verdict: CLEAR F2 round 1 at aa6a228e (lows: worktree guard names the git dir when the common dir is not .git; no ignored-to-ignored move recipe, the migration's own case; recipes end with a bare lint; nits: GIT_CEILING_DIRECTORIES in one test, long lines)
decided: 2026-10-15T03:57Z cap — lows and nits with exact fixes: one finish round, read by the librarian (authority answer 145)
dispatch: implementer opus medium — resume, F2 finish round
agent: implementer aeaab9c573ce82b95 F2 round 2 (finish)
result: DONE F2 finish at cc3a4f64 (all five exact; read by the librarian)
verdict: CLEAR F2 after 0 fix rounds, 1 finish at cc3a4f64
landed: F2 locally e9ce3961 (Checks 12/12 OK)
dispatch: implementer opus medium — F3 dev-flow store lookups (worktree off e9ce3961)
dispatch: implementer opus medium — F4 context-guard rehydrate and checkpoint (worktree off e9ce3961)
dispatch: implementer opus medium — F5 ralph backlog-yaml and ownership claim_check (worktree off e9ce3961)
agent: implementer a5e878c739c73bc30 F3 round 1
agent: implementer a8d929df520e959a2 F4 round 1
agent: implementer a659b29ac5cfe5ebe F5 round 1
result: DONE F5 round 1 at 809f6ad1 (ralph backlog-yaml loop exports both names; claim_check STORES with .work-items first; checks.md; test; claim-md 72 OK)
dispatch: reviewer opus medium — F5 (small, two plugins)
agent: reviewer a34c31257d1312d48 F5 round 1 at 809f6ad1
result: DONE F4 round 1 at 45696581 (rehydrate STORE_DIRS, env precedence, store-only commits at all three; checkpoint loop exports both, skip-commit clause for an ignored store; handoff-format, design-rationale; 757 OK)
dispatch: reviewer opus high — fresh (rule 4), F4
agent: reviewer a392a869cf34323d1 F4 round 1 at 45696581
result: DONE F3 round 1 at e7f140b3 (both lookup copies, first-start --no-track per answer 232 a, brief Store: lines, skip-commit clauses, durable wording; test_store_lookup.py; dev-flow 101 OK; opt-in.md:51 Scope note deferred to this repo's store move)
dispatch: reviewer opus high — fresh (rule 4), F3
agent: reviewer a30965ea7fa25cb55 F3 round 1 at e7f140b3
verdict: CLEAR F5 round 1 at 809f6ad1 (nit: checks.md:29-30 wording; declined, optional)
verdict: NEEDS_CHANGES F4 round 1 at 45696581 (1 medium: the skip-commit clause asks the host repo, so a sidecar store, which wi records tracked, and a nested-repo store are wrongly skipped; ask the repo holding the store and commit there — the same fix applies to F3's copies; 2 low: design-rationale wording under 232 a, Lean OPEN line; 2 nits)
dispatch: implementer opus medium — resume, F4 fix round 1
agent: implementer a8d929df520e959a2 F4 round 2
verdict: CLEAR F3 round 1 at e7f140b3 (L1 ending-the-session tracked wording; nits opt-in Scope, exit 128, first-start line); plus F4's medium applies here: the skip-commit clause must ask the repo holding the store, not the host (a sidecar store is host-ignored yet tracked)
decided: 2026-10-15T04:31Z cap — one finish round on F3 with F4's exact clause, L1 and the nits (authority answer 145)
closed 229: superseded by answer 232 (d)
closed 230: superseded by answer 232 (b)
closed 231: superseded by answer 232 (librarian stores follow the ignored default, history in their own repo)
dispatch: implementer opus medium — resume, F3 finish round
agent: implementer a5e878c739c73bc30 F3 round 2 (finish)
result: DONE F4 round 2 at d44c2cb8 (clause asks the repo holding the store at 4a and 4a½; design-rationale; Lean OPEN; secret guard; reflow; suites OK)
dispatch: reviewer opus high — resume, F4 round 2
agent: reviewer a392a869cf34323d1 F4 round 2 at d44c2cb8
result: DONE F3 finish at 5fe1515b, main merged as a35d3f06 (clause asks the repo holding the store at every site; exact; read by the librarian)
verdict: CLEAR F3 after 0 fix rounds, 1 finish at a35d3f06
