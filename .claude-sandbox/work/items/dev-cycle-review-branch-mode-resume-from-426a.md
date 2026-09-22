---
id: dev-cycle-review-branch-mode-resume-from-426a
title: "dev-cycle: review <branch> mode + resume from item record (07c3 F4)"
type: feature
status: done
priority: 3
deps:
  - dev-flow-add-the-dev-cycle-skill-07c3-f1-325d
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
created: 2026-09-18
updated: 2026-09-22
closed: 2026-09-22
---

07c3 plan §F4. Size S-M; sonnet/opus.

## Handoff
- doing: implementer dispatched (sonnet, agent ad99423445ed4c9a0)
- next: on DONE: review r1 (opus)
- blocked: review cap hit (4 rounds); decision 51
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92
- dispatch: implementer sonnet — plan 07c3 routing table: one skill, 2 files, mechanical once §2 is fixed
- 2026-09-22 done: 400154c

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

## Review round 3 (4th review, cap) — NEEDS_CHANGES (opus) at 58bece4
- round-2 A, C-J fixed; B partial. Core guarantees hold (CLEAR at current HEAD only; checks always run; landed stops reruns; no land-only mode).
- [high] bindings.md:252-257 § Resume rule 5: a resumed review-mode run with last verdict NEEDS_CHANGES dispatches an implementer onto the author's branch, bypassing the operator's recorded "dispatch an implementer?" answer (declined / unanswered).
- [medium] bindings.md:230-234 rule 3 reviews after ANY implementer return; NEEDS_CONTEXT / BLOCKED must follow Step 3.5.
- lows: define "relevant" lines (dispatch/return/verdict/landed); rule 7 re-dispatches a BLOCKED reviewer without the twice-at-most count.
- reviewer: both are a few lines in § Resume rules 3 and 5, not a sign the brief or target is wrong.
decision 51: 426a hit the 4-review cap on a few-line § Resume fix (rule 5 review-mode dispatch answer; rule 3 return status) — (a) waive the cap for one more fix round on opus (rule 3: fix round 3 after a high → fable, unavailable → opus) plus one review [recommended: the fixes are specified line-by-line; everything else is CLEAR]; (b) land review mode without resume: split § Resume into a new item and have the implementer revert it on this branch, then review; (c) park 426a as is.
answer 51: (a) another round approved (operator 2026-09-22)
- dispatch: implementer opus — fix round 3 after a high (rule 3 → fable; fable fallback → opus per answer 51's recommendation); fresh agent in the same worktree (the sonnet implementer cannot be resumed at a higher tier)
- fix round 3 DONE 0f0a254 (opus, cap waived by answer 51): § Resume rule 5 dispatches onto the author's branch only on a recorded yes (decline → report/handoff/stop; unanswered → raise the decision); rule 3 by return status (NEEDS_CONTEXT/BLOCKED → Step 3.5); relevant lines = dispatch:/return:/verdict:/landed:; rule 7 BLOCKED reviewer at most twice.
- dispatch: reviewer opus — review r5 (the waived round; fresh reviewer, the r1–r4 reviewer ran in the prior session)

## Review round 5 (waived by answer 51) — NEEDS_CHANGES (opus, fresh reviewer) at 0f0a254
- round-3 high, medium and both lows fixed; every last-line state walked: no double dispatch, no action on the author's branch without a recorded yes, no land without CLEAR at HEAD, checks always run.
- [medium] bindings.md:260-265, 272-274 — rules 5 and 6 define the cap differently: CLEAR r1 → HEAD moves → NEEDS_CHANGES r2–r4 → interrupt matches no rule. Pass: one cap test (count verdict rounds; exclude only a CLEAR current at HEAD) used by both.
- [medium] bindings.md:204-205, 129-157 (+ rules 3/5/6/7) — every guard reads a decision's "recorded answer" but no step writes one; no answer shape in § Record line shapes; resume re-raises answered decisions; caller's `decision N:`/`answer N:` not matched. Pass: add `answer:` shape, write it in § Decisions and Step 3.5, read it in rules 3/5/6/7, name `answer N:` equivalent.
- lows: rule 5 declined path `$WI handoff` without "(no item: nothing further)"; rule 7 re-dispatches a permission-denied BLOCKED (should block + decide); rule 6 silent on acting once an answer is recorded.
- both mediums predate 0f0a254 (from 58bece4).
decision 57: 426a's waived round is not CLEAR — the § Resume state machine drew new mediums for the fifth review running (a cap mismatch between rules 5/6; decision answers never recorded). Review mode itself has been CLEAR since round 4. (a) land review mode without § Resume: the implementer reverts § Resume on this branch, a short review confirms, and § Resume becomes a new item planned first (plan mode) so its state machine is designed whole [recommended: stops a fix-by-fix spiral; everything else is ready]; (b) one more fix round for the two mediums + lows and one review; (c) park 426a.
answer 57: (b) one more fix round for the two mediums + lows and one review (operator 2026-09-22)
- dispatch: implementer opus — fix round 4 (answer 57), resume the round-3 opus implementer
- fix round 4 DONE 54f022c (opus, answer 57): one cap test (counts CLEAR/NEEDS_CHANGES/SHOW_STOPPER, excluding only a CLEAR current at HEAD) used by rules 4–6; `decision:`/`answer:` shapes (librarian's `decision N:`/`answer N:` equivalent) written in § Decisions and Step 3.5, read by rules 3/5/6/7; lows fixed; state-walk table in the report; deviation: rule 4's stale-CLEAR branch runs the cap test.
- dispatch: reviewer opus — review r6 (the answer-57 round; resume the r5 reviewer)

## Review round 6 (answer 57) — NEEDS_CHANGES (opus) at 54f022c
- round-5 mediums and lows fixed; the deviation is judged correct; state walk: no double dispatch, no land without a current CLEAR, checks always run, no action on the author's branch without a yes.
- [medium] bindings.md:265, 294, 300, 308 — "recorded but unanswered → wait" deadlocks a standalone resume: the AskUserQuestion that asked died with the old session; the new one waits and never asks. Pass: standalone re-asks the same question (no new decision: line); only a caller's persistent channel (librarian `decision N:`) waits.
- [medium] bindings.md:285-295 — review mode: a recorded "no", then the author pushes fixes, and the rerun re-reports the old findings forever; rules 5/6 lack rule 4's stale-sha test. Pass: a verdict whose <sha> ≠ HEAD is stale in rules 5/6 → fresh review under the cap test; the old "no" is not reused.
- [low] rule 7 reuses an answer recorded before the latest BLOCKED run.
decision 59: 426a — the approved round (57b) fixed its findings, but § Resume drew two new mediums for the sixth review running (a standalone resume waits forever on a question nobody still asks; review mode can never re-review a branch after a "no"). Review mode itself has been CLEAR since round 4. (a) land review mode without § Resume: the implementer reverts § Resume (and its Step 0 hooks) on this branch, a short review confirms, and § Resume becomes a new item planned first in dev-cycle plan mode so the state machine is designed whole, with these six rounds of findings as its input [recommended: every fix round has exposed a new edge; a design pass is cheaper than more rounds]; (b) another fix round for the two mediums + the low; (c) park 426a as is.
answer 59: (a) land review mode without § Resume; record the work already done and the current feedback for the redesign (operator 2026-09-22)
librarian (answer 59a): the § Resume work stays recoverable because 426a merges with its full history (fa4ef02…54f022c) plus a revert commit on top; the redesign is item dev-cycle-design-resume-whole-split-from-e770, whose body carries the shas and the open findings; this body keeps the six review rounds verbatim.
dispatch: implementer opus — revert § Resume (and its Step 0/SKILL.md hooks) on this branch as a new commit (resume abb824e); then reviewer opus — confirm review mode stands alone (resume a393294)
- revert DONE 3becdf5 (opus, answer 59a): § Resume body → pointer to e770 (heading kept); return:/landed: shapes and writes removed; Step 0.4 removed; troubleshooting resume row removed; review mode + decision:/answer: shapes kept; grep clean.
- dispatch: reviewer opus — confirm review mode stands alone (resume a393294)
- review (opus) at 3becdf5: CLEAR — review mode stands alone; no dangling pointers; every kept record shape written and read. Lows: the shipped `## Resume` heading points at a local work-item id (unreachable for marketplace installs) → moved to e770; fa4ef02 subject mentions resume → carried in the merge message.
- Review result: 7 reviews over the item's life (cap waived by answers 51, 57; split by 59); review mode CLEAR since r4; impl sonnet r1–r2, opus r3–r5; review opus.
