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

## Implementer result
- round 1 DONE 38b82a7 (opus): all points + folded 0c59/b9e8/9d8c; TestB020Lows 10 tests (fail 48+3 without; answer-40 is a pin test). Deviations: wi set … "" hint for all statuses; export quotes a notes value holding line separators; import restores ext deps on new items only.
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at 38b82a7
- fuzz (78 items, every YAML indicator) validates --strict; live-store copy lint clean, 3 cycles byte-identical; 0c59 really fixed (main fails to parse the same export).
- [high] wi.py:2015,2212 suffix strip not tied to the ext deps export appended: a real reason containing "; requires ext:" is cut, "requires ext: …" alone becomes None (lint fails). Fix: on --update strip only the exact suffix built from the item's ext deps; new item: last group; tests for both reasons over N cycles.
- lows: format.md:281 overstates which writes refuse separators (or add _LINE_BREAK_RE to _front_one_line); 9d8c prefix on single-item path names an unwritten file; cycle-0 drift for punctuation-only park/groom reasons (out of scope → follow-up if not fixed).
- dispatch: implementer opus — fix round 1 (same agent resumed)
