---
id: wi-lint-misses-a-sidecar-store-recorded-3c06
title: wi lint misses a sidecar store recorded ignored
short_display_name: lint misses ignored sidecar store
type: bug
status: todo
priority: 2
created: 2026-10-13
updated: 2026-10-13
refs:
  - work-items-wi-init-rule-a-sidecar-store-00fc
---

From 00fc's scratch test, 2026-10-13: wi init --no-track in a sidecar layout records tracking: ignored and writes /work/ into .claude-sandbox/.gitignore, so new items land in no repo, and wi lint stays clean. Acceptance: lint (and prime) warn when a sidecar store is recorded ignored or its sidecar ignores it; wi init --no-track in a sidecar layout refuses or warns, naming --track.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree branch off main (832cec4f); plugins/work-items/skills/work-items/{scripts/wi.py,tests/test_wi.py,SKILL.md,references/format.md}
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — lint/prime warn on an ignored sidecar store; init --no-track in a sidecar warns or refuses
agent: implementer ac34548631423ee4a round 1
result: DONE round 1 at 012293db (372 tests OK; lint finding exit 3; init refuses ignored choices in a sidecar incl. the no-terminal default)
dispatch: reviewer opus high — fresh (rule 4), review 012293db against main
agent: reviewer a93ea09796cd7b81e round 1 at 012293db
