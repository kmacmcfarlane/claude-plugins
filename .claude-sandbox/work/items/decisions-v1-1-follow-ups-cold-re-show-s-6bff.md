---
id: decisions-v1-1-follow-ups-cold-re-show-s-6bff
title: "decisions v1.1 follow-ups: cold re-show scope wording, session-end placement clause, in-situ render"
type: chore
status: done
priority: 2
parent: checkpoint-around-continuation-how-agent-d3ee
created: 2026-09-24
updated: 2026-09-28
closed: 2026-09-28
refs:
  - ed26 review round 2 lows
---

From ed26's CLEAR review: (1) SKILL.md:155-158 'shows every open decision at card level' can read as re-rendering all when any one is unseen — make it 'each open decision the reader is cold on'; (2) librarian-mode ending-the-session.md:57-61 add that the decisions block stays last, as in step 4; (3) nits: a stray blank line in decisions.md:25, over-width lines at decisions.md:79, ending-the-session.md:125, worksheet.md:40, rendering.md:93. Also still unexercised (fable finding): a render pass in situ — librarian-mode loaded beside the skill, a real stored card as input, a full Report with push outcome and team summary. Decision 84 (paging) pending.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-decisions-v1-1-follow-ups-cold-re-show-s-6bff at .claude/worktrees/decisions-v1-1-follow-ups-cold-re-show-s-6bff, base main (9cafb1a)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
librarian decision: items 1-3 (wording, the placement clause restating the ruled step-4 rule, nits) now; the in-situ render pass split off as a later render test; decision 84 was dropped
dispatch: implementer sonnet — wording and a restated ruled clause, no behaviour change (rule 1)
agent: implementer a9aad903a3be9aee7 round 1
return: implementer DONE 059f084
changed: plugins/operator-interaction/skills/decisions/SKILL.md, references/rendering.md, references/worksheet.md; plugins/dev-flow/skills/librarian-mode/references/ending-the-session.md, references/decisions.md
dispatch: reviewer opus — fresh (rule 4; skill text keeps a reviewer)
agent: reviewer a4e01e24c1b91bd05 round 1 at 059f084
verdict: NEEDS_CHANGES round 1 at 059f084 (2 high, 2 medium, 2 low — all line width; meaning unchanged)
findings:
  [high] worksheet.md:40 — named nit not fixed; line now 119 cols; rewrap 38-41 to <=95
  [high] ending-the-session.md:129 — named nit moved, 107 cols; rewrap 126-130
  [medium] decisions SKILL.md:157 — new 106-col line; rewrap 155-158
  [medium] rendering.md:181 — new 115-col line; rewrap 180-185
  [low] librarian decisions.md:79 — 97 cols; optional
  [low] decisions SKILL.md:155 — "cold on the open decisions" vs "cold on any open decision"; optional
dispatch: implementer opus — fix round 1, fresh (rule 6 bump: high findings on a sonnet implementer)
agent: implementer ae76ece7d4236a8f7 round 2
return: implementer DONE 9dd5a24 (fix round 1; both optional lows taken)
dispatch: reviewer opus — resume, round 2
agent: reviewer a4e01e24c1b91bd05 round 2 at 9dd5a24
verdict: CLEAR round 2 at 9dd5a24 (1 low: SKILL.md:156 'since they were shown' → 'since it was shown'; applied after landing as the one-line wording bypass)
landed: 25a6b44 (+ cbc7509 one-word bypass for the review low)
- 2026-09-28 done: 25a6b44; in-situ render pass split out
