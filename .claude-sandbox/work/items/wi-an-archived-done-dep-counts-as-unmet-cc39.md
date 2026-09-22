---
id: wi-an-archived-done-dep-counts-as-unmet-cc39
title: "wi: an archived done dep counts as unmet in next and claim; show --json disagrees"
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:24Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - 1d1c implementer
---

1d1c implementer OQ, 2026-09-22: the ready rule resolves deps against items/ only, so once a done dep is archived its dependents vanish from next and claim refuses them, while show --json (blocked_by_unresolved) also reads the archive. Acceptance: one dep-resolution rule reads the archive for next, ready, claim and show alike; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- rider from 1d1c review (2026-09-22): add claim tests for a dep at doing+stage uat (met) and for re-claiming an owned doing item with unmet deps (unchanged).

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full wi-an-archived-done-dep-counts-as-unmet-cc39 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/wi-an-archived-done-dep-counts-as-unmet-cc39
dispatch: implementer opus — executable logic (wi.py), rule 2
agent: implementer abb14e345a6345416 round 1
return: implementer DONE 9d7b88a
changed: wi.py (DepIndex, load_paths), tests/test_wi.py, references/format.md (deps row), SKILL.md (next row)
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a123dd58079c56144 round 1
