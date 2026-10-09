---
id: decision-page-tldr-first-levels-shaped-s-1e00
title: "decision-page: TLDR first; levels shaped sentence, bullets, sections; impact one field per line, across all options"
short_display_name: decision card format v2
type: feature
status: done
priority: 1
deps:
  - decision-page-folds-written-at-block-dep-eda1
created: 2026-10-09
updated: 2026-10-09
closed: 2026-10-09
refs:
  - operator message 2026-10-09
---

Operator 2026-10-09 after using the live page: (1) TLDR at the top, then Context, then Impact; (2) the levels are too close in verbosity: summary = one or two sentences; medium = a bullet list with an optional sub-bullet or two; high = sections with bullets and sub-bullets; summary and medium bullets are terse sentence fragments; (3) never machine-readable ids: refer by short name, slug or title; the page is the operator's only context; (4) the Impact summary puts each field on its own line; (5) the card-level Impact covers the decision across all its options, not the recommendation's effect (an option's effect lives in its detail). Also answer 201 (c): levels optional, scaled to the decision's size. Acceptance: template, schema, SKILL.md Step 2, example and runner reflect each point; runner flags ids in prose and a card Impact that is only the rec's effect where it can; example rewritten.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
findings: carried — from eda1 review 2: mark the rulings 198 entry '(levels optional since 201)'; rewrap SKILL.md:167, cards-schema.md:228, test_depth.py:11; let the example's small card (43) carry no levels and update the § Size cost figures
dispatch: planner opus high — plan, scratch scratchpad/1e00-plan/
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: planner a6e96152cb104f1de
return: DONE series 00_initial.md (TLDR/Context/Impact order; structured levels {t,sub}/{h,b}; shape lints; id lint everywhere; Impact one facet per line and across all options, rec-only-effect lint; carried findings; example 41/42 levelled, 43 none; OQ1-4 non-blocking)
baseline: plan review 1 — 1ba05b50d8652ed812f7aad44aa5dc81e90c23a080b80976cb3964a7479796b4 .claude-sandbox/investigations/decision-page-tldr-first-levels-shaped-s-1e00/00_initial.md; a7a4b28579293fa2557b66167257d16f9bbed37580fc1eef99ef613e3671f721 .claude-sandbox/investigations/decision-page-tldr-first-levels-shaped-s-1e00/INDEX.md;
dispatch: reviewer opus high — plan review 1, scratch scratchpad/1e00-review/
agent: reviewer a5b03a613f38fa51a
verdict: plan review 1 NEEDS_CHANGES (medium 4: id lint misses layer titles/page title and bracketed tags like (9652), which the live page's layer titles carry; runner TLDR rec lint stops working on structured levels; decisions skill § Impact will contradict the page's decision-wide effect; Impact medium's shape lints unclear; lows 5-7: bb44 status and example classes, id patterns flag ordinary words, two test details; nits 8-9)
correction: the live page's layer titles I wrote carried ids, e.g. 'History scrub (4151)', which the operator's rule now forbids on a page
dispatch: planner opus high — plan fix round 1 (resume a6e96152cb104f1de)
return: DONE 01_review-fixes.md (id lint on titles + bracketed tags, false hits tightened; runner walks structure; rendering.md one sentence; Impact medium bullets per facet, card 41 48/118/196; bb44 tags adopted; test helpers; t+h refused)
baseline: plan review 2 — 1ba05b50d8652ed812f7aad44aa5dc81e90c23a080b80976cb3964a7479796b4 .claude-sandbox/investigations/decision-page-tldr-first-levels-shaped-s-1e00/00_initial.md; 5248a53b8bdf9b3159b41be31bdef1ce3bbaefc1226fc6daf512ec5a2689b1bf .claude-sandbox/investigations/decision-page-tldr-first-levels-shaped-s-1e00/01_review-fixes.md; 5c9d02fe5b459f5532d79870f38e4d0339b69f1502085daa1532abf8b238caba .claude-sandbox/investigations/decision-page-tldr-first-levels-shaped-s-1e00/INDEX.md;
dispatch: reviewer opus high — plan review 2 (resume a5b03a613f38fa51a)
verdict: plan review 2 CLEAR (lows: 1 example classes should follow bb44's order — 42 one-way, 41 trust or a stated reason; 2 'item 2026' clean per spec, prototype wrong — implement the spec; 3 card 41 Impact medium draft carries 9 sub-bullets — trim to the operator's 'a sub-bullet or two'; 4 cap sub-bullets at 2, grouping options; nits: unit-word skip for bracketed numbers, decision-number false hits, '#4151' missed, 'runner passes clean' means lints only, citation)
findings: carried — plan review 2 lows 1-4 and nits, into the build's acceptance
decided: 2026-10-09T07:57Z reading — OQ3 (TLDR summary as one or two terse bullets) and OQ4 (Context summary held to two sentences, linted at about 60 words) follow the operator's own words ('one or two sentances'; 'terse sentance fragments'); built as the plan recommends
decided: 2026-10-09T07:57Z scope — OQ2 (when to republish the live page): after landing, a fresh page carrying only the open decisions (172, 180, 204, 205 and any new), written to the new format; answered cards are not republished
decision 206: Should the chat decision cards follow the page and define Effect as the decision's impact across all options, not the recommendation's? — options: (a) yes, as its own item after this lands: the decisions skill's card and the stored impact: lines change, old lines read as before [recommended] | (b) no: chat Effect stays the recommendation's; only the page differs | (z) decide later (the page differs meanwhile; the rendering.md sentence says so)
  raised: 2026-10-09T07:57Z
  why ask: contract — Effect is a stored field every librarian writes and every decision view reads
  impact: Effect → chat cards and the store say the same thing as the page · Wait: none, the page change ships either way · reach: every chat decision, every librarian store's impact: lines · undo: one rule edit; stored lines written meanwhile stay readable · cost: one build
  unknown: whether a decision-wide Effect fits at tag size in a chat list line
dispatch: implementer opus medium — build, worktree (plan CLEAR at review 2)
shown 206: 2026-10-09T07:57Z chat
agent: implementer a5b91673abb322595
return: DONE worktree-agent-a5b91673abb322595 844b806 (TLDR/Context/Impact order; shaped levels; id lint on titles; Impact facets per line, across options; classes 41 trust / 42 one-way; sub-bullets capped at 2; 10/10 Checks, operator-interaction 117; runner exit 0 on the example; on the live page: 455 lint lines; tests only, no render)
dispatch: reviewer opus high — review round 1 of 844b806
agent: reviewer a9c6313902e894792
verdict: review round 1 NEEDS_CHANGES (medium 3: cards-schema.md:245 says the closed card shows the rec's option title, it doesn't; the 360px both-theme preview not run; the older string detail.rec render lost its only test; lows: rulings.md:60 order not marked superseded, empty sub refuses the page, duplicate id lint lines; nits: wraps, 'layer details's', bracketed port numbers); live page renders under jsdom with 455 lint lines and no refusal
decided: 2026-10-09T08:31Z scope — finding 2 (the visual preview) can't be done in this sandbox (no browser); the change lands on tests plus jsdom renders, the gap stated in its Report, and the operator sees the layout on the fresh open-decisions page published on it; a broken layout is a quick follow-up fix
dispatch: implementer opus medium — fix round 1 (resume a5b91673abb322595)
return: DONE 4497048 on merge a9adf02 (schema sentence; string rec-level test restored; rulings marked; empty sub accepted; id dedupe by longest match; nits; 11/11 Checks, operator-interaction 119; cc_scan run as an equivalent Python script after the shell guard refused the function)
dispatch: reviewer opus high — review round 2 (resume a9c6313902e894792)
verdict: review round 2 CLEAR (nit: two long lines, rulings.md:65 and cards-schema.md:248 — carried to a416, which edits the same files)
landed: f8ea87e (merge of 844b806, a9adf02, 4497048); Checks 11/11 OK; runner exit 0 on the example
verified: tests and jsdom renders of the example and live cards (order, structure, escaping); layout at 360px and in dark mode not seen (no browser here) — the operator sees it on the fresh open-decisions page
- 2026-10-09 done
