---
id: decisions-skill-every-decision-gets-its-18c4
title: "decisions skill: every decision gets its own plain integer; no letter-suffixed (8b) or dotted (8.1) numbers"
short_display_name: no lettered decision numbers
type: feature
status: done
priority: 1
created: 2026-10-08
updated: 2026-10-08
closed: 2026-10-08
refs:
  - peer claude-analytics 2026-10-08 (operator request there)
---

Relayed 2026-10-08 by peer claude-analytics from the operator there: a follow-up raised as '8b' read as 'decision 8, option (b)', the hint's own form ('72: a'); the operator called it confusing and asked for guidance. Acceptance: decisions SKILL.md (Critical, next to 'Keep the caller's numbering … Never reuse a number') says every decision, sub-decisions and follow-ups included, takes its own plain integer from the counter, never a letter suffix or dotted form; a dependent follow-up names its dependency in words ('only if 9 is (a)'); option letters stay the only lettered thing. A gallery or replies note if one fits. Same file as dcf8's build: land this first.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decided: wording — adopt the peer's suggested rule as written; the operator asked for it in their session, and it extends "never reuse a number" without changing any answer
target: full main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/decisions-skill-every-decision-gets-its-18c4
budget: 2026-10-08T05:21Z build $22 — default other build
dispatch: implementer opus medium — skill rule wording

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a12e3ca2d8538e3a5
return: DONE b7b2336 (Critical bullet plain-integer rule; Plain integers ruling; gallery Not this under example 10; replies.md unchanged: it parses N: letter only)
changed: decisions SKILL.md (rule + ruling), references/gallery.md (Not this)
dispatch: reviewer opus high — review round 1
agent: reviewer aa5f510bd78c812af
verdict: review 1 CLEAR at b7b2336 (must-fix 0; lows: ruling names this setup's session in a shipped skill, "follow-ups" collides with decision-page's reply shortcuts; nit: gallery follow-up points at the withdrawn 79)
decided: wording — fix round 1 for the three exact Fix: lines (a shipped skill should not name this setup's session; review 1 is below the cap)
dispatch: implementer opus medium — fix round 1, lows 1-3 (resume a12e3ca2d8538e3a5)
return: DONE 71dce90 fix round 1 (three Fix: lines as given)
dispatch: reviewer opus high — review round 2 (resume aa5f510bd78c812af)
verdict: review 2 CLEAR at 71dce90 (must-fix 0)
landed: d00a84f (merge --no-ff into main; Checks 10/10 OK; push scan read, clean)
- 2026-10-08 done
