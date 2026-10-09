---
id: decision-page-tldr-first-levels-shaped-s-1e00
title: "decision-page: TLDR first; levels shaped sentence, bullets, sections; impact one field per line, across all options"
short_display_name: decision card format v2
type: feature
status: todo
priority: 1
deps:
  - decision-page-folds-written-at-block-dep-eda1
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
