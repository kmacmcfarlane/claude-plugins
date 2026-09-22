---
id: librarian-mode-troubleshooting-leftover-c100
title: "librarian-mode troubleshooting: leftover MERGE_HEAD wording and the neither-case"
type: chore
status: done
priority: 4
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
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
agent: implementer af158576325ab4ad0 round 1
return: implementer DONE 2406cd8
changed: plugins/dev-flow/skills/librarian-mode/references/troubleshooting.md
dispatch: reviewer opus — rule 4 floor (impl sonnet)
agent: reviewer aa66557a6276d4d6d round 1
verdict: CLEAR round 1 at 2406cd8
lows: :75 give the origin/main short-sha command — declined by the librarian (polish; the reader can shorten it); SKILL.md:105-109 "redo the matching one" vs the neither case — sent as a rider to e770 F4 (d81c), which is editing that file now.
landed: 04d5b0f
- 2026-09-22 done: 04d5b0f
