---
id: context-guard-status-line-records-rate-l-81a5
title: "context-guard: status line records rate_limits in the context-gate state record"
type: feature
status: todo
priority: 3
created: 2026-09-18
updated: 2026-09-18
refs:
  - f696 impl open question 3
---

From f696/7db3 (2026-09-18): librarian-mode's fable-unavailable fallback reads the reset time from rate_limits in claude-kit/context-gate/<session>.json, but statusline.py only displays rate_limits and stores only the exact block. Acceptance: statusline.py writes rate_limits (five_hour/seven_day resets_at and used %, and any per-model limit the payload carries) into the state record next to exact, with at; tests; never raises. Lands after dd8c (same file).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

- 2026-09-18 (from dd8c review): also make a non-numeric used_percentage fall back to "ctx --" instead of blanking the line through the last-resort guard.
