---
id: work-items-pin-the-json-of-wi-s-four-rea-8c42
title: "work-items: pin the JSON of wi's four read subcommands the agents back end consumes, and announce changes"
short_display_name: pin wi read JSON for the back end
type: chore
status: todo
priority: 2
created: 2026-10-03
updated: 2026-10-03
refs:
  - peer agents 2026-10-03 (their 29d6)
---

Peer agents 2026-10-03: the control-plane back end will run a hash-pinned wi.py with four read subcommands only — estate --dir=, and ls, needs-input, show with --root= — every data argument after --. If their JSON changes, the pinned copy lags until the operator re-pins, so changes must be announced. Acceptance: contract tests pin each subcommand's JSON shape (keys, types) and argument form (--dir=/--root=, data after --); the format or provider reference names the consumer and says a change to these shapes is announced to the agents librarian before landing; check that each subcommand already accepts the -- form.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
