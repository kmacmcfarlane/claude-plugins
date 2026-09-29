# Rendering decisions

Templates for the three levels, how several decisions share one message, the order, and the
labels. Markdown only: **bold** titles and the recommended option, *italic* impacts and hint,
`code` for reply words.
Terminals give no colour control; italics and code spans are the quiet tools.

The examples below are **illustrative**: invented, generic, not about any real project.

## Choosing the level

The line-only rule, when a block is due, and what counts as seen are in SKILL.md § Levels;
they are not restated here. `expand` on a line gives a card, on a card a block. Detail is
bought by stakes, never spent by default.

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
- One line per decision, its own recommendation in its own rec slot: never a range or a
  group on one line (SKILL.md § Critical).
- A line for a named template may end with its fixed options, after the age slot (gallery
  example 5); they run in letter order and only the recommended one is bold.
- An ask for another round carries its justification after the basis: *if left: what the
  leftover findings would break · a round: time, quota, your attention* (SKILL.md § The
  floor).
- Stakes slot: *reversible, narrow* · *one-way, narrow* · ⚠ one-way (for Type 1; the ⚠ is
  followed by a space). The preference and authority labels take the rec slot (above); a
  template's label, *template: name*, has its own slot just before the stakes.
- A deadline is written as the absolute time in the operator's zone when you know it, with
  the relative time and when you wrote it: *storage lease lapses ~17:45 (90 min from 16:15)*.
  With the zone unknown, say which: *17:45 UTC*.
- In a message where other decisions are rendered above the list, a line with nothing above
  it ends *(line only)*, so the operator knows `expand` exists for it. A line whose card was
  seen and is unchanged ends *(shown before)*; one held back by paging ends *(expand for the
  card)*.

Example:

- **42 Clear the docs build cache?** — rec **(a) clear it** · *template: cache reset* · *reversible, narrow* · basis **strong** · *10 min old, blocks the docs build* *(line only)*

## Card

```
**N — Title as a question?**
**What:** what is decided, in plain words, ids glossed.
**Why now:** why it is up, and what it blocks.
- (a) Option — *what happens if chosen*
- **(b) Option** — *what happens if chosen*
- (z) Decide later — *what waiting costs; at a deadline, what happens then*

Rec **(b)** · basis **word** — *one-clause reason* · unknown: what isn't known, or none
```

- One line per option, in letter order; its impact in italics after the dash. Only the
  recommended option is bold — (b) above, in its own place, not moved first (SKILL.md
  § Critical). With no recommendation, none is.
- An ask for another round adds two lines after **Why now:** — **If left:** *each leftover
  finding, and what it would break* and **A round costs:** *the time, the quota, and your
  attention: this answer, and another if the round does not settle it* (SKILL.md § The
  floor).
- When a status-quo default applies, add: **If unanswered:** *I leave X as it is and carry on
  with other work.*
- When investigating could change the choice, add a priced option: (c) Investigate first —
  *about 15 minutes: read the access logs for other callers; could change the answer if …*
- A small call gets a short card. Do not pad a two-way, narrow decision with sections it does
  not need.

## Block

```
**N — Title as a question?** ⚠ one-way
**What:** …
**Why now:** … Blocks: …
**Context you may have lost:** the two or three facts a cold reader needs.

(a) Option
- *What happens:* …
- *Undo:* … (or: cannot be undone, because …)
- *Who is affected:* …

**(b) Option**
- *What happens:* …
- *Undo:* …
- *Who is affected:* …

(c) Investigate first — *time and cost; what it would settle*

(z) Decide later — *wake; what happens at the deadline if there is one*

Rec **(b)** · basis **partial** — *reason*
*Basis:* observed — … (link) · inferred — … · unknown — …
*If you pick (a), I'll repeat it back and act only once you confirm: it can't be undone.*
```

- The options follow the card's rule: letter order, and only the recommended option's
  heading bold. The opening lines run **What:**, **Why now:**, **Context you may have
  lost:**, then a round ask's **If left:** and **A round costs:**.
- A block **includes** the basis drill-down (the tags and links). `expand` on a block is
  answered: *already at full detail — `tell me [what]` for something specific?*
- The read-back line (⚠ blocks only) names the one-way option(s). A block for a wide
  decision that is not ⚠ drops it.
- Write every option's *Undo* line plainly — it is what decides whether an answer is read
  back (`references/replies.md`).
- Never use the words "answer alone" as a label; the ⚠ and the read-back line carry it.

## Several decisions in one message

The layout is SKILL.md § Several decisions in one message: the decisions close the message,
the rendered cards and blocks first, the compact list and the hint last. In template form:

```
**Decisions** — *4 · one ⚠ one-way*

**41 — …card…**
**43 — …block…** ⚠ one-way

**Open questions** *(not decisions yet — each needs your framing)*
- …

- **41 …list line…**
- **43 …list line…**
- **44 …list line…** *(line only)*
- **42 …list line…** *(shown before)*

*Reply with a letter (`41: a`) or in your own words · `later [when]` · `tell me [what]` · `expand` · `dig into [what]` · `you decide` · `drop`*
```

Use a real number from the list in the hint's example. A message with one decision carries no
hint and no separate list: the card itself is enough.

In a turn that also reports work — a status report, a push outcome, a summary for others —
all of that comes first and the decisions block is the last thing written.

After an `expand`, the next round renders the expanded decision at its new level, plus any
decision a rule requires above list level that the operator has not seen at that level (new,
changed, or the reader went cold). Everything else is a list line.

## Order

The precedence is SKILL.md § Order. Two notes on applying it: a group is placed by its most
pressing member and kept together, the same precedence holding inside it; and a deadline
decision placed first "because the return is unknown" costs nothing if the operator is back
sooner — both get answered — while one placed low can lose the lease.

## Labels

| Case | Label | Where it goes |
|---|---|---|
| One-way and high impact | ⚠ one-way | the stakes slot; after the title on a card or block |
| One-way, narrow | *one-way, narrow* | the stakes slot; after the title on a card |
| No fact settles it | *your preference — no recommendation* | the rec slot (*your preference, no rec*); after the title on a card |
| Not the agent's call | *no recommendation — outside my authority*, and a clause saying why | the rec slot; after the title on a card, the why on its own line |
| A recurring decision with fixed options | *template: name* — shown as a card the first time the operator meets it | its own slot, before the stakes |
| Time-critical, options not ready (not a decision yet) | **Alert:** in bold, bare; *options follow* | its own line, in place of a card |
| Not defined yet (not a decision yet) | listed under **Open questions**, unnumbered | the *Open questions* section |

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

**From the store.** When the caller's store keeps the card (the floor's fields under the
decision's record, with its raised-at time), a re-show renders that stored card and adds
only the *while it waited* line — read from the caller's record, never from memory — and a
gloss for any id the stored text left bare. Composing the card again from memory can shift
the letters or the recommendation, and the operator would answer an (a) that is not the (a)
they read. Before rendering, check the stored card against now: a floor field it lacks, or
one events have made false — a *why now* that no longer holds, a basis word the rule
(`references/evidence-basis.md`) no longer gives — is a revision. The caller stores the
revised card (a missing field no record holds reads *not recorded*), and *while it waited*
says what changed. When the options or recommendation really changed, say which and why, and
the caller stores the new card.

**A cold re-show** — whenever the reader is cold (SKILL.md § Before you write) — shows each
open decision the reader is cold on at card level or above, never as a line only except as
paged (SKILL.md § Levels, the line-only rule), each opening with what changed while it
waited (*nothing changed* is worth saying). A deferred decision whose wake has not come is a
card too, opening with its wake: *deferred until the release; no answer needed before then*;
it leaves its group and goes last, in the cards and the list alike, so paging reaches it
last. Open
questions still open are listed under *Open questions*. A cold re-show's heading has one
form: **Decisions** — *N open · shown again after a context reset · M shown in full · one ⚠
one-way*, naming what made the reader cold, and dropping *M shown in full* when nothing is
paged and the ⚠ part when there is none. With more than five, SKILL.md's paging rule applies
*(provisional — pending the operator's ruling)*: the rest are lines ending *(expand for the
card)*.
