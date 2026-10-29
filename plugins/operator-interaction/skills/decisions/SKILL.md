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
out → read it cold (`references/worksheet.md` § The cold read) before it goes out.

## Critical

- **Every decision meets the floor before it is raised** (below). Without options it is not
  a decision: it is an open question, labelled as one.
- **Every view shows the decision's impact**, at its size (§ Levels): the recommended
  option's effect on the smallest (with no recommendation, each option's), more facets as
  space grows. No list line, card, block or caller's row without it.
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
  session. Never reuse a number. Every decision, sub-decisions and follow-up decisions included,
  takes its own plain integer: never `8b` or `8.1`, since `8b` reads as option (b) of 8, as in
  `72: a`; option letters stay the only lettered thing, and a dependent follow-up says so on its
  dependency line, second on its card, read from the caller's stored dependency where it
  keeps one (*depends: only if 9 (name) is (a)*).
- **Scale the card to the decision.** A small call gets a short card; stakes buy detail.

## The floor

Every decision carries, at any level:

1. **What is decided**, in plain words, and for a set, every item it acts on, one bullet each
   under **What:**, never a count alone (`references/rendering.md` § Card). Gloss every id, hash, file or item name on first use —
   a bare `a3f9` or `7c41e0d` tells a cold reader nothing. Define every term the operator may
   not know (a source document's label or number, an acronym, a term of art) where it first
   appears in each view, preferring the words it stands for; on a card or block, its
   **Context:** is where the terms are introduced. A source's own label goes first with its
   short name, *F7 (oversize upload)* (`references/rendering.md` § Source labels). Name
   items in plain words, the id at most a trailing tag: load the `plain-names` skill (same
   plugin) and follow it.
2. **Its impact**, in facets: **Wait**, **Reach**, **Undo**, **Cost** for the decision, and
   each option's own **Effect** (with its reach, undo and cost) (`references/rendering.md`
   § Impact). Effect and Reach are about the thing the work builds, never the process (that
   is Wait); Undo only where an option is one-way or costly. Written when it is raised, as
   the Impact line, which carries no effect: each option says its own. Stored with the card
   where the caller keeps one; each option's own impact is stored with the option.
3. **Why now**, and what it blocks (the Wait facet). When nothing forces it, say so —
   *why now: nothing forces it; raised because the audit turned it up* — and *blocks:
   nothing* is an honest answer.
4. **Why ask** — why it comes to the operator instead of being decided and shown after: what
   would go wrong if you took your recommendation alone (with no recommendation, why the call
   is not yours). It opens with the decision's **class** when the caller names classes of
   decision. A question that cannot fill it is decided alone when the FYI rule (§ Before you
   write) allows; otherwise it is asked. On a card, why now and why ask sit in its
   Background fold, closed, its summary the first sentence of why now; a block shows it open
   (`references/rendering.md` § Folds).
5. **The options**, each with its consequence — what happens to the world if it is chosen,
   by what mechanism, to whom, before and after — and its own reach, undo and cost where
   they apply.
   Include "do nothing" when it is a real option.
6. **Decide later**, always, as its own option (`(z)`), distinct from "do nothing": it says what
   waiting costs, and when there is a deadline, what happens at the deadline.
7. **The recommendation**, or the labelled reason there is none.
8. **The basis** — what the claims rest on (§ Evidence) — and the **assumptions** the
   recommendation rests on, each with its **tripwire**, the sign that would change the call;
   shown in the card's ▸ Assumptions fold, closed, its summary the basis word and their count
   (`references/rendering.md` § Folds).
9. **What is still open**: the open questions, one line each, shown in the card's
   ▸ Open questions fold (`references/rendering.md` § Folds); with none open, no fold.
10. **What it takes to act**: when an option asks the operator to do something beyond
    answering, the card carries everything they need to do it now, as its **To act on (x):**
    part (`references/rendering.md` § Card).
11. **Its scope**, wherever the work states requirements: *required* with the criterion it
    rests on, *shapes the work* with what it decides, or *outside the criteria*, on its
    **Scope:** line (`references/rendering.md` § Card); with no stated requirements, no line.
12. **Its likelihood**, on a risk decision (its options trade against a failure that may or
    may not happen): **Likelihood:**, naming the event, with the strongest concrete fact (an
    observed count with its window and source, else another fact, else the evidence there is
    and what would settle it; never a bare *no data*, never an estimate), and
    **Best response?:**, whether acting here is the most important response to that failure
    (`references/evidence-basis.md` § Keep it apart from likelihood).

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

Answer six questions for each decision (`references/worksheet.md` has the fields and who can
supply each):

| Group | Question | It sets |
|---|---|---|
| A | Who is reading, and how warm are they? | how much to re-explain |
| B | What is at stake if it is wrong? | how it is answered; the Undo and Reach facets |
| C | How well is it understood? | what evidence is shown; whether to offer "investigate first" |
| D | What does waiting cost? | its place in the order; the Wait facet |
| E | What kind of ask is it? | the card's shape |
| F | What does the operator need in hand? | its terms and its **To act on** part |

**Warm or cold.** The reader is **cold** on a decision after any of: a context compaction or
clear; a different session or repo in between; a hand-off; or **no operator turn since it was
last shown** — a card printed while the operator was away has not been seen. Otherwise warm.

**Shown and seen, recorded.** Where the caller keeps a record, the session that displays a
decision records each showing at card or block level as it goes out (the time and where:
chat, page or doc), and the operator turn or page or doc answer that sees it. A list line, a
tag-size mention or an echo is not a showing. The caller's rules give the record's shape and
any hold on it.

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

- **Tag size** — `46 (→ (a) effect)`, the recommended option's effect, its letter first, for
  a caller's tightest views (a row of open items, a report line naming numbers, a page's
  summary list); never in place of a level.
- **List line** — every decision gets one, with no Context: **bold number and title**,
  recommendation, `→` that option's effect (with no recommendation, each option's), `later:`
  Wait, its class when the caller names classes, ⚠ one-way when it is, basis, its age and
  any deadline; a round ask, its justification; a line-only decision, its
  why ask.
- **Card** — in the answer page's order (the v5 order): the title; then the TLDR, one or two
  terse bullets saying what is decided and what rides on it, never the recommendation; then,
  on a decision that waits on another's answer, its dependency line, `*depends: only if 41
  (name) is (a) or (c), and after 47 (name) is answered, whatever its answer*`, read from the
  caller's stored dependency where it keeps one; then **Context:**, then **What:** (what
  is decided, and a set's items one bullet each), then, on a decision raised from a finding,
  **Finding:** (its label and short name, its title, where it lives, how it happens, and its
  excerpt in a fenced block), then, where the work states requirements, **Scope:** (*required*
  and the criterion, *shapes the work* and what, or *outside the criteria*), then, on a risk
  decision, **Likelihood:** and **Best response?:**; then the ▸ Open questions fold line when
  anything is open, then the ▸ Assumptions fold line (the basis word and the assumptions with
  their tripwires); then an **Impact:** line, with no effect of its own; then the options,
  each with its own impact (effect, reach, a one-way or costly option's `⚠ undo:`, cost) on
  an italic line under it and its `*pros: …*` and `*cons: …*` lines under that, and decide
  later; then any **To act on (x):** part, a round ask's justification and any **If
  unanswered:** line (the page puts these round lines above its options, and each To act
  on under its own option; chat puts both after the options; on the page a decision the
  dependency line names that is on the page opens its card on a click); then the ▸ Background fold line (why now and
  why ask), then, on a card whose decision rests on material it can only name, the
  ▸ Attached fold line (their count and titles), and last, on a card that weighed
  alternatives it does not offer, the ▸ Rejected alternatives fold line (their count and
  titles). A part with nothing to say is left out; what is shown keeps this order. There is
  no Rec line, the recommended option being the bold one. Its **Context:** is one or two
  sentences, the page's summary size: the terms the card uses, then the resume cue (where
  you left it · what you decide now). It is written for every decision when it is raised,
  stored with the card where the caller keeps one, and shown every time the card is shown,
  warm reader or cold (`references/rendering.md` § Context).
- **Block** — the card with every fold open (▾), in the card's order: the title, the TLDR, the
  dependency line when there is one, then **Context:** at the page's medium size, a bullet list that adds the context the reader
  may have lost; What, Finding, Scope and Likelihood as on a card; the Open questions fold
  open, then the Assumptions fold open with its basis drill-down and evidence links; the
  Impact line, followed by a table (a row per option, its effect, reach, undo and cost, plus
  a Wait row) in place of the options' impact lines;
  then each option's *plan in brief:* and its `Pros | Cons` table; then any To act on part
  and round lines; then the Background fold
  open, why now and why ask on two lines, then any Attached fold open, each attachment's bold
  head line over its body, then any Rejected alternatives fold open, each title in bold over
  its reasons as bullets; and, on a ⚠ block, the read-back line last.

**The line-only rule.** A decision may stay a list line only when all of these hold: the
reader is warm; the stakes are low (two-way and narrow); the basis is strong (for a
preference: you checked that nothing depends on the choice); and either a template the
operator has already seen carries the floor, or the options converge (any of them would do);
and no option asks the operator to act. Anything else is at least a card.

**A block** for: a ⚠ decision on first show and whenever the reader is cold; a wide one shown
to a cold reader or on a thin basis; a card the operator asked to `expand`.

**Seen.** A card or block counts as seen once the operator has taken a turn since it was
shown — the turn the caller's record of shown and seen stores, where it keeps one. One
seen, with nothing changed, is not rendered again: its line ends *(shown before)*.
This holds for ⚠ too — the line keeps its ⚠ label, and `expand` brings the block back.

The higher the stakes, the more information and the slower the decision.

**⚠ one-way** marks a decision that is one-way *and* high impact. Write it `⚠ one-way`, with a
space after the symbol. An option one-way or costly to undo carries `⚠ undo:`, which marks
the option, never the decision; a narrow one-way decision is a card with no ⚠ label. An
option with no undo shown is reversible at little cost.

## Order

Related decisions (same repo, same topic) form a **group**, kept together to spare the
operator context switches; a lone decision is a group of one. A group the caller stores is the
group, and related decisions are the rule only where it stores none; a stored group goes by
its plain name, its id never shown (`references/rendering.md` § A bundle as a group). A **bundle** whose items need
different answers is a group of whole item cards (`references/rendering.md` § A bundle as a
group); when one answer fits every item, it stays one card. Groups go in this order, each
placed by its most pressing member:

1. **Breaks before the operator is back** — a stated deadline (a lock, a lease, a due time)
   that falls before their known return; when their return is unknown, **every** stated
   deadline, soonest first. Say the deadline on the line.
2. **⚠ one-way.**
3. **Waiting cost** — what it blocks, and who else waits on it.
4. **Oldest first**; a tie goes to the lower number.

**Inside a group, dependents come after what they depend on:** each decision goes after every
decision it depends on in the same group, and among those free to go, the same precedence
holds. The members of a dependency cycle (a work-item store's lint flags one) are ordered among
themselves by the precedence alone; their other dependencies still hold. Across groups the order is the precedence's (`references/rendering.md`
§ Order). A group's heading shows its decisions' numbers after its name, runs of consecutive
numbers as ranges (*· 233–239, 242–250*), so the operator sees where the numbers jump; the
order itself is unchanged (`references/rendering.md` § A bundle as a group).

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
A **findings-style set** (raised from a review, an audit, a test run or a scan) goes to chat
by default, each card with its **Finding:** part; the page shows each finding too (its Finding
part, the excerpt as a code block), so offer it for such a set as for any other.

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
| a source label for the number (`F7: a`) | read it as the decision whose title carries that label, and echo both (`references/replies.md`) |
| `later [when]` | set the wake (a time, an event, or the next time you finish a piece of work and report); re-ask with what changed |
| `tell me [what]` | answer under the same number with an **Added:** line and only the lines the fact changes; `tell me (x)` answers with that option's view: its *plan in brief:*, its `Pros \| Cons` table, then its facet line |
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

What the operator has ruled, each with the alternative not taken, and the parts that were
designs made in review: `references/rulings.md` — read it before proposing a change to any
rule here or offering an alternative a ruling did not take. Still provisional, marked where
it appears: **paging** on a cold re-show.

## References

- `references/worksheet.md` — the six groups, their fields, who supplies each, the two clocks, the Context and the Impact line, the cold read
- `references/rendering.md` — the impact facets and Impact line, the Context section, the tag size, list line, card and block templates, an option's view (`tell me (x)`), the message layout, a bundle as a group, labels, source labels, the re-show
- `references/replies.md` — reply parsing, echo, read-back, batch, later and re-ask, reframe
- `references/evidence-basis.md` — the basis word, its tags and the rule
- `references/rationale.md` — why each rule, with its sources
- `references/rulings.md` — what the operator has ruled, each with the alternative not taken; designs made in review marked
- `references/gallery.md` — worked examples of every case (illustrative)
- `references/card-record.md` — the card as data, `decision-card/5`: its fields, what each requires, an option, the levels
- `references/legacy-cards.md` — reading a card with no format: the reader rules, the maps to the record, the older eras
