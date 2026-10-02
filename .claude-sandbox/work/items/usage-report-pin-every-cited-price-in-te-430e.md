---
id: usage-report-pin-every-cited-price-in-te-430e
title: "usage-report: pin every cited price in tests, fix the fast-mode note, retire or test the uncertain flag"
short_display_name: usage-report price test follow-ups
type: chore
status: todo
priority: 3
created: 2026-10-02
updated: 2026-10-02
refs:
  - usage-report-price-the-5-5-models-opus-5-ebbe
---

Review lows on ebbe (landed 614b738): 1 CITED_PRICES in tests/test_usage_report.py covers only the new models — add claude-opus-5 ($5/$25/$6.25/$10/$0.50), claude-sonnet-5 ($2/$10/$2.50/$4/$0.20), claude-haiku-4-5 ($1/$5/$1.25/$2/$0.10) and check the Opus 4.7/4.8 aliases resolve to Opus 5; 2 prices.json:15 fast-mode note: Opus 5.5 fast is $8/$40, Opus 4.8 shares Opus 5's; 3 usage_report.py:213, :705 is_uncertain and its warning are dead code — remove both, or keep with a fixture test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
