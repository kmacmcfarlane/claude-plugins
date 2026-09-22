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
agent: implementer ab3c9d45a0eab13c3 round 1
return: implementer DONE 095bc57
changed: investigate SKILL.md (Steps 3, 13, 14 trims; 2909->2908), references/investigation-format.md (§ A repo not yet created), README.md (### dev-flow prose), dev-flow plugin.json (description 1072->1018)
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a8b6adb9fe5179633 round 1
verdict: NEEDS_CHANGES round 1 at 095bc57
findings:
- [high] investigation-format.md:52 — the move is given to "the next session working in the new repo", which on the realistic path is create-repo's launched session: it has no pointer to the old series (starts a fresh 00) and usually cannot reach the old repo from its sandbox. Pass: the session holding the series moves it as soon as the repo exists (right after create-repo returns, before the launch command); under an orchestrator the orchestrator's; a later session in the new repo only as a fallback when told where the series is.
- [low] :54 "commit it there" — which git (host or sidecar per tracking mode; point at l.308-311).
- [low] :55 Moved-from SHA — of whichever history holds the series.
- [nit] SKILL.md:336 name the file in "(§ A repo not yet created)".
filed separately: create-repo bootstrap prompt names an existing series path.
dispatch: implementer opus — fix round 1 (resume)
agent: implementer ab3c9d45a0eab13c3 round 2
return: implementer DONE c81b590
dispatch: reviewer opus — review r2 (resume)
agent: reviewer a8b6adb9fe5179633 round 2
