---
id: wi-front-matter-escape-amplification-cor-0401
title: "wi: front-matter escape amplification corrupts values with : and \\\\\\\" on every rewrite"
type: bug
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-21T19:08Z
created: 2026-09-21
updated: 2026-09-21
---

Found by the ca20 reviewer (2026-09-21), pre-existing on main: a value containing both ':' and '"' gains backslashes on every rewrite — title: "x: \"y\"" becomes "x: \\\"y\\\"" after one unrelated 'wi set priority'. The parser does not unescape what the writer escapes: silent data loss that compounds; migrate and export propagate it. Acceptance: emit and parse are exact inverses for every scalar (round-trip property test over quotes, backslashes, colons, #, leading/trailing spaces, unicode); existing items already amplified are left readable (no crash) and a one-time repair is documented or offered; e832/23a8 invariants hold.

## Handoff
- doing: dispatched
- next: review
- blocked: —
- learned: —

## Also seen (1dab review)
- wi add escapes a title containing " or \ twice; a strict YAML loader reads it back with extra backslashes. Same root as the amplification above — cover add in the fix and its test.

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — executable logic (wi.py parser/writer), data loss

## Implementer result
- round 1 DONE_WITH_CONCERNS aab13b6 (opus): scalar emit/parse exact inverses (control chars escaped; unknown escapes kept; YAML indicators quoted; flow lists split outside quotes); repair-escapes [--id] [--apply] dry-run by default; 121 tests; property test vs ruamel. Live store (temp copy): 1 amplified item (this one, title). "wi add escapes twice" did not reproduce — same root cause (reader).
- scope widening before review: SKILL.md command row + format.md quoting line.
- after landing: librarian runs repair-escapes --apply --id on this item.
