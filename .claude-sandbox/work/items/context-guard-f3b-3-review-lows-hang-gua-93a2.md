---
id: context-guard-f3b-3-review-lows-hang-gua-93a2
title: "context-guard F3b-3 review lows: hang-guard the mark FIFO test; reflow the playbook copy clause"
type: chore
status: doing
priority: 4
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:52Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - F3b-3 review r2
---

F3b-3 review r2 lows, 2026-09-22: test_lineage.py test_a_fifo_at_the_recorded_path_does_not_hang_the_mark hangs (not fails) on a regression — wrap in signal.alarm or a joined thread; operator-playbook.md:172-173 reflow.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- riders from F3b-5 review r2 (2026-09-22): operator-playbook.md:152-153 say the env -u lookup prompts (the allow rule does not cover it); :132-135 state the two reasons without internal ids "answer 47"/"decision 65".

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full context-guard-f3b-3-review-lows-hang-gua-93a2 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/context-guard-f3b-3-review-lows-hang-gua-93a2
dispatch: implementer opus — executable logic (context-guard test) + playbook wording
agent: implementer aebea3e811b0125fb round 1
return: implementer DONE 0a6a72c
changed: hooks/tests/test_lineage.py, checkpoint references/operator-playbook.md
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a9a74b2833ac9c12e round 1
