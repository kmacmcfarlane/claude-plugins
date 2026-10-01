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
- next: —
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
