---
id: wi-lint-bare-lowercase-pass-keys-pw-more-dc23
title: "wi lint: bare lowercase pass keys, pw, more Authorization forms, spaced args"
short_display_name: wi lint remaining secret gaps
type: bug
status: todo
priority: 4
created: 2026-10-09
updated: 2026-10-09
refs:
  - wi-lint-camelcase-keys-secret-words-insi-ac83
---

From ac83 review 3 follow-ups, 2026-10-09; gaps main shares, not regressions: bare lowercase colon keys dbpass:/dbpassword:/passphrase: miss the shape rule; pw as a key (keys need 3+ chars); Authorization with an f-string credential, a credential holding : or %, or a continued header; a call argument holding a space never treated as secret. Also the earlier notes on ac83: YAML | and \ continuations, Markdown table rows, kebab-case keys, passwords inside URLs, --password v.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
