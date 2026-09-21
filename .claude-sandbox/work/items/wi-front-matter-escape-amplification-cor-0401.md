---
id: wi-front-matter-escape-amplification-cor-0401
title: "wi: front-matter escape amplification corrupts values with : and \" on every rewrite"
type: bug
status: todo
priority: 1
created: 2026-09-21
updated: 2026-09-21
---

Found by the ca20 reviewer (2026-09-21), pre-existing on main: a value containing both ':' and '"' gains backslashes on every rewrite — title: "x: \"y\"" becomes "x: \\\"y\\\"" after one unrelated 'wi set priority'. The parser does not unescape what the writer escapes: silent data loss that compounds; migrate and export propagate it. Acceptance: emit and parse are exact inverses for every scalar (round-trip property test over quotes, backslashes, colons, #, leading/trailing spaces, unicode); existing items already amplified are left readable (no crash) and a one-time repair is documented or offered; e832/23a8 invariants hold.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Also seen (1dab review)
- wi add escapes a title containing " or \ twice; a strict YAML loader reads it back with extra backslashes. Same root as the amplification above — cover add in the fix and its test.
