---
id: research-skills-effort-based-routing-par-e184
title: "research skills: effort-based routing parity with dev-cycle's role profiles"
short_display_name: research routing parity
type: feature
status: done
priority: 1
created: 2026-10-02
updated: 2026-10-06
closed: 2026-10-06
refs:
  - operator 2026-10-02
---

Operator 2026-10-02, verbatim: 'is the effort-based model routing agent persona stuff in the research skill entrypoints like it is for dev-cycle?' Answer at filing (librarian read): only partly. research, research-deep, research-refine, research-prune launch two pinned agents (research-lane sonnet/medium, research-verifier haiku/low), with model: on the call only to override; research-deep's exhaustive adversarial lane overrides to opus but keeps the lane's medium effort (effort cannot change per call); the synthesis forks on the session's own model. dev-cycle references/model-routing.md:8-11 says the research skills keep their own routing and nothing there governs them: no profiles or -deep effort variants, no dispatch: lines, no quota reserve, no fable offer. deep-investigation launches lanes with a 'cheap model from Step 1' on a plain Agent; chain-of-verification uses general-purpose. Spike: decide whether to bring research dispatches under model-routing.md's profiles (e.g. an opus/high or -deep lane file for adversarial and exhaustive lanes, routed verifier tiers, dispatch: records and the quota sense), and how that interacts with the cost-budget work (f65b, decision 145) and the research-security builds (819f, 1ffd).

## Handoff
- doing: CLEAR r2 at 7806e08 (worktree-research-skills-effort-based-routing-par-e184)
- next: on 147/148: merge main into the branch (5bdd e92f0e3 touched resume.md/record-lines.md/model-routing.md/SKILL.md), re-review the merge (reviewer aeedf8a6c590ba4eb), then land; file carried 13-16 as a follow-up; if an answer changes a name/scope, implementer a40f03413970add35 applies it first
- blocked: —
- learned: —
note: operator 2026-10-02, verbatim: "Since the skills are in the same plugin, we could just piggy-back on the dev-cycle's routing schema, right? Does the shape fit, or does it need some refactoring in that case?" Librarian's read (model-routing.md § Mechanism, § Profiles, § Below the quota reserve, § Fallback, § Recording): the mechanism fits as is (role file + per-call model, one effort per file, dispatch: lines, reserve, fallback, pins composing); a same-plugin pointer is allowed by CLAUDE.md's cross-skill rule. Refactor needed: (1) split model-routing.md into plugin-wide sections and cycle-only sections, and drop the "research keeps its own routing" carve-out (:8-11); (2) a research binding for the record sink (a run's brief/ledger, not an item body) and for which signals exist outside an item; (3) the mechanism puts haiku out of scope but research-verifier is pinned haiku/low — a real choice; (4) a second lane file for adversarial/exhaustive lanes, since effort cannot move per call; (5) research passes model: only to override, the mechanism wants it on every call; (6) research rows in Profiles and the below-reserve table; test_agents.py follows. deep-investigation and chain-of-verification are a scope question.

## Notes
- 2026-10-02 claimed by Kyle-McFarlane@401123cbad11
note: operator 2026-10-02, verbatim: "let's just update the research skills' routing to be shaped along the lines of how dev-cycle was updated in-place instead of depnding on the dev-cycle skills. That seems cleaner. / 1. keep them separate / 2. we should have a work item for all research runs, then we can adopt that as the place to store that similarly / 3. it's okay for us to use haiku for this task if evidence supports that decision / 4. approved a second file to control effort / 5. let's have it for every call in research skills too / 6. you decide / bring along deep-investigation and chain-of-verification / go ahead and plan it and land it" (read as: plan and land; research gets its own routing reference shaped like dev-cycle's model-routing.md, in place, not a pointer into dev-cycle; every research run files a work item, which becomes its record sink for dispatch: lines; the verifier stays on haiku only if evidence supports it, else sonnet low; a second lane file at a higher effort is approved; model: on every research dispatch; deep-investigation and chain-of-verification are in scope)
decided: 2026-10-02T21:57Z design — tests: plugins/dev-flow/tests/test_agents.py keeps every research agent file's model and effort pin in step with the research routing table, as it does for dev-cycle's Profiles · authority: the operator's "6. you decide" (2026-10-02) · reopen: say so
decided: 2026-10-02T21:57Z contract — the second lane file is named research-lane-deep, after planner-deep and implementer-deep; its effort is the plan's to set from evidence · authority: the operator's "4. approved a second file to control effort" (2026-10-02) · reopen: rename in the reply
dispatch: planner opus high — plan (operator: plan it and land it)
target: plan research-skills-effort-based-routing-par-e184 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/e184-research-routing
agent: planner a755d6374fee501cb round 1
return: planner PLAN_READY .claude-sandbox/investigations/e184-research-routing/ (INDEX, 00, evidence/verifier-record.md); verifier to sonnet/low on evidence; research-lane-deep opus/high
baseline: 978f34264739 00_initial.md 
dispatch: reviewer opus high — plan review round 1
agent: reviewer a20dd05df1987148f round 1
verdict: NEEDS_CHANGES round 1 (plan)
findings:
  haiku evidence spot-checked and holds (7113 r2, r2-local-routing, initiative-layer, r4-control-plane; arXiv 2607.08700 F1/κ match, FP figures unverifiable from HTML, labelled approximate)
  1. [high] 00:317-330 — rule order: --item before "nested" lets a nested run write onto the cycle's item (breaks single writer) and double-counts lane ids in the spend reader; fix: the sub-agent rule first; acceptance 9 and 14
  2. [medium] 00:286,960-966 — OQ2's "runs that dispatch an agent" means every chain-of-verification call files an item; name CoVe and offer an option where it records only under --item or in its summary
  3. [medium] 00:234-235,625-628,881-883 — CoVe on dev-cycle's scout: a88a F5 may strip scout's web tools; scout is outside F3's guard; test or F5 note, § Security line
  4. [medium] 00:246,936-937; INDEX Risk — deep-investigation's interim general-purpose row may last long (1ffd waits on 819f); POC hand-off dispatch unrouted; name the partial delivery, add a § 3 row
  5-8. [low] verifier cost ~0.4 lane not one; "at least 13 not grounded in an opened source"; the one sonnet run also broke header counts; 819f also touches research-refine/SKILL.md; acceptance gaps (--item hints, § 7/8 tables, scout description, CoVe Record: line, later waves); the deep pin set from the role (decided: line)
  9-10. [nit] two quota signals; CoVe bare Bash
dispatch: planner opus high — resume (plan fix round 1)
agent: planner a755d6374fee501cb round 2
return: planner PLAN_READY — serial 01_review-fixes.md (1-10)
decided: 2026-10-02T22:21Z design — research-lane-deep's pin is opus/high, set from the role (the exhaustive adversarial lane) because no exhaustive run has happened; revisit after the first exhaustive runs · authority: the operator's "4. approved a second file to control effort" (2026-10-02) · reopen: say so
baseline: 978f34264739 00_initial.md 8592c7657d6b 01_review-fixes.md 
dispatch: reviewer opus high — resume (plan review round 2)
agent: reviewer a20dd05df1987148f round 2
verdict: CLEAR round 2 (plan)
findings:
  prior 1-10 FIXED
  11. [low] 00:767-768, 00:577 — acceptance 10 and the run-record.md outline still say ## Record is the no-store case only; say "used when the run records on no item: a sub-agent run, or no store"
  12. [nit] 00:730-731 — § 14 cites "§ 5 rule 2" for nested runs, now 01 § 1 rule 1
findings: carried — 11 [low], 12 [nit] above, verbatim; into this item's build
decided: 2026-10-02T22:22Z scope — the verifier's procedure faults (OQ3 of the research-routing plan) go to a filed follow-up, research-verifier-fix-its-procedure-faul-2e75, landing after 819f; this build moves only the verifier's pin · authority: class narrowing (the plan's recommended option) · reopen: pull it back into this build
decision 147: The research-routing build adds six stored names: the research-run tag, an item: field, a ## Record section, an --item argument, the synthesis role word, and chain-of-verification's Record: line; keep them as named? — options: (a) keep them as named [recommended] | (b) rename some (say which) | (z) decide later
  raised: 2026-10-02T22:22Z
  what: names stored in work items and briefs, or parsed by the spend reader (was OQ1 of the research-routing plan, e184)
  why now: the build starts now with these names; renaming before it lands costs a search-and-replace, after it a migration of stored lines; blocks: the landing, not the build
  why ask: contract — new stored, parsed names are yours (answer 111 b)
  context: you approved research routing in place, a work item per research run, and said plan it and land it · you approve the names it writes — then: none
  stakes: reversible, narrow — research runs' records
  (a) keep them as named — research-run (tag on the item each run files), item: (the run's item in its brief), ## Record (where a run with no item writes its lines), --item <id> (name an existing item), synthesis (role word on a dispatch line), Record: (chain-of-verification's summary line) — undo: a rename later migrates stored lines — who: research runs, the spend reader
  (b) rename some — the build uses your names before it lands, no migration
  (z) decide later — the build finishes with these names and waits to land
  rec: (a) · basis partial — each follows an existing shape (tags, front-matter fields, dispatch role words); the reviewer found no clash
  unknown: none
decision 148: Which research runs should file a work item of their own? — options: (a) research-family and deep-investigation runs that dispatch an agent; chain-of-verification records on an item only when one is named, otherwise in its own summary [recommended] | (b) every run that dispatches an agent, chain-of-verification included | (c) every run, quick inline answers included | (z) decide later
  raised: 2026-10-02T22:22Z
  what: the reach of your "a work item for all research runs" (was OQ2 of the research-routing plan, e184)
  why now: the build starts now with (a); blocks: the landing, not the build
  why ask: trade-off — complete records against an item for every quick check
  context: you said every research run should have a work item as its record · you decide where "every" stops — then: chain-of-verification always dispatches agents, and the model invokes it on its own ("verify this"), so under (b) each such check files an item; a run inside a sub-agent (e.g. research a planner runs) never files its own item under any option, because its spend is already on the parent's item and writing there would double-count it
  stakes: reversible, narrow — the work-item stores of repos where research runs
  (a) research and deep-investigation runs that dispatch — every real research run is on an item; chain-of-verification's quick checks stay out of the store unless you name an item, and their spend is not on any item — undo: an edit — who: research runs
  (b) every run that dispatches — complete spend records; one item per chain-of-verification call, several a day in some sessions
  (c) every run, inline answers too — most complete, noisiest
  (z) decide later — the build finishes with (a) and waits to land
  rec: (a) · basis partial — follows your intent for research runs without filing an item per quick check; chain-of-verification's spend is small
  unknown: how often chain-of-verification runs across sessions
target: full research-skills-effort-based-routing-par-e184 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/research-skills-effort-based-routing-par-e184
dispatch: implementer opus medium — build (plan CLEAR r2; prose, agent files, tests)
agent: implementer a40f03413970add35 round 1
return: implementer DONE_WITH_CONCERNS 296dd9b (deep-investigation partial until 1ffd; prose rules untested; store-lookup snippet restated from dev-cycle bindings.md by "keep them separate")
librarian ruling: concerns accepted — the partial delivery is the plan's stated interim; the restated snippet follows the operator's "keep them separate"; the reviewer reads the prose criteria
dispatch: reviewer opus high — review round 1
agent: reviewer aeedf8a6c590ba4eb round 1
verdict: NEEDS_CHANGES round 1 at 296dd9b
findings:
  acceptance 1-7, 11-13, 15, 17, 19 and carried 11, 12 hold; acceptance 14 walk: 4 of 7 pass; lane body test, test rows, principle 4, no dev-cycle dependency, snippet logic, security contract all fine
  1. [medium] run-record.md:172, research-strategy-format.md:107 — ## Record placed after the append-only Ledger, so >> ledger lines land under ## Record; put ## Record above the Ledger; fix intensity-and-routing.md:273 "last section"
  2. [medium] research/SKILL.md:111-118 — the quick-to-disk path files an item but never closes it; with no item, its record has no COST field to go in; close per § Closing in Step 4, name where record: none goes in the quick reply
  3. [medium, merge] research/SKILL.md conflicts with the scan floor (now landed 66cc7ff) in Step 4, 6, 8 hunks — keep both sides; the scan floor's toolkit-gate script review is a new verifier dispatch missing from the Profiles row and § Recording; add its dispatched-when case, dispatch shape and round, the record step; check low effort still fits
  4-8. [low] snippet results don't persist across shell calls — write the resolved command and item path into the brief, test -f as rule 4's test; $WI lint flags the open item — set a handoff at filing or say the warning is expected; Step 7's round N+1 routing/recording clause; ## Record when-rule and Record: format restated in 2 places each — point at § Stored names; deep-investigation paraphrase order and unresolved-store under --item falls to rule 4
  9-12. [nit] ## Acceptance placement; CoVe template model placeholder; deep-investigation POC wording; "(sonnet, opus or fable)"
dispatch: implementer opus medium — resume (fix round 1, plus merging main with the landed scan floor)
agent: implementer a40f03413970add35 round 2
return: implementer DONE 7806e08 (merged main with the scan floor; 1-12 fixed; record lines into the state file by edit, not >>; verifier low kept for script review and flag verdicts)
dispatch: reviewer opus high — resume (round 2)
agent: reviewer aeedf8a6c590ba4eb round 2
verdict: CLEAR round 2 at 7806e08
findings:
  prior 1-12 FIXED; merge kept all of the scan floor (scan-findings.py, its tests, research-criteria.md, storage-and-knowledge-base.md byte-identical to main); acceptance 14's seven runs re-walked and pass; the low verifier pin for script review acceptable
  13. [low] intensity-and-routing.md:198-201 — the pin rationale names only the cheap miss; name the false-CLEAR risk and what bounds it (the --scripts scanner's HOLD floor; sonnet/low is an upgrade over the haiku the gate was designed with); optionally a missed script-review hold as a revisit trigger
  14. [nit] § Recording "one append" → "one write"
  15. [nit] chain-of-verification/SKILL.md:217 — "- Record: item <id> | none — <dispatch lines> (§ Stored names)"
  16. [nit] chain-of-verification/SKILL.md:107-110 — under --item, re-run the store snippet per call or name $WI_ROOT/items/<id>.md
findings: carried — 13 [low], 14-16 [nit] above, verbatim; folded into the pre-landing round if 147 or 148 changes anything, else filed as a follow-up at landing
hold: landing waits on decisions 147 and 148 (blocks the landing, not the build); the branch is CLEAR at 7806e08
note: main moved (the budget rule e92f0e3 edits dev-cycle resume.md, record-lines.md, model-routing.md, SKILL.md — files this branch also edits); before landing, merge main into the branch and re-review the merge
decision 147: The research-routing build adds six stored names: the research-run tag, an item: field, a ## Record section, an --item argument, the synthesis role word, and chain-of-verification's Record: line; keep them as named? — options: (a) keep them as named [recommended] | (b) rename some (say which) | (z) decide later
  raised: 2026-10-02T22:22Z
  revised: 2026-10-06T01:50Z — why now stale (the build has finished); options and recommendation unchanged
  what: names stored in work items and briefs, or parsed by the spend reader (was OQ1 of the research-routing plan, e184)
  why now: the build is done and passed review (round 2); landing it needs these names settled; blocks: the research-routing landing
  why ask: contract — new stored, parsed names are yours (answer 111 b)
  context: you approved research routing in place, a work item per research run, and said plan it and land it · you approve the names it writes — then: none
  stakes: reversible, narrow — research runs' records
  (a) keep them as named — research-run (tag on the item each run files), item: (the run's item in its brief), ## Record (where a run with no item writes its lines), --item <id> (name an existing item), synthesis (role word on a dispatch line), Record: (chain-of-verification's summary line) — undo: a rename later migrates stored lines — who: research runs, the spend reader
  (b) rename some — the build uses your names before it lands, no migration
  (z) decide later — the build finishes with these names and waits to land
  rec: (a) · basis partial — each follows an existing shape (tags, front-matter fields, dispatch role words); the reviewer found no clash
  unknown: none
decision 148: Which research runs should file a work item of their own? — options: (a) research-family and deep-investigation runs that dispatch an agent; chain-of-verification records on an item only when one is named, otherwise in its own summary [recommended] | (b) every run that dispatches an agent, chain-of-verification included | (c) every run, quick inline answers included | (z) decide later
  raised: 2026-10-02T22:22Z
  revised: 2026-10-06T01:50Z — why now stale (the build has finished); options and recommendation unchanged
  what: the reach of your "a work item for all research runs" (was OQ2 of the research-routing plan, e184)
  why now: the build is done with (a) and passed review (round 2); blocks: the research-routing landing
  why ask: trade-off — complete records against an item for every quick check
  context: you said every research run should have a work item as its record · you decide where "every" stops — then: chain-of-verification always dispatches agents, and the model invokes it on its own ("verify this"), so under (b) each such check files an item; a run inside a sub-agent (e.g. research a planner runs) never files its own item under any option, because its spend is already on the parent's item and writing there would double-count it
  stakes: reversible, narrow — the work-item stores of repos where research runs
  (a) research and deep-investigation runs that dispatch — every real research run is on an item; chain-of-verification's quick checks stay out of the store unless you name an item, and their spend is not on any item — undo: an edit — who: research runs
  (b) every run that dispatches — complete spend records; one item per chain-of-verification call, several a day in some sessions
  (c) every run, inline answers too — most complete, noisiest
  (z) decide later — the build finishes with (a) and waits to land
  rec: (a) · basis partial — follows your intent for research runs without filing an item per quick check; chain-of-verification's spend is small
  unknown: how often chain-of-verification runs across sessions
answer 147: 147a (2026-10-06T01:37Z, chat; read as: (a) keep the six names as named)
answer 148: 148b (2026-10-06T01:37Z, chat; read as: (b) every run that dispatches an agent files or names a work item, chain-of-verification included; the build, which used (a), changes before landing)
dispatch: implementer opus medium — resume (round 3: answer 148 b applied, main merged in)
agent: implementer a40f03413970add35 round 3
return: implementer DONE_WITH_CONCERNS 77a54d5 (40cfe15 answer 148 b; 77a54d5 merge of main; concerns: CoVe allowed-tools lacks Bash per acceptance 17, so a model-invoked CoVe prompts per wi call where Bash is not allowed; synthesis role word unmapped in the spend reader (falls back, as planned); deep-investigation partial until 1ffd)
librarian ruling: concerns go to the reviewer; the allowed-tools one is weighed there against acceptance 17 and the house rule that leaving allowed-tools out is the default
dispatch: reviewer opus high — resume (round 3: answer 148 b + merge of main)
agent: reviewer aeedf8a6c590ba4eb round 3
verdict: CLEAR round 3 at 77a54d5
cost: 2026-10-06T01:50Z build $13.58 of $22 after review 3 — must-fix 0 — prices 2 (no budget: line: the phase opened before the budget rule; default other build)
landed: 7bd41bc
findings: carried — round 2 lows 13-15, round 3 lows 1-2 into research-routing-carried-review-lows; 16 fixed by 40cfe15
- 2026-10-06 done: 7bd41bc
correction: 2026-10-06 the e184 landing was pushed (da35c1a..2ba07c1) before its Report was printed; the Report follows in the same turn
