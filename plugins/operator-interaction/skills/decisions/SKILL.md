---
name: decisions
description: "Put a decision to the operator so they can understand and answer it where it is shown: a content floor every decision carries, detail that scales with the stakes and with how far the operator is from the work, a set order, natural-language replies with an echo, and 'decide later' with a wake. Use whenever you are about to ask the operator to decide, choose, approve or confirm something, list open decisions, re-show decisions after a break or a context reset, read the operator's reply to one, or judge whether an action may be taken and reported afterwards instead of asked about first. Not for progress updates that ask nothing."
---

# Decisions

The goal is not to get an answer. The goal is for the operator to **understand the decision
— its context and its impact — where it is shown**, and answer it from there. A decision they
cannot act on from what is on the screen costs them a scroll back through hours of text, or a
blind answer.

The operator reads with their attention; you can juggle every dimension. So you do the
analysis (`references/worksheet.md`) and they see only its results: how much detail, which
order, how to answer.

*Examples in this skill and its references are illustrative: invented, not about any real
project.*

**Per decision, before you write:** meet the floor → fill the worksheet → pick the level →
place it in the order. Then write the message as § Several decisions in one message lays it
out.

## Critical

- **Every decision meets the floor before it is raised** (below). Without options it is not
  a decision: it is an open question, labelled as one.
- **⚠ one-way decisions** — one-way *and* high impact — are never ratified inside a batch and
  never defaulted. Shown as a block the first time and whenever the reader is cold. An answer
  that picks a **one-way option** is repeated back and acted on only once confirmed, and
  `you decide` never takes the one-way option.
- **No timed defaults on actions.** Silence never turns into an action.
- **Never show a confidence percentage**, and never use one to order decisions.
- **Raise decisions as text in your message**, per this skill — not through a modal dialog
  (AskUserQuestion) unless the rules you are running under require one: a dialog cannot
  carry the list, the hint, the echo or `later`.
- **The decisions come last in the message**, the list and the hint at the very end, where the
  operator's eye is when you stop.
- **Keep the caller's numbering** when it has a counter; otherwise number from 1 in this
  session. Never reuse a number.
- **Scale the card to the decision.** A small call gets a short card; stakes buy detail.

## The floor

Every decision carries, at any level:

1. **What is decided**, in plain words. Gloss every id, hash, file or item name on first use —
   a bare `a3f9` or `7c41e0d` tells a cold reader nothing.
2. **Why now**, and what it blocks. When nothing forces it, say so — *why now: nothing forces
   it; raised because the audit turned it up* — and *blocks: nothing* is an honest answer.
3. **The options**, each with its consequence — what happens to the world if it is chosen.
   Include "do nothing" when it is a real option.
4. **Decide later**, always, as its own option (`(z)`), distinct from "do nothing": it says what
   waiting costs, and when there is a deadline, what happens at the deadline.
5. **The recommendation**, or the labelled reason there is none.
6. **The basis** — what the claims rest on (§ Evidence).
7. **What is unknown.**

**Labelled exceptions** — each carries its label, since a silent gap is a floor failure:

- *your preference — no recommendation*: no fact settles it; options, no recommendation.
- *no recommendation — outside my authority*: the call belongs to the operator (a product or
  policy judgement); say why.
- A named **template** — a recurring decision with fixed options, such as a fixed
  review-round cap waiver — meets the floor by reference once the operator has seen the
  template; show it as a card the first time.

Two labels mark things that are **not decisions yet**: an **Alert** (a time-critical fact, sent
bare now because forming options would cost more than the alert is worth; the options follow)
and an **Open question** (not defined yet; listed under *Open questions*, unnumbered, until it
has options).

## Before you write: the worksheet

Answer five questions for each decision (`references/worksheet.md` has the fields and who can
supply each):

| Group | Question | It sets |
|---|---|---|
| A | Who is reading, and how warm are they? | how much to re-explain |
| B | What is at stake if it is wrong? | how it is answered |
| C | How well is it understood? | what evidence is shown; whether to offer "investigate first" |
| D | What does waiting cost? | its place in the order |
| E | What kind of ask is it? | the card's shape |

**Warm or cold.** The reader is **cold** on a decision after any of: a context compaction or
clear; a different session or repo in between; a hand-off; or **no operator turn since it was
last shown** — a card printed while the operator was away has not been seen. Otherwise warm.

**FYI after acting** (nothing to answer) is allowed only for an action that is
two-way, narrow, relied on by nobody before the operator reviews it, and inside authority the
operator already gave (an answered decision, or the task you were assigned). Never for ⚠,
never when others rely on it. When in doubt, ask.

## Levels

Three levels; the templates are in `references/rendering.md`:

- **List line** — every decision gets one: **bold number and title**, recommendation, stakes,
  basis, and its age, what it blocks and any deadline.
- **Card** — what is decided, why now, the options with their impact in italics, decide
  later, then `Rec · basis — reason · unknown`.
- **Block** — a card plus: context the reader may have lost, a section per option (*what
  happens*, *undo*, *who is affected*), and the basis drill-down with evidence links.

**The line-only rule.** A decision may stay a list line only when all of these hold: the
reader is warm; the stakes are low (two-way and narrow); the basis is strong (for a
preference: you checked that nothing depends on the choice); and either a template the
operator has already seen carries the floor, or the options converge (any of them would do).
Anything else is at least a card.

**A block** for: a ⚠ decision on first show and whenever the reader is cold; a wide one shown
to a cold reader or on a thin basis; a card the operator asked to `expand`.

**Seen.** A card or block counts as seen once the operator has taken a turn since it was
shown. One seen, with nothing changed, is not rendered again: its line ends *(shown before)*.
This holds for ⚠ too — the line keeps its ⚠ label, and `expand` brings the block back.

The higher the stakes, the more information and the slower the decision.

**⚠ one-way** marks a decision that is one-way *and* high impact. Write it `⚠ one-way`, with a
space after the symbol. A narrow one-way decision is a card with *one-way, narrow* in its
stakes slot and no ⚠.

## Order

Related decisions (same repo, same topic) form a **group**, kept together to spare the
operator context switches; a lone decision is a group of one. Groups go in this order, each
placed by its most pressing member, and the same precedence holds inside a group:

1. **Breaks before the operator is back** — a stated deadline (a lock, a lease, a due time)
   that falls before their known return; when their return is unknown, **every** stated
   deadline, soonest first. Say the deadline on the line.
2. **⚠ one-way.**
3. **Waiting cost** — what it blocks, and who else waits on it.
4. **Oldest first.**

## Several decisions in one message

The decisions close the message — after any report, push outcome or summary:

1. A heading line with the count: **Decisions** — *4 · one ⚠ one-way*.
2. Every decision above list level, **in list order**, each at its level under its bold
   number.
3. **Open questions**, if any, unnumbered.
4. The **list**, last: one line per decision, in order, so the operator can answer some or all
   of them without scrolling up. A line with nothing rendered above ends *(line only)*.
5. On a message carrying **two or more** decisions, the hint, in italics, the very last line:

   *Reply with a letter (`72: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

`expand` raises a decision one level in the next round (line → card → block); it keeps its
number and position and stays raised on later re-shows.

**A cold re-show** — after a context reset, a clear, or the operator's return — shows every
open decision at card level or above, each opening with what changed while it waited
(`references/rendering.md` § Re-show with what changed). When the store carries the card,
render the stored card; do not compose it again. **Paging:** when more than five would be
shown, render in full the first group or the first three decisions, whichever is larger, plus
every ⚠; the rest are lines ending *(expand for the card)*, and the heading says *8 open · 4
shown in full*. *(provisional — pending the operator's ruling)*

## Replies

Read replies in natural language; the words in the hint are shortcuts, never a requirement.
Details, echo wording and edge cases: `references/replies.md`.

| Reply | What you do |
|---|---|
| `N: letter`, or a choice in words | act — when the chosen option is one-way, repeat it back and act only once confirmed |
| `later [when]` | set the wake (a time, an event, or the next time you finish a piece of work and report); re-ask with what changed |
| `tell me [what]` | answer under the same number with an **Added:** line and only the lines the fact changes |
| `expand` | show it one level higher next round; on a block, say it is already at full detail |
| `dig into [what]`, or picking a priced *investigate first* option | echo it (no read-back: it acts on nothing), run the bounded investigation, cost stated up front; bring the same number back |
| `you decide` | decide, record why, report it — on ⚠ only a reversible option, said so; if the only good answer is the one-way option, repeat your recommendation and re-ask |
| `drop` | retire it; it does not come back |
| `ok N-M` | accept the recommendation for each in the range, skipping ⚠ items and items with no recommendation, and re-ask those |
| anything else that changes the question | a reframe: withdraw it and raise the new question under a new number that points back |

**Echo** every reply that is not an exact `N: letter` — one italic line, *Read as: 43 → dig
into (other callers in the access logs)* — so a misreading is caught in one turn.

**Decide later** always has a wake. With no `[when]`, it is the next time you finish a piece
of work and report — for a caller with a status report, that report; the echo says so and
asks once whether another time suits. When the decision has a deadline and the wake is not
known to fall before it, the echo warns and restates what happens at the deadline. A re-ask
carries a diff: *while it waited: …; options and recommendation unchanged | changed because …*

## Defaults

No timed default on an action. A **status-quo** default may be stated on the card — *if
unanswered: I leave X as it is and carry on with other work* — because it changes nothing.

## Evidence

Show what the claims rest on as one word and a reason — `basis: strong | partial | thin |
none — reason` — derived from the provenance of the weakest load-bearing claim, never chosen
freely, and never as a percentage (`references/evidence-basis.md`). A claim is *observed* only
when it points at a tool result you produced.

## Rulings

The operator has ruled on these; each keeps the alternative not taken, in case practice
argues for it.

- **Labelled exceptions** (2026-09-24) — the labels above. Not taken: no exceptions at all.
- **Basis word** (2026-09-24) — `strong | partial | thin | none` from the weakest load-bearing
  claim. Not taken: a confidence bucket; a step-down arithmetic over every tag.
- **No confidence percentage** (2026-09-24), shown or used for ordering. Not taken: a
  calibrated number used internally.
- **Defaults** (2026-09-24) — status-quo only; no timed action defaults. Not taken: timed
  defaults for reversible, narrow decisions.
- **Default wake** (2026-09-24) — the next time you finish a piece of work and report. Not
  taken: the next operator turn after one other exchange; events only.
- **Deadlines first** (2026-09-24) — before the operator's known return, else every stated
  deadline. Not taken: a 4-hour "likely back" window.
- **Read-back scope** (2026-09-24) — only when the chosen option is one-way. Not taken: every
  answer on a ⚠ decision.
- **⚠ blocks** (2026-09-24) — on first show and when cold. Not taken: a block in every message.
- **Placement** (2026-09-24) — decisions last, the list and hint at the tail. Not taken: the
  list first.
- **Seen** (2026-09-24) — the operator has taken a turn since it was shown. Not taken: rendered
  once.
- **Hint scope** — messages with two or more decisions. Not taken: every message that asks
  for a decision.

Still provisional, marked where it appears: **paging** on a cold re-show.

## References

- `references/worksheet.md` — the five groups, their fields, who supplies each, the two clocks
- `references/rendering.md` — the list line, card and block templates, the message layout, labels, the re-show
- `references/replies.md` — reply parsing, echo, read-back, batch, later and re-ask, reframe
- `references/evidence-basis.md` — the basis word, its tags and the rule
- `references/rationale.md` — why each rule, with its sources
- `references/gallery.md` — worked examples of every case (illustrative)
