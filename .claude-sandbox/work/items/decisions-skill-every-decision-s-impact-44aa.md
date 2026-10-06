---
id: decisions-skill-every-decision-s-impact-44aa
title: "decisions skill: every decision's impact is visible at every level, the one-line list included"
short_display_name: impact on every decision line
type: feature
status: doing
priority: 0
owner: Kyle-McFarlane@401123cbad11
claimed: 2026-10-06T06:10Z
created: 2026-10-06
updated: 2026-10-06
refs:
  - operator 2026-10-06
---

Operator 2026-10-06, verbatim: 'I have an important improvement I'd like to see to the decision skill ASAP. I want to ALWAYS see some form of impact that a decision has, even in the one-line version. The impact of the decision is critical for me, and it's not currently visible in a way I can understand it at all times. Propose how to address this, and let's prioritize this over other work for now until it lands.' Priority: ahead of all other work until it lands (operator). Acceptance: the proposal approved by the operator, then built in the decisions skill (list line, card, block, re-show and (shown before) lines, the Groom row) and every caller that restates the list line.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
proposal: 2026-10-06T04:07Z — every list line gets two plain-word impact slots right after the recommendation: "→ <what changes if the recommendation is taken, for whom>" and "later: <what waiting costs, what it blocks>"; both rendered from the stored card's recommended option and its (z) line, so no new stored field; mandatory on every line, (shown before) and (expand for the card) lines and Groom rows included; a no-recommendation line shows each option's impact in a few words instead; the stakes and blocks slots fold into them; class, basis and age stay, after them
decision 165: Should every decision line show its impact like this: "→ what changes if you take the recommendation · later: what waiting costs", on every line including shown-before ones and Groom rows? — options: (a) yes, as proposed [recommended] | (b) impact only, no later: slot | (c) two lines per decision: the title line, then an indented impact line | (z) decide later
  raised: 2026-10-06T04:07Z
  what: the shape of the impact you asked to see on every decision, including the one-line version
  why now: you asked for it ASAP, ahead of other work; blocks: the build
  why ask: your-call — it is the format you read every decision in
  context: you said the impact of a decision is critical and not visible at all times · you approve the shape before it is built
  stakes: reversible, wide — every decision every session shows you
  (a) as proposed — every line answers "what happens if I say yes" and "what happens if I wait" in plain words; lines grow by about a third; class, basis and age move after the impact — undo: an edit — who: every session using the decisions skill
  (b) impact only — shorter; what waiting costs stays on the card — undo: an edit
  (c) two lines per decision — roomier impact text, the list twice as tall
  (z) decide later — lines stay as they are
  rec: (a) · basis partial — the two things a decider weighs are the effect of yes and the cost of waiting; both already exist on every stored card, so lines can always carry them
  unknown: whether one line stays readable at your terminal width with both slots
note: 2026-10-06T06:07Z operator, verbatim: "You showed me examples per line, but I want it to be in the other sizes of outputs too. Show me your proposal so every view of a decision includes the impact. Consider how to structure the impact as you get more space to work with" (read as: reframe of 165's scope — every view, with impact structure growing with space)
proposal r2: 2026-10-06T06:07Z — five impact facets, one vocabulary, shown more fully as space grows: Effect (what changes if the recommendation is taken), Wait (what waiting costs, what it blocks), Reach (who or what is affected: you, sessions, repos, public), Undo (how to reverse it, or one-way), Cost (time, money, quota, your attention). Tag size (Groom row, page summary chip, Report's decisions-needed line): Effect. Line: Effect · Wait. Card: an Impact line under the title (Effect · Wait · Reach · Undo) and each option's impact in the same facet order. Block: an Impact table, one row per option, columns Effect, Reach, Undo, Cost, plus a Wait row. Re-show: while-it-waited says whether the impact changed. Decision page: the card's Impact line and the block's table. Store: a mandatory impact: card line (Effect · Wait · Reach · Undo) written at raise, read by every view including the Groom row; existing cards backfilled from their rec option and (z) lines.
decision 165: Should every view of a decision show its impact, in five facets (effect, wait, reach, undo, cost) shown more fully as space grows, from the Groom row to the block? — options: (a) yes, as proposed [recommended] | (b) yes, but lines show the effect only (no wait) | (c) yes, but no new stored line: views derive impact from the options each time | (z) decide later
  raised: 2026-10-06T03:16Z
  revised: 2026-10-06T06:07Z — reframed by the operator to cover every view; options and recommendation restated for the full proposal
  what: how every view of a decision shows its impact: the Groom row, the Report's decisions-needed line, the list line, the card, the block, the re-show and the decision page
  why now: you asked for it ASAP, ahead of other work; blocks: the build, and the held work behind it
  why ask: your-call — it is the format you read every decision in
  context: you asked for impact in every view, structured as space grows · you approve the shape before it is built
  stakes: reversible, wide — every decision every session shows you
  (a) as proposed — one five-facet vocabulary everywhere; the smallest view shows the effect, each larger view adds facets in a fixed order; a new impact: line stored with every decision so even a one-line view never has to guess — undo: an edit — who: every session using the decisions skill, the librarian, the decision page
  (b) lines show the effect only — shorter lines; what waiting costs appears from the card up
  (c) no stored line — nothing new written; each view derives impact from the option text, so short views may read less clearly
  (z) decide later — views stay as they are, and the held work stays held
  rec: (a) · basis partial — one vocabulary learned once, read at every size; storing it at raise means the tightest views (Groom row, headline) can show it without opening the card
  unknown: whether the tag-size effect stays clear in under 10 words for complex decisions
answer 165: 165a do it now (2026-10-06T06:10Z, chat; read as: (a) as proposed — five facets in every view, a stored impact: line; build now, ahead of other work)

## Notes
- 2026-10-06 claimed by Kyle-McFarlane@401123cbad11
target: full decisions-skill-every-decision-s-impact-44aa /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/decisions-skill-every-decision-s-impact-44aa
budget: 2026-10-06T06:10Z build $22 — default other build
dispatch: implementer opus high — build (implementer-critical: the operator called it "important" and the impact "critical"; spec = proposal r2 + answer 165 a)
agent: implementer-critical abcdb2f429201bdfa round 1
