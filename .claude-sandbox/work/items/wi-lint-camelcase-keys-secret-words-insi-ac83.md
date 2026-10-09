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
agent: reviewer a65548473809d61f9
note: 2026-10-09 background security review flagged a possible secret-scanner bypass in wi.py (no details given); relayed to review round 1 as a bypass hunt; nothing lands until it is resolved
verdict: review round 1 NEEDS_CHANGES (must-fix 3: medium 1 a nested call closes at the first ) and skips a later quoted secret main caught; medium 2 the meta-word suffix exemption reopens b9fb r1 medium 3 (hex/symbol values under secret_ref, password_var, *_file …), no real-store need behind it; medium 3 acronym-led PascalCase keys (JWTSecret:, AWSSecretKey:) missed; low 4 $-led values under a bare lowercase key, format.md overstates; low 5 Authorization with = or => and a quoted credential; nits 6-8 a stale comment name, subpass/renderpass/multipass deny-list, the template lookahead accepts a trailing .; low 9 spaced argument judged acceptable); the background security flag is answered by findings 1 and 2; reviewer's tested patch at scratchpad/ac83-review/wi_fix.py
dispatch: implementer opus medium — fix round 1 (resume a15cd24ab91b0fc91)
return: DONE 8e7fdfe (fix round 1); work-items 315 OK, kit-dev 18 OK; corpus: 0 main-only misses outside the nine meta keys; 11,285 main-only under meta keys (letters-only, short alnum, digits, paths, UUIDs); 15,533 newly caught; real store clean
dispatch: reviewer opus high — review round 2 of 8e7fdfe (resume a65548473809d61f9)
