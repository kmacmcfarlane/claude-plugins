---
id: dev-cycle-routing-policy-sonnet-mechanic-c0d6
title: "dev-cycle routing policy: Sonnet mechanical / Opus otherwise, fresh Opus reviewer, self-review pure prose"
type: feature
status: done
priority: 0
parent: dev-cycle-routing-a-cheaper-lane-for-doc-1293
created: 2026-09-24
updated: 2026-09-24
closed: 2026-09-24
refs:
  - operator 2026-09-24 (decisions 82 e, 83 a)
---

Implements decision 82 (e) and 83 (a), operator 2026-09-24; see the parent item for the full policy text and the operator's words. In dev-flow's dev-cycle Step 2 and references/model-routing.md (the one home; the research skills' routing stays separate):
(1) implementer: sonnet for mechanical edits (pointer and path fixes, frontmatter, catalog rows, wording that changes no behaviour); opus for anything that changes what a skill does, format bumps and scripts;
(2) reviewer: always opus (Opus 5.5), always a fresh sub-agent that never saw the implementer's conversation; fable only as a second opinion on a complex opus-made plan;
(3) the review waiver: pure prose with no operational claim gets an orchestrator self-review ('review: self'); skill text, CLAUDE.md, references and scripts keep a reviewer.
This replaces rule 3 (fable for security and gating code) and rule 4 (reviewer = implementer's tier). librarian-mode's bindings and record lines follow. Send the landed commit to marketplace - librarian. Operator: implement immediately after the checkpoint.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- checkpoint 2026-09-24 (continue): the next step is to build c0d6 at once after the compaction (operator)

## Notes
- 2026-09-24 claimed by Kyle-McFarlane@bf9f9839222c
target: branch worktree-dev-cycle-routing-policy-sonnet-mechanic-c0d6 at .claude/worktrees/dev-cycle-routing-policy-sonnet-mechanic-c0d6, base main (61b0df6)
dispatch: implementer opus — changes what a skill does (routing rules in dev-cycle Step 2); operator routing
agent: implementer a213fb820d8ffc606 round 1
return: implementer round 1 DONE_WITH_CONCERNS f025fc0 (bump: sonnet→opus after crit/high or at fix round 2; breadth signal dropped; waiver never in plan/review modes; second opinion once per cycle)
dispatch: reviewer opus — always opus, fresh (new policy)
agent: reviewer a33dc1f546750d008 round 1 at f025fc0
verdict: reviewer round 1 NEEDS_CHANGES at f025fc0 — 4 medium (fable-only re-review after a second opinion; pinned item can take the waiver; README 82/289 still describe auto fallback; record-lines.md:40 bullet folded), 7 low, 1 nit
dispatch: implementer opus — resume, fix round 1
agent: implementer a213fb820d8ffc606 fix round 1
return: implementer fix round 1 DONE 81e340c (all 11 fixed; second opinion only in plan mode)
dispatch: reviewer opus — resume, round 2
agent: reviewer a33dc1f546750d008 round 2 at 81e340c
verdict: reviewer round 2 NEEDS_CHANGES at 81e340c — 10/11 fixed; 1 medium (fix-loop.md:28-32 and Step 4.3 would resume the fable reviewer after a second opinion), 1 low, 2 nits
dispatch: implementer opus — resume, fix round 2
agent: implementer a213fb820d8ffc606 fix round 2
return: implementer fix round 2 DONE 6a60a38
dispatch: reviewer opus — resume, round 3
agent: reviewer a33dc1f546750d008 round 3 at 6a60a38
verdict: reviewer round 3 CLEAR at 6a60a38 (no findings)
landed: 8b88f29 (merge --no-ff into main)
- 2026-09-24 done
- 2026-09-24 marketplace - librarian acknowledged: prompting the operator to update and reload; filed its re-point of CLAUDE.md § Models and kappa-agents to dev-cycle references/model-routing.md (CLAUDE.md half awaits the operator grant)
