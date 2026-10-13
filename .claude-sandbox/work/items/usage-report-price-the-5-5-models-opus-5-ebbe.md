---
id: usage-report-price-the-5-5-models-opus-5-ebbe
title: "usage-report: price the 5.5 models (opus-5-5, sonnet-5-5) and fable-5-1 from a cited source"
short_display_name: price the 5.5 models
type: bug
status: done
priority: 2
created: 2026-10-02
updated: 2026-10-02
closed: 2026-10-02
refs:
  - dev-cycle-review-spend-as-a-per-item-cos-f65b
---

Found by the cost-budget investigation (f65b, 00-01): plugins/context-guard/skills/usage-report/scripts/prices.json has no entry for claude-opus-5-5 or claude-sonnet-5-5, so usage_report.py prices opus-5-5 as sonnet-5 (14-day opus-5-5 spend reads $749 vs $1,079 at cited prices, ~1.44x under). Cited (claude-api skill model table, cached 2026-09-25): Opus 5.5 $4/$20/$0.20 cache read, Sonnet 5.5 $2/$10/$0.20, Fable 5.1 $10/$50/$0.25; cache-write rates derived (1.25x / 2x input) unless a source gives them. Evidence: .claude-sandbox/investigations/f65b-review-cost-budget/evidence/prices_cited.json. Acceptance: entries with their source cited; a test that the 5.5 models price at those rates; an unknown model is reported, not silently priced as another. Independent of decisions 141/142.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-02 claimed by Kyle-McFarlane@401123cbad11
target: full usage-report-price-the-5-5-models-opus-5-ebbe /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/usage-report-price-the-5-5-models-opus-5-ebbe
dispatch: implementer opus medium — build (data table + test; cited source)
agent: implementer aad59d4eef75ceee3 round 1
return: implementer DONE ad14b87 (concern: removed "uncertain" flags — the prices are now cited and verified)
librarian ruling: the uncertain flags go — the figures are verified against the pricing page and the claude-api table, so the warning would be false; the reviewer checks it
dispatch: reviewer opus high — review round 1
agent: reviewer a51c90bbdabe873b6 round 1
verdict: CLEAR round 1 at ad14b87
findings:
  all 35 figures match the pricing page (7 entries); removing every uncertain flag is supported; aliases and totals unchanged
  1. [low] tests/test_usage_report.py:672 — CITED_PRICES covers only the new models; add opus-5, sonnet-5, haiku-4-5 and check the 4.7/4.8 aliases
  2. [nit] prices.json:15 — fast-mode note lists only Opus 5; Opus 5.5 fast is $8/$40
  3. [nit] usage_report.py:213,705 — is_uncertain and its warning are now dead; remove or add a fixture test
landed: 614b738
- 2026-10-02 done: landed 614b738 (CLEAR r1)
