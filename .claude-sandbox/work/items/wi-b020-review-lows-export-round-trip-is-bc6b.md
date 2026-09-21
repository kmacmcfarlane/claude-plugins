---
id: wi-b020-review-lows-export-round-trip-is-bc6b
title: "wi: b020 review lows + export round-trip issues"
type: bug
status: doing
priority: 3
owner: unknown@360f41058e92
claimed: 2026-09-21T23:07Z
created: 2026-09-21
updated: 2026-09-21
refs:
  - b020 reviewer
---

From b020 review 2026-09-21 (CLEAR with lows). Fix: (1) lint hint for grooming item with stray parked: (and vice versa) names a verb that works; (2) needs-input keeps the LAST decision N text or format.md says revise in place; (3) test that answer 40 leaves decision 4 open; (4) ls --dep re-raises an ambiguous prefix; (5) SKILL.md mentions prime HOLD / hold tag. Inherited: (6) U+2028 passes _one_line and breaks wi export YAML; (7) '; requires ext:' suffix leaks into blocked reason on export and grows over round trips, import drops the ext: dep.

## Handoff
- doing: implementer dispatched (opus, agent ab6958c99e211d4dc)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Folded in (librarian 2026-09-21)
- 0c59: _yaml_scalar passes a value starting with [ or { raw → export unparseable; quote it; export of such a store validates --strict; test.
- b9e8 (= item 7 above): '; requires ext:…' appended again on every export → import --update; round trip idempotent (N cycles byte-identical).
- 9d8c: a batch write refused over a control character names the key but not the item; include item id/path in the WiError.
- dispatch: implementer opus — executable logic (wi.py), several fixes

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
