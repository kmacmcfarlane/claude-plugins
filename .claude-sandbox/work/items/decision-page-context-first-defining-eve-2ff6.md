---
id: decision-page-context-first-defining-eve-2ff6
title: "decision-page: Context first, defining every term; no rec in the TLDR; fuller background"
short_display_name: decision card context first
type: feature
status: done
priority: 1
created: 2026-10-08
updated: 2026-10-08
closed: 2026-10-08
refs:
  - operator message 2026-10-08
---

Operator 2026-10-08, looking at another session's answer page (card 67, a KAPPA-3570 review): (1) the TLDR/impact named 'four changes' and 'content mode' with nothing saying what they are; (2) 'Rec: start the three now' in the TLDR is redundant, the rec is marked in the options; (3) every card needs a first section called Context that at minimum introduces the terms, items and concepts the Impact, TLDR and options use; (4) the Background fold is scarce: asks whether to auto-expand at publish. Acceptance: decision-page schema + template render a required context first, defining every term the flat part uses; the check refuses a TLDR bullet carrying the recommendation; a call on Background depth/expansion (decision 197); the decisions skill's card Context cue kept consistent. The page itself could not be read from this session (artifact not found for this account).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
decided: wording — the operator's points 1-3 are direction, not a question: Context becomes a required first section defining every term the flat part uses, and the TLDR carries no recommendation; authority the operator's message 2026-10-08
decision 197: Should the page auto-expand the Background fold, or move the substance a cold reader needs into the new flat Context? — options: (a) no auto-expand; Context (flat, first) absorbs What, and is counted outside the ~150-word flat budget [recommended] | (b) auto-expand Background on every card at publish | (c) both | (z) decide later
  raised: 2026-10-08T20:15Z
  why ask: your-call — you asked what I think; it sets how much every card shows unfolded
  impact: Effect → the substance sits flat in Context; Background keeps only why now and why ask · Wait: the plan proceeds under (a) and changes at step 1 if you pick otherwise · reach: every decision page · undo: one template edit · cost: none
budget: waived (operator 2026-10-08); spend measured
dispatch: planner opus high — plan, scratch scratchpad/2ff6-plan/
agent: planner a04ef97916d875b77
shown 197: 2026-10-08T20:16Z chat
return: DONE series 00_initial.md (context required and first, absorbs what; Rec-bullet and undefined-id refusals; check_cards.js pre-publish; chat card one-sentence mapping; OQ1 = 197, OQ2 chat cards open on Context, not blocking)
baseline: plan review 1 — 2164952866460e8432c1174ef8a3528f06f26c723cfbe219a11cb7d87b0bd4c3 .claude-sandbox/investigations/decision-page-context-first-defining-eve-2ff6/00_initial.md; eaba1e217cb65a0cafa8094446f5d9311fb791b2bf48a83382e2bc20ae76c563 .claude-sandbox/investigations/decision-page-context-first-defining-eve-2ff6/INDEX.md;
dispatch: reviewer opus high — plan review 1, scratch scratchpad/2ff6-review/
agent: reviewer ab0d87af0996dbbec
verdict: plan review 1 NEEDS_CHANGES (must-fix 4: keep-rev too broad, breaks tell-me; old cue-only context silently drops what; id check refuses UTF-8/SHA-256/ISO-8601/S3/hex colours and blanks the page; counts and named modes have no named rule; lows 5-11: TLDR regex misses, runner path, test gaps, named-only passes, rendering.md reason, README node, blast radius views)
dispatch: planner opus high — plan fix round 1 (resume a04ef97916d875b77)
return: DONE series 01_review-fixes.md (page refuses only missing context and clear rec bullets; id/count/named-thing checks are runner lints, exit 2; old what rendered at the end of Context; new info gets a new rev, only the format migration keeps it; card 42 models a counted gloss)
baseline: plan review 2 — 2164952866460e8432c1174ef8a3528f06f26c723cfbe219a11cb7d87b0bd4c3 .claude-sandbox/investigations/decision-page-context-first-defining-eve-2ff6/00_initial.md; ddc88e6890f320f6af3e7302bd11a3296a886d68af999f959dbff165460c8852 .claude-sandbox/investigations/decision-page-context-first-defining-eve-2ff6/01_review-fixes.md; 52badaf268cd7a4b7ac89c1fe749b628cf9caa1aa67449b682ba7ec614311ae6 .claude-sandbox/investigations/decision-page-context-first-defining-eve-2ff6/INDEX.md;
dispatch: reviewer opus high — plan review 2 (resume ab0d87af0996dbbec)
verdict: plan review 2 NEEDS_CHANGES (must-fix 2, down from 4: example card 43 trips the named lint so 'runner prints nothing on the example' is false; migration keep-rev clause contradicts itself on facts from the caller's record; lows 3-8: rev wording, leftover what order and duplicate lint, TLDR third-party refusals, noisy count/named lints, runner on malformed input, card 42's own terms)
dispatch: planner opus high — plan fix round 2 (resume a04ef97916d875b77)
return: DONE series 02_review-2-fixes.md (one rev rule in identical words, the caller's record dropped; cards 42/43 lint-clean, probe5; TLDR passes 'recommended by'; lints quieter, residue in R3; runner lints only after check())
baseline: plan review 3 — 2164952866460e8432c1174ef8a3528f06f26c723cfbe219a11cb7d87b0bd4c3 .claude-sandbox/investigations/decision-page-context-first-defining-eve-2ff6/00_initial.md; ddc88e6890f320f6af3e7302bd11a3296a886d68af999f959dbff165460c8852 .claude-sandbox/investigations/decision-page-context-first-defining-eve-2ff6/01_review-fixes.md; 8eba1bcd713ca6eeaf82b2a801e6d3f51e47a65458b7f05144a6466230b7afae .claude-sandbox/investigations/decision-page-context-first-defining-eve-2ff6/02_review-2-fixes.md; 28330a46b785d46208ec853c64886415866ef0f809e170815fe5d4ba6814a59c .claude-sandbox/investigations/decision-page-context-first-defining-eve-2ff6/INDEX.md;
dispatch: reviewer opus high — plan review 3 (resume ab0d87af0996dbbec)
verdict: plan review 3 CLEAR (lows carried: 1 rev rule opens 'any change', a re-ask named; 2 % exclusion \b; 3 'Rec -b'/'Rec-(b)' accepted misses + tests; 4 probe5 path arg; 5 Fix G fixture contradictory; 6 runner exit-1 also on template unreadable or marker missing)
findings: carried — plan review 3 lows 1-6, into the build's acceptance
decided: placement — build now under 197 (a); the merge waits on the operator's answer to 197, since (a) is the substance of the change and they asked for my view; authority: the operator's request, decision 197 open
dispatch: implementer opus medium — build, worktree
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a14da422f7db4d314
answer 197: a — "197a" (chat, 2026-10-08)
return: DONE worktree-agent-a14da422f7db4d314 9573ed1 (12 files; carried lows 1-6 done; beyond plan: ids stripped before counting; checks all OK; page not opened)
dispatch: reviewer opus high — review round 1 of 9573ed1, scratch scratchpad/2ff6-codereview/
agent: reviewer ad3df856de943941b
verdict: review round 1 CLEAR (must-fix 0; lows: 1 broad TLDR lint flags Recent/Records; 2 schema dash wording; 3 rulings.md lacks the 197 ruling and its alternative; 4 record lacks the verification tier and the artifact-design note)
verified: tests only — the page was not published or opened; light/dark and phone width of the new .ctx block unseen; the implementer loaded artifact-design for the style change (its return); tokens reused, no new colours
decided: cap — finish round of exact-fix leftovers 1-3 (authority answer 145); 4 is this record line
dispatch: implementer opus medium — finish round (resume a14da422f7db4d314)
return: DONE c2748db (finish round: REC_BROAD rec whole word + recommend…; schema dash wording; rulings 197 line; 62 tests OK; cc_scan clean)
review: self
verdict: finish round CLEAR — diff read: exactly the three fixes plus one test; suggest… pre-existing
landed: 7932512 (merge of 9573ed1, c2748db); Checks 10/10 OK
follow-up: note on 729e that Context now opens the card; the session owning decision 67's page needs context on every card, no Rec bullet, and a new rev on 67 — relay via the operator (that page's session is not known here)
- 2026-10-08 done
correction: 2026-10-08 pushed a7dae3e..3fa8e10 before printing the Report (rule: push right after the Report); content unaffected, Checks and scan read first
