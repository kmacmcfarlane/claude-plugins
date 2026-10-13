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
verdict: NEEDS_CHANGES round 1 at 012293db (1 medium needs the operator: refusing the no-terminal default in a sidecar overrides answer 211 b; lows: menu defaults to the refused option, untested; unrecorded-store note still offers --no-track; format.md bullet omits the exception; nits: SKILL.md cell, SIDECAR_NO_REPO wording; code sound, 372 OK)
dispatch: implementer opus medium — resume, fix round 1 part 1 (findings 3, 6: independent of the ruling)
agent: implementer ac34548631423ee4a round 2
decision 214: In a sidecar layout (.claude-sandbox/ is its own git repo) what should a bare wi init with no terminal do, given answer 211 b chose an ignored store plus a warning for that case in general? — options: (a) refuse, exit 1, nothing written, naming --track (as built; reverses 211 b for sidecars only) | (b) default to tracked in a sidecar: exit 0, the store is committed in the sidecar repo, the host still never sees it, so 211 b's foreign-safe reason holds [recommended] | (c) ignored store plus a warning as 211 b reads literally: wi then flags the store as broken on every prime | (z) decide later: 3c06 waits, the bug stays on main
