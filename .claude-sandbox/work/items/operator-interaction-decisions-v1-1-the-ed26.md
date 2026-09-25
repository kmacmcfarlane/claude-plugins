---
id: operator-interaction-decisions-v1-1-the-ed26
title: "operator-interaction decisions v1.1: the fable review's findings (seen test, turn placement, stored card)"
type: feature
status: done
priority: 1
parent: checkpoint-around-continuation-how-agent-d3ee
created: 2026-09-23
updated: 2026-09-24
closed: 2026-09-24
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

## Notes
- 2026-09-24 claimed by Kyle-McFarlane@bf9f9839222c
target: branch worktree-operator-interaction-decisions-v1-1-the-ed26 at .claude/worktrees/operator-interaction-decisions-v1-1-the-ed26, base main (3ee1319)
dispatch: implementer opus (fork, carries the operator rulings) — changes what a skill does; plans in its series first
agent: implementer aa7cd9fef7703fb2b (fork) round 1
return: implementer (fork) round 1 DONE_WITH_CONCERNS 3a5ca0b (render pass not run: forks cannot spawn; paging narrows the cold re-show, provisional)
librarian decision: existing decisions (68-81) get their stored card written the next time each is re-shown, not back-filled
dispatch: render agent sonnet — render pass r3 (a test, not a role)
agent: render a17311cfcdd2a34ad r3
decision 84: paging on a cold re-show — (a) with more than five open, the most pressing group and every ⚠ in full, the rest as lines ending (expand for the card) [recommended]; (b) every open decision as a card, as ruled; (z) decide later
  raised: 2026-09-24
  what: whether a cold re-show of many open decisions may show only the most pressing ones in full
  why now: v1.1 adds it as a provisional rule; it narrows the ruled "every open decision as a card"
  (a): six or more open → first group (or first three) and every ⚠ as cards, the rest one line each with the count stated; shorter messages, the rest one `expand` away
  (b): every one a card; nothing hidden, but a re-show of eight runs past 100 lines
  (z): ships provisional as (a) until ruled
  rec: (a) · basis: partial — fable's review and a 70-line four-decision render; no operator use yet
  unknown: how often you have more than five open in one repo
return: render r3 done — 3 renders; gaps: cold re-show heading with a ⚠, parsing embedded deadlines; after a one-way read-back with no confirmation; one later naming two decisions
dispatch: reviewer opus — fresh (grades the renders too)
agent: reviewer a3d57640ea3ca68a2 round 1 at 3a5ca0b
verdict: reviewer round 1 NEEDS_CHANGES at 3a5ca0b — 7 medium (worksheet restates old ⚠ rules; read-back widened to narrow one-way cards; "operator return" cold trigger undefined; stored card lacks who/basis drill-down for a ⚠ block; README dangling § Provisional rules; ending-the-session.md and dev-cycle SKILL.md standalone placement), 4 low; renders: no medium gaps
librarian decision: the read-back stays scoped to ⚠ decisions (answer 75 narrowed it within ⚠; a narrow one-way card never had one); files in scope widen to ending-the-session.md and dev-cycle SKILL.md § Report for the placement
dispatch: implementer opus (fork) — resume, fix round 1
agent: implementer aa7cd9fef7703fb2b fix round 1
return: implementer fix round 1 DONE 9f3cbca (who/basis required for any block)
dispatch: reviewer opus — resume, round 2
agent: reviewer a3d57640ea3ca68a2 round 2 at 9f3cbca
verdict: reviewer round 2 CLEAR at 9f3cbca (2 low, 1 nit — filed as a follow-up)
landed: 3385876 (merge --no-ff into main)
- 2026-09-24 done
- 2026-09-24 marketplace - librarian filed relay-operator-interaction-decisions-v1-dc77 and is relaying the update + /reload-plugins ask to the operator
decision 84: paging on a cold re-show — options: (a) with six or more open, the most pressing group and every ⚠ in full, the rest as lines [recommended] | (b) every open decision in full | (z) decide later
  raised: 2026-09-24T20:30Z
  revised: 2026-09-25 — expanded to a block at the operator's request; context, undo, who and basis added, options unchanged
  what: whether a cold re-show of many open decisions may show only the most pressing ones in full
  why now: v1.1 shipped it provisional and it is live as (a); it narrows the ruled "every open decision as a card"
  context: a cold re-show happens after a reset or /clear, or when you have not taken a turn since a decision was shown; each shown decision appears twice (card above, line at the tail)
  (a) first group (or first three, whichever is larger) plus every ⚠ as cards; the rest one line ending "(expand for the card)", with "N open · M shown in full" stated — undo: one edit to the skill — who: you, and every agent that raises decisions
  (b) every open decision a card — undo: one edit — who: same; long messages when many are open
  (z) decide later — it stays live as (a)
  rec: (a) · basis partial — fable review finding 7; one render; no real use yet
  basis: inferred — eight open decisions run past 100 lines (fable-review.md finding 7) · observed — four decisions took 70 lines before the hint (7113 test-round renders-r2 r2-08) · observed — the estate held 29 unanswered decisions across 16 items (fable-review.md finding 7, operator-attention's count)
  unknown: how often one repo has more than five open at once
