---
id: operator-interaction-decisions-v1-1-the-ed26
title: "operator-interaction decisions v1.1: the fable review's findings (seen test, turn placement, stored card)"
type: feature
status: todo
priority: 1
parent: checkpoint-around-continuation-how-agent-d3ee
created: 2026-09-23
updated: 2026-09-23
refs:
  - fable review 4fb0
---

From the fable review (4fb0; .claude-sandbox/investigations/7113-decisions/reviews/fable-review.md). Three high findings: (1) 'shown before' is measured by rendering, not by the operator's presence, so the fix is 'seen' = the operator has taken a turn since; (2) in the terminal the turn ends with the team summary, not the decisions, and the most pressing decision sits furthest from the prompt; (3) the store line cannot rebuild the card, so the cold re-show is re-composed (pull 0134 forward: floor fields as indented lines plus raised-at). Mediums 4-10 and lows 11-15 are in the review. Scope waits on the operator's decisions 74-79.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
decision 74: fable's three high findings — (a) fix now as v1.1: 'seen' = the operator took a turn since; the decisions block last in the turn; the store carries the card and a raised-at time (pulls 0134 forward) [recommended: these are the cold-operator case you complained about]; (b) fix only 1 and 2 now, 0134 later; (z) decide later
decision 75: narrow the ⚠ read-back and the `you decide` refusal to answers that pick a one-way option (a reversible choice on a ⚠ decision, e.g. 'keep and alias', acts at once) — this narrows your P3 (2) ruling — (a) narrow [recommended: the friction lands only where it prevents harm]; (b) keep as ruled (every ⚠ choice is read back); (z) decide later
decision 76: ⚠ decisions render as a full block on first show and on a cold re-show only, otherwise as a list line — (a) yes [recommended: stops every Report re-sending every ⚠ block]; (b) keep a block in every Report; (z) decide later
decision 77: where decisions sit in the terminal — (a) the decisions block is last in the turn, cards above, list and hint at the tail [recommended: what is on screen when the agent stops]; (b) last in the turn, list first, plus a 'first: N' pointer by the hint; (c) keep as built; (z) decide later after a render test in your own terminal
decision 78: two provisional rules fable would change — (a) the default wake becomes 'the next time I finish a piece of work and report', and the 4-hour threshold is dropped (with an unknown return, any stated deadline goes first) [recommended: no arbitrary numbers, and the asymmetry favours listing deadlines first]; (b) keep as shipped; (z) decide later
decision 79: rule the other provisional rules in as shipped — the labelled exceptions (R1), the basis word with a simplified derivation (R4), no confidence percentage (R7), status-quo defaults only (R6) — (a) rule them in [recommended: fable and both research rounds agree]; (b) keep them provisional; (z) decide later
answer 74: (a) fix all three high findings as v1.1 (operator 2026-09-24)
answer 75: (z) decide later (operator 2026-09-24)
wake 75: next Report
answer 76: (a) ⚠ in full on first show and when cold, else a line (operator 2026-09-24)
answer 77: (a) — operator: "it'd be more useful to have the compact, one-line decision list below the cards/blocks so you can answer some/all of them without scrolling up" (read as: (a), cards above, list + hint at the tail; the build today is (c), list first)
answer 78: expand — re-show at block level next round (operator 2026-09-24)
answer 75: (a) read back and refuse `you decide` only when the chosen option is one-way (operator 2026-09-24)
answer 78: (a) default wake = next time I finish a piece of work and report; drop the 4-hour threshold; unknown return → any stated deadline first (operator 2026-09-24)
answer 79: (a) rule in the labelled exceptions, the basis word (simplified derivation), no confidence percentage, status-quo defaults only (operator 2026-09-24)
- 2026-09-24 all v1.1 decisions answered (74 a, 75 a, 76 a, 77 a, 78 a, 79 a); ready to plan
