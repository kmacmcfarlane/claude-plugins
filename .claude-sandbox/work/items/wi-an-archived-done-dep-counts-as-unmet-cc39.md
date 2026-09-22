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
verdict: NEEDS_CHANGES round 1 at 9d7b88a (live-store check: HEAD's ready queue unchanged after archiving 183 items; main loses 4 — the bug)
findings:
- [medium] wi.py:1177 — an id in both items/ and archive/: archived=True commands take the archive copy (last wins), next/ls --ready/prime/claim take items/. Pass: first entry wins (items/ before archive/), test across show, ls --status all --ready, next, claim.
- [medium] wi.py:1194 — one malformed archive file (no front matter; non-UTF-8) now stops next/prime/ls --ready (rc 3 / traceback). Pass: skip an unparseable archive file with a one-time stderr warning; test with garbage + binary files.
- [medium] test_wi.py:1318 — prime untested for archived deps; add it to assert_ready_everywhere.
dispatch: implementer opus — fix round 1 (resume)
agent: implementer abb14e345a6345416 round 2
