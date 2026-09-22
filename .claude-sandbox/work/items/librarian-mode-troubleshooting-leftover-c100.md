---
id: librarian-mode-troubleshooting-leftover-c100
title: "librarian-mode troubleshooting: leftover MERGE_HEAD wording and the neither-case"
type: chore
status: doing
priority: 4
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:10Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - d978 review r2
---

d978 review r2 lows, 2026-09-22: troubleshooting.md:70 says '--no-commit' for a landing merge that has none (say: a push-rejection merge after --no-commit, a landing merge stopped on a conflict); :73-81 no rule for a MERGE_HEAD matching neither origin/main nor a worktree-* tip (abort, then a numbered decision); :74 compare with rev-parse --short.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full librarian-mode-troubleshooting-leftover-c100 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/librarian-mode-troubleshooting-leftover-c100
dispatch: implementer sonnet — one reference doc, wording, no signal
