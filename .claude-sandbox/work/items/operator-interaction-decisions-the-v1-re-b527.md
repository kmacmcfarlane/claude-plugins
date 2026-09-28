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
