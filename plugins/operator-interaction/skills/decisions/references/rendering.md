# Rendering decisions

The impact every view carries, the Context every card and block carries, the templates
for each view (tag size, list line, card, block), how several decisions share one message, the order, and the labels. Markdown only:
**bold** titles and the recommended option, *italic* impacts and hint, `code` for reply words.
Terminals give no colour control; italics and code spans are the quiet tools.

The examples below are **illustrative**: invented, generic, not about any real project.

## Choosing the level

The line-only rule, when a block is due, and what counts as seen are in SKILL.md § Levels;
they are not restated here. `expand` on a line gives a card, on a card a block. Detail is
bought by stakes, never spent by default.

## Impact

Every view of a decision shows its impact, in one vocabulary of five facets, always in this
order:

| Facet | What it says | Written |
|---|---|---|
| **Effect** | what the decision changes and settles, across all its options, favouring none | `→ effect` |
| **Wait** | what waiting costs, and what it blocks | `later: …` |
| **Reach** | who or what is affected: the operator, sessions, which repos, the public | `reach: …` |
| **Undo** | how it is reversed, or that it is one-way and why | `undo: …` |
| **Cost** | time, money, quota, the operator's attention | `cost: …` |

The smallest view shows Effect; each larger view adds facets in that order:

| View | Impact shown |
|---|---|
| Tag size | Effect |
| List line | the recommended option's effect (with no recommendation, the Effect) · Wait |
| Card | an **Impact:** line, Effect · Wait · Reach · Undo; under each option, its own impact line: effect · reach · undo · cost |
| Block | the card's **Impact:** line, then the Impact table: a row per option, then a Wait row; columns Effect, Reach, Undo, Cost |

- Plain words, about the world, for the operator. **Effect covers the decision across all
  its options, favouring none**, as the answer page's does (the `decision-page` skill's
  `references/cards-schema.md`, `impact`): what the decision changes and settles whichever
  option is taken — *sets which units the dashboard shows* — or, where the options' outcomes
  differ, each in a few words: `→ *(a) sizes match the OS tools; (b) sizes match the bill*`.
  Write it from the options' own effects (each option's impact line), never from the
  recommendation alone; the recommendation is marked by the bold option and the Rec line,
  not by the Effect. At tag size it stands alone in under about 10 words. With no
  recommendation it reads the same way.
- **Each option's impact** is its own: on a card, an italic line under the option, in facet
  order, `*→ effect · reach: … · undo: … · cost: …*`, each facet after the first labelled so
  Reach is never read as more Effect. A facet that is empty or does not apply to that option
  (nobody beyond the work, nothing to undo, no cost worth naming) is left out, so a small
  option's line may be its effect alone. An Undo that says the option cannot be undone, or
  only at real cost, is never left out, since it decides the read-back
  (`references/replies.md`); on a ⚠ decision every option's line carries its undo, as the
  block's table does. (z) keeps its one line: what waiting costs. A block carries the same
  facets in its table, a row per option. A list line carries none: it stays terse.
- **Undo replaces the old stakes words** (*reversible, narrow*, *one-way, narrow*): it says
  how, *undo: one edit*, or why not, *undo: none — a deleted snapshot is gone*. The
  ⚠ one-way label stays on a decision that is one-way *and* high impact; its Undo states the
  one-way part.
- **The Impact line's Undo names the one-way option's undo whenever any option is one-way**,
  not only the recommended option's: *undo: (a) remove the redirect lines; (b) none — the
  lost ranking cannot be won back*. A line whose Undo reads fully reversible on a decision
  with a one-way option misleads.
- **Wait absorbs the old *what it blocks* slot**: *later: the docs build stays blocked*. At a
  deadline, it says what happens then.
- **Cost** lives on each option's impact line and the block's table; the Impact line carries
  it only when it is what the operator weighs.
- On the Impact line and in the table, a facet no record holds reads `not recorded`; a facet
  that does not apply, `—`. On an option's impact line, one that does not apply is left out
  and `not recorded` stays. Never invent one at render time.

**The Impact line** is written when the decision is raised, one line:

```
→ <effect> · later: <wait> · reach: <reach> · undo: <undo>
```

When the caller keeps the card in a store, the line is stored with it, and every view reads
it from there, a caller's tag-size views included, so the report line never has to open the
options. A stored card without one is revised before it renders (§ Re-show with what
changed, From the store). Each option's impact is stored with its option, so the card's
option lines read from there too.

**Older stored lines read as written.** An Impact line stored before Effect covered the
options (2026-10-14) may give the recommended option's effect alone. It renders as stored —
never recomposed at render time — and the option lines under it show what each option does.
When such a card is revised for any other reason, its Effect is rewritten across the options
and stored with the revision. An option stored on one line, its impact after a dash (a
caller's store form included), renders in the new one: its facets on the line under the
option.

## Context

Every card and block carries a **Context** section, shaped like the answer page's `context`
field (the `decision-page` skill's `references/cards-schema.md`), in the page's order: the
decision line first — the title and **What:**, which do the page TLDR's work — then
**Context:**, then the Impact and the options. A list line and a tag-size mention carry no
Context: a line stays a line.

What it holds, in this order:

- the terms, items, counts and named things the card or block uses, each introduced in plain
  words (SKILL.md § The floor, item 1): a count says what the things are, or lists them; a
  named mode, setting, review, plan or document gets a one-line gloss — what it is, and where
  it comes from; an item goes by its plain name, the id at most a trailing tag;
- then the **resume cue**, as its last clause: where the operator left it (what they last saw
  or decided on this subject) · what they decide now. For a decision whose subject they have
  never seen, where it came from, worded so it stays true after they have seen it: *raised
  when the audit you asked for turned it up*. Never what changed
  since: that is *while it waited*, which opens a re-show (§ Re-show with what changed).

It does not restate what is decided: **What:** says that, as the page's TLDR does.

Its size follows the page's detail levels:

| View | Context at | Shape |
|---|---|---|
| Card | the page's summary | one or two sentences, about 30–60 words, on the **Context:** line |
| Block | the page's medium | bullets of terse fragments, each with a sub-bullet or two at most. The first bullet is the card's Context; the rest are the context the reader may have lost: what was tried, what was answered before, where a list or number came from |

**Written when raised, shown every time.** Write it when the decision is raised, from the
worksheet (`references/worksheet.md` § The Context), and show it on every card and block,
warm reader or cold, each time one is shown — not only to a cold reader. *Seen* still holds
(SKILL.md § Levels): a seen, unchanged decision is a line ending *(shown before)*, and the
line carries no Context.

**The cue folds into Context**, as its last clause, rather than standing on a line of its
own: that is the page's order (terms, then the cue), so one stored Context reads the same in
chat and on a page, and a card no longer changes shape with the reader's warmth.

**Stored with the card.** Where the caller keeps the card in a store, Context is stored with
it when the decision is raised, on one physical line: the card's Context, then a block's
further facts. In a caller's format that splits the line with a separator — `context: <the
card's Context> — then: <a block's further facts, or none>` — the text before the separator
is the card's **Context:** line, and a block shows it as its first bullet and each sentence
after the separator as a bullet of its own. A re-show renders the stored Context; it never
composes it again (§ Re-show with what changed, From the store).

**Older stored cards render as before.** A stored Context holding the cue alone, from before
Context took the terms, is the card's **Context:** line as it stands. A stored card with no
Context at all renders as it did before Context existed: the **Impact:** line directly under
the title, then **What:**, **Why now:**, **Why ask:** and the options, with no Context
section; a cold re-show still backfills its cue from the record (§ Re-show with what changed),
and the revised card, stored with the cue as its Context, renders in the order above from
then on.

## Tag size

The number and the Effect alone, after an arrow, for a caller's tightest views: a table row
of open items, a report line that names decision numbers, a page's summary list.

```
N (→ effect)
```

*46 (→ (a) preview up in about 4 minutes; (b) yesterday's page)* · *45 (→ (a) OS units;
(b) bill units)*. Where the caller's row already shows the question and the recommendation,
the arrow follows the recommendation, so it carries that option's effect, read from its
stored impact: *decision 46: Retry the failed preview deploy? — rec (a) → preview up in about
4 minutes*.

## List line

```
- **N Title as a question?** — rec **(x) short label** → *effect* · *later: wait* · *class* · basis **word** · *age, deadline*
```

The arrow follows the rec label, so the effect slot carries the recommended option's own
effect, in a few words, read from its option's impact; the Effect across the options is on
the card. For a decision with no recommendation, the label takes the rec slot and the Effect,
each option's in a few words, the effect slot; the wait and basis slots stay, since the floor
needs them:

```
- **N Title as a question?** — *your preference, no rec* → *(a) effect; (b) effect* · *later: wait* · *class* · basis **word** · *age*
```

- The number and title are bold together.
- One line per decision, its own recommendation in its own rec slot: never a range or a
  group on one line (SKILL.md § Critical).
- An effect and Wait are on every line: *(line only)*, *(shown before)* and *(expand for the
  card)* lines too. No option's reach, undo or cost is: those are on the card.
- A line for a named template may end with its fixed options, after the age slot (gallery
  example 5); they run in letter order and only the recommended one is bold.
- An ask for another round carries its justification after the basis: *if left: what the
  leftover findings would break · a round: time, quota, your attention* (SKILL.md § The
  floor).
- Class slot: the decision's class, when the caller names classes of decision; left out
  when it names none. A template's slot, when there is one, comes before it.
- A line-only decision — nothing of it rendered above, now or before — carries its why ask
  after the basis: *why ask: what would go wrong if I took the recommendation alone*; on a
  round ask, its *if left* and *a round* stand in for it. A line whose card was shown carries
  the class alone; the card has the rest.
- ⚠ slot: ⚠ one-way (one-way and high impact; the ⚠ is followed by a space), after the class
  (after the wait when there is no class). A decision that is not ⚠ has no slot here; its
  Undo, on the card, says how it is reversed. The preference and authority labels take the
  rec slot (above); a template's label, *template: name*, has its own slot just before the
  class slot (just before the ⚠ slot or the basis when there is no class).
- A deadline stays on the line, in the age slot, written as the absolute time in the
  operator's zone when you know it, with the relative time and when you wrote it: *storage
  lease lapses ~17:45 (90 min from 16:15)*. With the zone unknown, say which: *17:45 UTC*.
  The wait slot says what happens at it.
- A line never stands in for a card with a **To act on** part: a decision whose option asks
  the operator to act is at least a card (SKILL.md § Levels, the line-only rule).
- In a message where other decisions are rendered above the list, a line with nothing above
  it ends *(line only)*, so the operator knows `expand` exists for it. A line whose card was
  seen and is unchanged ends *(shown before)*; one held back by paging ends *(expand for the
  card)*.

Example:

- **42 Clear the docs build cache?** — rec **(a) clear it** → *the docs build runs again* · *later: the docs build stays blocked* · *template: cache reset* · basis **strong** · *why ask: clearing it drops the other branch's cached build too* · *10 min old* *(line only)*

## Card

```
**N — Title as a question?**
**What:** what is decided, in plain words; items by plain name, the id as a trailing tag; other ids glossed.
**Context:** the terms, items and counts the card uses, each in plain words; then where you left it · what you decide now.
**Impact:** → (a) effect; (b) effect, or what the decision settles · later: wait · reach: who or what · undo: how, or one-way
**Why now:** why it is up now.
**Why ask:** *class* — what would go wrong if I took the recommendation alone.
- (a) Option
  *→ effect · reach: … · undo: … · cost: …*
- **(b) Option**
  *→ effect · undo: …*
- (z) Decide later — *what waiting costs; at a deadline, what happens then*

**To act on (b):** *(only for an option that asks the operator to act)*
1. step, with its `/…` path or whole command in `code`
2. …

Rec **(b)** · basis **word** — *one-clause reason* · unknown: what isn't known, or none
```

- **The order is the page's**: the decision line (the title, then **What:**), then
  **Context:**, then **Impact:** — and under them **Why now:**, **Why ask:** and the options
  (§ Context). A stored card with no Context keeps the older order, its **Impact:** line
  directly under the title (§ Context, Older stored cards).
- **What:** the decision line: what is decided, in plain words — the page's TLDR in chat.
- **Context:** one or two sentences at the page's summary size, on every card each time it
  is shown: the terms the card uses, then the resume cue (§ Context). Read from the store
  when the caller keeps one.
- **Impact:** right after **Context:**, on every card: the Impact line (§ Impact), read from
  the store when the caller keeps one. Its arrow carries the Effect across all the options,
  favouring none: each option's in a few words where their outcomes differ.
- **Why now:** says why it is up; what it blocks is the Impact line's *later:*, and need not
  be said twice.
- One option a bullet, in letter order, and under each but (z) its own impact on an italic
  line, indented to sit under it: `*→ effect · reach: … · undo: … · cost: …*`, in facet
  order, each facet after the first labelled (`reach:`, `undo:`, `cost:`) so Reach is never
  read as more Effect, and a facet that is empty or does not apply left out (§ Impact, Each
  option's impact). The bullet holds the option's label, and any plain-words gloss it needs;
  the consequence is on the impact line. (z) stays one line, what waiting costs after the
  dash. Only the recommended option is bold — (b) above, in its own place, not moved first
  (SKILL.md § Critical). With no recommendation, none is.
- **Why ask:** opens with the class in italics when the caller names classes; otherwise it
  is the reason alone. With no recommendation it says why the call is not yours. On an ask
  for another round it may point at the two lines below: *cap — the finding under If left*.
- **Context, kept.** Write it when the decision is raised, not at the re-show, so it is
  there when the reader has gone cold. When the caller's store keeps the card, it is stored
  with it (§ Context). With no store, keep it with your notes on the decision; with nowhere
  to keep it, a re-show copies it from the message that first showed it.
  On an answer page the card's Impact covers all its options and Background is folded (the
  `decision-page` skill's `references/cards-schema.md`); its Context has the same shape.
- **To act on (x):** after the options and before the Rec line, on a card where an option
  asks the operator to act (SKILL.md § The floor, what it takes to act). This bullet is
  where its specifics live:
  - one part per option that asks the operator to act, headed with its letter; numbered
    steps;
  - each file and directory by a `/…` path, reachable from where the operator will act for
    as long as the decision is open (never a session's scratch space that goes away; a
    `~/` path depends on the account they act from, so it does not count);
  - each command whole, copyable as it stands, with nothing to fill in: no `<word>`
    placeholder, no "your path here";
  - the text to paste inline, in a fenced block, when it is short; when it is long, the
    `/…` path of the file that holds it and what it does;
  - each URL in full;
  - a secret by where it is kept, never its value;
  - never "I'll give you the steps": the steps are on the card.

  **Stored with the card** where the caller keeps one, so a re-show renders it rather than
  composing it again. A step's multi-line text is stored on one physical line, its line
  breaks written ` / ` (as a store's answer lines write a reply's), or as the `/…` path of
  a file that holds it — the file form whenever the text itself holds ` / `, since nothing
  in a stored line is escaped. A re-show renders it back as a fenced block.
- An ask for another round adds two lines after **Why ask:** —
  **If left:** *each leftover finding, and what it would break* and **A round costs:** *the
  time, the quota, and your attention: this answer, and another if the round does not settle
  it* (SKILL.md § The floor).
- When a status-quo default applies, add: **If unanswered:** *I leave X as it is and carry on
  with other work.*
- When investigating could change the choice, add a priced option: (c) Investigate first —
  *about 15 minutes: read the access logs for other callers; could change the answer if …*
- A small call gets a short card. Do not pad a two-way, narrow decision with sections it does
  not need; its Context, short, and its Impact line stay.

## Block

```
**N — Title as a question?** ⚠ one-way
**What:** …
**Context:**
- the card's Context: the terms the block uses, then where you left it · what you decide now
- a fact the reader may have lost: what was tried, what was answered before
  - a sub-bullet, two at most
- …

**Impact:** → (a) effect; (b) effect, or what the decision settles · later: wait · reach: who or what · undo: how, or one-way

| Impact | Effect | Reach | Undo | Cost |
|---|---|---|---|---|
| (a) Option | … | … | … (or: none, because …) | … |
| **(b) Option** | … | … | … | … |
| (c) Investigate first | what it would settle | — | nothing to undo | time and spend |
| (z) Wait | what waiting costs; what it blocks; at the deadline, what happens | who waits | answer any time, or what a deadline loses for good | … |

**Why now:** …
**Why ask:** *class* — …

**To act on (b):** *(only for an option that asks the operator to act, as on a card)*
1. …

Rec **(b)** · basis **partial** — *reason*
*Basis:* observed — … (link) · inferred — … · unknown — …
*If you pick (a), I'll repeat it back and act only once you confirm: it can't be undone.*
```

- The block opens as a card does, in the page's order: the title, **What:**, then
  **Context:** as a bullet list at the page's medium size, its first bullet the card's
  Context and the rest the context the reader may have lost (§ Context). It is shown on
  every block, warm reader or cold.
- The card's **Impact:** line comes right after Context, the Effect across all the options
  as on a card, and the **Impact table** right under it: one row per option, in letter
  order, each option's own effect, reach, undo and cost, then the **Wait row** — decide
  later's, labelled `(z) Wait` — with the columns Effect, Reach, Undo and Cost. Only the
  recommended option's row label is bold. The table takes the place of a section per option
  and of the options' impact lines.
- The lines under the table run **Why now:**, **Why ask:**, then a round ask's **If left:**
  and **A round costs:**, then any **To act on (x):** part, before the Rec line (§ Card).
  A block stored with no Context keeps the older order: its impact directly under the title,
  then **What:**, **Why now:**, **Why ask:** (§ Context, Older stored cards).
- A block **includes** the basis drill-down (the tags and links). `expand` on a block is
  answered: *already at full detail — `tell me [what]` for something specific?*
- The read-back line (⚠ blocks only) names the one-way option(s). A block for a wide
  decision that is not ⚠ drops it.
- Write every option's **Undo** cell plainly — it is what decides whether an answer is read
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
| One-way and high impact | ⚠ one-way | the ⚠ slot on the list line (§ List line); after the title on a card or block |
| One-way, narrow | no label: its Undo says so, *undo: none — …* | the Impact line's *undo:*, and the option's own impact |
| No fact settles it | *your preference — no recommendation* | the rec slot (*your preference, no rec*); after the title on a card |
| Not the agent's call | *no recommendation — outside my authority*, and a clause saying why | the rec slot; after the title on a card, the why on its own line |
| A recurring decision with fixed options | *template: name* — shown as a card the first time the operator meets it | its own slot (§ List line) |
| Time-critical, options not ready (not a decision yet) | **Alert:** in bold, bare; *options follow* | its own line, in place of a card |
| Not defined yet (not a decision yet) | listed under **Open questions**, unnumbered | the *Open questions* section |

## FYI after acting

Not a decision: no number, no options, no hint. One `Done:` line per thing decided alone,
in a **Done alone** group the next time you report — before the decisions block, which stays
last:

```
**Done alone** — *N since my last report · say so in your own words to undo or reopen any*
- **Done: what was done** — *class · why it was safe: two-way, narrow · authority · undo: how*
```

- **Done: fixed a broken link in the contributing guide, on my task branch** — *two-way, nobody else uses the branch · inside the task you gave me · undo: one revert*

- The class slot is filled when the caller names classes of decision, and left out
  otherwise, as on the list line.
- The authority is the one the FYI rule accepted: an answered decision (by number), the
  task you were assigned, or the decide-alone class the caller's rules define.
- One line per ruling, never merged: the operator reopens them one at a time. With a single
  line, the heading may be left out and the line stands alone, as above.
- Where the caller keeps a record, each line matches a record the caller wrote when it
  acted, and that record holds every part of the line — why it was safe included; the line
  is rendered from that record, not from memory.

Only for actions that pass the guard in `references/worksheet.md` § E. An action that happens
unless the operator stops it is an approve ask, rendered as a card, and it waits. A reply
that objects to a `Done:` line — *undo the rename*, *I'd rather decide that one* — is read
like any reply (`references/replies.md`): an undo is echoed and done; a reopen is raised as a
new numbered decision that names the line it reopens.

## Re-show with what changed

When a decision comes back (a wake fired, a context reset, `tell me`, `dig into`), open it
with what changed since the operator last saw it, then the card or block as usual — its
**What:**, its stored **Context:** and its Impact line (and a block's table), right after
the *while it waited* line:

**62 — back, as you asked ("until the load test finishes"):** move the job queue to the new
message broker?
*While it waited (1 day): the load test finished with no lost messages; nothing else changed.
Options and recommendation unchanged; impact unchanged.*
**What:** switch every worker service from the old job queue to the new message broker.
**Context:** the new broker has carried the email worker alone for two weeks as a trial, and the load test was the last check before the rest move. You left it at that trial · you decide whether every worker moves now or one goes first.
**Impact:** → (a) every worker reads from the new broker today; (b) the email worker moves first, the rest in two days · later: the worker rollout stays paused · reach: every worker service and its on-call · undo: switch each config back within the week

*While it waited* always says whether the impact changed: *impact unchanged*, or what changed
in it — *impact changed: waiting now also holds the release*. When the options or
recommendation changed, say which and why: *Recommendation changed from (a) vendor the font
to (b) fetch it, because the CDN outage ended.*

**From the store.** When the caller's store keeps the card (the floor's fields under the
decision's record, with its raised-at time), a re-show renders that stored card and adds
only the *while it waited* line — read from the caller's record, never from memory — and a
plain name (the `plain-names` skill) for any item, and a gloss for any other id, that the
stored text left bare. *While it waited*, its window and its duration, counts from the last
showing the record marks as seen, where the caller records shown and seen (SKILL.md § Before
you write), else from the raising: what changed after the showing the operator read is in
it, even when it came before the turn that saw it. Age and order still count from the
raising, and the re-show is itself a showing the caller records. Composing the card again
from memory can shift the letters or the recommendation, and the operator would answer an
(a) that is not the (a) they read. Before rendering, check the stored card against now: a floor field it lacks, or
one events have made false — a *why now* that no longer holds, an Impact facet that no
longer holds, an input path that no longer resolves, a basis word the rule (`references/evidence-basis.md`) no longer gives — is a
revision. **A stored card without an Impact line** is backfilled the same way, from its
options' impacts, across them all, and its (z) line (and any older stakes words, for reach
and undo), each facet no record holds written *not recorded*, and stored as a revised card
before it renders in any view. The caller stores the
revised card (a missing field no record holds reads *not recorded*), and *while it waited*
says what changed. When the options or recommendation really changed, say which and why, and
the caller stores the new card.

**A cold re-show** — whenever the reader is cold (SKILL.md § Before you write) — shows each
open decision the reader is cold on at card level or above, never as a line only except as
paged (SKILL.md § Levels, the line-only rule), each opening with what changed while it
waited (*nothing changed* is worth saying, and so is *impact unchanged*). Under it the card
runs **What:**, **Context:** (its stored Context, ending on where the operator left it),
**Impact:**, **Why now:**, **Why ask:**; a block's **Context:** bullets open with the same
Context. A stored card from before the cue existed is revised as above: its cue backfilled
from the record, *not recorded* when no record holds it, and stored as its Context. A deferred decision whose
wake has not come is a card too, opening with its wake: *deferred until the release; no
answer needed before then*; it leaves its group and goes last, in the cards and the list
alike, so paging reaches it last. Open
questions still open are listed under *Open questions*. A cold re-show's heading has one
form: **Decisions** — *N open · shown again after a context reset · M shown in full · one ⚠
one-way*, naming what made the reader cold, and dropping *M shown in full* when nothing is
paged and the ⚠ part when there is none. With more than five, SKILL.md's paging rule applies
*(provisional — pending the operator's ruling)*: the rest are lines ending *(expand for the
card)*.
