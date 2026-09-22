---
id: dev-cycle-design-resume-whole-split-from-e770
title: "dev-cycle: design § Resume whole (split from 426a)"
type: feature
status: doing
priority: 3
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
owner: unknown@360f41058e92
claimed: 2026-09-22T17:54Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - 426a answer 59
---

Split from 426a by operator answer 59(a), 2026-09-22. 426a lands review <branch> mode without § Resume; this item designs the resume state machine as a whole in dev-cycle plan mode before any build. Prior work (kept in main's history once 426a merges — git show <sha>:plugins/dev-flow/skills/dev-cycle/references/bindings.md): fa4ef02 (first cut), d802a19, 58bece4, 0f0a254, 54f022c (last full version). Feedback: 426a's body holds six review rounds verbatim (sections 'Review round 1'…'Review round 6'); the open mediums at 54f022c are (1) standalone 'recorded but unanswered → wait' deadlocks a resume in a new session (re-ask via the standalone channel; only a caller's persistent channel waits), (2) review mode never re-reviews after a recorded 'no' once the author moves the branch (rules 5/6 need rule 4's stale-sha test); low: rule 7 reuses an answer recorded before the latest BLOCKED run. Acceptance: a plan series whose 00 consolidates the six rounds into requirements + a state table, reviewed CLEAR before any implementer dispatch.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- from 426a final review (low): the shipped dev-cycle bindings.md '## Resume' heading points at this item's id, which marketplace installs cannot reach; the redesign replaces it (or, until then, 'not specified yet: an interrupted run restarts at Step 0').
dispatch: planner opus — plan mode, no worktree; series .claude-sandbox/investigations/e770-dev-cycle-resume/

## Notes
- 2026-09-22 claimed by unknown@360f41058e92

## Plan result (opus, 2026-09-22) — series .claude-sandbox/investigations/e770-dev-cycle-resume/ (00_initial.md, INDEX.md)
Diagnosis: the removed version was a rule list where each rule carried its own copy of the cross-cutting tests (cap, answered, staleness, channel), so every review found another rule with the wrong copy. Fix: compute those facts ONCE before the table is read. 19 requirements (R1–R19) each citing its round; phase lines (dispatch/return/verdict/landed) vs riders; reduction LANDED → PHASE → FRESH → ROUNDS → GATE with CHANNEL as a binding; one 12-row state table (S0–S12), a 4-row gate table, a 5-step liveness probe. r6 medium 1 settled by deleting "wait" entirely (ephemeral channel re-asks the same decision verbatim; durable hands back via wi handoff --blocked and the caller's idle turn resumes). r6 medium 2 settled by making a stale verdict its own state that spends findings AND answers — reviewing needs no permission, only dispatching onto the author's branch does. Line shapes: restore return:/landed:, add `agent: <role> <id> round <n>` and `baseline:`, widen target: and decision: (self-contained + options), generalise `at <sha>` → `at <token>`. Caller split: dev-cycle owns shapes/reduction/table/gate/probe; the caller owns queue, channel + durability, waiting, and carrying agent ids. Features F1→F4 strictly serial: F1 shapes (opus), F2 channel durability (opus), F3 § Resume whole (opus), F4 caller boundary (sonnet, opus review). No fable signal.
librarian decisions on the planner's questions: Q2 (a) → (b) accepted: § Resume lives in a new references/resume.md with a pointer from bindings.md (a state machine is not a binding; bindings.md is already 272 lines). Q3 (a): answer scope expressed positionally ("in force only when no phase line follows it") plus the named review-mode run-scoped exception. Q4 (a): a store-less run states its resume limit in the Step 0 summary; no new durable sink. Q5 (a): the interrupt walk is a review record, not a shipped walkthrough. F4 stays sonnet with an opus review; its files are two and mechanical once F3 lands.
decision 64: does a pending decision ever block a resume? — (a) never: an ephemeral channel re-asks the same decision now, a durable one hands back to its caller [recommended by the planner; goes further than review round 6, which proposed that only a caller's persistent channel waits — the planner's point is that a durable channel with no reader deadlocks the same way]; (b) keep "wait" on a durable channel with a timeout.
dispatch: plan reviewer opus — dev-cycle plan-review variant on 00_initial.md

## Plan review round 1 — NEEDS_CHANGES (opus) on 00_initial.md
Coverage: every medium+ finding from r1–r6 maps to a requirement; two map to a requirement the model does not close (r1 m9 → H2, r5 m2 → H3). Format conforms (Confirmed Assumptions present).
- [high 1] :199 S11's AT_CAP arm carries no phase constraint, so any record with 4 counted verdicts also matches S3/S4/S5/S6/S7/S12 — the waived-cap-then-dispatch path (this item's own history, answers 51/57) matches two rows with contradictory actions. 54f022c had "first that applies wins"; :183 drops precedence without replacing it. Pass: a phase constraint on S11's AT_CAP arm, or an explicit read order.
- [high 2] plan mode falls through: S4/S5/S6 key on `return: implementer`, a planner return matches nothing; Step 3.5 (the only `return:` writer) never runs in plan mode; F1's acceptance "target: carries … worktree path in every mode" is unsatisfiable (plan mode has no worktree).
- [high 3] S6/S12 read "a permission denial", which no line writes — :317-332 has no field for it; the plan's own R4 grep (:340-343) fails on its own model. This is r5 m2 reproduced with a new fact.
- [medium] CURRENT undefined for non-phase verdicts, so the one cap test is not evaluable (:161 vs :168-171); GATE ephemeral "re-ask now" contradicts the no-asking-after-heavy-analysis rule two rows above (:220 vs :221); the probe is a second writer and a resume-of-a-resume can double-dispatch (no state or detector for two live agents); R18 (a scratchpad sink from another session) has no state; the brief variant is decided in two cells with different answers; F2 is not independently landable (its exception names S10, which F3 introduces); F4's two-line scope cannot reach its own acceptance — four restatement sites exist (librarian SKILL.md:95 and :108, ending-the-session :17-18, :79, :101).
- lows: a misattributed quote drives F4's edit at the wrong line; probe step 5 has no reference point on a first dispatch; `at <token>` already ships for plan mode; the no-fable claim contradicts F3's fix-round-3 rule.
- reviewer: "computing the facts once" is directionally true and worth keeping — fold ROUNDS' freshness, S12's second count and the brief-variant choice into the reduction and it becomes true. Run the interrupt walk on the revised table as part of the re-plan, not at F3's review.
- on decision 64: only one cell changes either way; (b) also reopens the split's "waiting → caller" row and duplicates what `wi needs-input` + the Groom table already do. (a) stands.
dispatch: planner opus — plan fix round 1 (resume); revision as serial 01 with Supersedes

## Plan fix round 1 (opus) — serial 01_partition-and-walk.md (438 lines), Supersedes names 15 statements in 00
H1 closed by re-keying the table on PHASE, which partitions the record six ways (NONE/RIDERS/LANDED/DISPATCH/RETURN/VERDICT); AT_CAP stops being a state and becomes an axis inside the verdict group only, so the waived-cap-then-dispatch path is S3 and nothing else — rows cannot overlap by construction. A latent bug fell out: a CLEAR current at HEAD after four rounds now lands instead of deadlocking (that flaw has been in the cap test since 58bece4). H2 closed: group C keys on STATUS with <role> as a field; SKILL.md Step 1 becomes the planner's return: writer; target:'s third field is a workspace (worktree path, or the series path in plan mode). H3 closed: BLOCKED phase lines carry a reason from a closed set (permission | setup). Mediums: fresh(v) over any verdict; the ephemeral gate arm becomes "end the turn, ask at the start of the next" (obeys bindings.md:197-205, still not waiting); the probe no longer writes (it routes its report into Steps 3.5/4.5); a new S13 "two live agents" (stop, raise, kill nothing) and S0b "sink unreachable + live remnant", which also closes a silent-restart hazard where a lost scratchpad read as S0 and would have re-dispatched over a live worktree; VARIANT computed once; F2's exception restated without naming a state, so it lands before F3; F4's scope is five sites. The reduction is now eight facts and no row recomputes any. The interrupt walk is § 7: 22 rows, every state reached — rows 17b and 20 are the two that would have caught the highs.
librarian: the planner numbered a new question "65", which collides with the F3b decision of that number; renumbered here as 66.
decision 66: S13, two live agents on one worktree — (a) always a decision; the cycle never kills an agent on its own say-so [recommended by the planner and the librarian: killing on the cycle's own judgement is what S13 exists to prevent]; (b) keep the newest and report the other.
dispatch: plan reviewer opus — plan-review round 2 (resume) on serial 01
