---
id: operator-interaction-decisions-the-v1-re-b527
title: "operator-interaction decisions: the v1 review's remaining lows"
type: chore
status: doing
priority: 2
parent: checkpoint-around-continuation-how-agent-d3ee
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T23:16Z
created: 2026-09-23
updated: 2026-09-28
refs:
  - 9f98 review r2
---

9f98 review r2 (CLEAR at 709c75b) left: (1) worksheet.md:47, 'a new decision raises the level' needs 'unless its options converge'; (2) rendering.md:43-44 and :148, the stakes-slot list still includes the preference and template labels, which have their own slots; (3) SKILL.md:101-102 / rendering.md:181, 'the operator's return' as a cold trigger versus worksheet § A's event-only definition (add 'returned from a stated absence' to the events, or drop it); (4) evidence-basis.md:47-48, name the load-bearing claim for a decision with no recommendation (renders fell back to basis none); (5) replies.md:9-10, one verb over several numbers applies to each, keeping per-decision rules. Nits: gallery.md:19/:35 vs :50 on what 43 blocks; gallery.md:203-207, ages missing on the expand re-show. Also record for the operator: the *(shown before)* marker narrows plan R-14 for the round after an expand.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 71: operator-interaction catalog aim — (a) keep "…your agents to put what they need from you in a form you can act on where it appears" [recommended: one clause, and it leaves room for more interaction skills than decisions]; (b) narrow it to decisions only; (z) decide later
decision 72: skill name `decisions` (provisional in README name status) — (a) confirm `decisions` [recommended: plain, and cheap to rename while unshipped]; (b) rename (e.g. `decide`, `operator-decisions`); (z) decide later
decision 73: the "(shown before)" marker narrows plan R-14 for the round after an expand (already-seen cards are not re-rendered) — (a) keep [recommended: less repetition in long lists]; (b) re-render every card each round; (z) decide later
- (6) from operator-attention 2026-09-23: replies.md should state that something must evaluate event wakes (the collector does for event wakes; a time wake anyone can check), since a deferral nobody evaluates is a default by omission. A decision with a wake re-enters the list only when its wake has fired.
answer 71: (a) keep the aim line (operator 2026-09-24)
answer 72: (a) confirm `decisions` (operator 2026-09-24)
answer 73: (a) keep (shown before) (operator 2026-09-24)
target: branch worktree-operator-interaction-decisions-the-v1-re-b527 at .claude/worktrees/operator-interaction-decisions-the-v1-re-b527, base main (a66d203)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — decisions-skill rule wording (rule 2)
agent: implementer a77af10acb8c50b38 round 1
return: implementer DONE 6c28d20 (1,2,3,5,6 + nits taken; 4 declined already fixed at evidence-basis.md:60-64; open q: rationale.md two-clocks could name the stated absence)
changed: plugins/operator-interaction/skills/decisions/SKILL.md, references/worksheet.md, rendering.md, replies.md, gallery.md
dispatch: reviewer opus — fresh (rule 4)
agent: reviewer a06424d4e723e69f4 round 1 at 6c28d20
verdict: NEEDS_CHANGES round 1 at 6c28d20 (3 medium, 4 low)
findings:
  [medium] point (3) was settled the other way in v1.1 (9f3cbca removed "the operator's return"); re-adding "stated absence" changes ruled behaviour (re-shows every seen card, every ⚠ as a block) and drifts from librarian-mode decisions.md:39/:113 — decline (3) and revert, or raise to the operator
  [medium] replies.md:68-69 — a deferred decision would drop off the list; stays a list line with its wake until the wake fires
  [medium] replies.md:10-13 — one verb over several numbers could ratify a ⚠ in a batch; acting verbs skip ⚠ and re-ask, as ok N-M does
  [low] SKILL.md:156-158 trigger list incomplete (point, or list all five); [low] SKILL.md:160 ~125-char line; [low] worksheet.md:21-22 moot if reverted; [low] rationale.md fine as is
librarian decision: decline (3) as already resolved at 9f3cbca and revert its additions — it would reverse a ruled v1.1 behaviour; not worth a decision to the operator
dispatch: implementer opus — resume, fix round 1
agent: implementer a77af10acb8c50b38 round 2
