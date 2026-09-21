---
id: wi-export-a-value-starting-with-or-is-em-0c59
title: "wi export: a value starting with [ or { is emitted raw as JSON → invalid backlog.yaml"
type: bug
status: todo
priority: 2
created: 2026-09-21
updated: 2026-09-21
---

Found in the 0401 review (pre-existing): wi.py _yaml_scalar (~1765-1771) passes a title or value starting with [ or { through raw, so 'wi add "[wip] x"' then export produces a backlog.yaml that ruamel and backlog.py validate cannot parse. Acceptance: such values are quoted; export of a store containing them validates --strict; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
