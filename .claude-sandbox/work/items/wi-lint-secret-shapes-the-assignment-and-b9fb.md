---
id: wi-lint-secret-shapes-the-assignment-and-b9fb
title: "wi lint: secret shapes the assignment and key/value rules still miss"
short_display_name: lint misses other secret shapes
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T11:04Z
created: 2026-10-08
updated: 2026-10-09
refs:
  - wi-lint-catch-key-value-secrets-after-a-d8a5 review 1
---

From the d8a5 review 1 notes, 2026-10-08: lowercase or mixed-case keys (db_pass=...), spaces around = (KEY = value), KEY: value, JSON "KEY":"value", and --flag=value pass both rules unless the key holds a key/value-rule word. Acceptance: decide per shape with real-store before/after; tests pin each.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree (bug)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a7035ad4054cec38e
return: DONE worktree-agent-a7035ad4054cec38e f526872 (third rule SECRET_SHAPE_RE for five looser shapes, value gated: 12+ chars, letter and digit, not hex, not date-led, not short-segment id/path; placeholders ignored; 13 caught, 25 clean, 4 refused tests; store scan 0 hits over 461 files after two false positives fixed; reported 10 Checks)
dispatch: reviewer opus high — review round 1 of f526872
agent: reviewer ae593bcd6eb1d1d1a
verdict: review round 1 NEEDS_CHANGES (high 1: quoted values missed in every new shape but JSON; medium 2: short-segment exemption misses ~17% of 22-char url-safe tokens and flags long path segments; medium 3: hex/letters/UUID exemptions ignore the key — a 40-hex value under a secret-word key passes; lows: symbol passwords, a dot before the key, => and := forms, test gaps; low 6 (camelCase, Bearer) for a follow-up)
dispatch: implementer opus medium — fix round 1 (resume a7035ad4054cec38e)
