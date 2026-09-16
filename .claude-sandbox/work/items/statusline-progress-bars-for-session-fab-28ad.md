---
id: statusline-progress-bars-for-session-fab-28ad
title: "statusline: progress bars for session, fable and weekly plan usage"
type: feature
status: done
priority: 2
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator 2026-09-16: add progress bars to the claude-kit status line for the current-session, Fable, and weekly usage against the current subscription plan's limits, shown only when running on a plan (Pro/Max style rate-limit windows — the librarian reads 'plan mode' as the subscription plan, not Claude Code's planning mode; correct if wrong). Research first: what the statusline JSON payload and hooks actually receive about rate-limit/plan usage (fields, versions), whether /usage data is reachable from a script, and what the 5-hour / weekly windows look like; then a plan for the operator; then implementation in hooks/statusline.py (harness file — fable per rule 3) with tests.

## Handoff
- doing: unblocked; dispatching
- next: implement in hooks/statusline.py + tests
- blocked: awaiting operator decision
- learned: —

## Research (2026-09-16, claude-code-guide agent; docs: code.claude.com/docs/en/statusline, /costs)
- Claude Code >= 2.1.251 passes `rate_limits` on the statusline stdin: `five_hour` and `seven_day` (each
  `used_percentage`, `resets_at` epoch s), plus `spend_limit` behind a gateway. Present only on Pro/Max
  subscriptions, only after the first API response; a window disappears once its resets_at passes.
- NO per-model (Opus/Fable) weekly window in the official payload. /usage shows aggregate bars only. The only
  per-model source is the undocumented https://api.anthropic.com/oauth/usage endpoint read with the OAuth
  token from ~/.claude/.credentials.json (used by ohugonnot/claude-code-statusline and
  leeguooooo/claude-code-usage-bar as an optional fallback).
- Plan detection: presence of rate_limits is the signal (API-key sessions never get it).

## Librarian's proposed plan (awaiting operator decision on the Fable bar)
Implement from the official payload only: two bars (5h session, 7-day weekly) with used % and a reset countdown,
rendered only when rate_limits is present; same bar style as the context gauge; hooks/statusline.py + tests.
The Fable-specific weekly bar is NOT available officially — recommend leaving it out (an undocumented endpoint
plus reading the credentials file from a status line that runs every render is a risk the kit should not take
by default); revisit when the payload carries per-model windows. Routing: fable (harness file, rule 3).
- OPERATOR 2026-09-16 (decision 4): official payload only — 5h and 7-day bars from rate_limits; no Fable-specific bar, no undocumented endpoint.
dispatch: implementer fable — rule 3 (harness file hooks/statusline.py)
dispatch: reviewer fable — rule 4

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
- implementer fable returned DONE, commit aa6d0e3 (100 hook tests); reviewer fable round 1 dispatched 2026-09-16 17:56:27
- review round 1: NEEDS_CHANGES — 2 high (NaN/Infinity resets_at crashes to a blank line; no test for spend_limit), 2 medium (millisecond resets_at renders a 56,000-year countdown; clamping/threshold/round-up behaviours untested), 3 low, 1 note. Fix round 1 sent 2026-09-16 17:59:47, tier unchanged (fable, resumed).
- fix round 1 returned DONE, new commit 134b7d9 (105 tests); declined low 6 (window without resets_at dropped as malformed) and note 8. Re-review dispatched 2026-09-16 18:02:11 (reviewer fable, resumed).
- 2026-09-16 done: b9ce2f6
- re-review CLEAR (all FIXED or DECLINED-accepted; 1 new low: the 366-day edge is not pinned by a test). Landed merge b9ce2f6 2026-09-16 18:04:33; 105 hook tests OK on main.
