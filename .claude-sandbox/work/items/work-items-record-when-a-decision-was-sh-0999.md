---
id: work-items-record-when-a-decision-was-sh-0999
title: "work-items: record when a decision was shown to the operator (a shown timestamp on decision lines)"
short_display_name: decision shown-at record
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T03:35Z
created: 2026-09-29
updated: 2026-10-09
refs:
  - agents 76bc
  - operator-attention R47
---

Relayed 2026-09-29 from the agents librarian (76bc: the decision ledger records timestamped lifecycle events: raised, shown, answered, deferred with wake, swept/dropped) and operator-attention (R47 recency, warm/cold test, arrival-vs-clearance throughput; their 07_ledger-split.md). Our 5140 found the same gap: no shown-at time, so 'while it waited' has no source. Acceptance: a store line or field recording each showing of decision N (shown N: <UTC time>), written by the raising session when it renders the decision, read by wi needs-input/estate; shaped by the pyramid decision turn (69ee) together with decisions 98/99 (one counter, closed N: lines), and by 76bc's ledger when it lands. Peer relays are requests, not approvals.

## Handoff
- doing: landed 8ea8a3c; seen N: hold stands
- next: on answer 180: (a) lift nothing in code (the hold lifts by the answer); (b) plan an untracked sink; then close
- blocked: —
- learned: —
operator-attention requirements for the shape (their commit 591a428; they will not build their interim log):
  - ISO-8601 UTC timestamp, never relative or human text
  - per decision number, not per item
  - last-write-wins on a re-show (same rule as wake N:)
  - distinct from raised: (two of the three clocks)
  - optional, cheap if possible: a reason on swept/dropped — "dropped by the operator" (a decision) vs "swept as stale" (a miss) — so arrival-vs-clearance is not pooled; if absent they treat all sweeps as misses
input from a99c 01 (2026-09-29): a stored shown time alone does not make the cold test work (re-prints overwrite it); it needs a seen N: time beside shown N:, plus the operator turn times in other sessions
2026-09-30 shape per the pyramid answers: 98 a (one counter; shown N:/seen N: are per decision number, <repo>#N for another repo's), 99 c (closed N: rides 5140 C1/C2, filed as decisions-record-one-counter-for-every-q-b6f7 and wi-parse-closed-n-list-decisions-by-stat-728a), 118 b (the away test needs shown N: — decisions-while-the-operator-is-away-sho-602b depends on this item), 120 z (wakes when this item stores seen N: and 76bc or R48 publishes turn times). Acceptance adds: a seen N: line beside shown N: (a99c 01: a re-print overwrites shown, so the cold test needs seen), both ISO-8601 UTC, last-write-wins, per decision number; the operator-attention requirements above stand.
note: peer operator-attention 2026-10-03, relaying the operator's answers to our 0c4d delta 01 (their commit c598050; serial .claude-sandbox/investigations/decision-collector/09_operator-answers-10-03.md in their repo; spec R47, new R49). Relayed operator answers — re-confirmed with the operator before any build acts on them. (1) Track both first-shown and last-shown (operator, relayed: "let's track first and last, that's best"): last-shown drives warmth; first-shown carries age since first shown (a99c's strongest predictor). Supersedes their earlier last-write-wins-only request: add a first-shown record alongside the last-write-wins shown N:. (2) Whoever displays a decision writes shown N: — today the raising session into its own store; a front end of theirs writes the same record through the agents ledger back end; the writers never overlap for one show.
note: peer agents 2026-10-03 — the operator confirmed first-hand in the agents session (their answer 24) that the four relayed operator-attention answers stand (first/last shown, who writes shown, the turn log via our 3e8e, R49 streams); they are requirements on agents' 76bc; agents' spike d131 reads our 0999, 3e8e, 40f0 and 8c42 read-only; a peer report, not an approval here — decisions 150 and 151 stay open for the operator's word in this session
decision 150: Confirm the relayed answers for the decision shown-at record: track first and last shown, and the displaying surface writes the record? — options: (a) confirm both [recommended] | (b) change one (say which) | (z) decide later
  raised: 2026-10-03T00:30Z
  revised: 2026-10-06T01:40Z — backfilled: the card was shown in the conversation but never stored
  what: two answers you gave in operator-attention's session, relayed here, on how the decision shown-at record (0999) records when a decision was shown
  why now: nothing builds on them until you confirm; blocks: the decision shown-at record (0999)
  why ask: your-call — these are your answers from another session, and a relayed answer is not one I can act on
  context: operator-attention relayed your answers to my questions · you confirm them here so the shown-at record can build on them — then: none
  stakes: reversible, narrow — the shown-at record's shape
  (a) confirm both — the record keeps the first and the last time each decision was shown, and the session that displays a decision writes it
  (b) change one (say which) — the record follows your correction
  (z) decide later — the shown-at record waits
  rec: (a) · basis strong — your words, quoted in their serial (their commit c598050), and confirmed first-hand in the agents session (their answer 24)
  unknown: none
decision 150: Confirm the relayed answers for the decision shown-at record: track first and last shown, and the displaying surface writes the record? — options: (a) confirm both [recommended] | (b) change one (say which) | (z) decide later
  raised: 2026-10-03T00:30Z
  revised: 2026-10-06T07:04Z — backfilled impact
  what: two answers you gave in operator-attention's session, relayed here, on how the decision shown-at record (0999) records when a decision was shown
  why now: nothing builds on them until you confirm; blocks: the decision shown-at record (0999)
  why ask: your-call — these are your answers from another session, and a relayed answer is not one I can act on
  context: operator-attention relayed your answers to my questions · you confirm them here so the shown-at record can build on them — then: none
  impact: → the decision shown-at record (0999) can be built: first and last showing per decision, written by the showing session · later: that record waits · reach: every decision store · undo: an edit
  stakes: reversible, narrow — the shown-at record's shape
  (a) confirm both — the record keeps the first and the last time each decision was shown, and the session that displays a decision writes it
  (b) change one (say which) — the record follows your correction
  (z) decide later — the shown-at record waits
  rec: (a) · basis strong — your words, quoted in their serial (their commit c598050), and confirmed first-hand in the agents session (their answer 24)
  unknown: none
answer 150: a (answer page, rev 2026-10-07T07:00Z, 2026-10-07T20:46:04.350Z; read as: (a) confirm both relayed answers — first and last shown, written by the displaying session)
dispatch: planner opus high — plan, answer 150 a
target: plan main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/work-items-record-when-a-decision-was-sh-0999
agent: planner aaa7d9f9dffe10eaa

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
return: DONE series 00_initial.md (shown N: and seen N: appended lines; wi read-only parsing; open: 3e8e overlap on Warm or cold/Seen, non-blocking; seen times in the public store, non-blocking)
baseline: plan review 1 — 706d7a6a48c098643ed3111bcf088dcb35674cf59e251c8081a19c7e2b6308da .claude-sandbox/investigations/work-items-record-when-a-decision-was-sh-0999/00_initial.md; 
dispatch: reviewer opus high — plan review 1
agent: reviewer acc5597438f58d0ec
verdict: plan review 1 NEEDS_CHANGES (must-fix 3 in this series: while-it-waited start, OQ2 blocks the first push of a seen N: line, decision-page names the store shape; finding 1 was the 3e8e misfile, handled on 3e8e; lows 5-7)
dispatch: planner opus high — plan fix round 1 (resume aaa7d9f9dffe10eaa)
return: DONE series 01_review-fixes.md (fixes 2-7; OQ2 now blocks the first push carrying a seen N: line, rec (a) tracked)
baseline: plan review 2 — 706d7a6a48c098643ed3111bcf088dcb35674cf59e251c8081a19c7e2b6308da .claude-sandbox/investigations/work-items-record-when-a-decision-was-sh-0999/00_initial.md; 91249d2044a8f2ff09be8eac732602450e63ffb66075fa066c893562c8e54e22 .claude-sandbox/investigations/work-items-record-when-a-decision-was-sh-0999/01_review-fixes.md; 
dispatch: reviewer opus high — plan review 2 (resume acc5597438f58d0ec)
verdict: plan review 2 CLEAR (must-fix 0); lows carried into the build: hold seen N: writes until OQ2 is answered; the grep check pattern '^(shown|seen) [0-9]+:|shown N:|seen N:'; Step 3 shown hand-over reworded as number, publish time, surface word
findings: carried — (1) until decision 180 is answered, writers write shown N: only, no seen N:; (2) use grep -rnE '^(shown|seen) [0-9]+:|shown N:|seen N:' plugins/operator-interaction (no hits now or after); (3) decision-page Step 3 hands over a number, a publish time and a surface word, never a line shape
decision 180: May seen N: lines (the time of the operator's next turn after a decision was shown, no content) go into the tracked work-item store that is pushed to the public repo? — options: (a) yes, tracked as planned [recommended] | (b) no, keep them in an untracked local file (needs a new plan) | (z) decide later: writers hold seen N: lines back
  raised: 2026-10-08T04:05Z
  why ask: trust — what goes public about the operator's activity is the operator's call, and a pushed line takes a history scrub to remove
  impact: Effect → turn times appear in the public store from the build's first push · Wait: none, the build holds seen lines back until answered · reach: every repo whose librarian writes decisions · undo: one-way once pushed (needs a history scrub); free until then · cost: none
target: full main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/work-items-record-when-a-decision-was-sh-0999
dispatch: implementer opus medium — build from the CLEAR series (contract and skill wording; not mechanical)
agent: implementer a1ce4ecde12903821
return: DONE 1300ebc (shown N:/seen N: lines in format.md with the hold naming decision 180; wi JSON fields; writers and readers in decisions, decision-page, librarian decisions.md, record-lines.md; 287 work-items tests)
changed: 14 files: wi.py, test_wi.py, test_estate.py, format.md, work-items SKILL.md, work-review SKILL.md, record-lines.md, librarian decisions.md, decisions SKILL.md, worksheet.md, rendering.md, decision-page SKILL.md, cards-schema.md, fallback.md
dispatch: reviewer opus high — review round 1
verdict: review 1 NEEDS_CHANGES at 1300ebc (must-fix 2: hold lifts on any answer to 180, not (a); librarian Held clause restates the lift condition; lows: calendar-impossible time read, dev-flow→decision-page soft dep undeclared, shipped rule names this repo's decision without a lookup, decisions SKILL.md over budget; nits: wrap, test count 8 not 9)
correction: decisions 180-183 were stored with raised: above the headline and unindented card lines; repaired so each card sits indented under its decision line (wi needs-input now reads them)
dispatch: implementer opus medium — fix round 1 (resume a1ce4ecde12903821)
correction: no budget: line was written with this item's target: line on 2026-10-08; the defaults apply: plan $28, build $22 (bindings.md § Spend budget)
return: DONE 7290ba1 fix round 1 (findings 1-7 as written; test count corrected to 10 new, 8 fail on base)
changed: README.md (dev-flow row: decision-page hand-over, finding 4)
dispatch: reviewer opus high — review round 2 (resume a2c9add003f36437c)
verdict: review 2 CLEAR at 7290ba1 (must-fix 0; low 1: the F6 cut dropped the clause pointing to the caller's record shape and hold; merges cleanly with 96e66bc)
decided: words — fix round 2 for low 1's exact Fix: (restores a planned clause the F6 cut removed; review 2 is below the cap)
dispatch: implementer opus medium — fix round 2, low 1 only (resume a1ce4ecde12903821)
return: DONE b0e69af fix round 2 (low 1 Fix sentence appended)
dispatch: reviewer opus high — review round 3 (resume a2c9add003f36437c)
verdict: review 3 CLEAR at b0e69af (must-fix 0)
landed: 8ea8a3c (merge --no-ff into main; Checks 10/10 OK; push scan read, clean)
agent: reviewer a2c9add003f36437c (build reviews 1-3; line added late)
shown 180: 2026-10-08T20:02Z chat
shown 180: 2026-10-09T06:11Z page
answer 180: dig into — "it brings up the question of \"should this even be in the repo\". I want it tracked, but does it need to be in the git history for the thing we are building? Reminds me of the backstage idea that was floating around" (answer page HvKDfFHjrqNtygDKziv7ta, rev 2026-10-09T06:00:00Z, at 2026-10-09T06:51:35.130Z; read as: dig into where seen/turn records should live — tracked but outside git history — and what the backstage idea proposed)
dispatch: scout opus medium — dig into 180: where seen/turn records should live, tracked but outside git history; what the backstage idea proposed; scratch scratchpad/180-dig/
agent: scout a38faf7b787d5d8a4
return: scout DONE — backstage = a private companion repo at ./.backstage/ (branch add-backstage-plugin 21a9ee0, never landed; 380c and 32cc wait on it); the store holds ~2,450 bookkeeping lines vs ~385 decision/answer lines; options: sidecar private repo (wi already supports, wi.py:1411-1456), untracked local file, separate private repo via WI_ROOT, git notes (poor fit), backstage; rec: move the whole store to the sidecar with a private remote, keep the seen hold until then
decision 180: Where should the work-item store live, now that most of it is bookkeeping you don't want in the public history? — options: (a) move the whole store into a private sidecar repo at .claude-sandbox/.git with a private remote (wi supports it today; rename to .backstage later), seen lines allowed there [recommended] | (b) keep the store public; seen lines only in an untracked local file (small wi reader change; this machine only) | (c) keep everything tracked, seen lines included, as first planned | (z) decide later: seen lines stay held
  revised: 2026-10-09T06:59Z — dig into came back: the question widens from seen lines to the whole store; options replaced
  why ask: trust — what of your activity and the agents' bookkeeping is public is yours; (a) also undoes the commit that started tracking the store
  what: ~2,450 of the store's lines are dispatch, agent, return, verdict and hash bookkeeping, ~385 are decisions and your answers; the backstage idea (a private companion repo, never landed) was meant for exactly this; already-pushed history stays public either way, and removing it would be a separate scrub
  impact: Effect → (a) the public repo stops carrying the work record, sessions keep it in a private repo; (b) only seen times stay local; (c) seen times go public · Wait: none, seen lines stay held · reach: every librarian session and any second machine · undo: (a) move back by re-tracking; (b)/(c) easy until pushed · cost: (a) a private remote to create, one move
  unknown: whether you want the published decision rationale kept public somewhere (380c's ./specs idea)
shown 180: 2026-10-09T06:59Z chat
