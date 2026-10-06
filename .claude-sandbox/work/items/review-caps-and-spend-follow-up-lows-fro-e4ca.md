---
id: review-caps-and-spend-follow-up-lows-fro-e4ca
title: "review caps and spend: follow-up lows from round 6 (plan-item grep, E2 resume record, reflow)"
short_display_name: review caps follow-up lows
type: chore
status: done
priority: 3
created: 2026-10-01
updated: 2026-10-05
closed: 2026-10-05
refs:
  - review-caps-and-spend-plans-raise-only-o-5579
---

Round-6 review lows on 5579 (landed 2f071a8): 5 agent-brief.md:51-52 the series-path grep can hit several items and misses archived ones — the plan item is the hit with findings: carried lines; include archive/*/*.md. 6 resume.md:225-227 + bindings.md:237-243 — the end of a granted plan path (8dee E2) carries findings but writes no decided: cap line, so a resume between the carry and wi done writes the block twice; write the same decided: line with the grant's answer as authority, or let the resume test accept findings: carried after the last verdict. 7 record-lines.md:121-122 reflow.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
landed in e92f0e3 (the budget rule, 5bdd): lows 5, 6, 7 folded in and closed there

## Notes
- 2026-10-05 done: closed by 5bdd (e92f0e3)
