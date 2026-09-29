---
id: wi-refuse-unicode-format-characters-in-s-d8b6
title: "wi: refuse Unicode format characters in short_display_name; test the two untested display behaviours"
type: chore
status: todo
priority: 3
created: 2026-09-29
updated: 2026-09-29
refs:
  - 928d
---

From 928d review r1 2026-09-29: a name of only U+200B or holding U+202E passes add/set/lint and prints blank or reordered (str.strip does not treat them as whitespace; titles share the exposure). Acceptance: refuse category Cf in the name (and decide titles), plus one assertion each for title_cell stripping a padded hand-written name and a bare hand-written key reaching --json as [] (lint flags both); optional format.md sentence on mixed wi versions moving the key below x_backlog (cosmetic churn).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
