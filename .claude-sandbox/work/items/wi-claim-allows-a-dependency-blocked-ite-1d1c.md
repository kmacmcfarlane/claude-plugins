---
id: wi-claim-allows-a-dependency-blocked-ite-1d1c
title: wi claim allows a dependency-blocked item
type: bug
status: doing
priority: 3
owner: unknown@bf9f9839222c
claimed: 2026-09-22T22:26Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - "peer: agents - librarian (uds 122.sock), operator relay"
---

Relayed 2026-09-22 from the agents store (wi-claim-allows-dependency-blocked-items-77f7). wi claim refuses status:blocked but claims an item hidden from the ready queue by an unmet --on dependency (live-fired 2026-09-01 on brainboy). Acceptance: claim refuses an item whose deps are not all done/dropped (same rule as next/ready), with a message naming the dep; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@bf9f9839222c

target: full wi-claim-allows-a-dependency-blocked-ite-1d1c /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/wi-claim-allows-a-dependency-blocked-ite-1d1c
dispatch: implementer opus — executable logic (wi.py)
agent: implementer adb7ce476b4fa37ed round 1
return: implementer DONE 2c7e9bb
changed: wi.py, tests/test_wi.py, SKILL.md (claim row), references/format.md (deps row)
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a817cbd835b9bd49f round 1
