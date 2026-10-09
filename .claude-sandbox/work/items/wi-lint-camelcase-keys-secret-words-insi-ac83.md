---
id: wi-lint-camelcase-keys-secret-words-insi-ac83
title: "wi lint: camelCase keys, secret words inside longer keys, and Authorization: Bearer"
short_display_name: wi lint more secret keys
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T13:56Z
created: 2026-10-09
updated: 2026-10-09
refs:
  - wi-lint-secret-shapes-the-assignment-and-b9fb
---

From b9fb review 1, finding 6, outside b9fb: camelCase colon keys (clientSecret: …, dbPassword: …) are missed; the key/value rule's word boundaries miss a secret word inside a longer key (api_secret, secret_key, dbPassword) in its colon forms; an Authorization: Bearer <token> header is caught by nothing. Build after b9fb lands, on its key-aware gate.

Also carried from b9fb review 4's follow-ups: tighter $/{} placeholders; a pass suffix (passphrase, passcode) with a deny-list for harmless words (passthrough, compass, bypass); a spaced second call argument.
target: wi lint flags camelCase and compound secret keys in colon and assignment forms, and an Authorization: Bearer header, with tests; no new finding over the real store; lint stays linear on long lines.
dispatch: implementer opus medium — build (security-relevant lint; not a canonical mechanical kind)
agent: a15cd24ab91b0fc91 (implementer, build)

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
note: also from b9fb review 2 low 5: a value on the next line (YAML |, \ continuation), a Markdown table row | db_pass | v |, kebab-case db-pass=, a password inside a URL (scheme://user:v@host), --password v with a space
note: also from b9fb review 4: tighten placeholders to $NAME, ${NAME}, {name} (catches bcrypt-style $2b$…); a pass suffix as a secret word with a deny-list (bypass, compass, surpass, trespass, overpass, underpass, encompass); a secret as a spaced second call argument
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
return: DONE 8ca9a19 on worktree-agent-a15cd24ab91b0fc91; work-items 315 OK; real-store lint no secret findings; old vs new over ~198k lines: no new findings, two false positives gone; judgement calls: meta-word key suffixes (policy, file, name…), spaced call args never secret; not built: the note extras (YAML continuation, table rows, kebab keys, URL passwords, --password v)
dispatch: reviewer opus high — review round 1 of 8ca9a19
