---
id: model-routing-f2b-the-xhigh-trial-fable-fa73
title: "model routing F2b: the xhigh trial, fable cross-checks offered, reviewer effort by kind, quota step-down"
short_display_name: routing F2b
type: feature
status: doing
priority: 1
parent: model-routing-set-reasoning-effort-per-r-2eb7
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-09-30T22:27Z
created: 2026-09-30
updated: 2026-09-30
refs:
  - .claude-sandbox/investigations/6421-tier-criteria/INDEX.md
  - 69ee answers 123-127, decision 130
---

2eb7 F2b per the 6421 answers (pyramid answers 2026-09-30 (69ee, answer page)): 123 a (plans at opus high; xhigh on the next planner round of half the plans that turn hard in review 1-2, two-week trial; pins always); 124 b with the operator's words — fable cross-checks are OFFERED at (b)'s stages with why, never run unasked; the keep rule counts accepted ones; 125 per decision 130 (estate-wide: offered or automatic); 126 b (opus medium reviews only for fact/docs changes in the home-network and product-docs repos); 127 a (below the reserve xhigh steps down to high and fable offers wait; pins still ask). Home: dev-cycle references/model-routing.md. Carries a88a review r4's three fixes and 2eb7 r4's lows.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
2026-09-30 130 a: the estate-wide stage is an offer (once per series, final plan, fable xhigh), like 124's

## Notes
- 2026-09-30 claimed by Kyle-McFarlane@401123cbad11
target: full model-routing-f2b-the-xhigh-trial-fable-fa73 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/model-routing-f2b-the-xhigh-trial-fable-fa73
dispatch: implementer opus medium — opus signal: routing rules skill text; feature with no own series: /investigate then /implement from 2eb7 04 + 6421 03 + answers (waves 1-3, 132 a)
agent: implementer a61d37fcc4f73c086 round 1
return: implementer DONE_WITH_CONCERNS 3a9e338
changed: undeclared Files in scope — 22 files; reasons per the implementer's CHANGED (model-routing.md home; agents reviewer-light (new), reviewer, cross-checker, cross-checker-deep, planner-deep descriptions; tests/test_agents.py; dev-cycle SKILL.md, record-lines.md, resume.md, fix-loop.md, review-brief.md, troubleshooting.md; librarian-mode SKILL.md, budget.md, idle-turn.md, troubleshooting.md; dev-flow plugin.json + marketplace.json (pin test); CLAUDE.md + README.md (agent added); kit-dev update-kit repo-map.md (agent listing))
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer a5abb53ae3c3981d6 round 1
verdict: NEEDS_CHANGES round 1 at 3a9e338
findings:
  1. [medium] model-routing.md:244-247 (with :470) — an open fable offer holds the plan's build; below the reserve the offer waits for reset and the item is handed off — stalls builds for days, contradicts 127 a's stated effect ("deep items keep moving") and the series' own non-blocking mitigation; undeclared
  2. [medium] librarian-mode references/budget.md:8-11 — restates the routing threshold and effect (second home); insertion also breaks the following "The reason is…" sentence
  3. [low] model-routing.md:233 (with :8-11, record-lines.md:184) — research-synthesis plan stage has no trigger and a one-writer contract that forbids its lines
  4. [low] model-routing.md:249-251 — author-rule opus stand-in: dispatch line, round counting, cross-check line unspecified; reads against "a pinned tier never falls below its pin"
  5. [low] model-routing.md:262-268 — keep rule counts 8+ lines unordered, not "first 8"
  6. [low] resume.md:199 (S7) — resumed plan run whose record ends in an old second-opinion CLEAR gets a fresh offer
  7. [low] dev-cycle SKILL.md Steps 5-6 — no step names the post-landing offer
  8. [low] dev-cycle SKILL.md — 4601 words, +107 over main's already-over size (fefd)
  9. [low] agents/cross-checker*.md:3, README.md:286-287 — stage lists restate the routing table; README "the same" misstates the post-landing stage
  10. [nit] tests/test_agents.py:47,280 — dead "conditional" branch
  11. [nit] review-brief.md:10 — cross-checker-deep lacks dev-flow: prefix
  12. [nit] model-routing.md:650 — example decision line lacks per-option impact
  13. [nit] model-routing.md:468 — below the reserve only bump units excluded; selection bias
decided: 2026-09-30 reply-reading — finding 1: an offer never holds the build; 127 a's card said deep items keep moving. The plan's build proceeds while an offer is open or deferred; an accepted plan-stage check runs when headroom allows and its findings enter the build's fix loop before landing, or become a follow-up item after it · authority: answer 127 · reopen: say "hold builds on open offers"
decided: 2026-09-30 reply-reading — the five-hour window's reserve does not trigger the step-down; "below the reserve" is the weekly window (127 a's grant stops at the 15% weekly reserve; the five-hour default reserve would trip it constantly) · authority: answers 88, 127 · reopen: say "both windows"
dispatch: implementer opus medium — resume
agent: implementer a61d37fcc4f73c086 round 2
