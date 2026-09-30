---
id: model-routing-f2b-the-xhigh-trial-fable-fa73
title: "model routing F2b: the xhigh trial, fable cross-checks offered, reviewer effort by kind, quota step-down"
short_display_name: routing F2b
type: feature
status: done
priority: 1
parent: model-routing-set-reasoning-effort-per-r-2eb7
created: 2026-09-30
updated: 2026-09-30
closed: 2026-09-30
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
return: implementer DONE 12ee2cc
changed: (this round adds nothing new to the file set; README.md, cross-checker*.md, test_agents.py, model-routing.md, record-lines.md, resume.md, SKILL.md, budget.md, review-brief.md edited again)
dispatch: reviewer opus high — resume
agent: reviewer a5abb53ae3c3981d6 round 2
verdict: NEEDS_CHANGES round 2 at 12ee2cc
findings:
  prior 1-7, 9-13 FIXED; 8 DECLINED (accepted)
  1. [medium] resume.md:200 (S7) with :108-119 (GATE) — the offer's own decision:/answer: lines are not excluded like the tagged dispatch-permission lines: a pending offer holds the plan run (PENDING), an answered offer after a pending blocking question bypasses it (ANSWERED)
  2. [medium] model-routing.md:248-250, 289-293 — accepted plan-stage/estate-wide findings "enter the build's next fix round" but nothing hands them to the build's record; no state opens a fix round from a fresh CLEAR; CLEARed-not-merged and not-started cases open
  3. [low] fix-loop.md:45-51 — "the last agent: reviewer line" can pick the author-rule opus stand-in rider on a fable-pinned item
  4. [low] resume.md:108-112 with :179 — a lost cross-check rider is never probed or reported on resume
decided: 2026-09-30 reply-reading — finding 2: an accepted check's findings that arrive before the build's CLEAR are written onto the build item as a findings: block and open its next fix round (counted toward the cap); any that arrive after the build's CLEAR — merged or not, or before the build starts on a plan already closed — become a follow-up item; no new resume state · authority: answer 127, ruling A · reopen: say "hold the landing for late findings"
dispatch: implementer opus medium — resume
agent: implementer a61d37fcc4f73c086 round 3
return: implementer DONE be5b465
changed: (same 22-file set; this round: model-routing.md, record-lines.md, resume.md, fix-loop.md, review-brief.md)
note: implementer's first combined Checks run was killed (exit 144) during work-items; re-run separately, all pass — watch at Land
dispatch: reviewer opus high — resume
agent: reviewer a5abb53ae3c3981d6 round 3
verdict: NEEDS_CHANGES round 3 at be5b465
findings:
  prior 1, 3 FIXED; 2, 4 PARTIAL
  1. [medium] record-lines.md:181-183, model-routing.md:282 — keep-rule grep counts `dropped` lines as misses; breaks "a check counts only when it ran"
  2. [medium] review-brief.md:17-19, model-routing.md:252-256 — the build reviewer can CLEAR over accepted cross-check findings with no record of which it overruled; cross-check: line already counted them
  3. [low] resume.md:36-40 — a finished-but-uncollected cross-check is treated as alive and never collected
  4. [low] resume.md:36-40 — old second-opinion lines match the drop probe → false dropped line
  5. [low] resume.md:207 (S9), fix-loop.md — "the findings: block" singular; a cross-check block after a reviewer's NEEDS_CHANGES hides the reviewer's findings
  6. [nit] record-lines.md:162 "the one tagged decision"; model-routing.md:612 opus+fable
dispatch: implementer opus medium — resume (fix round 3; the next review is round 4, the cap)
agent: implementer a61d37fcc4f73c086 round 4
return: implementer DONE 592c47c
dispatch: reviewer opus high — resume
agent: reviewer a5abb53ae3c3981d6 round 4
verdict: CLEAR round 4 at 592c47c
notes: prior 1-6 FIXED; new low 1: SKILL.md Step 4.5 does not name the cross-check-rulings: block (record-lines.md:206 does) — carried to fefd's trim as a ~12-word pointer
landed: a597939
- 2026-09-30 done: a597939
