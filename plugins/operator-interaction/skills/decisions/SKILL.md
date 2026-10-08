---
name: decisions
description: "Put a decision to the operator so they can understand and answer it where it is shown: a content floor every decision carries, its impact shown in every view, detail that scales with the stakes and with how far the operator is from the work, a set order, natural-language replies with an echo, and 'decide later' with a wake. Use whenever you are about to ask the operator to decide, choose, approve or confirm something, list open decisions, re-show decisions after a break or a context reset, read the operator's reply to one, or judge whether an action may be taken and reported afterwards instead of asked about first. Not for progress updates that ask nothing."
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
- **Every view shows the decision's impact**, at its size (§ Levels): the effect on the
  smallest, more facets as space grows. No list line, card, block or caller's row without it.
- **⚠ one-way decisions** — one-way *and* high impact — are never ratified inside a batch and
  never defaulted. Shown as a block the first time and whenever the reader is cold. On a ⚠
  decision, an answer that picks a **one-way option** is repeated back and acted on only once
  confirmed, and `you decide` never takes the one-way option.
- **No timed defaults on actions.** Silence never turns into an action. A **status-quo**
  default, which changes nothing, may be stated on the card (`references/replies.md`
  § Defaults).
- **Never show a confidence percentage**, and never use one to order decisions.
- **Options in letter order.** (a), (b), (c) …, with decide later last as (z). The
  recommended option keeps its letter and its place and is the one option in **bold**; it
  is never moved first. With no recommendation, no option is bold.
- **Every decision shows its own recommendation where the operator reads it** — its own
  list line, and its own card or block. Never fold several decisions into one line or card
  that lists their recommendations together (`92–95 — …`), however related: a group
  (§ Order) keeps them side by side, each one whole.
- **Raise decisions as text in your message**, per this skill — not through a modal dialog
  (AskUserQuestion) unless the rules you are running under require one: a dialog cannot
  carry the list, the hint, the echo or `later`.
- **The decisions come last in the message** — the last thing written before you stop, after
  any follow-up in the same turn — the list and the hint at the very end, where the
  operator's eye is when you stop.
- **Keep the caller's numbering** when it has a counter; otherwise number from 1 in this
  session. Never reuse a number.
- **Scale the card to the decision.** A small call gets a short card; stakes buy detail.

## The floor

Every decision carries, at any level:

1. **What is decided**, in plain words. Gloss every id, hash, file or item name on first use —
   a bare `a3f9` or `7c41e0d` tells a cold reader nothing. Name items in plain words, the id
   at most a trailing tag: load the `plain-names` skill (same plugin) and follow it.
2. **Its impact**, in five facets in this order: **Effect**, **Wait**, **Reach**, **Undo**,
   **Cost** (`references/rendering.md` § Impact). Written when it is raised, as the Impact
   line, and stored with the card where the caller keeps one.
3. **Why now**, and what it blocks (the Wait facet). When nothing forces it, say so —
   *why now: nothing forces it; raised because the audit turned it up* — and *blocks:
   nothing* is an honest answer.
4. **Why ask** — why it comes to the operator instead of being decided and shown after: what
   would go wrong if you took your recommendation alone (with no recommendation, why the call
   is not yours). It opens with the decision's **class** when the caller names classes of
   decision. A question that cannot fill it is decided alone when the FYI rule (§ Before you
   write) allows; otherwise it is asked.
5. **The options**, each with its consequence — what happens to the world if it is chosen.
   Include "do nothing" when it is a real option.
6. **Decide later**, always, as its own option (`(z)`), distinct from "do nothing": it says what
   waiting costs, and when there is a deadline, what happens at the deadline.
7. **The recommendation**, or the labelled reason there is none.
8. **The basis** — what the claims rest on (§ Evidence).
9. **What is unknown.**

**An ask for another round** — a review-round cap waiver, or any ask for one more round of
work, review or investigation — also carries its **justification**, or the operator has
nothing to weigh it by:

- **If left:** each leftover finding, and what it would break if the work stops here.
- **A round costs:** the time, the quota, and the operator's attention — this answer, and
  another if the round does not settle it.

High impact at a modest cost justifies the round; the recommendation's reason says which
way it falls.

**Labelled exceptions** — each carries its label, since a silent gap is a floor failure:

- *your preference — no recommendation*: no fact settles it; options, no recommendation.
- *no recommendation — outside my authority*: the call belongs to the operator (a product or
  policy judgement); say why.
- A named **template** — a recurring decision with fixed options, such as a fixed
  review-round cap waiver — meets the floor by reference once the operator has seen the
  template; show it as a card the first time. Only the fixed options ride by reference: an
  ask for another round shows its justification every time, since what is left and what a
  round costs change each time. Only the caller names templates, with their options; a
  decision whose options differ is not that template, and a caller that names none has
  none.

Two labels mark things that are **not decisions yet**: an **Alert** (a time-critical fact,
sent bare because forming options would cost more than it is worth; the options follow) and
an **Open question** (listed under *Open questions*, unnumbered, until it has options).

## Before you write: the worksheet

Answer five questions for each decision (`references/worksheet.md` has the fields and who can
supply each):

| Group | Question | It sets |
|---|---|---|
| A | Who is reading, and how warm are they? | how much to re-explain |
| B | What is at stake if it is wrong? | how it is answered; the Undo and Reach facets |
| C | How well is it understood? | what evidence is shown; whether to offer "investigate first" |
| D | What does waiting cost? | its place in the order; the Wait facet |
| E | What kind of ask is it? | the card's shape |

**Warm or cold.** The reader is **cold** on a decision after any of: a context compaction or
clear; a different session or repo in between; a hand-off; or **no operator turn since it was
last shown** — a card printed while the operator was away has not been seen. Otherwise warm.

**Shown and seen, recorded.** Where the caller keeps a record, the session that displays a
decision records each showing at card or block level as it goes out (the time and where:
chat, page or doc), and the operator turn or page or doc answer that sees it. A list line, a
tag-size mention or an echo is not a showing. The first and the last showing are kept, and
the caller's rules give the record's shape and any hold on it. In your own session the
transcript answers the warm-or-cold test; a reader without it (after a reset, another
session, a collector) reads it from the record: no showing recorded, or none seen since the
last showing, is cold.

**FYI after acting** (nothing to answer) is allowed only for an action that is
two-way, narrow, relied on by nobody before the operator reviews it, and inside authority the
operator already gave (an answered decision, the task you were assigned, or a decide-alone
class the caller's rules define). Never for ⚠, never when others rely on it. When in doubt,
ask.

**Decided alone is recorded and shown.** Each choice made under the FYI rule gets a record
where the caller keeps one and a `Done:` line the next time you report, in a *Done alone*
group; an objection reopens or undoes it (`references/rendering.md` § FYI after acting).

## Levels

Smallest to largest, each showing more of the impact in facet order (templates in
`references/rendering.md`):

- **Tag size** — `46 (→ effect)`, for a caller's tightest views (a row of open items, a
  report line naming numbers, a page's summary list); never in place of a level.
- **List line** — every decision gets one: **bold number and title**, recommendation,
  `→` Effect, `later:` Wait, its class when the caller names classes, ⚠ one-way when it is,
  basis, its age and any deadline; a round ask, its justification; a line-only decision, its
  why ask.
- **Card** — an **Impact:** line under the title, then what is decided, why now, why ask
  (and a round ask's justification), the options with their impact in italics, decide
  later, then `Rec · basis — reason · unknown`. Its **Context:** cue (where you left it ·
  what you decide now) is written for every decision when it is raised, and shown to a cold
  reader (with nowhere to keep it, at the first showing too).
- **Block** — a card whose Impact line becomes a table (a row per option plus a Wait row),
  plus context the reader may have lost and the basis drill-down with evidence links.

**The line-only rule.** A decision may stay a list line only when all of these hold: the
reader is warm; the stakes are low (two-way and narrow); the basis is strong (for a
preference: you checked that nothing depends on the choice); and either a template the
operator has already seen carries the floor, or the options converge (any of them would do).
Anything else is at least a card.

**A block** for: a ⚠ decision on first show and whenever the reader is cold; a wide one shown
to a cold reader or on a thin basis; a card the operator asked to `expand`.

**Seen.** A card or block counts as seen once the operator has taken a turn since it was
shown — the turn the caller's record of shown and seen stores, where it keeps one. One
seen, with nothing changed, is not rendered again: its line ends *(shown before)*.
This holds for ⚠ too — the line keeps its ⚠ label, and `expand` brings the block back.

The higher the stakes, the more information and the slower the decision.

**⚠ one-way** marks a decision that is one-way *and* high impact. Write it `⚠ one-way`, with a
space after the symbol; its Undo states the one-way part. A narrow one-way decision is a card
with no ⚠: its Undo says it cannot be undone.

## Order

Related decisions (same repo, same topic) form a **group**, kept together to spare the
operator context switches; a lone decision is a group of one. Groups go in this order, each
placed by its most pressing member, and the same precedence holds inside a group:

1. **Breaks before the operator is back** — a stated deadline (a lock, a lease, a due time)
   that falls before their known return; when their return is unknown, **every** stated
   deadline, soonest first. Say the deadline on the line.
2. **⚠ one-way.**
3. **Waiting cost** — what it blocks, and who else waits on it.
4. **Oldest first**; a tie goes to the lower number.

On a cold re-show, a deferred decision whose wake has not come goes last
(`references/rendering.md` § Re-show with what changed).

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

To put several decisions on a page the operator answers by clicking, instead of in the
message, use the `decision-page` skill (same plugin); the cards it renders are this skill's.

`expand` raises a decision one level in the next round (line → card → block); it keeps its
number and position and stays raised on later re-shows.

**A cold re-show** — whenever the reader is cold on any open decision (§ Before you write) —
shows each open decision the reader is cold on at card level or above, each opening with what
changed while it waited, the impact included (`references/rendering.md` § Re-show with what
changed, which also gives its heading). When the store carries the card, render the stored
card, checked and repaired as that section says; do not compose it again. **Paging:** when more than five
would be shown, render in full whole groups, in list order, until at least three decisions
are shown, plus every ⚠; the rest are lines ending *(expand for the card)*, and the heading
says how many are shown in full. *(provisional — pending the operator's ruling)*

## Replies

Read replies in natural language; the words in the hint are shortcuts, never a requirement.
Details, echo wording and edge cases: `references/replies.md`.

| Reply | What you do |
|---|---|
| `N: letter`, or a choice in words | act — on a ⚠ decision, when the chosen option is one-way, repeat it back and act only once confirmed |
| `later [when]` | set the wake (a time, an event, or the next time you finish a piece of work and report); re-ask with what changed |
| `tell me [what]` | answer under the same number with an **Added:** line and only the lines the fact changes |
| `expand` | show it one level higher next round; on a block, say it is already at full detail |
| `dig into [what]`, or picking a priced *investigate first* option | echo it (no read-back: it acts on nothing), run the bounded investigation, cost stated up front; bring the same number back |
| `you decide` | decide, record why, report it — on ⚠ only a reversible option, said so; if the only good answer is the one-way option, repeat your recommendation and re-ask |
| `drop` | retire it; it does not come back |
| `ok N-M` | accept the recommendation for each in the range, skipping ⚠ items and items with no recommendation, and re-ask those |
| anything else that changes the question | a reframe: withdraw it and raise the new question under a new number that points back |
| one message answering several, with questions or requests mixed in | answer every question inside it in words, also when an action is the fix; echo each part that is not an exact `N: letter` (`references/replies.md` § A message with several replies) |

**Echo** every reply that is not an exact `N: letter` — one italic line, *Read as: 43 → dig
into (other callers in the access logs)* — so a misreading is caught in one turn.

**Decide later** always has a wake. With no `[when]`, it is the next time you finish a piece
of work and report — for a caller with a status report, that report; the echo says so and
asks once whether another time suits. When the decision has a deadline and the wake is not
known to fall before it, the echo warns and restates what happens at the deadline. A re-ask
carries a diff: *while it waited: …; options and recommendation unchanged | changed because …;
impact unchanged | what changed in it*

## Evidence

Show what the claims rest on as one word and a reason, `basis: strong | partial | thin |
none — reason`, derived from the weakest load-bearing claim's provenance, never chosen
freely, never as a percentage (`references/evidence-basis.md`). A claim is *observed* only
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
- **Option order** (2026-09-29) — (a), (b), (c) … (z), the recommended option in bold in
  its own place. Not taken: the recommended option moved first, as a modal dialog lists it.
- **A recommendation on every decision** (2026-09-29) — shown on the decision's own line
  and card, never folded into a line or card shared with others. Not taken: one grouped
  entry for related decisions, listing their recommendations together.
- **Round asks justify themselves** (2026-09-29) — what the leftover findings would break,
  and what the round costs in time, quota and attention. Not taken: a bare waiver ask whose
  template carries the floor by reference.
- **Every ask justifies itself** (2026-09-30) — *why ask* on every decision, opening with its
  class when the caller names classes. Not taken: the justification on round asks only.
- **Resume cue** (2026-09-30) — a **Context:** cue stored when raised, shown to a cold reader
  under *while it waited*. Not taken: every cold decision as a block.
- **Shown after** (2026-09-30) — what a caller's rules let you decide alone is recorded and
  shown as a `Done:` line in a *Done alone* group, never left unseen. Not taken: a record seen
  only on request.
- **Impact in every view** (2026-10-06) — five facets in one order, the smallest view
  showing the effect, each larger view adding facets; the Impact line stored at raise and
  read by every view; Undo replaces the stakes words, Wait the *blocks* slot. Not taken:
  lines with the effect only, no wait; no stored line, each view deriving impact from the
  options each time.
- **Shown record** (2026-10-07) — the first and the last showing of each decision are
  recorded, with the turn that sees each, written by the session that displays it. Not
  taken: the last showing only (last-write-wins).

Still provisional, marked where it appears: **paging** on a cold re-show.

## References

- `references/worksheet.md` — the five groups, their fields, who supplies each, the two clocks
- `references/rendering.md` — the impact facets and Impact line, the tag size, list line, card and block templates, the message layout, labels, the re-show
- `references/replies.md` — reply parsing, echo, read-back, batch, later and re-ask, reframe
- `references/evidence-basis.md` — the basis word, its tags and the rule
- `references/rationale.md` — why each rule, with its sources
- `references/gallery.md` — worked examples of every case (illustrative)
