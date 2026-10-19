---
id: wi-a-work-items-store-with-its-own-local-d1e9
title: "wi: a .work-items/ store with its own local git repo, committed under wi's lock"
short_display_name: wi nested store repo
type: feature
status: done
priority: 1
created: 2026-10-15
updated: 2026-10-19
closed: 2026-10-19
refs:
  - answer 232 a
---

Answer 232 a (operator 2026-10-15; claude-sandbox 117 a, 118 a): every .work-items/ store gets its own local git repo with no remote; the host ignores /.work-items/. wi treats such a store as tracked, init sets the repo up, and wi commits each item change into it under its lock; a failed commit never loses the item write (save first, warn), with a fallback identity only when git var GIT_AUTHOR_IDENT fails; lint warns about git clean -ff near a store. Builds on 5f46.

## Handoff
- doing: F2 building (wi commit + sites); F1 on local main unpushed
- next: F2 review; then F3, F5, F4 relays; one push
- blocked: —
- learned: —
target: series .claude-sandbox/investigations/wi-a-work-items-store-with-its-own-local-d1e9/
budget: waived (operator 2026-10-08); spend measured
dispatch: planner opus high — plan the nested store repo (answer 232 a)
agent: planner ac5d8b6d969db2d50 round 1
note: F-R1..F-R5 from b2df handed to the d1e9 planner (F-R5: landed store commits under flock or wi before stores nest)
return: planner DONE .claude-sandbox/investigations/wi-a-work-items-store-with-its-own-local-d1e9 (00_initial.md; store.yaml repo: own; hardened store git runner with ceiling and hooksPath=/dev/null; new wi commit verb replacing every landed store-commit site (closes b2df F-R5, two more sites found); init creates or adopts; per-change commits; F1-F5 with F4 a relay; OQ1 names, OQ2 migration waiting)
baseline: 57b8bc4b87f6de3a6edf8c70a9c585107fbef27fd98b87bdf3eb1699e0848210  00_initial.md f5a5db2660075459e4f2c7aa95a894cef89add67fbdc66632a789305b90c0724  INDEX.md 
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer a3b8f5b2c3a80ea24 plan round 1
verdict: NEEDS_CHANGES plan round 1 (7 must-fix: fixed pathspec list fails on a store with no archive/; custody reads run unpinned git (fsmonitor); attribute-selected clean filters run under every pin; own-but-unrecorded store gets unhardened commits; uncommitted as a lint problem breaks the lint-then-commit rule; the plan ignores claude-sandbox's agreed hold; A9 notes and Q1 (iii) also need relaying; 6 low incl. lock deadline, journal sources, idempotent rerun, cc_scan before wi commit; 1 nit)
dispatch: planner opus high — resume, plan fix round 1
agent: planner ac5d8b6d969db2d50 round 2
return: planner DONE .claude-sandbox/investigations/wi-a-work-items-store-with-its-own-local-d1e9 (01_review-round-1.md; all 14 applied plus blast-radius line; OQ1 names (rec keep --no-track), OQ2 rec keep the hold)
baseline: 57b8bc4b87f6de3a6edf8c70a9c585107fbef27fd98b87bdf3eb1699e0848210  00_initial.md 069ab639f391e5af8d26b3aaed83087b9a48f9a86b5496f88e4ef25177cf4de4  01_review-round-1.md 641b4a26479a6d2f7d836b60a4df2d18e71f7cbb67b85d31cc19cf908d3b4d98  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 2
agent: reviewer a3b8f5b2c3a80ea24 plan round 2
verdict: NEEDS_CHANGES plan round 2 (12 of 14 closed; 2 medium exact: attribute files deeper than the store shape or index-only still run a filter; check-ignore refuses GIT_LITERAL_PATHSPECS so custody goes silent; 3 low exact: validation before the lock with a 2 s timeout, a dedicated top-of-repo store keeps attributes, relay the lift only at the push; nit; note: scrub GIT_ATTR_SOURCE, check attr.tree on newer git)
dispatch: planner opus high — resume, plan fix round 2
agent: planner ac5d8b6d969db2d50 round 3
return: planner DONE .claude-sandbox/investigations/wi-a-work-items-store-with-its-own-local-d1e9 (02_review-round-2.md; six exact fixes; attr.tree risk recorded)
baseline: 57b8bc4b87f6de3a6edf8c70a9c585107fbef27fd98b87bdf3eb1699e0848210  00_initial.md 069ab639f391e5af8d26b3aaed83087b9a48f9a86b5496f88e4ef25177cf4de4  01_review-round-1.md 5e7df59960dcfc76f565fa0c23bb8b99f5943f1b3ec2c9ab9d194cd6a2af1fee  02_review-round-2.md daa906d3241f6821b3948939c3bc2cd272cc222dd5a03fa24becd258b2b38666  INDEX.md 
dispatch: reviewer opus high — resume, plan review round 3
agent: reviewer a3b8f5b2c3a80ea24 plan round 3
verdict: CLEAR plan round 3 (low: pin -c attr.tree=<empty tree> in the runner, no version check needed; nit: skip the GIT_ATTR_SOURCE test below the git that reads it — both carried into F1's brief)
findings: carried — D2 pins add -c attr.tree=4b825dc642cb6eb9a060e54bf8d69288fbee4904 (https://github.com/git/git/blob/master/Documentation/config/attr.adoc); the GIT_ATTR_SOURCE test is skipped below the git that reads it
decision 240: OQ1 — names for a store with its own repo — options: (a) keep --no-track; store.yaml records tracking: tracked plus repo: own (the flag describes the host, the record the store's own repo) [recommended] | (b) a new --own-repo flag | (c) a third value, tracking: own-repo | (z) decide later: F3 builds (a)
decision 241: OQ2 — lift claude-sandbox's hold (no nested store repo before d1e9 lands)? — options: (a) lift it now: claude-sandbox creates the repos by hand, adopted later with history kept | (b) keep it: only history between a store's move and d1e9's push is lost [recommended] | (z) decide later: the hold stands
target: an agent worktree off main (3e1b96bb); work-items wi.py and tests (F1)
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus high — d1e9 F1: own-repo recognition, the hardened store git runner, prime/lint checks (security-sensitive)
agent: implementer a00b3d4405bafe651 F1 round 1
result: DONE F1 round 1 at 0582a34a (store_repo_state, _store_git with every pin incl. attr.tree, custody and claimant via the runner, F1 prime/lint rows; test_store_repo.py 52 tests, 11 mutations caught; work-items 467 OK, 2 skipped on git 2.39.5; departures: commit on an unmatched pathspec exits 1; attr.tree pin replaces the broken rule)
dispatch: reviewer opus high — fresh (rule 4), d1e9 F1 (security-sensitive)
agent: reviewer a399339a8327c6ba6 F1 round 1 at 0582a34a
note: 2026-10-15T05:50Z a background commit security review flagged 'command-execution in wi.py' with no detail; forwarded to the F1 reviewer to sweep every subprocess path (config-driven execution: include.path, core.*, filter.*, diff.*, credential/ssh/askpass, editors; shell use)
verdict: NEEDS_CHANGES F1 round 1 at 0582a34a (1 medium: git status recurses into a gitlink submodule and runs its clean filter from prime and lint; lows: ceiling with ':' in the parent path, GIT_*_PATHSPECS not scrubbed, read-only store lint traceback, case-insensitive attribute names; nit: prime wording; sweep: no shell, only two subprocess sites, host ls-files runs host fsmonitor (by spec; harden anyway); departures accepted, F1 never pushed without F2 and F3)
dispatch: implementer opus high — resume, F1 fix round 1
agent: implementer a00b3d4405bafe651 F1 round 2
result: DONE F1 round 2 at f91ae111 (all seven applied; six new tests; seven mutations caught; 473 OK)
dispatch: reviewer opus high — resume, F1 round 2
agent: reviewer a399339a8327c6ba6 F1 round 2 at f91ae111
note: 2026-10-15T06:26Z operator: checkpoint and compact as soon as this dev cycle (d1e9 F1 review) completes; no new dispatches after it
verdict: CLEAR F1 round 2 at f91ae111 (22-case sweep silent; 50k-file store prime 147 ms; nit: no test pins the host ls-files fsmonitor pin — carried into F2's brief; nit: .GIT dir counted, no change)
findings: carried — add a host core.fsmonitor marker to TestChecks.test_host_tracks_the_store and assert none after lint
landed: F1 locally 6fb686d2 (Checks 12/12 OK); NOT pushed — F1 ships only with F2, F3, F5 (its fix texts name wi commit and init adoption)
target: an agent worktree off main (eee4e1d2); wi.py commit verb, tests, and the dev-flow and context-guard store-commit sites (F2)
dispatch: implementer opus high — d1e9 F2: wi commit and every store-commit site (same file and effort as F1: one tier for the whole build)
agent: implementer ad0e653ee6fafc636 F2 round 1
result: DONE F2 round 1 at 4324cdfd (wi commit; dev-flow and context-guard sites; carried host fsmonitor test; 536/105/762/21 OK; 21 mutations caught; departures: intensity-and-routing edit deferred to F5, gc --auto overrides gc.auto pin, recorded-ignored never committed, git missing exit 0, validation timeout exit 3)
dispatch: reviewer opus high — fresh (rule 4), d1e9 F2 (security-sensitive)
agent: reviewer add9a9ef6d85711e5 F2 round 1 at 4324cdfd
verdict: NEEDS_CHANGES F2 round 1 at 4324cdfd (high: own store config runs commands via promisor lazy fetch (uploadpack/sshCommand) — GIT_NO_LAZY_FETCH=1 plus broken-store check; medium: wi commit exits 3 on an empty items/ (pathspec unmatched; breaks F3's first commit); lows: host lookup failure reads as dedicated, git missing exit 0 on an own store; nits: tracked path pathspec env scrub, index.lock note, SKILL row wording; departures 1,2,3,5 accepted)
carry: F5's brief carries research intensity-and-routing.md's clause (departure 1)
dispatch: implementer opus high — resume, F2 fix round 1
agent: implementer ad0e653ee6fafc636 F2 round 2
result: DONE F2 round 2 at 3a057c2c (all 7; GIT_NO_LAZY_FETCH + promisor/partialclone broken; ls-files listing rule; HOST_UNKNOWN; git-missing exit 3 on own; scrub at 3 sites incl. _store_repo; 547/105/762/21 OK; 15 new mutants killed)
dispatch: reviewer opus high — resume, F2 round 2
agent: reviewer add9a9ef6d85711e5 F2 round 2 at 3a057c2c
verdict: CLEAR F2 round 2 at 3a057c2c (all 7 closed; nits: _unsafe_path key cut at a space (cosmetic); lazy-fetch test fails rather than skips on git < 2.39.4)
carry: F3's brief — _store_repo env scrub at init (reviewer flag c)
landed: F2 locally 390c60c5 (Checks 12/12 OK; cc_scan clean: own helper names only); NOT pushed — ships with F1, F3, F5
note: wi commit stages every store path, so in a store two sessions write it sweeps the other session's finished item writes into this commit (attribution only; F5's per-change commits end it). Until F5 lands this librarian keeps committing named store files.
target: an agent worktree off main (390c60c5); wi init create/adopt, own-unrecorded and no-history checks (F3)
dispatch: implementer opus high — d1e9 F3: init creates or adopts the store's repo (same file and effort as F1/F2)
agent: implementer a56d080820c81b88a F3 round 1
result: DONE F3 round 1 at 8712bd83 (init create/adopt via _store_git, --template= empty, env scrub, local hooksPath/fsmonitor; 573/105/762/21 OK; 19 mutants caught; departures: old locations not refused (note instead), a remote does not refuse adoption (plan), test_wi fixtures moved to --track, extra refusals and notices)
dispatch: reviewer opus high — fresh (rule 4), d1e9 F3 (security-sensitive)
agent: reviewer a68637230a53cccf7 F3 round 1 at 8712bd83
note: 2026-10-15 session restarted; reviewer a68637230a53cccf7 (F3 round 1) stopped unfinished — resumed
ruling: operator 2026-10-15, verbatim: "It seems like `wi init` should just error out if it finds un-migrated `.work` or `.claude-sandbox` prompting agents to do the migration (with an override flag to bypass if for some reason a different project is using the .work convention)" — replaces F3 departure 1 (and goes past D3 step 2): init exits non-zero on a store at an old location, naming the move (format.md § Moving a store); one override flag keeps today's plain store there
decided: the flag's name is the implementer's to propose (two-way until the push); dev-flow first-start's init line handles the new exit
peer: claude-sandbox 2026-10-15 — freeze not yet (its operator confirmation comes later); wants d1e9 F1-F5 pushed before part A; step 0: prune merged worktrees/branches, never backup/*, /reload-plugins before G0. Asked: does `wi --root .work-items init --no-track` on a moved store create/adopt .git (yes after F3: creates, or adopts an existing one, host ignore line first, first commit of all items); does the old-location exit fire with .claude-sandbox/work gone but /work/ still in the sidecar .gitignore
decided: the old-location exit keys on an old location that holds items/ (a real store), never on ignore lines; a store already moved does not trip it (two-way; matches the ruling's 'un-migrated')
verdict: NEEDS_CHANGES F3 round 1 at 8712bd83 (3 medium: a rule in the store's own .gitignore counts as host-ignored (gitlink staged by host add -A); a git dir inside items/ accepted and committed; git init over any non-store directory; lows: include.path overrides hooksPath for hand git, other-files check reads only the index, adopt computed before the lock; nits; departures 2, 3 accepted)
decided: old-location ruling built as: refuse (exit 1, nothing written) when the root is an old location holding items/, or when an old location beside the root's repo top still holds items/; also on re-runs of init there; sidecar --track included (the operator's ruling names .claude-sandbox), 3c06 tests rewritten through the override; override works with every mode, rejected at .work-items/, never yields an own repo at an old location, not recorded (each init needs it; notices stay)
dispatch: implementer opus high — resume, F3 fix round 1 + the operator's old-location ruling
agent: implementer a56d080820c81b88a F3 round 2
result: DONE F3 round 2 at 0bf03f96 (all 7 + the ruling; flag --allow-old-location; 587/106/762/21 OK; 39 mutants caught; choices: flag refused only where it overrides nothing; a new store at an old location (no items/) not refused)
dispatch: reviewer opus high — resume, F3 round 2
agent: reviewer a68637230a53cccf7 F3 round 2 at 0bf03f96
verdict: NEEDS_CHANGES F3 round 2 at 0bf03f96 (1-3, 5-7 and the ruling closed; open low exact: config.worktree (extensions.worktreeConfig) include or direct core.hooksPath adopted — verify effective hooksPath/fsmonitor without pins; low judgement: a new store at an old location is created, then the next init refuses it)
decided: a new store at an old location is refused too without --allow-old-location (one rule: no store is made or kept at an old location without the flag; 3c06 tests pass the flag when creating)
dispatch: implementer opus high — resume, F3 fix round 2
agent: implementer a56d080820c81b88a F3 round 3
result: DONE F3 round 3 at 13c9f4ee (read-back of effective hooksPath/fsmonitor without pins; new old-location stores need the flag; 588/106/762/21 OK; 41 mutants; fixed own mutation runner false-catch)
dispatch: reviewer opus high — resume, F3 round 3
agent: reviewer a68637230a53cccf7 F3 round 3 at 13c9f4ee
verdict: CLEAR F3 round 3 at 13c9f4ee (lows: caller GIT_CONFIG_COUNT/PARAMETERS reach the pins=False read-back and give a wrong reason (exact); a refused adoption leaves the two safe keys written (judgement, declined: safe values, documented); nit: two long lines)
decided: finish round of exact leftovers (finding 1 scrub for the read-back, nit 3) — authority answer 145
dispatch: implementer opus high — resume, F3 finish round
agent: implementer a56d080820c81b88a F3 finish round
review: self — finish round at 980558dc: exactly the two leftovers (command-scope config stripped for the pins=False read-back only; two lines rewrapped); test added; work-items 589 OK, kit-dev 21 OK
landed: F3 locally 6e5140fb (Checks 12/12 OK; cc_scan clean: own tags only); NOT pushed — ships with F1, F2, F5
target: an agent worktree off main (6e5140fb); per-change commits from every write verb (F5)
dispatch: implementer opus high — d1e9 F5: each change committed under the lock
agent: implementer aa14330e5be79d2bc F5 round 1
result: DONE F5 round 1 at 281efed9 (Lock commits the journal on exit under the flock; only paths written; save first, warn; 611/107/762/21 OK; 18 mutants caught; +20 ms per own-store write, prime unchanged; departures: ~10 git calls per write (validation reuses store_repo_state), Lock commit= kwarg, writes journaled in _atomic_write/_move_no_clobber, archive 1 item wording, no closing rev-parse, deadline test patched, two extra pins, research SKILL line kept)
dispatch: reviewer opus high — fresh (rule 4), d1e9 F5 (security-sensitive)
agent: reviewer a7a477b3d31a6408e F5 round 1 at 281efed9
verdict: NEEDS_CHANGES F5 round 1 at 281efed9 (medium reproduced: wi export into items/.gitattributes is journaled and committed, the store's clean filter runs — narrow the journal to wi's own shapes, export refuses an output inside the store, re-walk before add; lows: an ignored new item skipped silently, 200-char cut hides index.lock, format.md overstates never-swept; nit: pyright false positive at _host_repo; departures 1-8 accepted; concurrency verified)
dispatch: implementer opus high — resume, F5 fix round 1
agent: implementer aa14330e5be79d2bc F5 round 2
result: DONE F5 round 2 at 66c64d59 (journal narrowed to wi shapes; export refuses inside the store; re-walk before add; ignored-item warning; index.lock reason; format.md wording; _git annotated; 616/107/762/21 OK; 23 mutants)
dispatch: reviewer opus high — resume, F5 round 2
agent: reviewer a7a477b3d31a6408e F5 round 2 at 66c64d59
verdict: CLEAR F5 round 2 at 66c64d59 (nits: re-walk before add skips <git-dir>/info/attributes; export refuses any output inside a store)
declined: nit 1 for this push — the gap needs a write into the store's .git/info inside one command's lock window, by a party that can already write the store's config; filed as a follow-up rather than delaying the push claude-sandbox waits on. nit 2: kept, as the reviewer allows.
landed: F5 locally f77dab82 (Checks 12/12 OK); F1-F5 all on local main; pre-push scan over main --not --remotes (66 commits): deny-list no hits; phrase hits are git bundle and a Go binary, not Claude Code; no Claude Code version lines; shape hits are our own code
follow-up: re-walk before add also checks <git-dir>/info/attributes (F5 review nit 1)
decision 251: push local main (d1e9 F1-F5 and 66 commits) to origin now? — options: (a) push now: ships the nested store repo, lifts claude-sandbox's no-nested-.git hold, and lets its part A start from a smaller diff [recommended] | (b) hold until a time you name | (z) decide later
  why ask: the librarian said it would put this push to the operator (2026-10-15); claude-sandbox asked for it before its part A
answer 251: a (operator, chat, 2026-10-19, verbatim: "251a")
landed: pushed 63f7c0d2..c4374660 (F1-F5 on origin); relay 2 to claude-sandbox: hold lifted

## Notes
- 2026-10-19 done
