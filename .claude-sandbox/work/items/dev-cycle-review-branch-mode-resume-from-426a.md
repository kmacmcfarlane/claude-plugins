---
id: dev-cycle-review-branch-mode-resume-from-426a
title: "dev-cycle: review <branch> mode + resume from item record (07c3 F4)"
type: feature
status: doing
priority: 3
deps:
  - dev-flow-add-the-dev-cycle-skill-07c3-f1-325d
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
owner: unknown@360f41058e92
claimed: 2026-09-21T23:07Z
created: 2026-09-18
updated: 2026-09-21
---

07c3 plan §F4. Size S-M; sonnet/opus.

## Handoff
- doing: implementer dispatched (sonnet, agent ad99423445ed4c9a0)
- next: on DONE: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer sonnet — plan 07c3 routing table: one skill, 2 files, mechanical once §2 is fixed

## Implementer result
- round 1 DONE fa4ef02 (sonnet): review <branch> mode (was a stub) + Step 0.4 Resume; bindings.md Review target + Resume. Scope widening accepted (librarian): troubleshooting.md stale 'not available yet' stub replaced (contradicted the new mode).
- dispatch: reviewer opus — rule 4

## Review round 1 — NEEDS_CHANGES (opus) at fa4ef02
- [high] review mode "Step 4 runs as usual": review-brief/agent-brief require worktree-<name> and implementer claims → BLOCKED twice; need a review-mode brief variant.
- [high] Land in review mode merges worktree-<name>, removes a found worktree and deletes the author's branch; case 1 can match the main checkout.
- [medium] review <branch> with no item/plan has no intent; every file graded "no reason" medium.
- [medium] review mode skips Step 2 routing (reviewer tier, fable signals, dispatch line).
- [medium] resume rules 2/3 overlap; record lines have no fixed shape; review target not recorded.
- [medium] resume after NEEDS_CHANGES/SHOW_STOPPER/BLOCKED maps to the wrong next step; findings not kept verbatim.
- [medium] re-dispatch without checking a still-running agent → two agents in one worktree.
- [medium] troubleshooting "rebuild the worktree" rebuilds a landed change; no landed state; -b fails when the branch survived.
- [medium] plan mode resume not covered.
- lows: NEEDS_CHANGES ask contradicts Step 4.4 and the red flag; <branch> raw in paths (feature/x); git -C "$MAIN"/<path> for an outside worktree; declined path item handling.
- dispatch: implementer sonnet — fix round 1 (tier kept, rule 6); scope widened to references/review-brief.md, agent-brief.md
