---
id: dev-cycle-at-the-review-cap-the-orchestr-5bdd
title: "dev-cycle: at the review cap, the orchestrator finishes trivial leftover fixes by default instead of raising a decision"
short_display_name: finish trivial fixes at the cap
type: feature
status: doing
priority: 1
deps:
  - review-caps-and-spend-plans-raise-only-o-5579
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-01T07:22Z
created: 2026-10-01
updated: 2026-10-02
refs:
  - operator 2026-10-01, answer 137
---

Operator 2026-10-01 on decision 137, verbatim: 'I think the orchestrator should just finish trivial changes when the cap is reached. Make a work-item to make that the default behavior'. Acceptance: when a review hits the round cap and every leftover finding is trivial (to be defined: e.g. one-sentence or one-line fixes the reviewer states exactly, no design choice), the orchestrator (librarian or standalone dev-cycle) finishes them without a cap decision — whether by one more implementer round or its own edit is a plan question, as is the trivial test and the review it gets afterwards; non-trivial leftovers still raise the cap decision. Depends on review caps and spend (5579), which rewrites the same cap rules. Authority: answer 137 (rule-change, operator-requested).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-01 claimed by Kyle-McFarlane@401123cbad11
dispatch: planner opus high — plan (operator-requested rule change, answer 137)
target: plan dev-cycle-at-the-review-cap-the-orchestr-5bdd /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/5bdd-finish-trivial-at-cap
agent: planner ab1a5ac379668d226 round 1
return: planner PLAN_READY .claude-sandbox/investigations/5bdd-finish-trivial-at-cap/ (INDEX, 00) — 5 operator questions, all blocking the build
dispatch: reviewer opus high — plan review round 1
agent: reviewer ad602e1cf89b0aad2 round 1
verdict: NEEDS_CHANGES round 1 (plan)
findings:
  1. [medium] 00:162-168,318 — a finish round in plan mode cannot work as written (serials immutable; PLAN_READY has no CONCERNS); add agent-brief § Plan variant finish clause, re-review "applied" against the new serial, acceptance + trace
  2. [medium] 00:164-168 — "DONE_WITH_CONCERNS raises" contradicts resume.md:197 S4; name the specific concern, decide partly-applied commits, add a resume touch point
  3. [medium] 00:312 — bindings.md:237-240 "a granted round that does not clear … is raised" untouched, contradicts D5
  4. [medium] 00:488-495,246-255 — OQ5 (a) not honestly costed: spends during a hold, with no quota signal, under a fable pin, outside the spend class's grant; reconcile budget.md:273-290; name answer 137 as spend authority or not
  5. [medium] 00:140-145,431-432 — "exact fix" lexical test rejects ordinary sentences; define "no alternative" structurally; documenting a landed shape is not adding one; 5579 walk overstated (round-5 fix was exact-but-incomplete)
  6. [medium] 00:278-280 — A1 single-home claim contradicted (bindings restates Fix: conditions; SKILL.md restates the bound); one home each, drop "up to two" from SKILL.md
  7. [medium] 00:208-217,176-179 — resume cannot reconstruct the bound or the finish-round brief; define the bound by ROUNDS or read the dispatch signal; VARIANT note; traces
  8. [medium] 00:273-304,373-385 — acceptance and traces incomplete (819f r4/r5 raised; if left: names finish rounds; budget.md; model-routing § Rounds; fix-loop:68-70; review-brief § Verdict meanings; bindings:249; hold/no signal/fable; plan mode; DONE_WITH_CONCERNS)
  9-15. [low] OQ3 costing omits that 137's rec named a fresh review and round 5's fresh reviewer caught 21; size bound under 5k tokens already breached; Fix: is an api-name; no Fix: on review: self; "21 restates 4 and 19" is inference; lows without Fix: declined "outside the finish round"; OQ2/OQ3 may be plan calls
  16-17. [nit] resume dispatch signal shape; "a fourth without CLEAR means the brief is wrong" qualifier
dispatch: planner opus high — resume (plan fix round 1)
agent: planner ab1a5ac379668d226 round 2
return: planner PLAN_READY — serial 01_review-fixes.md (1-17); Q2 decided in plan (producer edits; authority: 113 (c) declined, answer 137); Q5 rec moved to (d)
dispatch: reviewer opus high — resume (plan review round 2)
agent: reviewer ad602e1cf89b0aad2 round 2
verdict: NEEDS_CHANGES round 2 (plan)
findings:
  prior 1-17 FIXED
  18. [medium] 01:210-214,440-445,460; INDEX:76,85-86,104 — R8 makes the reviewer's words binding every round (a different edit that removes the failure is ruled OPEN), past answer 137, unshown to the operator, and contradicts Out of Scope; fix: re-review rules FIXED when the failure is gone by the given words or another edit graded like any commit; or state it plainly in Q1(a), re-grade R8, withdraw the scope line
  19. [medium] 01:312-323,426,518-522 — (d)'s "a fable pin's finish round is not raised" overrides the pin's own asks (below the reserve; fable unavailable); fix: "not raised as a cap; the pin's own asks still apply"; reviewer at fable too; split trace 12 into above-reserve / below-reserve / 429
  20. [medium] 01:433,447 — Risk Assessment and Open Questions not ## sections; promote
  21-22. [low] hold rule as a caller binding in bindings.md, librarian SKILL.md the home, add to B1; Q2 decided in the plan needs a decided: line (librarian writes it)
  23-24. [nit] "would be expected to"; "when the four conditions hold"
librarian ruling on 18: take the first fix (grade the failure, not the words) — it keeps review-brief.md's "grade the failure" rule and keeps rounds 1-3 out of scope; no new operator question
decided: 2026-10-01T07:45Z minor-design — who makes a finish round's edit: the producer (implementer or planner) resumed, never the orchestrator; changes no rule, and the alternative (the librarian edits itself) was declined at decision 113 (c) · authority: answer 137 · reopen: say so and it goes back to the operator as a question on this item
dispatch: planner opus high — resume (plan fix round 2)
agent: planner ab1a5ac379668d226 round 3
return: planner PLAN_READY — serial 02_review-r2-fixes.md (18-24)
dispatch: reviewer opus high — resume (plan review round 3)
agent: reviewer ad602e1cf89b0aad2 round 3
verdict: CLEAR round 3 (plan)
findings:
  prior 18-24 FIXED
  25. [low] 02:171 — B4' "nothing below the cap reads Fix:" vs the producer's every-round default; "nothing below the cap grades, counts or routes on Fix:"
  26. [low] 02:65-68, INDEX:57-58 — the Q2 decided: line's class should be ruled-rule-case, not minor-design (corrected below)
  27. [low] 02:190-198 — give the librarian SKILL.md row in full (no grant/reading conditions; decided: class cap, authority answer 137); B7 depends on it
  28. [nit] trace 12b — "the pin's ask, unless an earlier answer still covers the item"
  29. [nit] 02:11-12 — drop "01's lines were reflowed after it was written"
findings: carried — 25 [low], 26 [low], 27 [low], 28 [nit], 29 [nit] above, verbatim; into this item's build
decided: 2026-10-01T07:49Z ruled-rule-case — who makes a finish round's edit: the producer (implementer or planner) resumed, never the orchestrator; changes no rule, and the alternative (the librarian edits itself) was declined at decision 113 (c) · authority: answer 137 · reopen: say so and it goes back to the operator as a question on this item
note: corrects the class on the decided: line above it (minor-design → ruled-rule-case), per plan review finding 26
C: I skipped dev-cycle Step 4.1's baseline: line (sha256 of the series serials) before each plan review on this item and on 90bc; no harm found (the reviewer checked 00/01 unchanged by size and mtime), but write it before every plan review from now on
decision 139: For finishing trivial fixes at the cap, what counts as a trivial leftover? — options: (a) the reviewer certifies each with a Fix: clause, and the orchestrator checks only its shape [recommended] | (b) the orchestrator applies a checklist to the reviewer's free-text findings | (c) the reviewer adds one whole-report EXACT-FIX yes/no line | (z) decide later
  raised: 2026-10-01T07:49Z
  what: the test that lets a finish round run without asking you (was OQ1 of the finish-at-cap plan, 5bdd); two sub-choices ride with (a): at most 3 leftovers (or 2), and prose and skill text only (or code too) — say them in your reply to change them
  why now: the plan cleared review in 3 rounds; blocks: the build of finishing trivial fixes at the cap
  why ask: api-name — (a) makes Fix: a stored, parsed name, and the test sets what runs without you
  context: you asked for trivial leftovers at the cap to be finished by default (answer 137) · you decide what counts as trivial — then: none
  stakes: reversible, wide — every dev-cycle run at a review cap, librarian or standalone
  (a) reviewer certifies — a Fix: is one set of words for one place, at most one sentence or one line, no new choice; the orchestrator checks: changes needed, no high left, every leftover a medium with a Fix:, at most 3; tonight's review-caps rounds would have finished unasked, the scan floor's code fixes still come to you — undo: an edit to review-brief.md and bindings.md — who: every capped run
  (b) orchestrator checklist — no new reviewer clause; the orchestrator judges free text, which is the drift the plan tried to avoid
  (c) one EXACT-FIX line — simplest for the reviewer; all-or-nothing, so one non-trivial leftover blocks every trivial one
  (z) decide later — the build waits; caps keep coming to you as today
  rec: (a) · basis partial — traced on tonight's two real cases (review caps finishes, scan floor still asks) and 17 traces; untested in use
  unknown: how often reviewers will certify in practice
decision 140: What review does a finish round get before it can land? — options: (a) the same reviewer, resumed, grading each finding on its failure [recommended] | (b) a fresh full review | (c) the orchestrator reviews it itself | (z) decide later
  raised: 2026-10-01T07:49Z
  what: the check after a finish round applies the reviewer's fixes (was OQ3 of the finish-at-cap plan, 5bdd)
  why now: blocks the build of finishing trivial fixes at the cap
  why ask: trade-off — cost against what a fresh look catches
  context: you asked for trivial leftovers at the cap to be finished by default (answer 137) · you decide who checks the finish round — then: none
  stakes: reversible, narrow — capped runs
  (a) same reviewer resumed — cheapest, a few minutes; it attacks the fix it asked for; on a fable-pinned item it runs at fable — undo: an edit to bindings.md — who: capped runs
  (b) fresh full review — likeliest to find something new: tonight's fresh round 5 caught a half-fixed finding; also likeliest to loop, as round 5 led to round 6; your 137 card's recommended option named a fresh review
  (c) orchestrator self-review — fastest; the orchestrator checks fixes it routed, with no independent eye
  (z) decide later — the build waits
  rec: (a) · basis partial — the reviewer that wrote a fix knows the failure best; but the one real case where a fresh reviewer caught more argues for (b)
  unknown: how often a resumed reviewer misses what a fresh one would catch
decision 141: How many finish rounds may run before the cap comes to you? — options: (a) one, at round 4 only | (b) round 4 always; round 5 only with fewer leftovers than round 4; never at 6 or later [recommended] | (c) as long as the leftover count keeps falling | (z) decide later
  raised: 2026-10-01T07:49Z
  what: the bound on finish rounds (was OQ4 of the finish-at-cap plan, 5bdd)
  why now: blocks the build of finishing trivial fixes at the cap
  why ask: spend — each round is agent time and quota taken without asking
  context: you asked for trivial leftovers at the cap to be finished by default (answer 137) · you decide how many such rounds run unasked — then: none
  stakes: reversible, narrow — capped runs
  (a) round 4 only — tightest; tonight's review caps would still have asked you once, at round 5
  (b) round 4, then round 5 if fewer leftovers — tonight's review caps would have landed at round 6 with no question; a run that is not converging stops at round 5 — undo: an edit to bindings.md — who: capped runs
  (c) while the count falls — fewest asks; no hard ceiling on quota per item
  (z) decide later — the build waits
  rec: (b) · basis partial — fits the one real case; the "fewer leftovers" test is a proxy for converging
  unknown: whether two is enough in practice
decision 142: When may a finish round spend without asking — during your hold, with no quota reading, under a fable pin? — options: (a) always, no exclusions | (b) only by lifting the self-granted round's grant condition (librarian only) | (c) never under a hold, a fable pin, or with no quota reading | (d) only your hold stops it; otherwise it runs with no grant or quota reading, and a fable pin's own asks still apply [recommended] | (z) decide later
  raised: 2026-10-01T07:49Z
  what: how finish rounds fit the review caps and spend rules (5579) (was OQ5 of the finish-at-cap plan, 5bdd); your answer here becomes the spend authority for finish rounds — answer 137 alone is not one
  why now: blocks the build of finishing trivial fixes at the cap
  why ask: spend — it sets when quota is used without asking you
  context: you asked for trivial leftovers at the cap to be finished by default (answer 137); review caps and spend landed with grant and quota conditions for the one self-granted round · you decide which of those conditions finish rounds keep — then: none
  stakes: reversible, narrow — capped runs and your holds
  (a) no exclusions — runs even during a hold you set, which overrides your hold
  (b) lift only the self-granted round's grant — covers the librarian only; a standalone dev-cycle still asks, which misses what you asked for
  (c) all exclusions — a hold, a fable pin, or no quota reading each send it to you; most asks
  (d) only your hold stops it — a hold still means ask; otherwise it runs with no grant or quota reading (rounds are small); on a fable-pinned item the pin still asks below the quota reserve or when fable is unavailable — undo: an edit to bindings.md and budget.md — who: capped runs
  (z) decide later — the build waits
  rec: (d) · basis partial — keeps your hold as the stop and finish rounds cheap; the fable pin keeps its own asks
  unknown: the quota cost of finish rounds across a busy night
answer 139: a
answer 140: 140a - reviewer can still tell the orchestrator to make non-trivial changes (read as: (a) the same reviewer, resumed, checks a finish round; it is not limited to grading the certified fixes — it may still return non-trivial findings, which go back through the orchestrator by the normal rules: a fix round inside the bound, else the cap comes to the operator)
decision 141: How many finish rounds may run before the cap comes to you? — options: (a) one, at round 4 only | (b) round 4 always; round 5 only with fewer leftovers than round 4; never at 6 or later [recommended] | (c) as long as the leftover count keeps falling | (z) decide later
  raised: 2026-10-01T07:49Z
  revised: 2026-10-02T16:46Z — expanded to a block on the operator's word: backfilled the lost-context facts, undo/who per option, basis drill-down
  what: the bound on finish rounds (was OQ4 of the finish-at-cap plan, 5bdd)
  why now: blocks the build of finishing trivial fixes at the cap
  why ask: spend — each round is agent time and quota taken without asking
  context: you asked for trivial leftovers at the cap to be finished by default (answer 137) · you decide how many such rounds run unasked — then: review caps and spend (on main since 2f071a8) already lets a plan with no high left stop and carry its findings, and a build take one self-granted round inside a standing grant with weekly headroom; a show-stopper, scope change or reversed decision always comes to you. Your 139 a and 140 a: a finish round runs only when every leftover is a medium with a certified one-place fix, at most 3, and the same reviewer checks it and may still send back non-trivial changes. Tonight's review caps run: round 4 left 2 exact fixes, round 5 left 1 exact medium plus 3 lows, round 6 was clear
  stakes: reversible, narrow — capped runs
  (a) one, at round 4 only — the tightest limit; tonight's review caps would still have asked you once, at round 5 — undo: an edit to bindings.md — who: every capped run
  (b) round 4, then round 5 only with fewer leftovers — tonight's review caps would have landed at round 6 with no question; a run that is not converging stops and asks at round 5; never more than two unasked — undo: an edit to bindings.md — who: every capped run
  (c) while the count falls — fewest asks; no hard ceiling, so a slowly converging item can spend several rounds unasked — undo: an edit to bindings.md — who: every capped run, and your quota
  (z) decide later — the build waits; caps keep coming to you as today
  rec: (b) · basis partial — fits the one real case; "fewer leftovers" stands in for "converging"
  basis: observed — review caps and spend rounds 4-6 (.claude-sandbox/work/items/review-caps-and-spend-plans-raise-only-o-5579.md) · observed — the plan's traces 1-19 (.claude-sandbox/investigations/5bdd-finish-trivial-at-cap/02_review-r2-fixes.md), plan review CLEAR round 3 · inferred — fewer leftovers approximates converging
  unknown: whether two is enough in practice
decision 142: When may a finish round spend without asking — during your hold, with no quota reading, under a fable pin? — options: (a) always, no exclusions | (b) only by lifting the self-granted round's grant condition (librarian only) | (c) never under a hold, a fable pin, or with no quota reading | (d) only your hold stops it; otherwise it runs with no grant or quota reading, and a fable pin's own asks still apply [recommended] | (z) decide later
  raised: 2026-10-01T07:49Z
  revised: 2026-10-02T16:46Z — expanded to a block on the operator's word: backfilled the lost-context facts, undo/who per option, basis drill-down
  what: how finish rounds fit the review caps and spend rules (5579) (was OQ5 of the finish-at-cap plan, 5bdd); your answer here becomes the spend authority for finish rounds — answer 137 alone is not one
  why now: blocks the build of finishing trivial fixes at the cap
  why ask: spend — it sets when quota is used without asking you
  context: you asked for trivial leftovers at the cap to be finished by default (answer 137); review caps and spend landed with grant and quota conditions for the one self-granted round · you decide which of those conditions finish rounds keep — then: the self-granted build round needs a standing grant (an answer that authorizes spend, like your wave approvals) and a fresh quota reading with weekly headroom, and is never taken during a hold or under a fable pin; a hold is your standing stop on dispatch; a fable pin asks you below the quota reserve and when fable is unavailable, never falling back; a finish round is small (one sentence or line per leftover, at most 3)
  stakes: reversible, narrow — capped runs and your holds
  (a) always, no exclusions — runs even during a hold you set — undo: an edit to bindings.md and budget.md — who: you (your hold stops dispatch but not finish rounds)
  (b) lift only the self-granted round's grant — a librarian still needs a quota reading; a standalone dev-cycle has no grant to lift and still asks, which misses what you asked for — undo: an edit — who: standalone dev-cycle users
  (c) all exclusions — a hold, a fable pin, or no quota reading each send it to you; the most asks — undo: an edit — who: you (more questions)
  (d) only your hold stops it — a hold still means ask; otherwise it runs with no grant or quota reading; on a fable-pinned item the pin still asks below the reserve or when fable is unavailable, and the reviewer runs at fable — undo: an edit to bindings.md and budget.md — who: capped runs
  (z) decide later — the build waits
  rec: (d) · basis partial — keeps your hold as the stop and finish rounds cheap; the fable pin keeps its own asks
  basis: observed — the self-granted round's conditions (plugins/dev-flow/skills/librarian-mode/references/budget.md, § round budget; dev-cycle references/bindings.md § Decisions) · observed — the plan's traces 7, 10-12c (.claude-sandbox/investigations/5bdd-finish-trivial-at-cap/02_review-r2-fixes.md) · inferred — finish rounds stay small enough that a quota reading adds little
  unknown: the quota cost of finish rounds across a busy night
note: operator 2026-10-02 on decision 141, verbatim: "141 - what I REALLY care about is cost, not number of rounds. Investigate how we could frame the threshold that way instead. A spend budget set when the research is created and authorization to increase budget with a justifacation for the budget increase matches the actual problem better" (read as: dig into — investigate framing the cap as a per-item spend budget set when the work starts, raised with a justified increase; covers 142 too; the result comes back on 141 and 142) — spike dev-cycle-review-spend-as-a-per-item-cos-f65b
answer 141: reframed as decision 145 — "141 - what I REALLY care about is cost, not number of rounds. Investigate how we could frame the threshold that way instead. A spend budget set when the research is created and authorization to increase budget with a justifacation for the budget increase matches the actual problem better"
answer 142: reframed as decision 145 — folded by the librarian into 141's dig into (both are about spend); the operator was told 2026-10-02 and did not object
closed 141: superseded by 145
closed 142: superseded by 145
decision 145: Should a spend budget per item, set when each phase starts and raised only on a justified ask, replace the 4-round review cap? — options: (a) yes: a per-item spend budget replaces the round count as the trigger to ask, with the recommended settings [recommended] | (b) keep the cap; finish rounds past it spend from a small allowance (about $2) instead of a count | (c) keep counting rounds: round 4, then round 5 only with fewer leftovers; only your hold stops a finish round | (z) decide later
  raised: 2026-10-02T17:35Z
  what: how the review loop decides when to stop and ask you, in cost instead of rounds; replaces 141 and 142 (the result of your dig into on 141, spike f65b). (a)'s settings, each yours to change in the reply: unit — list-price dollars, shown with their share of a week (Q2); defaults by phase — spike plan $32, other plans $18, chore and bug builds $6, other builds $18, a fable pin doubles them, and a plan's own estimate sets its build's budget, put to you when over the default (Q3); the 4-round count stays only as a convergence stop (ask when the must-fix count stops falling) and the fallback when spend cannot be read (Q4); at the budget, one finish round of exact fixes (about $1) may still run (Q5); ask once spend reaches the budget, so at most one round goes over (Q6); past the 4th review your hold and the quota reserve still stop it, only the standing grant goes, and a standalone run past the 4th is a named loosening (Q7); a plan with no high left at its 4th review still stops and carries its findings, unasked under a librarian (Q8). New stored names: budget:, cost:, must-fix, Estimated cost:, the reviewer's MUST-FIX:
  why now: the finish-at-cap build (5bdd) waits on it; the plan cleared review in 4 rounds
  why ask: spend — it sets when quota is used without asking you, and (a) adds five stored names (api-name)
  context: you said you care about cost, not rounds, and asked for a budget set when the work starts with justified increases · you decide whether a budget replaces the round cap, and its settings — then: measured over the last 14 days (112 items, cited list prices): a fix round costs about $4-5 (about 0.2% of a week); 1% of a week is about $22; spike plans median $24, build plans $9, features $9, chores $2; under (a) with these settings the scan floor (819f) asks at the same four points as tonight, caef once or twice (today once, at round 4), a $21 "chore" (dbfc) once (new), and a88a, a99c, ec4f and c79e stop and carry with no ask where today each asked once at round 4; my earlier cap cards overstated a round's cost (I wrote ~1% of a week, 30-40 min)
  stakes: reversible, wide — every dev-cycle run, librarian or standalone
  (a) a spend budget replaces the round count — asks come at real cost: a cheap loop finishes, an expensive one asks with what is left, what was spent, and what the next round buys; needs two context-guard items first (price the 5.5 models; a spend reader by agent id) and supersedes most of the finish-at-cap plan (its bound, its rule order, its spend and hold sections) — undo: edits to dev-cycle and librarian-mode rules; stored lines stay readable — who: every capped run; standalone runs past the 4th review loosen (Q7 offers keeping them as today)
  (b) keep the cap with a small spend allowance for finish rounds — the smallest change to the finish-at-cap plan; cheap leftovers that are not exact fixes still ask at round 4 — undo: an edit — who: capped runs
  (c) keep rounds — no spend reader needed; cap cards keep guessing the cost — undo: an edit — who: capped runs
  (z) decide later — the finish-at-cap build keeps waiting; caps come to you as today
  rec: (a) · basis partial — simulated on 112 real items with cited prices and reviewed 4 rounds; the defaults sit near each kind's maximum, so margins are thin, and the sample is one repo over two weeks
  basis: observed — 112 items' spend at cited prices (.claude-sandbox/investigations/f65b-review-cost-budget/evidence/item-costs.md, item_cost.py) · observed — the asks simulated with the convergence stop (03_convergence-simulated.md § 1) · inferred — product repos likely cost more than this kit (an open question)
  unknown: whether repos need their own defaults; whether effort xhigh should scale the budget; whether the research skills' cost line should show measured spend (all three non-blocking)
note: operator 2026-10-02 on decision 145, verbatim: "145 - where did you get these numbers? Are they based off real usage? if not, you should investigate better thresholds from web search and our real conversation data. You can kick that off in the appropriat sub-agent now" (read as: tell me where the numbers come from, and dig into — widen the evidence with web search and all of our real conversation data; the result comes back on 145)
decision 145: Should a spend budget per item, set when each phase starts and raised only on a justified ask, replace the 4-round review cap? — options: (a) yes: a per-item spend budget replaces the round count as the trigger to ask, with the headroom table [recommended] | (b) keep the cap; finish rounds past it spend from a small allowance (about $2) instead of a count | (c) keep counting rounds: round 4, then round 5 only with fewer leftovers; only your hold stops a finish round | (z) decide later
  raised: 2026-10-02T17:35Z
  revised: 2026-10-02T19:36Z — dig into came back (f65b reopened, serials 04-06, review CLEAR): evidence widened to six repos, 204 items, prices verified on Anthropic's pricing page, 13 external sources; defaults moved to a headroom table; the tight table kept as a setting
  what: how the review loop decides when to stop and ask you, in cost instead of rounds; replaces 141 and 142. (a)'s settings, each yours to change in the reply: unit — list-price dollars shown with their share of a week; budgets by phase (headroom table) — chore $10, bug $12, other build $22, plan $28, spike $40, a fable pin doubles them, a plan's estimate sets its build's budget and is put to you when over the default; or the tight table $8 / $10 / $18 / $22 / $32 to be asked sooner; the 4-round count stays only as a convergence stop and the fallback when spend cannot be read; at the budget one finish round of exact fixes (about $1) may still run; ask once spend reaches the budget; past the 4th review your hold and the quota reserve still stop it, only the standing grant goes, and a standalone run past the 4th is a named loosening; a plan with no high left at its 4th review still stops and carries its findings. New stored names: budget:, cost:, must-fix, Estimated cost:, the reviewer's MUST-FIX:
  why now: the finish-at-cap build (5bdd) waits on it; the widened evidence cleared review
  why ask: spend — it sets when quota is used without asking you, and (a) adds five stored names (api-name)
  context: you asked where the numbers came from and to widen them with web search and real conversation data · you decide whether a budget replaces the round cap, and which table — then: real usage, six repos with work records (claude-plugins, claude-sandbox, opencode, agents, agent-research, brainboy), 204 items, every agent joined to its transcript, but records only start 2026-09-22 (10 days); prices match Anthropic's pricing page (fetched 2026-10-02); on your plan dollars are notional, but locally $21-22 of list-price spend tracked each 1% of the weekly window; external practice: per-task dollar caps exist (Claude Agent SDK max_budget_usd, SWE-agent $3 per task), none asks a human with a justification or stops on non-convergence; a fix round costs about $4-5; early October spend runs +60-70% per dispatch (two days)
  stakes: reversible, wide — every dev-cycle run, librarian or standalone
  (a) a spend budget replaces the round count, headroom table — ordinary items stay clear until spend rises about 30%; the first extra asks are the outliers a budget should catch (the scan floor, a $21 "chore", caef — caef asks once spend rises 7%); 7-9 asks on 4-6 items over the 204, plus 2 pending in claude-sandbox, against today's 12 on 8; needs two context-guard items first (price the 5.5 models; a spend reader by agent id) and supersedes most of the finish-at-cap plan — undo: edits to dev-cycle and librarian-mode rules; stored lines stay readable — who: every capped run; standalone runs past the 4th review loosen (a setting keeps them as today)
  (b) keep the cap with a small spend allowance for finish rounds — the smallest change; cheap leftovers that are not exact fixes still ask at round 4 — undo: an edit — who: capped runs
  (c) keep counting rounds — no spend reader needed; cap cards keep guessing the cost — undo: an edit — who: capped runs
  (z) decide later — the finish-at-cap build keeps waiting; caps come to you as today
  rec: (a) with the headroom table · basis partial — real spend on 204 items across six repos at verified prices, simulated and reviewed; but only 10 days of records, and spend is drifting up
  basis: observed — .claude-sandbox/investigations/f65b-review-cost-budget/ serials 04-06, evidence/item-costs.md, item_cost.py, sim_asks.py, week_rate.py, prices_cited.json · observed — Anthropic pricing page https://platform.claude.com/docs/en/about-claude/pricing (2026-10-02) · cited — 13 external sources (04 § 4)
  unknown: whether repos need their own defaults (not enough data yet); whether the October rise holds; whether effort xhigh should scale the budget
answer 145: a (read as: (a) a per-item spend budget replaces the round count as the trigger to ask, with the headroom table and every recommended setting; build order per the cost-budget series: price the 5.5 models (ebbe), a spend reader by agent id in context-guard, then this item's dev-flow rule, which takes over from the finish-at-cap plan where they overlap)
dep note: build after ebbe (prices) and usage-report-read-an-item-s-spend-by-age-0865 (spend reader); e4ca (review caps follow-up lows) touches the same files — one at a time
dispatch: planner opus high — build spec: consolidate the cost-budget series (f65b 00-06, answer 145 a) with what survives of the finish-at-cap series (5bdd 00-02; answers 139 a, 140 a) into one serial a build follows
agent: planner a0e228e207574a68d round 1
return: planner PLAN_READY — serial 03_budget-rule-build-spec.md (14 files, C1-C27, T0-T18; folds e4ca's lows; three readings for the librarian to record under answer 145)
baseline: 4fc2a726583e 00_initial.md 6384700d074e 01_review-fixes.md e21d7438dc88 02_review-r2-fixes.md e061202eef72 03_budget-rule-build-spec.md 
dispatch: reviewer opus high — plan review round 1 (serial 03)
agent: reviewer adae8adce3ab7fb7b round 1
