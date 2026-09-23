# Rendering decisions

Templates for the three levels, how several decisions share one message, the order, and the
labels. Markdown only: **bold** titles, *italic* impacts and hint, `code` for reply words.
Terminals give no colour control; italics and code spans are the quiet tools.

The examples below are **illustrative**: invented, generic, not about any real project.

## Choosing the level

**The line-only rule.** A decision may stay a list line only when all of these hold:

- the reader is warm (group A);
- the stakes are low: two-way and narrow (group B);
- the basis is strong (group C);
- a template the operator has already seen carries the floor, or the options converge — any
  of them would do.

Anything else is at least a card. Raise it to a **block** when:

- it is **⚠ one-way** (always);
- it is wide and the reader is cold;
- it is wide and the basis is thin;
- the operator asked to `expand` a card.

`expand` on a line gives a card. The higher the stakes, the more information and the slower
the decision: detail is bought by stakes, never spent by default.

## List line

```
- **N Title as a question?** — rec **(x) short label** · *stakes* · basis **word** · *age, what it blocks, deadline*
```

For a decision with no recommendation, the label takes the rec slot; the stakes and basis
slots stay, since the floor needs them:

```
- **N Title as a question?** — *your preference, no rec* · *stakes* · basis **word** · *age, what it blocks*
```

- The number and title are bold together.
- Stakes slot: *reversible, narrow* · *one-way, narrow* · ⚠ one-way (for Type 1; the ⚠ is
  followed by a space) · *your preference, no rec* · *template*.
- A deadline is written as a clock time: *storage lease lapses 17:45*.
- In a message where other decisions are expanded below, a line with nothing below it ends
  *(line only)*, so the operator knows `expand` exists for it.

Example:

- **42 Clear the docs build cache?** — rec **(a) clear it** · *template: cache reset* · *reversible, narrow* · basis **strong** · *10 min old, blocks the docs build* *(line only)*

## Card

```
**N — Title as a question?**
**What:** what is decided, in plain words, ids glossed.
**Why now:** why it is up, and what it blocks.
- **(a) Option** — *what happens if chosen*
- **(b) Option** — *what happens if chosen*
- **(z) Decide later** — *what waiting costs; at a deadline, what happens then*

Rec **(a)** · basis **word** — *one-clause reason* · unknown: what isn't known, or none
```

- One line per option; its impact in italics after the dash.
- When a status-quo default applies, add: **If unanswered:** *I leave X as it is and carry on
  with other work.*
- When investigating could change the choice, add a priced option: **(c) Investigate first** —
  *about 15 minutes: read the access logs for other callers; could change the answer if …*
- A small call gets a short card. Do not pad a two-way, narrow decision with sections it does
  not need.

## Block

```
**N — Title as a question?** ⚠ one-way
**What:** …
**Why now:** … Blocks: …
**Context you may have lost:** the two or three facts a cold reader needs.

**(a) Option**
- *What happens:* …
- *Undo:* … (or: cannot be undone, because …)
- *Who is affected:* …

**(b) Option**
- *What happens:* …
- *Undo:* …
- *Who is affected:* …

**(c) Investigate first** — *time and cost; what it would settle*

**(z) Decide later** — *wake; what happens at the deadline if there is one*

Rec **(b)** · basis **partial** — *reason*
*Basis:* observed — … (link) · inferred — … · unknown — …
*I'll repeat your choice back and act only once you confirm.*
```

- A block **includes** the basis drill-down (the tags and links). `expand` on a block is
  answered: *already at full detail — `tell me [what]` for something specific?*
- A block for a wide decision that is not ⚠ drops the last line (no read-back).
- Never use the words "answer alone" as a label; the ⚠ and the read-back line carry it.

## Several decisions in one message

1. A heading line with the count: **Decisions** — *4 · one ⚠ one-way*.
2. The **list**: one line per decision, in the order below.
3. **Open questions**, if any: *(not decisions yet — each needs your framing)*, unnumbered.
4. The **detail section**: every decision above list level, rendered **in list order**, each
   at its own level, under its bold number.
5. On messages with **two or more** decisions, the hint, last, in italics:

*Reply with a letter (`72: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*

Use a real number from the list in the hint's example. A message with one decision carries no
hint: the card itself is enough.

`expand` raises one decision one level in the next round (line → card → block). It keeps its
number and its place in the order, and stays raised on later re-shows unless the operator says
otherwise. That next round shows:

1. the list, every open decision a line;
2. below it, the expanded decision at its new level;
3. any decision a rule requires at card or block that the operator has not yet seen at that
   level — a new one, one whose facts changed, or all of them if the reader went cold since.

A card or block the operator already saw, with nothing changed, is not re-rendered; its line
ends *(shown before)*.

## Order

Related decisions — same repo, same topic, one feeding another — form a **group**, kept
together so the operator is not switching context between neighbours. A lone decision is a
group of one. Order groups by their most pressing member, then apply the same precedence
inside each group:

1. **Breaks before the operator is likely back.** A stated clock deadline that falls before
   the operator's expected return when you know it, otherwise within 4 hours of being shown.
   (The rule is the operator's; the test is *provisional — pending the operator's ruling*.)
2. **⚠ one-way.**
3. **Waiting cost:** what it blocks, and how many wait on it.
4. **Oldest first.**

## Labels

| Case | Label, in the stakes slot or under the title |
|---|---|
| One-way and high impact | ⚠ one-way |
| One-way, narrow | *one-way, narrow* |
| No fact settles it | *your preference — no recommendation* |
| Not the agent's call | *no recommendation — outside my authority*, and a clause saying why |
| A recurring decision with fixed options | *template: name* — shown as a card the first time the operator meets it |
| Time-critical, options not ready | **Alert:** in bold, bare; *options follow* |
| Not defined yet | listed under **Open questions**, unnumbered |

## FYI after acting

Not a decision: no number, no options, no hint. One line, under a **Done** heading when there
are several:

- **Done: fixed a broken link in the contributing guide, on my task branch** — *two-way (one revert), nobody else uses the branch; inside the task you gave me.*

Only for actions that pass the guard in `references/worksheet.md` § E. An action that happens
unless the operator stops it is an approve ask, rendered as a card, and it waits.

## Re-show with what changed

When a decision comes back (a wake fired, a context reset, `tell me`, `dig into`), open it
with what changed since the operator last saw it, then the card or block as usual:

**62 — back, as you asked ("until the load test finishes"):** move the job queue to the new
message broker?
*While it waited (1 day): the load test finished with no lost messages; nothing else changed.
Options and recommendation unchanged.*

When the options or recommendation changed, say which and why: *Recommendation changed from
(a) vendor the font to (b) fetch it, because the CDN outage ended.*

**A cold re-show** — after a context reset, a clear, or the operator's return — shows **every
open decision at card level or above**, never as a line only: a cold reader needs the medium
or high detail view to decide without scrolling back. The list still comes first, and each
decision opens with what changed while it waited (*nothing changed* is worth saying).
