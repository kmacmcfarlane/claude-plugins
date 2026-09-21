---
id: wi-front-matter-escape-amplification-cor-0401
title: "wi: front-matter escape amplification corrupts values with : and \\\\\\\\\\\\\\\" on every rewrite"
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
- doing: review round 2 (opus) at bc3321d
- next: land on CLEAR; then run wi repair-escapes --apply --id wi-front-matter-escape-amplification-cor-0401 on the live store
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
- widening feb4d69: SKILL.md repair-escapes row; format.md Quoting paragraph.
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at feb4d69
- main vs HEAD reader: 1 difference in 146 live items (the amplified title), 4 in 491 historical blobs (same title); render byte-identical; repair correct on this item; export validates --strict.
- [medium] bare internal tab emitted unquoted → strict YAML fails; [medium] property test never hits a bare tab; [medium] repair-escapes can "repair" a correct value (heuristic) — docs must say review + --id; [medium] hand-written "C:\Users\foo" now decodes \f \b etc. → lint warns on quoted values decoding to control chars (or repair lists them).
- lows: bare ~/null/true/0x10 typed by YAML (docs overclaim); U+FFFE raw; quoted "—" now literal (document); repair --id positive test; unterminated flow quote.
- pre-existing, filed separately: export passes a title starting with [ or { raw as JSON → invalid backlog.yaml.
- dispatch: implementer opus — fix round 1 (resume)
- round 1 fix bc3321d: tabs quoted; U+FFFE/surrogates escaped; lint reports control chars in values; repair-escapes heuristic documented, --key, checks bare values too; import reads "—" as none; flow-list fallback. Live copy: 1 reader diff (this title).
- dispatch: reviewer opus — round 2 (resume)

## Review round 2 — NEEDS_CHANGES (opus) at bc3321d
- core holds (1 reader diff on live copy + history); fuzz clean except value "="; export validates.
- [medium] lint skips tab, so "C:\temp" decodes to a tab silently: flag tabs too (wi never writes a raw tab now) + test. lows: bare "=" / "<<"; repair lists more bare values (acceptable, documented).
- dispatch: implementer opus — fix round 2 (resume)
