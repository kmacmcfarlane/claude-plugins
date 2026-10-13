---
id: dev-cycle-step-5-numbering-puts-the-push-f6fd
title: "dev-cycle: Step 5 numbering puts the push (5.3) before landed: (5.5); a run dying between merge and landed: reads STALE"
type: bug
status: done
priority: 3
created: 2026-09-28
updated: 2026-09-28
closed: 2026-09-28
refs:
  - 16da review
---

From the 16da review 2026-09-28: SKILL.md Step 5 numbering puts the push at 5.3 and landed: at 5.5; only 'the moment the merge succeeds' says landed: comes first — an executor following the numbers pushes before recording; Step 5 never runs the MERGE_HEAD check the troubleshooting bullet says happens at Land; and a run that dies between merge and landed: (worktree already cleaned) reads STALE and may re-land merged work. Acceptance: the order made explicit in Step 5; Land checks MERGE_HEAD; the STALE case handled or documented.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-28 from the 16da review (lows): S0b's report reads 'not resumable' even when the pending MERGE_HEAD may be the operator's own — say 'a merge is pending in the main checkout (one this run may not have made)'; troubleshooting.md:60-62 S0b symptom bullet still says the orphan-worktree rule decides, but a pending merge now routes to the merge bullet
target: branch worktree-dev-cycle-step-5-numbering-puts-the-push-f6fd at .claude/worktrees/dev-cycle-step-5-numbering-puts-the-push-f6fd, base main (4dcf3de)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — changes Step 5's order and Land's checks (rule 2)
agent: implementer ad34ddcd4498110e0 round 1
return: implementer DONE 58920ed (landed: moved into 5.3 before checks/push/cleanup; MERGED fact + S2b; S0b wording; troubleshooting S0b + S2b bullets; record-lines pointer)
changed: plugins/dev-flow/skills/dev-cycle/SKILL.md, references/resume.md, references/troubleshooting.md, references/record-lines.md
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer a8c21f2e82d60050d round 1 at 58920ed
verdict: NEEDS_CHANGES round 1 at 58920ed (2 high, 2 medium, 1 low; MERGED command holds in all 8 tried cases)
findings:
  [high] SKILL.md:319-323 (+333-335, review-checklist.md:365-368, troubleshooting.md:111-113) — landed: now precedes the base checks, but the red-check paragraph and checklist §6 still send a red base back into the fix loop while resume S2 treats landed: as terminal; "Merge and push pushes only after both" never requires green; S2b has the same gap. Pass: red base check after the merge follows troubleshooting "A check is red on the base after the merge" (file/raise, report, no push, no fix loop); push needs green base checks; §6 wording reconciled
  [high] resume.md:153 S2 — a run dying after landed: leaves base checks, push, cleanup, $WI done undone; S2 reports and stops, item stays doing forever. Pass: S2 and S2b share the post-merge tail and do what is undone, naming any push not made
  [medium] resume.md:124-125 — MERGED "computed when LANDED is absent" uses the file's word for an unreachable-sink fact; can never hold. Pass: "LANDED is no"; unify yes/no spelling
  [medium] resume.md:154 S2b — "push only when the Terminal action binding names one" lets a cycle under a librarian push before the librarian's Report. Pass: under a librarian the cycle never pushes (as troubleshooting.md:118-120)
  [low] resume.md:154 — S2b ignores "a push the invocation asked for in words" (bindings.md:266); say reported unpushed explicitly
dispatch: implementer opus — resume, fix round 1
agent: implementer ad34ddcd4498110e0 round 2
return: implementer DONE 2543c2a (fix round 1; shared landing tail for S2/S2b)
dispatch: reviewer opus — resume, round 2
agent: reviewer a8c21f2e82d60050d round 2 at 2543c2a
verdict: NEEDS_CHANGES round 2 at 2543c2a (3 medium, 1 low; all round-1 fixed)
findings:
  [medium] resume.md:223 tail step 3 — base range undefined on resume; pass: BASE=<merge sha>^1 for §6, checks on the base as it stands, attribute a red to this merge only after checking git log <merge sha>..<base>, naming later commits
  [medium] resume.md:220-222 tail step 2 no-item arm — true from the start for a review <branch> run whose worktree the cycle didn't add; pass: a positive completion record (e.g. a closed: line) or always run steps 3-5 (idempotent)
  [medium] troubleshooting.md:113, SKILL.md:323-325 vs librarian-mode — "nothing is pushed past it" contradicts the librarian's unconditional push after its Report; pass: scope to the cycle's own push, under a librarian the red goes on decisions needed and the push is the librarian's call
  [low] SKILL.md:336 — 118-char line, rewrap
librarian decision: finding 3 takes the scoping option inside dev-cycle; gating librarian-mode's push on green base checks filed as its own item (librarian-mode is outside this item's files)
dispatch: implementer opus — resume, fix round 2
agent: implementer ad34ddcd4498110e0 round 3
return: implementer DONE 0af7908 (fix round 2: 734ffa7 + 0af7908)
dispatch: reviewer opus — resume, round 3
agent: reviewer a8c21f2e82d60050d round 3 at 0af7908
verdict: CLEAR round 3 at 0af7908 (2 low: a resumed push may carry later local commits — name them as step 3 does; store-less S2 re-runs base checks each time — declined, both safe and doctrine-consistent)
landed: 9f2c425
- 2026-09-28 done: 9f2c425
