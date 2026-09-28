---
id: dev-cycle-step-5-numbering-puts-the-push-f6fd
title: "dev-cycle: Step 5 numbering puts the push (5.3) before landed: (5.5); a run dying between merge and landed: reads STALE"
type: bug
status: doing
priority: 3
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T23:02Z
created: 2026-09-28
updated: 2026-09-28
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
