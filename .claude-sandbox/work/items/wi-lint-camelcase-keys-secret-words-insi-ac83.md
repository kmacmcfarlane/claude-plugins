---
id: wi-lint-camelcase-keys-secret-words-insi-ac83
title: "wi lint: camelCase keys, secret words inside longer keys, and Authorization: Bearer"
short_display_name: wi lint more secret keys
type: bug
status: todo
priority: 3
created: 2026-10-09
updated: 2026-10-09
refs:
  - wi-lint-secret-shapes-the-assignment-and-b9fb
---

From b9fb review 1, finding 6, outside b9fb: camelCase colon keys (clientSecret: …, dbPassword: …) are missed; the key/value rule's word boundaries miss a secret word inside a longer key (api_secret, secret_key, dbPassword) in its colon forms; an Authorization: Bearer <token> header is caught by nothing. Build after b9fb lands, on its key-aware gate.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
