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
agent: implementer ad174bb9bfc266a07
return: DONE 4cb0ac3; all nine gaps tested, each with documented residue; reviewer corpus 0 main-only, per-gap corpus 0 main-only; real store 0 secret findings, 0 diff vs main; slowest 1.99s at 2M (aB: chained); one-line state for continuations; loose forms gated on a secret-word key; work-items 317 OK, kit-dev 18 OK
dispatch: reviewer opus high — review round 1 of 4cb0ac3
agent: reviewer affe530eaa9d397c5
verdict: review round 1 NEEDS_CHANGES (must-fix 2: medium 1 — Authorization credential of letters with a colon (AdminUserName:FakeSecretPass) passes as words, main caught it (1,664 main-only in 707,616); medium-low 2 — spaced flag and kebab key swallow the opening quote of a following JSON pair, pos = m.start("quote") at both sites; lows: capitalised one-word keys, _PLAIN_RE and _DATE_RE wider than documented, env-var table false positives, empty-user URL, undocumented gaps; patched copies at scratchpad/dc23-review/wi_fix.py and wi_fix2.py)
dispatch: implementer opus medium — fix round 1 (resume ad174bb9bfc266a07)
