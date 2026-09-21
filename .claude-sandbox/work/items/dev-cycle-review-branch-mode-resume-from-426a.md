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
- fix round 1 DONE d802a19 (sonnet): review-mode brief variants, review-mode Land, Intent + record-line shapes, ordered resume map, ListAgents check, plan-mode resume, troubleshooting landed/re-add; all lows fixed.
- dispatch: reviewer opus — review r2 (same reviewer resumed)

## Review round 2 — NEEDS_CHANGES (opus) at d802a19
- round-1: 1,4,10 fixed; 2,3,5,6,7,8,9 partial.
- [high] A case 1 (main checkout on <branch>): merge is a no-op ("Already up to date", reproduced) yet the item closes → Land stops and asks, or reviews in an added worktree and merges only when main is on base.
- [high] B resume order: rules 2/3 match any earlier verdict, not the last state; "dispatch with no return" (most common interrupt) hits rule 2 → duplicate fix, ListAgents skipped; stale CLEAR undefined; no reviewer return line.
- [high] C review mode fails at Land: Step 5.2 "implementer's reason", checklist §1 changed-block and one-commit checks.
- [medium] D FINDINGS block never written; E landed test needs a `landed:` line; F plan target vs plan mode conflation; G verdict `at <sha>` drops plan-mode coverage; H fix-loop.md conflict/leak paths assume worktree-<name> and rewrite branches.
- lows: I BLOCKED verdicts counted toward cap; J review mode never claims the item.
- dispatch: implementer sonnet — fix round 2 (tier kept, rule 6; scope widened to fix-loop.md and review-checklist.md). Next round (fix round 3) would bump per rule 3.
- fix round 2 DONE 58bece4 (sonnet): case 1 stops and asks; resume as a last-line state machine (walk-through table in the report); findings:/landed: shapes; review-mode checklist exemption; fix-loop carve-outs; claim in Step 0; BLOCKED not counted.
- dispatch: reviewer opus — review r3 (same reviewer resumed); last round before the cap
