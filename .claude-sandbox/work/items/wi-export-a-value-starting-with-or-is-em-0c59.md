---
id: wi-export-a-value-starting-with-or-is-em-0c59
title: "wi export: a value starting with [ or { is emitted raw as JSON → invalid backlog.yaml"
type: bug
status: dropped
priority: 2
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
---

Found in the 0401 review (pre-existing): wi.py _yaml_scalar (~1765-1771) passes a title or value starting with [ or { through raw, so 'wi add "[wip] x"' then export produces a backlog.yaml that ruamel and backlog.py validate cannot parse. Acceptance: such values are quoted; export of a store containing them validates --strict; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- folded into wi-b020-review-lows-export-round-trip-is-bc6b (librarian 2026-09-21): same wi.py export/write surface; one branch avoids three-way conflicts

## Notes
- 2026-09-21 dropped
