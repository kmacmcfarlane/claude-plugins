# Rendering decisions

The impact every view carries, the Context every card and block carries, the folds, the templates
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
| **Effect** | what an option changes in the thing the work builds — its code, data, users, deploys, downstream consumers — by its mechanism; an option's facet, never the decision's | `→ effect` |
| **Wait** | what waiting costs, and what it blocks; the only facet for effects on the process (a review comment held, a round, a session blocked) | `later: …` |
| **Reach** | who or what in and around that system is affected: users, consumers, deploys, which repos, the public | `reach: …` |
| **Undo** | shown only for an option that is one-way or costly to undo: how it is reversed and at what cost, or that it cannot be and why | `⚠ undo: …` |
| **Cost** | build time, money, quota; the operator's time where an option asks them to act; their attention only on a round ask | `cost: …` |

The smallest view shows the recommended option's effect; each larger view adds facets in
that order:

| View | Impact shown |
|---|---|
| Tag size | the recommended option's effect, its letter first (with no recommendation, each option's in a few words) |
| List line | the recommended option's effect (with no recommendation, each option's in a few words) · Wait |
| Card | an **Impact:** line, Wait · Reach, then Undo when an option is one-way or costly, then Cost when it is what the operator weighs, and no effect; under each option, its own impact line: effect · reach · undo (one-way or costly only) · cost |
| Block | the card's **Impact:** line, then the Impact table: a row per option, then a Wait row; columns Effect, Reach, Undo (`—` on a reversible row), Cost; under it, each option's view: its plan in brief and its Pros \| Cons table (§ An option's view) |

- **Impact names the system, not the process.** Effect and Reach describe the thing the
  work builds and those who depend on it: code, data, users, deploys, downstream consumers,
  other repos. An effect on the process — a review comment held, another round, a session
  blocked, the operator's attention — goes only in Wait. Where the change is to agent
  behaviour, as in a kit of skills, sessions and the operator are that system's users and
  may stand in Reach. *Not: → the comment to the developer waits*; *but: → the upload
  service keeps reading oversize files into memory*.
- **Say the mechanism, not the label.** An effect, a finding or a risk says how it happens,
  who meets it and when, and the before and after: not *exposes an archived library in its
  public API*, but *every app that imports the client must install the archived library,
  and never gets its security fixes; after the switch, the client takes the standard type*.
- **No card-level effect.** Effect is an option's: each option says its own, by its
  mechanism, on its impact line (a card) or its row (a block's table). The **Impact:** line
  carries none, since it would only repeat the options' (the operator's v5 ruling,
  2026-10-22), as the answer page's Impact carries none (`references/card-record.md`,
  `impact`). Where a closed view shows one effect — tag size, the list line, a caller's row
  — it is the
  **recommended option's own**, marked with its letter: `→ (a) …`, or the list line's rec
  slot just before the arrow (answer 340 (a)). With no recommendation, each real option's
  effect in a few words, `→ *(a) sizes match the OS tools; (b) sizes match the bill*`. Plain
  words, about the world, for the operator; at tag size, under about 10 words.
- **Each option's impact** is its own: on a card, an italic line under the option, in facet
  order, `*→ effect · reach: … · ⚠ undo: … · cost: …*`, each facet after the first labelled
  so Reach is never read as more Effect. A facet that is empty or does not apply to that
  option (nobody beyond the work, no cost worth naming) is left out, so a small option's
  line may be its effect alone. (z) keeps its one line: what waiting costs. On a card the
  option's `*pros: …*` and `*cons: …*` lines follow its impact line (§ Card); they are not
  facets. A block carries the same facets in its table, a row per option. A list line carries
  none: it stays terse.
- **Undo only where it bites.** Most options are reversible without consequence, so Undo is
  shown only on an option that is one-way or costly to undo, and marked to draw the eye:
  `⚠ undo: none — a deleted snapshot is gone`, or
  `⚠ undo: start the backup again, about 3 hours`. An option with no undo shown is
  reversible at little cost; that is how the read-back reads it (`references/replies.md`).
  A one-way option is never written without
  its marker, since the marker decides the read-back. The marker marks the option only:
  the decision is ⚠ only by its `⚠ one-way` label (one-way *and* high impact), which alone
  governs batches, `you decide` and the block on first show (SKILL.md § Critical). Undo
  replaces the old stakes words (*reversible, narrow*, *one-way, narrow*).
- **The Impact line carries Undo only when an option is one-way or costly**, as
  `⚠ undo:`, naming that option, not only the recommended one: *⚠ undo: (b) none — the lost
  ranking cannot be won back*. With every option reversible at little cost, the line carries
  no undo.
- **Wait absorbs the old *what it blocks* slot**: *later: the docs build stays blocked*. At a
  deadline, it says what happens then.
- **Cost** lives on each option's impact line and the block's table; the Impact line carries
  it only when it is what the operator weighs.
- On the Impact line and in the table, a facet no record holds reads `not recorded`; a facet
  that does not apply, `—` (the Impact line's undo is left off, as above). On an option's
  impact line, one that does not apply is left out and `not recorded` stays. Never invent
  one at render time.

**The Impact line** is written when the decision is raised, one line, with no effect:

```
later: <wait> · reach: <reach> · ⚠ undo: <the one-way or costly option's undo> · cost: <cost>
```

The undo is there only when an option is one-way or costly to undo, and the cost only when it
is what the operator weighs.

When the caller keeps the card in a store, the line is stored with it, and every view reads
it from there. A stored card without one is revised before it renders (§ Re-show with what
changed, From the store). Each option's impact is stored with its option, so the card's
option lines read from there too, and so do the closed views that show the recommended
option's effect (tag size, the list line, a caller's row), so the report line never has to
open the card.

A card stored in an earlier form — an Impact line that carries an effect, an option's impact
after a dash on the option's own line, a plain `undo:` — is read by
`references/legacy-cards.md`.

## Context

Every card and block carries a **Context** section, shaped like the answer page's `context`
field (the `decision-page` skill's `references/cards-schema.md`), in the page's order: the
title first, which does the page TLDR's work, then **Context:**, then **What:** (what is
decided, and for a set each item, § Card), then **Finding:** on a card raised from a finding
(§ Card), then the folds above the Impact (▸ Open questions when anything is open, then
▸ Assumptions, § Folds), then the Impact and the options. A list line and a tag-size mention
carry no Context: a line stays a line.

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

It does not restate what is decided: **What:**, right after it, says that, and lists a set's
items.

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

A stored card with a cue-only Context, or none, is read by `references/legacy-cards.md`.

## Folds

A part a reader may not need opens folded, on one line:

```
▸ <name> — <summary>
```

- **The summary** says what is inside in a few words, so the line alone tells whether to
  open it.
- **Open.** `tell me <name>` (`tell me open questions`) answers with the fold open, and
  `expand` and a block show it open: the line as `▾ <name> — <summary>`, its content under
  it, one bullet an item (Assumptions' Basis line first, and Background's two labelled lines,
  below).
- **Empty.** A fold with nothing in it is left out, line and all (none is not shown).

**▸ Open questions** — what is still open about the decision (SKILL.md § The floor, item 9;
the card record's `open`): each open question one line, said as what is not known yet. Its
summary is `N open: <the first, cut at about 12 words>`, as on the answer page. On a card
and a block it sits after **Context:** (and after Finding, Scope and Likelihood when the card
has them), before ▸ Assumptions and the **Impact:**. It is not the message's **Open
questions** section, which lists
questions that are not decisions yet (SKILL.md § The floor).

**▸ Assumptions** — the basis of the call and what it rests on (SKILL.md § The floor, item 8;
the card record's `basis`, `reason`, `evidence` and `assume`), on every card and block, since
the basis word is always shown. It sits after ▸ Open questions (after **Context:** when
nothing is open) and before the **Impact:**. Its summary is the basis line, `basis: **word**`,
then the count of assumptions with their tripwires: `basis: **partial** · 2 assumptions with
tripwires`, `1 assumption with its tripwire`, or `basis: **strong**` alone when the card names
none (none is not shown). `tell me assumptions`, `expand` and a block show it open:

```
▾ Assumptions — basis: **partial** · 2 assumptions with tripwires
**Basis:** partial — *the one-clause reason*
*Evidence:* observed — … (link) · inferred — …
- **what the call rests on**
  *tripwire:* the sign that would change it
- **another thing it rests on**
  *tripwire:* its own sign
```

Under the open line, the **Basis:** line (the word and its reason), then the basis drill-down
as an *Evidence:* line when there is one, then one bullet per assumption, in bold, its
*tripwire:* on the indented line under it. What is not known yet is never an assumption: it is
▸ Open questions. There is no Rec line: the recommended option is the bold one, and the basis
and its reason are in this fold.

**▸ Background** — why now and why ask (SKILL.md § The floor, items 3 and 4; the card
record's `why` and `whyask`): the first of the folds under the options, after the options and
their parts (any **To act on (x):**, **If left:**, **A round costs:** and **If
unanswered:**). Its summary is `why now:
<the first sentence of why now>`, about 25 words at most: a longer first sentence is
rewritten where the caller stores *why now*, never cut, and the summary is composed from
*why now* each time, never stored. `tell me background` (or `tell me why`) answers with it
open, and `expand` and a block show it open: `▾ Background — why now: …`, then **Why now:**
and **Why ask:** (the class first) on two lines under it. The answer page folds it the same
way, first of its bottom folds (the `decision-page` skill's `references/cards-schema.md`).

## Tag size

The number and the recommended option's own effect, after an arrow, its letter first, for a
caller's tightest views: a table row of open items, a report line that names decision numbers,
a page's summary list.

```
N (→ (x) <its effect>)
```

*46 (→ (a) preview up in about 4 minutes)*. With no recommendation, each real option's effect
in a few words: *45 (→ (a) OS units; (b) bill units)*. Read from the option's stored impact
where the caller keeps one. Where the caller's row already shows the question and the
recommended letter, the arrow follows that letter and carries that option's effect: *decision
46: Retry the failed preview deploy? — rec (a) → preview up in about 4 minutes*.

## List line

```
- **N Title as a question?** — rec **(x) short label** → *effect* · *later: wait* · *class* · basis **word** · *age, deadline*
```

The arrow follows the rec label, so the effect slot carries the recommended option's own
effect, in a few words, read from its option's impact (a card carries no card-level effect).
For a decision with no recommendation, the label takes the rec slot and each option's own
effect, in a few words, the effect slot; the wait and basis slots stay, since the floor needs
them:

```
- **N Title as a question?** — *your preference, no rec* → *(a) effect; (b) effect* · *later: wait* · *class* · basis **word** · *age*
```

- The number and title are bold together. A decision raised from one labelled item of a
  source carries that label first in its title, with its short name, on the line as on the
  card: `**41 F7 (oversize upload) · Cap the upload size?**` (§ Source labels).
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
**Context:** the terms, items and counts the card uses, each in plain words; then where you left it · what you decide now.
**What:** what is decided, in plain words; items by plain name, the id as a trailing tag; other ids glossed.
- an item's plain name, where it lives — what it is, in a few words · *(a) its outcome; (b) its outcome*
**Finding:** F7 (short name): the finding's own title — `path/to/file:40-52` *(only on a card raised from a finding)*
how it happens, who meets it and when, the before and after, in one to three sentences
*(then its excerpt, verbatim, in a fenced block tagged with its language)*
▸ Open questions — 2 open: what is not known yet, cut at about 12 words
▸ Assumptions — basis: **partial** · 2 assumptions with tripwires
**Impact:** later: wait · reach: who or what · ⚠ undo: (a) how, at what cost, or why not
- (a) Option
  *→ effect · reach: … · ⚠ undo: … · cost: …*
  *pros: its main upside, in one line*
  *cons: its main downside or risk, in one line*
- **(b) Option**
  *→ effect · cost: …*
  *pros: …*
  *cons: …*
- (z) Decide later — *what waiting costs; at a deadline, what happens then*

**To act on (b):** *(only for an option that asks the operator to act)*
1. step, with its `/…` path or whole command in `code`
2. …

▸ Background — why now: the first sentence of why it is up now, about 25 words at most
```

- **The order is the page's**: the title, then **Context:**, then **What:** with a set's
  item bullets, then **Finding:** on a card raised from a finding, then the ▸ Open questions
  line when anything is open, then the
  ▸ Assumptions line (§ Folds), then **Impact:** — and under them the options, any **To act
  on (x):** part, a round ask's **If left:** and **A round costs:**, any **If unanswered:**,
  then the ▸ Background line (§ Context, § Folds). There is no Rec line.
- **Title:** the question. A decision raised from one labelled item of a source opens its
  title on the label and its short name: **41 — F7 (oversize upload) · Cap the upload
  size?** (§ Source labels).
- **What:** after **Context:**, what is decided, in plain words (the record's `what`; the
  operator's v4 layout, answer 290 (a): *Context above What*). **For a set**, every item it
  acts on, one bullet each under it, never a count alone (the record's `items`): the item's
  plain name, where it lives when that helps, then ` — ` and what it is in a few words, then,
  only where the options treat it differently, ` · ` and its outcome under each, in letter
  order, *(a) …; (b) …* (the record's `per`). An item that fares the same under every option
  carries no outcome: its option's effect says it once. A bullet never opens on an option's
  letter. A card about one thing has no bullets.
- **Finding:** on a card raised from a finding (of a review, an audit, a test run or a scan),
  after **What:** and its item bullets, before the folds and the Impact, never folded (the
  record's `finding`; answer 337 (a), its worked findings card confirmed on item 9168). Its
  head line: `**Finding:**`, the source label with its short name, a colon and the finding's
  own title, then ` — ` and where it lives in `code` (a path and line range), then the
  excerpt's `src` when it is given: when it is the location exactly, nothing more; when it
  opens on the location, the rest of it, in `code` after a space
  (*`templates/welcome.html:14-16` `at 3f2a9c1`*); else ` · from ` and the whole `src` in
  `code`. With no location, the head ends on its title, then ` · from ` and the `src` in
  `code`. A location or `src` that holds a backtick takes a longer code-span delimiter, two
  backticks or more, with a space inside each end. **Finding:** F7 (oversize upload): the
  handler reads before it checks — `upload/handler.go:40-52` `at 3f2a9c1`. The label
  is the one the title carries, with the same short name (§ Source labels); a part the
  finding lacks is left out, so one with no label opens on its title, and one with neither on
  its location. Then the mechanism on its own line: how it happens, who meets it and when, the
  before and after (*Explain the mechanism*, SKILL.md § The floor), never the label restated.
  Then the excerpt, its code, log or failing output, in a fenced block tagged with its
  language: verbatim, about 15 lines in chat (cut longer ones, saying where in the block),
  never a secret's value, personal data, or another party's private source (the
  `decision-page` skill's `references/cards-schema.md` § An excerpt). **The fence is safe
  for the text:** longer than the longest run of backticks in it, three at least (a text
  holding ```` ``` ```` takes ````` ```` `````), or `~~~` when the text holds backticks and no
  tildes, so no line of the excerpt can close it; and each character the page tags (the
  `decision-page` skill's `references/cards-schema.md` § An excerpt), in the excerpt and its
  `src`, as its `U+` tag (`U+200B`, `U+202E`); tabs and line breaks stay as they are. A card
  carries one Finding part. A set raised from several findings lists them as its What items,
  and its one Finding may cover the set, naming each by its label with its location (*F2
  `app/middleware/log.py:22-25` · F1 `config/production.yaml:7`*), then how each happens,
  and the excerpt the choice turns on.
- **Context:** one or two sentences at the page's summary size, on every card each time it
  is shown: the terms the card uses, then the resume cue (§ Context). Read from the store
  when the caller keeps one.
- **▸ Assumptions:** the basis word, and the count of what the recommendation rests on, each
  with its tripwire (§ Folds), closed, just above the Impact; the basis's one-clause reason
  and its drill-down are inside it.
- **Impact:** after **Context:**, any ▸ Open questions line and the ▸ Assumptions line, on
  every card: the Impact line (§ Impact), read from the store when the caller keeps one. It carries no effect: each
  option's is on its own line under it.
- One option a bullet, in letter order, and under each but (z) its own impact on an italic
  line, indented to sit under it: `*→ effect · reach: … · ⚠ undo: … · cost: …*`, in facet
  order, each facet after the first labelled (`reach:`, `⚠ undo:`, `cost:`) so Reach is
  never read as more Effect, a facet that is empty or does not apply left out, and the undo
  only on an option that is one-way or costly to undo (§ Impact). The bullet holds the
  option's label, and any plain-words gloss it needs;
  the consequence is on the impact line. (z) stays one line, what waiting costs after the
  dash. Only the recommended option is bold — (b) above, in its own place, not moved first
  (SKILL.md § Critical). With no recommendation, none is.
- **Pros and cons**, under each option but (z), after its impact line: two italic lines,
  labelled as its facets are, `*pros: …*` then `*cons: …*`, the option's main upside and its
  main downside or risk, one line each (the record's `pro` and `con`; the answer page's
  **Pros** and **Cons** rows, from the operator's feedback on decision 302: pros and cons as
  their own labelled lines, like Effect and Reach, to make them easy to read). Every option
  but (z) carries both; the recommended option's cons line is never left out, since a
  recommendation with no downside is not weighed. A con is the option's own, not a reason
  against it relative to the recommendation: it says what choosing it costs or risks. A card
  upgraded from an older format may hold none: it shows none (nothing is invented), and gains
  them when it is next revised. (z) carries none, here and on the answer page: it stays one
  line.
- **▸ Background:** why now and why ask, in a closed fold, the first under the options, its
  summary `why now:` and the first sentence of why now (§ Folds). Inside it, **Why now:** says
  why it is up now, *nothing forces it* when nothing does (SKILL.md § The floor, item 3), and
  **Why ask:** why it comes to the operator (what would go wrong if you took the
  recommendation alone), opening with the class in italics when the caller names classes;
  with no recommendation it says why the call is not yours. On an ask for another round Why
  ask may point at the lines above it: *cap — the finding under If left*. The caller's store
  keeps *why now* and *why ask* as its own fields, as written; the fold shows them, and the
  card carries no separate why line.
- **Context, kept.** Write it when the decision is raised, not at the re-show, so it is
  there when the reader has gone cold. When the caller's store keeps the card, it is stored
  with it (§ Context). With no store, keep it with your notes on the decision; with nowhere
  to keep it, a re-show copies it from the message that first showed it.
  On an answer page the card's Impact carries no effect either, and Background is folded (the
  `decision-page` skill's `references/cards-schema.md`); its Context has the same shape.
- **To act on (x):** after the options and before the ▸ Background line, on a card where an
  option asks the operator to act (SKILL.md § The floor, what it takes to act). This bullet is
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
- **No Rec line.** The recommendation is the bold option; the basis word is the
  ▸ Assumptions summary, and its one-clause reason is inside that fold. What is not known yet
  is in the ▸ Open questions fold (§ Folds).
- An ask for another round adds two lines after the options and any **To act on** part,
  before the ▸ Background line —
  **If left:** *each leftover finding, and what it would break* and **A round costs:** *the
  time, the quota, and your attention: this answer, and another if the round does not settle
  it* (SKILL.md § The floor).
- When a status-quo default applies, add **If unanswered:** *I leave X as it is and carry on
  with other work.*, before the ▸ Background line.
- When investigating could change the choice, add a priced option: (c) Investigate first —
  *about 15 minutes: read the access logs for other callers; could change the answer if …*
- A small call gets a short card. Do not pad a two-way, narrow decision with sections it does
  not need; its Context, short, and its Impact line stay.

## Block

```
**N — Title as a question?** ⚠ one-way
**Context:**
- the card's Context: the terms the block uses, then where you left it · what you decide now
- a fact the reader may have lost: what was tried, what was answered before
  - a sub-bullet, two at most
- …
**What:** …
**Finding:** … *(as on a card: its head line, its mechanism, its excerpt fenced)*

▾ Open questions — 1 open: what is not known yet
- what is not known yet, one line

▾ Assumptions — basis: **partial** · 1 assumption with its tripwire
**Basis:** partial — *reason*
*Evidence:* observed — … (link) · inferred — …
- **what the call rests on**
  *tripwire:* the sign that would change it

**Impact:** later: wait · reach: who or what · ⚠ undo: (a) none, because …

| Impact | Effect | Reach | Undo | Cost |
|---|---|---|---|---|
| (a) Option | … | … | ⚠ none, because … (or: how, at what cost) | … |
| **(b) Option** | … | … | — | … |
| (c) Investigate first | what it would settle | — | — | time and spend |
| (z) Wait | what waiting costs; what it blocks; at the deadline, what happens | who waits | — (or: ⚠ what a deadline loses for good) | … |

**(a) Option**
*plan in brief:* what choosing it sets in motion, in 2–4 sentences

| Pros | Cons |
|---|---|
| an upside in full | a downside or risk in full |
| … | … |

**(b) Option**
*plan in brief:* …

| Pros | Cons |
|---|---|
| … | … |

**To act on (b):** *(only for an option that asks the operator to act, as on a card)*
1. …

▾ Background — why now: the first sentence of why now
**Why now:** …
**Why ask:** *class* — …

*If you pick (a), I'll repeat it back and act only once you confirm: it can't be undone.*
```

- The block opens as a card does, in the page's order: the title, then **Context:** as a
  bullet list at the page's medium size, its first bullet the card's Context and the rest the
  context the reader may have lost (§ Context), shown on every block, warm reader or cold;
  then **What:**, with a set's item bullets, and **Finding:** when it has one, as on a card.
- The folds above the Impact come next, open (`▾`, § Folds): ▸ Open questions when anything
  is open, then ▸ Assumptions with its **Basis:** line, the basis drill-down and each
  assumption with its tripwire. Then the card's **Impact:**
  line, with no effect, as on a card, and the **Impact table** right under it: one row per option, in letter
  order, each option's own effect, reach, undo and cost, then the **Wait row** — decide
  later's, labelled `(z) Wait` — with the columns Effect, Reach, Undo and Cost. An Undo cell
  holds `—` on a row that is reversible at little cost and starts with ⚠ on a row that is
  one-way or costly; with no such row, the Undo column is dropped. Only the recommended
  option's row label is bold. The table takes the place of the options' impact lines.
- Under the table, **each option's view** in letter order, (z) too, without its facets, which
  are its table row: its title in bold as its own line, then its *plan in brief:* line, then
  its **Pros | Cons** table (§ An option's view). An option with no points on either side has
  no table; an older option with no plan shows its text after its title instead.
- Under them run a round ask's **If left:** and **A round costs:**, then any **To act
  on (x):** part; then the Background fold stands open, as § Folds places it, first after
  the options and their parts: `▾ Background — why now: …` with its **Why now:** and **Why
  ask:** lines under it; only the read-back line, on a ⚠ block, follows it.
- A block **includes** the basis drill-down (the tags and links), in its open Assumptions
  fold. `expand` on a block is
  answered: *already at full detail — `tell me [what]` for something specific?*
- The read-back line (⚠ blocks only) names the one-way option(s). A block for a wide
  decision that is not ⚠ drops it.
- Write every one-way or costly **Undo** cell plainly, after its ⚠ — it is what decides
  whether an answer is read back (`references/replies.md`). Write a `|` inside a cell as `\|`.
- Never use the words "answer alone" as a label; the ⚠ and the read-back line carry it.

## An option's view

What choosing one option sets in motion, and its trade-offs in full, in the answer page's
order (the option's view: Plan in brief, the Pros | Cons table, then the facets; the
operator's v5 ordering, item 9168). `tell me (x)` (`46: tell me (b)`) answers with it, under
the decision's number; a block shows each option's under its Impact table, its facets being
the table's row.

```
**N (x) — Option title**
*plan in brief:* what choosing it sets in motion, in 2–4 sentences

| Pros | Cons |
|---|---|
| an upside in full, the weightiest first | a downside or risk in full |
| … | … |

*→ effect · reach: … · ⚠ undo: … · cost: …*
```

- **The order is fixed**: the *plan in brief:* line first, then the table, then the option's
  facet line, as its card shows it (§ Impact); on a ⚠ decision too.
- **Plan in brief** is the card record's `plan` (2–4 sentences, about 100 words at most, on
  one line), labelled as the facets are. An older card with no plan gives its option's text in full
  there.
- **The table** is two columns headed `Pros | Cons`, as the Impact table's are headed
  `Effect | Reach` (the operator's feedback on decision 302: pros and cons labelled like Effect
  and Reach), one point a row, at most five a side, the weightiest first: the record's `pros`
  and `cons`, the one-line `*pros:*` and `*cons:*` lines in full. A side shorter than the
  other leaves its cells empty; with no points on either side there is no table, and with
  points on one side only, the other column stays, empty. Write a `|` inside a cell as `\|`.
- (z)'s view is its plan, then its pros and cons where it gives any, and its facet line is what waiting costs.
- `tell me (x)` changes nothing on the card: it is shown, not revised, so no **Added:** line
  and no new revision. The card is one scroll up; do not send it again.

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

**Where the set goes.** A findings-style set — decisions raised from the findings of a
review, an audit, a test run or a scan — goes to chat by default: the operator decides a
finding from what it is, where it lives, its code and how it fails, which each card's
**Finding:** shows. The answer page shows them too (each card's Finding part, its excerpt as a
code block), so offer the page for such a set as for any other. Other sets go on a page when
the operator asks for one (the `decision-page` skill).

## A bundle as a group

A **bundle** is one ask over several items: a review's findings, a cleanup's files, a set of
endpoints. A card that names only their category (*housekeeping*, *the review's findings*)
does not say what is decided (SKILL.md § The floor, item 1).

- **The items need different answers: a group.** One card per item, each whole: its own
  number, Context, What, ▸ Assumptions line, Impact, options and ▸ Background line, as any card
  (SKILL.md § Critical, each one whole). An item card's Context may be short and lean on
  the heading for shared terms; it still ends on its cue. The cards sit under one heading:

  ```
  **Group: <plain name>** — *<N> decisions, <what they share>*
  **Shared context:** the terms and the source every card in the group uses, in plain words.
  ```

  The heading adds the shared context and replaces nothing on the cards. On an answer page a
  group is a layer carrying its shared context (the `decision-page` skill). The group keeps
  the order's rules (SKILL.md § Order): placed by its most pressing member, kept together.
  Each card has its own list line, and `ok 51-53` takes every recommendation in it, ⚠ cards
  skipped as in any batch.
- **One answer fits every item** (*fix all three now*): one card. Its **What:** lists every
  item, one bullet each (§ Card) — a count is always listed, never left bare — and each
  option's effect says what that answer does to them.

A group is never one card holding a pick per item (`41: F3 a, F7 z`): its picks would be
lettered sub-decisions (SKILL.md § Critical, plain integers), and their recommendations
folded into one card.

## Order

The precedence is SKILL.md § Order. Two notes on applying it: a group is placed by its most
pressing member and kept together, the same precedence holding inside it; and a deadline
decision placed first "because the return is unknown" costs nothing if the operator is back
sooner — both get answered — while one placed low can lose the lease.

## Labels

| Case | Label | Where it goes |
|---|---|---|
| One-way and high impact | ⚠ one-way | the ⚠ slot on the list line (§ List line); after the title on a card or block |
| An option one-way or costly to undo | `⚠ undo:` on that option, never a label on the decision; a decision with such an option and a narrow reach has no ⚠ label | the option's own impact line, its block's Undo cell, and the Impact line's *⚠ undo:* |
| No fact settles it | *your preference — no recommendation* | the rec slot (*your preference, no rec*); after the title on a card |
| Not the agent's call | *no recommendation — outside my authority*, and a clause saying why | the rec slot; after the title on a card, the why in its Background fold's **Why ask:** |
| A decision raised from one labelled item of a source | the label and its short name, *F7 (oversize upload)* | first in the title, on the card, block and list line (§ Source labels) |
| A recurring decision with fixed options | *template: name* — shown as a card the first time the operator meets it | its own slot (§ List line) |
| Time-critical, options not ready (not a decision yet) | **Alert:** in bold, bare; *options follow* | its own line, in place of a card |
| Not defined yet (not a decision yet) | listed under **Open questions**, unnumbered | the *Open questions* section |

## Source labels

A **source label** is a label a source document gives its own parts: a review's findings
(F7), a plan's questions (OQ3), a review round's findings (R2-1), a plan's features (B2).
Tracker ids — work items, tickets, commits, a ticket-style key — are not source labels: they
keep the `plain-names` skill's rule, the plain name first and the id a trailing tag.

- Label first with its short name, per the `plain-names` skill's § Source labels.
- **In the title.** A decision raised from one labelled item opens its title on the label:
  **41 — F7 (oversize upload) · Cap the upload size?** The number stays the decision's
  handle, and the store's. On an answer page the label follows the title (the
  `decision-page` skill).
- **Replies by label.** The operator may answer by the label (`F7: a`); it is read as the
  decision whose title carries it, and echoed with both: *Read as: 41 — F7 (oversize
  upload) → (a) …* (`references/replies.md`).

A label the operator has never read, from a source they have not opened, still needs its
words: the short name is the gloss (SKILL.md § The floor, item 1).

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
stored **Context:**, its **What:**, any **Finding:**, any ▸ Open questions line, its ▸ Assumptions line and its
Impact line (and a block's table), right after the *while it waited* line:

**62 — back, as you asked ("until the load test finishes"):** move the job queue to the new
message broker?
*While it waited (1 day): the load test finished with no lost messages; nothing else changed.
Options and recommendation unchanged; impact unchanged.*
**Context:** the new broker has carried the email worker alone for two weeks as a trial, and the load test was the last check before the rest move. You left it at that trial · you decide whether every worker moves now or one goes first.
**What:** switch every worker service from the old job queue to the new message broker.
▸ Open questions — 1 open: whether the two workers not read rely on the old queue's ordering
▸ Assumptions — basis: **partial** · 1 assumption with its tripwire
**Impact:** later: the worker rollout stays paused · reach: every worker service and its on-call · ⚠ undo: (a) switch each config back within the week; after that the old queue is gone

*While it waited* always says whether the impact changed: *impact unchanged*, or what changed
in it — *impact changed: waiting now also holds the release*. When the options or
recommendation changed, say which and why: *Recommendation changed from (a) vendor the font
to (b) fetch it, because the CDN outage ended.*

**From the store.** When the caller's store keeps the card (the floor's fields under the
decision's record, with its raised-at time), a re-show renders that stored card — a card
record (`decision-card/5`) by `references/card-record.md`, a card with no format by
`references/legacy-cards.md` — and adds
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
revision. **A stored card without an Impact line** is backfilled the same way, its wait from
its (z) line and its reach, undo and cost from its options' impacts, never an effect, each
facet no record holds written *not recorded*, and stored as a revised card before it renders
in any view. The caller stores the
revised card (a missing field no record holds reads *not recorded*), and *while it waited*
says what changed. When the options or recommendation really changed, say which and why, and
the caller stores the new card.

**A cold re-show** — whenever the reader is cold (SKILL.md § Before you write) — shows each
open decision the reader is cold on at card level or above, never as a line only except as
paged (SKILL.md § Levels, the line-only rule), each opening with what changed while it
waited (*nothing changed* is worth saying, and so is *impact unchanged*). Under it the card
runs **Context:** (its stored Context, ending on where the operator left it), **What:**,
any **Finding:**, any ▸ Open questions line, the ▸ Assumptions line, **Impact:**, the options, then the ▸ Background line from its
stored *why now* (the fold holding its stored *why now* and *why ask*); a block's **Context:** bullets open with the same
Context. A stored card in an earlier form is read, and revised where it lacks a floor field,
by `references/legacy-cards.md`. A deferred decision whose
wake has not come is a card too, opening with its wake: *deferred until the release; no
answer needed before then*; it leaves its group and goes last, in the cards and the list
alike, so paging reaches it last. Open
questions still open are listed under *Open questions*. A cold re-show's heading has one
form: **Decisions** — *N open · shown again after a context reset · M shown in full · one ⚠
one-way*, naming what made the reader cold, and dropping *M shown in full* when nothing is
paged and the ⚠ part when there is none. With more than five, SKILL.md's paging rule applies
*(provisional — pending the operator's ruling)*: the rest are lines ending *(expand for the
card)*.
