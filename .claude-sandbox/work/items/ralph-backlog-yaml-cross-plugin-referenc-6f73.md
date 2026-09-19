---
id: ralph-backlog-yaml-cross-plugin-referenc-6f73
title: "ralph backlog-yaml: cross-plugin reference into work-items"
type: chore
status: done
priority: 4
created: 2026-09-19
updated: 2026-09-19
closed: 2026-09-19
---

From 07c3 F0 (2026-09-19): plugins/ralph/skills/backlog-yaml/SKILL.md:18 points at the work-items skill's references/provider-interface.md — a path into another plugin, forbidden by the new cross-skill convention (README principle 4 soft dependency). Reword to name the skill/concept only (or state it as a declared soft dependency without a file path).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

dispatch: implementer sonnet — default (one line)

impl: DONE b7ca019 (reworded; ralph -> work-items soft dep already declared).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium: ralph plugin.json/marketplace description does not declare the work-items soft dep (principle 4; pre-existing, pulled in); lows: "that document" referent, name mismatch (work-source provider interface).
dispatch: implementer sonnet fix round 1 — resume; scope + ralph plugin.json and marketplace.json ralph description

fix round 1 (sonnet): DONE 7e24af4. subject-fix: 7e24af4 updated: ralph - declare the work-items soft dependency, clean up backlog-yaml wording
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR (low: "it implements" wording in the description — not re-dispatched).
- 2026-09-19 done: 2f7b871
