---
id: context-guard-status-line-records-rate-l-81a5
title: "context-guard: status line records rate_limits in the context-gate state record"
type: feature
status: done
priority: 3
created: 2026-09-18
updated: 2026-09-18
closed: 2026-09-18
refs:
  - f696 impl open question 3
---

From f696/7db3 (2026-09-18): librarian-mode's fable-unavailable fallback reads the reset time from rate_limits in claude-kit/context-gate/<session>.json, but statusline.py only displays rate_limits and stores only the exact block. Acceptance: statusline.py writes rate_limits (five_hour/seven_day resets_at and used %, and any per-model limit the payload carries) into the state record next to exact, with at; tests; never raises. Lands after dd8c (same file).

## Handoff
- doing: dispatched in worktree
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — executable logic

impl: DONE_WITH_CONCERNS 1e1996a (stored shape: rate_limits.<window>{used_percentage,resets_at} + at; no per-model window documented; stale block persists when payload lacks rate_limits).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — high 1 (WINDOWS_MAX untested), medium 2 (usage_bars OverflowError blanks the line; pre-existing, now in scope via acceptance 2); lows 3 (pct/size range), 4 (sid path — to follow-up), 5 (doc; noted on 07c3 F1).
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE 9dd0b21 (1-3; declined 4, 5 = out of scope, filed/noted).
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR. Declined 4 (41e7), 5 (07c3 F1 note). Low: fractional size 0<s<1 truncates to 0 in the display (carried to 41e7).
- 2026-09-18 done: ea313c0
