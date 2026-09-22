---
id: statusline-hub-soften-the-prune-race-cla-c18a
title: "statusline-hub: soften the prune-race claim in hook-contract § 11; test or drop _dead_segment's read-vs-lstat check"
type: chore
status: doing
priority: 4
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:24Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - 5cde review r1
---

5cde review lows, 2026-09-22: hook-contract.md:391 claims a rewrite during the pass always survives, but lstat→unlink leaves a microsecond window (POSIX cannot unlink by inode) — say so; housekeeping.py:187-189's identity check in _dead_segment is untested and redundant with _unlink_if_same — add a swap test or drop it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full statusline-hub-soften-the-prune-race-cla-c18a /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/statusline-hub-soften-the-prune-race-cla-c18a
dispatch: implementer opus — executable logic (statusline-hub hooks test), rule 2
agent: implementer a2b25e2beac04943f round 1
return: implementer DONE fd01a1d
changed: statusline-hub hook-contract.md § 11, hooks/housekeeping.py (docstrings), hooks/tests/test_segments.py
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a4c285f70fe3ddc17 round 1
