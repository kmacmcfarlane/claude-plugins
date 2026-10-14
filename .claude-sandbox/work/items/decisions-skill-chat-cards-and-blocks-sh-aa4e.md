---
id: decisions-skill-chat-cards-and-blocks-sh-aa4e
title: "decisions skill: chat cards and blocks show each option's effect, reach, undo and cost, with Effect across all options"
short_display_name: per-option impact in chat cards
type: feature
status: todo
priority: 2
created: 2026-10-14
updated: 2026-10-14
refs:
  - decision-page-tldr-first-levels-shaped-s-1e00
---

Answer 206 a (2026-10-14) widened by the operator: 'is there a provision for displaying the effect/reach/undo/cost in TUI cards/blocks per-option too? That parity seems valuable. Make it so'. Acceptance: the decisions skill's card and block templates give Effect across all options (as the page does) and each option's effect/reach/undo/cost; the stored impact: line's Effect follows; gallery and tests updated.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: an agent worktree off main (f4be55ec); operator-interaction decisions skill
budget: waived (operator 2026-10-08); spend measured
dispatch: implementer opus medium — per-option impact facets in chat cards and blocks (answer 206 a, widened)
agent: implementer a59b7de78c35ac530 round 1
result: DONE round 1 at 164c918c on worktree-agent-a59b7de78c35ac530 (base 60d40295; per-option facet line; Effect across options; stored impact: lines; gallery; decision-page 'never blindly'; rulings recorded; operator-interaction 153, dev-flow 96, kit-dev 21 OK)
dispatch: implementer opus medium — resume, merge main (6d12 landed in the same decision-page files) before review
result: DONE merge at eefe676e (CLAUDE.md tests line resolved; operator-interaction 160, dev-flow 91, kit-dev 21 OK)
dispatch: reviewer opus high — fresh (rule 4)
agent: reviewer a0253b12d610cb762 round 1 at eefe676e
verdict: NEEDS_CHANGES round 1 at eefe676e (2 medium: the list line keeps the recommendation's own effect, against SKILL.md and the across-options Effect; a ⚠ card does not carry every option's undo; 3 low: 'never blind' has no test, the gallery effect test and mutation, 3769 merge conflicts; 3 nits)
decision 219: On a decision's one-line list entry (the list at the end of a message and the librarian's Groom row), which effect follows the recommendation? The card now gives Effect across all options; the build kept the recommended option's own effect on the list line to stay terse — options: (a) the recommended option's own effect, as built: terse, and the rec label already names whose effect it is [recommended] | (b) the Effect across all options, as the page's map does: one meaning of Effect everywhere, but longer list lines | (z) decide later: the build lands as (a), marked pending your answer
dispatch: implementer opus medium — resume, fix round 1 (findings 1 wording, 2-4, 6-8; the list-line choice stays as built, pending decision 219)
agent: implementer a59b7de78c35ac530 round 2
result: DONE round 2 at bcb956e8 (all fixes; list line pending 219; 162 OK)
dispatch: implementer opus medium — resume, merge main (3769 landed) then review round 2
shown 219: 2026-10-14T08:14Z page
result: DONE merge at 64397fcb (main with 3769 merged; four conflicts resolved, both sides kept; 3769's More-order nit added; operator-interaction 175 OK)
dispatch: reviewer opus high — resume, round 2
agent: reviewer a0253b12d610cb762 round 2 at 64397fcb
verdict: CLEAR round 2 at 64397fcb (nit: chat stricter than the page on a bare undo; no action)
