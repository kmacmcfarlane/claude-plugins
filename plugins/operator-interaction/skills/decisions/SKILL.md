---
name: decisions
description: "Put a decision to the operator so they can understand and answer it where it is shown: a content floor every decision carries, detail that scales with the stakes and with how far the operator is from the work, a set order, natural-language replies with an echo, and 'decide later' with a wake. Use whenever you are about to ask the operator to decide, choose, approve or confirm something, list open decisions, re-show decisions after a break or a context reset, relay a decision raised elsewhere, or read the operator's reply to one. Not for progress updates that ask nothing."
---

# Decisions

The goal is not to get an answer. The goal is for the operator to **understand the decision
— its context and its impact — where it is shown**, and answer it from there. A decision they
cannot act on from what is on the screen costs them a scroll back through hours of text, or a
blind answer.

The operator reads with their attention; you can juggle every dimension. So you do the
analysis (`references/worksheet.md`) and they see only its results: how much detail, which
order, how to answer.

## Critical

- **Every decision meets the floor before it is raised** (below). Without options it is not
  a decision: it is an open question, labelled as one.
- **⚠ one-way decisions** — one-way *and* high impact — are shown as a block, never ratified
  inside a batch, never handed back with `you decide`, never defaulted, and your reading of
  the operator's choice is repeated back before you act on it.
- **No timed defaults on actions.** Silence never turns into an action.
  *(provisional — pending the operator's ruling)*
- **Never show a confidence percentage**, and never use one to order decisions.
  *(provisional — pending the operator's ruling)*
- **Raise decisions as text in your message**, per this skill — not through a modal dialog
  (AskUserQuestion) unless the rules you are running under require one: a dialog cannot
  carry the list, the hint, the echo or `later`.
- **Keep the caller's numbering** when it has a counter; otherwise number from 1 in this
  session. Never reuse a number.
- **Scale the card to the decision.** A small call gets a short card; stakes buy detail.

## The floor

Every decision carries, at any level:

1. **What is decided**, in plain words. Gloss every id, hash, file or item name on first use —
   a bare `a3f9` or `7c41e0d` tells a cold reader nothing.
2. **Why now**, and what it blocks.
3. **The options**, each with its consequence — what happens to the world if it is chosen.
   Include "do nothing" when it is a real option.
4. **Decide later**, always, as its own option (`(z)`), distinct from "do nothing": it says what
   waiting costs, and when there is a deadline, what happens at the deadline.
5. **The recommendation**, or the labelled reason there is none.
6. **The basis** — what the claims rest on (`references/evidence-basis.md`).
7. **What is unknown.**

**Labelled exceptions** — each carries its label, since a silent gap is a floor failure
*(provisional — pending the operator's ruling)*:

- *your preference — no recommendation*: no fact settles it; options, no recommendation.
- *no recommendation — outside my authority*: the call belongs to the operator (a product or
  policy judgement); say why.
- **Alert:** a time-critical fact, sent bare now because forming options would cost more than
  the alert is worth; the options follow.
- **Open question**: the decision is not defined yet (framing). Listed under *Open questions*,
  unnumbered, until it has options.
- A named **template** — a recurring decision with fixed options, such as a fixed
  review-round cap waiver — meets the floor by reference once the operator has seen the
  template; show it as a card the first time.

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

**Report-after-acting** (an FYI, nothing to answer) is allowed only for an action that is
two-way, narrow, relied on by nobody before the operator reviews it, and inside authority the
operator already gave (an answered decision, or the task you were assigned). Never for ⚠,
never when others rely on it. When in doubt, ask.

## Levels

Three levels (templates and worked shapes in `references/rendering.md`):

- **List line** — every decision gets one: **bold number and title**, recommendation, stakes,
  basis, and its age, what it blocks and any deadline.
- **Card** — what is decided, why now, the options with their impact in italics, decide
  later, then `Rec · basis — reason · unknown`. Used for anything above "warm, low stakes,
  strong basis, template or options that converge".
- **Block** — a card plus: context the reader may have lost, a section per option (*what
  happens*, *undo*, *who is affected*), and the basis drill-down with evidence links. Used for
  every ⚠ decision, and for a wide one shown to a cold reader or on a thin basis.

The higher the stakes, the more information and the slower the decision.

**⚠ one-way** marks a decision that is one-way *and* high impact. Write it `⚠ one-way`, with a
space after the symbol. A narrow one-way decision is a card with *one-way, narrow* in its
stakes slot and no ⚠.

## Order

Related decisions (same repo, same topic) form a **group**, kept together to spare the
operator context switches; a lone decision is a group of one. Groups go in this order, each
placed by its most pressing member, and the same precedence holds inside a group:

1. **Breaks before the operator is likely back** — a stated clock deadline (a lock, a lease, a
   due time) that falls before their expected return when you know it, otherwise within 4
   hours of being shown. Say the deadline on the line. (The rule is the operator's; the test
   for "likely back" is *provisional — pending the operator's ruling*.)
2. **⚠ one-way.**
3. **Waiting cost** — what it blocks, and who else waits on it.
4. **Oldest first.**

## Several decisions in one message

- The **list** comes first: one line per decision, in order.
- Below it, every decision above list level is rendered **in list order**, each at its own
  level, under its bold number. A list-only decision's line ends *(line only)*.
- `expand` raises a decision one level in the next round; it keeps its number and position
  and stays raised on later re-shows.
- On a message carrying **two or more** decisions, end with the hint, in italics, numbered
  from your list:

  *Reply with a letter (`72: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

## Replies

Read replies in natural language; the words in the hint are shortcuts, never a requirement.
Details, echo wording and edge cases: `references/replies.md`.

| Reply | What you do |
|---|---|
| `N: letter`, or a choice in words | act — for ⚠, repeat the choice back and act only once confirmed |
| `later [when]` | set the wake (a time, an event, or your next check-in); re-ask with what changed |
| `tell me [what]` | re-show the same decision, same number, with that fact added |
| `expand` | show it one level higher next round; on a block, say it is already at full detail |
| `dig into [what]` | run the bounded investigation, cost stated up front; bring the same number back |
| `you decide` | decide, record why, report it — **refused on ⚠**: repeat your recommendation and re-ask |
| `drop` | retire it; it does not come back |
| `ok N-M` | accept the recommendation for each in the range, skipping ⚠ items and items with no recommendation, and re-ask those |
| anything else that changes the question | a reframe: withdraw it and raise the new question under a new number that points back |

**Echo** every reply that is not an exact `N: letter` — one italic line, *Read as: 74 → dig
into (who imports the package)* — so a misreading is caught in one turn.

**Decide later** always has a wake. With no `[when]`, the default is your next check-in (a
status report, if you make them); if you have none, ask when and state the default: the next
time the operator starts a turn after at least one other exchange. *(provisional — pending
the operator's ruling)* When the decision has a deadline and the wake is not known to fall
before it, the echo warns and restates what happens at the deadline. A re-ask carries a diff:
*while it waited: …; options and recommendation unchanged | changed because …*

## Defaults

No timed default on an action. A **status-quo** default may be stated on the card — *if
unanswered: I leave X as it is and carry on with other work* — because it changes nothing.
*(provisional — pending the operator's ruling)*

## Evidence

Show what the claims rest on as one word and a reason — `basis: strong | partial | thin |
none — reason` — derived from tags, never chosen freely, and never as a percentage
(`references/evidence-basis.md`). A claim is *observed* only when it points at a tool result
you produced.

## Provisional rules

Rules the operator has not ruled on yet. Each is marked *(provisional — pending the
operator's ruling)* where it appears; when the operator rules, the marker and its line here
go in the same edit.

- **Labelled exceptions** — the four labelled cases above. Not taken: no exceptions at all.
- **Basis word** — `strong | partial | thin | none` from tags. Not taken: a confidence bucket.
- **No confidence percentage**, shown or used for ordering. Not taken: a calibrated number used
  internally.
- **Defaults** — status-quo only; no timed action defaults. Not taken: timed defaults for
  reversible, narrow decisions.
- **Default wake** — the caller's next check-in; with no rhythm, the next turn after one other
  exchange. Not taken: events only; time only.
- **"Likely back"** — the operator's expected return when known, else 4 hours. Not taken: the
  caller's next check-in.
- **Hint scope** — messages with two or more decisions. Not taken: every message that asks
  for a decision, for adoption.

## References

- `references/worksheet.md` — the five groups, their fields, who supplies each, the three clocks
- `references/rendering.md` — the list line, card and block templates, mixed levels, order, labels
- `references/replies.md` — reply parsing, echo, read-back, batch, later and re-ask, reframe
- `references/evidence-basis.md` — the basis word, its tags and the rule table
- `references/rationale.md` — why each rule, with its sources
- `references/gallery.md` — worked examples of every case (illustrative)
