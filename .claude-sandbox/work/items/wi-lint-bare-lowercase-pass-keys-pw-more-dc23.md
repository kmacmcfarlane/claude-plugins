---
id: wi-lint-bare-lowercase-pass-keys-pw-more-dc23
title: "wi lint: bare lowercase pass keys, pw, more Authorization forms, spaced args"
short_display_name: wi lint remaining secret gaps
type: bug
status: doing
priority: 4
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-12T19:47Z
created: 2026-10-09
updated: 2026-10-12
refs:
  - wi-lint-camelcase-keys-secret-words-insi-ac83
---

From ac83 review 3 follow-ups, 2026-10-09; gaps main shares, not regressions: bare lowercase colon keys dbpass:/dbpassword:/passphrase: miss the shape rule; pw as a key (keys need 3+ chars); Authorization with an f-string credential, a credential holding : or %, or a continued header; a call argument holding a space never treated as secret. Also the earlier notes on ac83: YAML | and \ continuations, Markdown table rows, kebab-case keys, passwords inside URLs, --password v.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-10-12 claimed by Kyle-McFarlane@2d49f8460283
target: wi lint catches the listed gaps without new false positives on the real store or repo; linear on long lines
dispatch: implementer opus medium — build (security-relevant lint)
