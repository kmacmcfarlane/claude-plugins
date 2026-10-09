---
id: decision-page-tldr-first-levels-shaped-s-1e00
title: "decision-page: TLDR first; levels shaped sentence, bullets, sections; impact one field per line, across all options"
short_display_name: decision card format v2
type: feature
status: doing
priority: 1
deps:
  - decision-page-folds-written-at-block-dep-eda1
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T07:11Z
created: 2026-10-09
updated: 2026-10-09
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
