---
id: investigate-steps-3-and-13-handle-a-targ-fc02
title: "investigate: Steps 3 and 13 handle a target repo that does not exist yet (where the series lands)"
type: chore
status: doing
priority: 3
owner: Kyle-McFarlane@bf9f9839222c
claimed: 2026-09-22T23:24Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - bb7e review r1
---

bb7e reviewer note, 2026-09-22: Step 2 now asks which repo owns the work, but Step 3 (resolve repositories) and Step 13 (save the series) still assume the target repo exists; the retro's problem was where to land the series after the work moved. Acceptance: say where the series lands when the owning repo is to be created (e.g. the current repo's Series home until create-repo runs, then moved), smallest edit.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- riders from bb7e review r2 (2026-09-22): README ### dev-flow soft-dependency paragraph gains one create-repo sentence; dev-flow plugin.json description is 1072 chars — trim its dependency parenthetical.

## Notes
- 2026-09-22 claimed by Kyle-McFarlane@bf9f9839222c

target: full investigate-steps-3-and-13-handle-a-targ-fc02 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/investigate-steps-3-and-13-handle-a-targ-fc02
dispatch: implementer opus — README catalog prose + plugin.json description (doctrine), rule 2
