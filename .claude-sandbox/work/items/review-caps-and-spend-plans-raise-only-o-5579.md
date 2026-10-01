---
id: review-caps-and-spend-plans-raise-only-o-5579
title: "review caps and spend: plans raise only on a high left; builds get one self-granted round inside a grant"
short_display_name: review caps and spend
type: feature
status: doing
priority: 2
deps:
  - decisions-record-and-show-what-is-decide-58f4
  - librarian-mode-the-decided-alone-class-t-00ef
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-01T00:01Z
created: 2026-09-30
updated: 2026-10-01
refs:
  - .claude-sandbox/investigations/8dee-the-line/INDEX.md
  - 69ee answer 114
---

8dee F3 (L2, answer 114 b, pyramid answers 2026-09-30 (69ee, answer page)). Acceptance: 8dee F3 — plans impact-gated (raise only when a high is left at the cap, else stop and carry); builds take at most one self-granted round inside a standing grant with headroom above the reserve, else ask; dev-cycle keeps the home, the caller supplies the budget (librarian: grant + quota_budget.py; standalone dev-cycle asks as today). Ruling changes per 8dee INDEX § Ruling changes (answer 30, 88 (b), 68).

## Handoff
- doing: —
- next: blocked on decision 137 (cap): (a) resume implementer ae4df26f8668a3cac for one round (agent-brief Acceptance clause + record-lines findings: carried) then a fresh review; (b) land as is + P1 follow-up
- blocked: —
- learned: —

## Notes
- 2026-10-01 claimed by Kyle-McFarlane@401123cbad11
target: full review-caps-and-spend-plans-raise-only-o-5579 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/review-caps-and-spend-plans-raise-only-o-5579
dispatch: implementer opus medium — opus signal: changes what dev-cycle and librarian-mode do (caps and spend); feature from 8dee F3 (wave 3, 132 a)
agent: implementer ae4df26f8668a3cac round 1
return: implementer DONE_WITH_CONCERNS 1b71912
changed: 9 files — dev-cycle bindings.md (cap rule home), SKILL.md (Step 4.3/4.4, red flag; 4571 words), fix-loop.md, model-routing.md (undeclared: § Rounds pointer), review-brief.md (undeclared: cap pointer), resume.md (undeclared: cap on a CURRENT verdict applies Step 4.3 first); librarian-mode SKILL.md (Hold, channel pointers), budget.md (§ A self-granted cap round), decide-alone.md (cap row)
note: commit subject verb "changed:" is outside the house set (low; carried in the merge message)
dispatch: reviewer opus high — review round 1 (rule 4)
agent: reviewer ad2a1543b77f3da33 round 1
verdict: NEEDS_CHANGES round 1 at 1b71912
findings:
  1. [medium] budget.md:276-281 — "the latest reading" is never taken (idle-turn wiring held on 68), "fresh" dropped
  2. [medium] budget.md:276-279 — restates model-routing's reading
  3. [medium] bindings.md:218-221 — plan stop-and-carry applies to standalone dev-cycle too
  4. [medium] bindings.md:219-220 — carried findings never reach the build's acceptance
  5. [medium] bindings.md:222-227 (resume.md:182) — 8dee E2 missing: a granted round ends on the path the grant named; the cap rule does not re-apply
  6. [medium] bindings.md:218 vs model-routing.md:302-306 — stop-and-carry via Step 1's tail brings in a plan-stage fable offer at the cap
  7-13. [low/nit] no-signal rationale; dangling 68 pointer; fable-pinned self-granted round; FYI two-way + reopen for cap; SKILL.md:235 reflow; "changed:" verb; SKILL.md description "capped at four"
librarian rulings: 1 — at the cap the librarian takes a fresh `quota_budget.py --read-only` reading itself (not the held idle-turn wiring); point to model-routing for what "below" means; 3 — standalone dev-cycle asks at every cap, plans included; stop-and-carry applies only under a caller that binds it (librarian); 4 — carried findings are written onto the build's item as acceptance (the build item named by the series, or filed if none); 5 — carry E2; 6 — a stopped plan gets no fable offer (the at-the-cap stage needs a high left); 9 — a model: fable pin's extra round stays asked; 10 — a self-granted round's reopen: "say stop: the round ends and its commits do not land"
dispatch: implementer opus medium — resume
agent: implementer ae4df26f8668a3cac round 2
return: implementer DONE bad98c3
dispatch: reviewer opus high — resume
agent: reviewer ad2a1543b77f3da33 round 2
verdict: NEEDS_CHANGES round 2 at bad98c3
findings:
  1, 2, 6-11, 13 FIXED; 12 DECLINED (accepted); 3, 4, 5 PARTIAL
  14. [high] bindings.md:234-236 (resume.md:181-183, 220-222) — E2 applied to builds: an operator-granted build round that does not clear can neither land nor be raised; contradicts :218; also overrides standalone
  15. [medium] bindings.md:216 vs 234 — standalone no longer matches today after a waiver round; a store-less run has no item for "build acceptance"
  16. [medium] bindings.md:221-222 — the filed build item: no source for "the item the series names"; title/type/short name/link unstated; could reach another repo's store
  17. [low] budget.md:279 — unreflowed 99-char line
librarian rulings: 14/15 — E2 applies only to plan runs under a caller-bound budget; a build's operator-granted round that does not clear is raised again, as today; standalone runs keep today's behaviour exactly (a waiver round's verdict tests the cap again); fix :218 to except the end of an E2 path; 16 — the build item is filed in the same store as the plan item, never another repo's (out of Scope routes as Intake step 4), with title "build: <series slug>", type feature, a short display name from the series, a --ref to the series path and --parent the plan item when it has one; a store-less run writes the carried findings to its record sink and Step 6's open questions only
dispatch: implementer opus medium — resume (fix round 2; the next review is round 3)
agent: implementer ae4df26f8668a3cac round 3
return: implementer DONE c5459a2
dispatch: reviewer opus high — resume
agent: reviewer ad2a1543b77f3da33 round 3
verdict: NEEDS_CHANGES round 3 at c5459a2
findings:
  3, 14, 15, 16, 17 FIXED; 4, 5 PARTIAL
  18. [medium] bindings.md:218-219 (resume.md:221-224) — the granted-plan-path exception also swallows a SHOW_STOPPER, scope change or reversed decision; card 114 says escalations raise at every cap
  19. [medium] bindings.md:220-229 vs librarian SKILL.md § Factor — an auto-filed "build: <slug>" item duplicates the librarian's factored features or loses the carried findings
  20. [low] bindings.md:222-224 — Intake step 4 drops with --drop; carried findings for a peer repo vanish until 3460
librarian rulings: 18 — the exception covers only "a high left"; a SHOW_STOPPER, scope change or reversed decision raises at every cap; 19 — no auto-filed build item: the carried findings are written onto the plan item as a `findings: carried …` block; a build dispatched from that series (each factored feature included) copies them into its acceptance — librarian § Factor copies them into each feature's acceptance; a standalone build from the series reads the plan item's block; 20 — a series naming another repo's work raises the carried findings to the operator as a blocker until forwarding (3460) lands, never --drop
dispatch: implementer opus medium — resume (fix round 3; the next review is round 4, the cap)
agent: implementer ae4df26f8668a3cac round 4
return: implementer DONE_WITH_CONCERNS 87ed36f
dispatch: reviewer opus high — resume
agent: reviewer ad2a1543b77f3da33 round 4
verdict: NEEDS_CHANGES round 4 at 87ed36f
findings:
  5, 18, 20 FIXED; 4, 19 PARTIAL
  21. [medium] bindings.md:224-225 — only librarian Factor carries the carried findings; a standalone /dev-cycle <series> build reads acceptance from the series alone (SKILL.md:45, :86; agent-brief.md:47)
  22. [medium] record-lines.md:110-117 — the contract file does not list the new `findings: carried` shape or its writer (no run-time reader affected today)
  23. [nit] bindings.md:228 — 93 chars
cap: 4 review rounds without CLEAR — blocked; decision 137
decision 137: Review caps and spend (the build of your 114 answer) hit the 4-round review cap with two medium gaps, each a one-sentence fix: carried findings reach a build only through the librarian's factoring, not a standalone dev-cycle build of the series; and the record-line contract file does not list the new carried-findings line. Finish it how? — options: (a) one more small fix round (one clause in agent-brief.md's Acceptance, one sentence in record-lines.md) and a fresh review [recommended] | (b) land it now and file the two as a P1 follow-up | (c) leave it unlanded until you look | (z) decide later
  raised: 2026-10-01
  what: whether review caps and spend lands after one more small round or as is
  why now: the review cap; the trivial-docs build (dabd) waits on it (same file)
  why ask: cap — another round past the cap is yours to grant
  (a): about 20 minutes and under 1% of weekly quota; lands with no known medium
  (b): lands now; until the follow-up lands, a standalone build of a capped series can miss carried mediums
  (c): nothing lands; dabd keeps waiting
  (z): as (c)
  rec: (a) · basis strong — the reviewer names both fixes exactly and says nothing else is open at medium or above
  unknown: none
decision 137: Review caps and spend hit the 4-round review cap with two medium gaps, each a one-sentence fix; finish it how? — options: (a) one more small fix round and a fresh review [recommended] | (b) land it now and file the two as a P1 follow-up | (c) leave it unlanded until you look | (z) decide later
  raised: 2026-10-01
  revised: 2026-10-01T07:06Z — backfilled: context:, if left:, round costs:, stakes:; headline trimmed to the question
  what: whether review caps and spend (the build of your answer 114) lands after one more small round or as is
  why now: the review cap; blocks: the trivial-docs build (dabd), which edits the same file
  why ask: cap — another round past the cap is yours to grant
  context: you saw this card on 2026-10-01 during the unattended run · you decide whether review caps and spend gets one more round — then: none
  if left: (1) carried findings reach a build only through the librarian's factoring, so a standalone dev-cycle build of a capped series can miss carried mediums (fix: one clause in agent-brief.md's Acceptance); (2) the record-line contract (record-lines.md) does not list the new findings: carried line (fix: one sentence)
  round costs: about 20 minutes and under 1% of weekly quota; another answer from you if it does not settle
  stakes: reversible, narrow — dev-cycle builds of capped series
  (a) one more small fix round — the two sentences and a fresh review; lands with no known medium — undo: n/a — who: dev-cycle users
  (b) land now, P1 follow-up — lands at once; until the follow-up lands, a standalone build of a capped series can miss carried mediums
  (c) leave it unlanded — nothing lands; the trivial-docs build keeps waiting
  (z) decide later — as (c)
  rec: (a) · basis strong — the reviewer names both fixes exactly and says nothing else is open at medium or above
  unknown: none
answer 137: 137 I think the orchestrator should just finish trivial changes when the cap is reached. Make a work-item to make that the default behavior (read as: (a) finish it — one more small fix round for findings 21-22, fresh review; and a new item making that the default: trivial leftovers at the cap are finished without a decision)
dispatch: implementer opus medium — resume (fix round 4 past the cap, answer 137: findings 21, 22, nit 23)
agent: implementer ae4df26f8668a3cac round 5
