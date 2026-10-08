---
id: decision-page-folds-written-at-block-dep-eda1
title: "decision-page: folds written at block depth, so the page never needs an expand round"
short_display_name: decision page rich folds
type: feature
status: todo
priority: 1
deps:
  - decision-page-context-first-defining-eve-2ff6
created: 2026-10-08
updated: 2026-10-08
refs:
  - operator message 2026-10-08
---

Operator 2026-10-08 (after 197 a): asked whether to relax word counts per medium (page vs chat card vs chat block); wants to open a page's panels and get rich extra info there instead of waiting a round for an expand. Today: only the flat part has limits (~150 words; effect ~10; t 2-6; title <=6; tldr 2-3 bullets); folds have no limit, but their fields are single strings copied from the chat card, so they hold card depth. Acceptance: the page's folds carry the decisions skill's block content for every card (per option what happens, undo, who, cost; why now / why ask in full; the basis drill-down with paths and links); stated soft sizes per fold; the writer draws from the series and record, not only the stored card; the chat card and block limits stay as they are.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
decision 198: Write every decision page's folds at block depth, with soft sizes per fold? — options: (a) yes: flat part as now (~150 words + Context); Background ~150 words; Options in full ~60-120 words per option (what happens, undo, who, cost) on every card; Evidence ~150 words with paths and links; a card ~600-900 words in all [recommended] | (b) yes, with no sizes at all | (c) only for ⚠ and wide cards | (z) decide later
  raised: 2026-10-08T21:10Z
  why ask: rule-change — it sets how every decision page is written, and its cost per page
  impact: Effect → opening a panel gives the block's detail, so an expand round is never needed for depth · Wait: none, this build follows 2ff6 · reach: every decision page · undo: one edit to the schema's size rule · cost: a writer pass per page that reads the series, about a few minutes and a small share of quota per page
shown 198: 2026-10-08T21:10Z chat
answer 198: a, with changes — "198 - close. The always visible parts should toggle a medium-detail and high-detail set of information when you click them. A button labeled \"more decision detail\" to the right of each of the options should toggle full-detail on that option." (chat, 2026-10-08; read as: (a)'s depth and soft sizes, but shown in place rather than in separate folds: clicking an always-visible section (Context, Impact, TLDR) steps it from summary to medium detail to high detail and back; each option row gets a 'more decision detail' button on its right that toggles that option's full detail (what happens, undo, who, cost); plan carries this reading, operator to correct)
dispatch: planner opus high — plan, scratch scratchpad/eda1-plan/
agent: planner a5c066fa5a90bb422
