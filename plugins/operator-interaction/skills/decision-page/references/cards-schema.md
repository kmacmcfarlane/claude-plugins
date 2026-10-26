# cards.json and the answers collection

The page (`assets/index.html`) renders whatever `cards.json` beside it holds, and writes one
answer document per decision to the artifact's `db`. This file is the schema for the page's
envelope, a page card, an excerpt and the answers collection. **Each card is a card record**,
`decision-card/5`, whose fields are the `decisions` skill's `references/card-record.md`; a
page card adds its layer `L` and its dependency line `dep`. `assets/cards.example.json` is a
complete, invented example: three decisions, each opening on its TLDR, then its Context, then
its Open questions fold, then its Assumptions fold, then its Impact. Its levels scale with the decision: a wide card with
every part a click from more detail, a ⚠ one-way card (every option with its reach, its
one-way option flagged) levelled too, and a small call raised from a source's labelled item
with no recommendation and no levels. One option carries the steps the operator takes to act
on it, and one slug names a decision not on the page.

**The page checks the data before it renders anything** and, when a check fails, shows *The
decisions can't be shown: cards.json is not valid* with the first problems found, and renders
nothing else. It refuses: a file with no `decision-page/5` stamp (*cards.json is in an older
format: upgrade it (`scripts/upgrade_cards.js`) and republish*), or a newer one (*this page
template is older than its data: update the plugins*); a card with no `decision-card/5` stamp,
or a newer one (named: the writer leaves that card off the page and hands it over); a card
holding a field the record no longer has (`o`, `blocks`, card-level `act`, `warn`, `unknown`,
`stakes`, `detail.o`); an `n` that is not a whole number of 1 or more, or is used twice; a `rev`
or `raised` that is not a UTC time; a `q` on more than one line; options that are not objects
with a single `a`–`z` letter and a title, out of letter order, or not ending in `z`; a `rec`
that is not one of the card's letters (or null without `norec`); a missing field the record
requires to render; a missing or blank `context`; a TLDR bullet that carries the
recommendation (one that opens with Rec, Recs, Recommend, Recommended or Recommendation
followed by a colon, a dash (a hyphen only with a space after it), a full stop, a bracket or
nothing, unless *by* follows; or one that says `rec (b)`, I or we recommend, my or our
recommendation, `(recommended)`, or `(b) is recommended`); an `impact` without its wait and
reach as text, or with an undo or cost that is not text; an `open` that is not a list of text;
an `assume` that is not a list of `{rests, tw}`, each non-empty text;
an option but (z) with no effect; on a ⚠ card, an option but (z) with no reach; an option
field that is not text; a `plan`, `pro` or `con` holding a line break (CR, LF, NEL, a line or
paragraph separator, a vertical tab or form feed); a `pros` or `cons` that is not a list of
text, holds more than five points, a point that is not text or one holding a line break, or is
empty on an option but (z); a `oneway` that is not true or false; an option flagged `oneway: true`
without its undo; an `act` on (z), or one that is not a non-empty list of steps as text, a step
holding a fill-in placeholder (an angle-bracketed word with no spaces, such as `<dir>` or
`<path>`), or a step holding a line break; a `label` that is not `{id, name}`, the id one word
and the name one line; a `basis` word outside the four; a layer whose fourth element
(`shared`) is not text; a `refs` entry for a decision still open (its `when` is `open`, or its
`a` says not yet answered), or for a number that is a card on the page; a `[[N]]` that is
neither a card nor a `refs` entry, in any card field, the lede or a layer's note or shared
context (an excerpt is not read); a `follow` list other than the fixed six; a `refs` key that
is not a number; an `evidence` that is neither text nor a non-empty list of text; a `detail`
that is not an object, or a malformed level (a bullet that is neither text nor `{t, sub}`, a
section that is not `{h, b}`, an object holding both `t` and `h`, a sub-bullet that is not
text, a list mixing bullets and sections, an Impact level with none of its four facets); an
option's `detail` that is not `[medium, high]`; a `detail.tldr` bullet that carries the
recommendation, at either level, its headings, bullets and sub-bullets counted in reading
order. Every text field is escaped wherever it reaches the page, attributes and ids included.

Text fields are plain text: the page escapes them. Two marks are rendered:

- `` `code` `` in backticks shows as code;
- `[[N]]` is a **decision slug**: it renders as *N · short name*; a click opens its card when
  it is on the page, and hovering or focusing it shows its tooltip (its Context and each
  option, the recommended one marked, and your answer; for a decision not on the page, the
  question, the answer and when), which a tap or click pins on a decision not on the page and
  a second tap, a tap elsewhere or Escape closes. N must be a card or a `refs` entry (its card's `t`, or the entry's
  `short`, is the short name): the page refuses any other N. Use a slug wherever a card
  mentions another decision by number.

**No ids on the page.** The page is the reader's only context: they are not in the
conversation. Refer to another decision by its slug, and to an item, a series, a branch or a
commit by its short name or title, with no id after it, in every field, titles included (the
page title, the layer titles). One exception: a source label a card declares in `label`
(F7), written with its short name beside it, *F7 (oversize upload)*, anywhere on the page;
bare, it is an id like any other. A fact that only an id carries (a commit hash the operator must
check out, say) goes in backticks in an option's `act` or in `evidence`, where it is something
to type or open. The runner lints an id anywhere the page shows text (SKILL.md step 2).

## Top level

| Key | Type | Required | What |
|---|---|---|---|
| `format` | `"decision-page/5"` | yes | the envelope's stamp: the template reads only this one (answer 343 (a)) |
| `page` | object | no | `title` (the heading and tab title; set by SKILL.md step 2's title rule), `lede` (one or two sentences: what this set of decisions is about; slugs allowed), `doc` (`{name, url}`, a reading copy; `url` must start `https://`, otherwise it is not shown) |
| `layers` | array | yes | the groups, in display order: `[key, title, note, shared]` each, `shared` optional. `note` is one sentence under the group heading, after *What they share:*. `shared`, text, marks a **bundle** (the `decisions` skill's `references/rendering.md` § A bundle as a group): the shared context, the terms and the source every card in it uses, in plain words, shown in a closed **Shared context** fold under the heading; each item is a whole card, whose Context may lean on it (the runner reads a card's Context with its bundle's shared context). A bundle holds two or more cards; one answer for every item stays one card naming each |
| `follow` | array | yes | the six follow-ups, exactly as in the example, in that order: `[key, label, placeholder, words prompt]`. Keys `later`, `tell me`, `expand`, `dig into`, `you decide`, `drop`; placeholders `[when]` on `later`, `[what]` on `tell me` and `dig into`, empty on the rest |
| `cards` | array | yes | one card per decision, in list order (the `decisions` skill's order) |
| `refs` | object | no | decisions mentioned by slug that are not on the page, keyed by number as a string: `{short, q, a, when}` — short name, the question as asked, the answer as given, when. Answered decisions only; one still open goes on the page as a card; a number that is a card is not a ref |

## A page card

A page card is a card record (`decision-card/5`, the `decisions` skill's
`references/card-record.md`: its fields, what each requires, an option, the levels) plus two
fields only a page has, never written into a record:

| Key | Type | Required | What |
|---|---|---|---|
| `L` | string | yes | its group: a `layers` key |
| `dep` | string | no | what it depends on, usually slugs with the answer that matters (`[[41]] (b)`), from the caller's `depends N:` lines; shown in the Dependencies fold, with its medium and high in `detail.dep`. Leave it out when the card depends on nothing: a card with no `dep`, or a none one, has no fold |

Each record field maps to a part of the `decisions` skill's card (its `references/rendering.md`
§ Card); the floor is met by the card. Where a page shows each:

- `t`, then `label` after it, muted, in every view: `t` · **F7** (oversize upload); a slug shows `t` alone;
- `tldr` first on the open card; then `context`; then the **What** part, never folded: `what`,
  what is decided in plain words, and for a set its `items`, every one listed, each its `name`, its
  `where` (muted), its `about`, and its `per` (its outcome under each option, in letter order, on a
  muted line under it; none when it fares the same under every option), the part labelled
  *What · N items* (F6, answer 290 (a)); then `open` in a closed **Open questions**
  fold, its summary the count and the first question; then the closed **Assumptions** fold,
  on every card: its summary *basis:* and the `basis` word, then the count of `assume`
  (*basis: partial · 2 assumptions with tripwires*; *basis: strong* alone with none), and
  inside, the Basis line (the word in a box, then `reason`, its levels in `detail.rec`), the
  `evidence` (its levels in `detail.evidence`), then each assumption in bold with its
  *tripwire:* under it; then the Impact, one facet a line
  (*later:*, *reach:*, *undo:* marked *⚠ undo:* when an option is flagged one-way, *cost:*);
  then `ifleft`, `roundcosts` and `ifunanswered`;
- the options, each its letter and `title`, the recommended one bold with a *recommended*
  pill, its `line` after the page's label (*because:* on the recommended option, *if chosen:*
  on every other but (z), *if left:* on (z)), then its `pro` and `con` as two rows under it,
  always visible, labelled **Pros** and **Cons** and laid out as its view's Effect, Reach,
  Undo and Cost are (the label in a column of its own, the text after it, no colon); (z) has no
  rows, even when given; then its
  `act` as **To act on (x):** under it, outside its view; and its **view** (F5, the v5 order of item
  9168), closed until the option is picked or its **More** pressed: **Plan in brief** (`plan`,
  labelled, opening at the plan, its `detail` levels stepping from it), then the **Pros | Cons**
  table (`pros` and `cons`, two columns side by side, each headed by its facet label, one point a
  row, at most five a side; a side with none is not drawn), then its Effect, Reach, Undo and Cost
  ((z)'s effect is its Wait). An older option with no `plan` shows its `text` in the plan's place,
  at its fullest level. The order is the same on every card, a ⚠ card's too, and every view
  starts closed;
- the recommendation is marked on its option (bold, the *recommended* pill and *because:*)
  and in the row's rec pill; there is no Recommendation part and no Rec line;
- the folds: **Background** (`why`, then `whyask` with `class` first; the first of the bottom
  folds; closed, its summary is *why now:* and the first sentence of `why`, a slug as its
  number, which the runner's `bgsum` lint keeps to about 25 words), then **Dependencies**
  (`dep`). The evidence is in the Assumptions fold, above.

**The closed row's effect** (answer 340 (a)): the recommended option's own `effect`, its letter
first, `→ (b) …`; with no recommendation, each option's in a few words, `(a) …; (b) …`.

**Context introduces every specific thing the card names.** Every label, number, acronym,
term of art or item that the flat part (`t`, the Impact, `tldr`, the option titles and one
lines) uses is introduced in `context`, or in the What part after it, as the `decisions` floor
requires: the flat part is what the operator reads, and an option's `plan` (or older `text`)
sits in its view. Two shapes need it most:

- **A count** ("four changes", "the three"). Where the card says what is decided (`t`, the
  TLDR, an option's title or line), a count names a set: list every item in `items`, the What
  part, one each with its name (*the four changes*: four items). The pre-publish runner
  **refuses** a card that counts two or more things there with no `items` list of that length
  (the set refusal; the page's `check()` never does, so an older published page still renders).
  Elsewhere, Context says what the things are, or lists them: *the review asked for four
  changes: X, Y, Z and W*.
- **A named mode, setting, review, plan or document** ("content mode", "the review"). Context
  gives it a one-line gloss: what it is, and where it comes from.

An item, a commit or a series is named by its short name or title, never by its id (§ No ids
on the page, above).

**The cold read** (the `decisions` skill's `references/worksheet.md` § The cold read, applied
to the flat part). Before publishing, list each noun phrase in the card's Impact, TLDR,
option titles and one lines that refers to a specific thing: a count, a named mode, setting,
review, plan or document, an item or a label. For each one, point to its gloss in
`context`. A phrase with no gloss gets one before the page goes out. The pre-publish runner
(SKILL.md step 2) lints counts and named things missing from `context` and the What part, and
ids wherever they are (the What part and its items included); those lints are proxies, and plain-word terms stay the cold read's. The same holds for
the medium and high renditions of the Impact and the TLDR, and each option's view (its `plan` and
the points of its Pros | Cons table, which picking the option opens), checked against
Context's **summary** only: each part steps alone, so the Context beside a TLDR at full
detail may be at its summary. A term a level introduces needs its gloss in Context's summary,
or in the level itself. Over an option's view the lint reads qualified names only ("content
mode"): a bare noun, a phrase opening on a function word ("to plan", "and review") and one
opening on a verb form ("reaches review") are left to the writer's cold read.

**Levels on the page.** A part with levels steps summary → medium → high → summary on a
click, the level replacing the part's text; a part steps alone, only through the levels it
has, and opens at its summary (an older option's `text` in its view opens at its fullest; a `plan` opens at the plan). Links
(`https://` only) are clickable in the medium and high renditions, in the fold parts at every
level and in an option's view; never in a heading, a visible part's summary, `act`, a
tooltip or a slug. Context's high holds the further facts the decisions block carries after
the card's Context (what was tried, what was answered before, where a list or number came
from). The page ignores a `detail` key it does not know; the runner lints it.

**Size.** The flat part of a card (title, Impact, TLDR, option titles and one-liners) stays
near 150 words; the basis reason sits in the closed Assumptions fold, so it is a fold part,
counted in the card in all at its top level and not in the flat part; each option's Pros and
Cons rows, and the points of its view's Pros | Cons table, count in the card in all too, not in the flat part; the folds carry the rest. `context` and an option's `act` are
outside that budget: what the operator needs to read the card, and to act on it, is never
folded away. Context's summary is one or two sentences, typically 30–60 words (the runner
lints past ~60); a term that needs a paragraph has its detail in its levels or a fold, with
its one-line gloss kept in Context.

Every card carries the decisions block's depth (decision 198), scaled to the decision, with
levels where the decision calls for them (decision 201). Each size is read at the
part's top level, its high when it has one, else its summary; words are counted as
whitespace-split:

| What | Size |
|---|---|
| The What part: `what`, one sentence; each item's `about` and `per`, a few words each | no cap: a set lists every item, and counts in the card in all |
| Background: `why` + `whyask`, each at its top level | ~150 |
| Each option but `z`: its top `plan` (or older `text`) + its effect, reach, undo and cost | ~60–120 |
| An option's `plan`, Plan in brief | 2–4 sentences, at most ~100 words |
| Evidence, at its top level | ~150, with the paths and links behind each claim |
| The card in all: the flat part and Context at their summary, the fold parts at their top level, each option's detail; not `act` | ~600–900 |
| A fold part's medium | between its summary and its high, about half its high |

The levels' own sizes are their shapes, linted as clear misses:

| What | Lint fires at |
|---|---|
| Context's summary | more than 2 sentences, or more than ~60 words |
| TLDR | more than 2 bullets |
| A summary or medium bullet, or a sub-bullet | more than one sentence, or more than ~14 words |
| A summary Impact facet | more than ~16 words |
| A fold part's summary, where the part has levels | more than 2 sentences |
| Medium | prose, sections, more than 6 bullets, or more than 2 sub-bullets on one bullet |
| The Impact's medium | a facet as a list rather than one bullet |
| High (not the Impact's) | anything but headed sections |

The sizes are soft. A small call gets a short card: do not pad. Depth is written from the
sources (SKILL.md step 2), and a fact no source holds goes under `open`, never into the
depth to fill a size. **The cost** falls on the cards that carry levels: the example's small
call (card 43) carries none, so it costs nothing extra. The pre-publish runner lints only
clear misses: thin (about 40% of a size) only on a part that carries levels, long (1.5 times)
on any.

**What the page adds.** The page opens on a map of its groups under the progress bar, a
button per group with its count, and **Expand all** and **Collapse all**; every card is closed
to its one-line row, in its group: the number, the title, the ⚠ pill on a one-way card, the
rec pill and the recommended option's effect with its letter, and the answer, with **Use
recommendation** (on a card with one) and **Later** beside the row, outside it. A click on the
row opens the card. Every view shows impact: a card's row the recommended option's effect; an
open card the Impact, one facet a line; and each option's view its own effect, reach,
undo (where it is one-way or costly) and cost. Each group opens on a band: the *Group* label,
its title, a count of its decisions and *What they share:* its note; a bundle adds a closed
**Shared context** fold whose summary is the context's first sentence. An Impact describes the system the work builds, never the review or the process, which
is its Wait: the lede says so, and the runner's `process` lint catches a process phrase in an
option's effect or reach, or the Impact's reach. A card with a `label` shows it after its title,
muted, with its short name, in every view. It opens every card on its TLDR, then its Context,
then its What, then its Open questions, then its Assumptions, then its Impact: a page is read away from the conversation, so its
reader is treated as cold. Any part with `detail` toggles its level on a click, on its button
or on its text (never on a link or a control, nor while text is selected, so it can be
copied); the folds (Open questions and Assumptions above the Impact, Background and
Dependencies after the answer) keep their order and stay closed; each option has a **More** button at its right, outside its label, which opens or closes the
option's view alone. **Picking an option** (its radio) opens its view and closes the card's other
open one, as **More** would (the operator: "Selecting an option opens it as if More is pressed");
a follow-up leaves the views as they are. A click on an option already picked opens its view too
(the browser sends no change then). A pick saved earlier and shown again on a reload leaves its
view closed, as every view starts. There is no Options in full fold: it repeated each option's **More** (the
operator, 2026-10-14). The basis word, the titles, the one lines, the Pros and Cons rows,
`act`, and the round and default lines are static. A `⚠ one-way` card's options start closed
too, until picked (the build design that opened them is reversed by F5); the ⚠ shows on the
card's border, its row's ⚠ pill, the Impact's *⚠ undo:* line and the *⚠ Undo* in the option's
view. It gets no special control: the read-back of a one-way pick happens in chat, when the
answers are read back.

**None is not shown** (the operator, 2026-10-14: *if any sub-section is empty or none, just
don't display it*). A part, facet or field that is missing, blank, or says only `none`,
`none.`, `n/a`, `n/a.` or a lone dash (trimmed, any case) is left off
the page, by one test in the template: a `dep` (no Dependencies fold), an `open` list (no Open
questions fold), a `what` and `items` (no What part), an item's `where`, `about` or `per` entry, an Impact `cost`, at every level, an option's effect, reach or cost, an
`evidence`, `ifleft`, `roundcosts`, `ifunanswered`, an option's one line, its `pro` or `con`
(a none one has no row). A writer may simply
leave such a field out; the optional ones were always optional. Shown whatever they say,
because their none is a statement: the required Impact facets (`wait`, `reach`) and an `undo`
when given (*undo: none* says an option is one-way), each option's Undo when given, and the
`basis` word (so every card has its Assumptions fold). An `assume` list that is empty,
or whose assumptions are none, shows none, and its summary reads *basis:* and the word alone.
The check still requires the two facets. A missing undo is not a none: it says
every option, or that option, is reversible at little cost.

## Republishing older data

A `cards.json` with no `decision-page/5` stamp is in an older format, and the template refuses
it. Upgrade it first with `scripts/upgrade_cards.js` (format only, every `rev` kept byte for byte), then
republish. Any change to a card gets a new `rev`, Context included: an **Added:** line after `tell me`, more detail after `expand`, a `dig into` finding, a corrected fact, a re-ask. Only a format-only upgrade keeps it: an older card moved to `decision-card/5` by the `decision-page` skill's `scripts/upgrade_cards.js`, its fields moved and none added. A fact drawn from anywhere outside the card is new information: a new `rev`.
What each older era held, and what a republish writes into it, is the `decisions` skill's
`references/legacy-cards.md`.

## An excerpt

An excerpt is verbatim multi-line text (code, a log, a diff, a config block, test output),
shown as a code block. No card field the page shows carries one yet: the finding body and the
excerpt attachment will, and each checks and draws it the same way.

| Key | Type | Required | What |
|---|---|---|---|
| `text` | string | yes | the lines, verbatim and non-blank. Line breaks and tabs are kept (CRLF and CR read as one break; one trailing break is dropped) |
| `lang` | string | no | a short label for what the text is (`python`, `diff`, `log`): a letter or digit, then letters, digits and `+ # . _ -`, 24 at most. Shown as a tag over the block; nothing is highlighted |
| `src` | string | no | where the text came from, on one line: a path and line range at a commit, or the command and when it ran. Plain text, shown over the block |

**The text is data, never markup.** Every character is escaped, and nothing in an excerpt is
parsed: a backtick, a `[[N]]`, an `https://` address, an HTML tag such as `</script>` or
`<img onerror=…>`, and a fence (```` ``` ```` or `~~~`) all show as the characters they are.
Write the lines bare, with no fence around them: the page draws the block. A control or
bidirectional character (a zero-width space, a right-to-left override) shows as a visible
tag naming it, `U+202E`, so the text cannot read other than it is. `src` is plain text the
same way.

**The page refuses**, wherever a field carries one, an excerpt that is not an object, with blank `text`, a `lang` outside its
label shape, or a `src` that is not one line of text.

**Size.** About 80 lines or 4 KB. Cut a longer one and say so where the cut is, in the text
(`… lines 40–120 left out; full at <where> …`). Long lines scroll inside the block, never
the page.

**Safety.** Never a secret's value: the line shows `[redacted: key <name> in <path>]`. Never
personal data from any source (logs, fixtures, configs, test output), and nothing from a third
party's private source. Never Claude Code's source, prompts or internal names.

## The answers collection

The page writes collection `answers`, one document per decision, id the decision number as a
string. Written on every click, and 600 ms after typing stops, one write at a time per
document; a cleared answer deletes the document. Only the artifact's owner can write it (the
publish rule in SKILL.md step 3); any other viewer sees the answers read-only.

| Field | Type | What |
|---|---|---|
| `n` | integer | the decision number |
| `choice` | string or null | an option letter, a follow-up key (`later`, `tell me`, `expand`, `dig into`, `you decide`, `drop`), or null for words only |
| `kind` | string or null | `option`, `follow-up`, or null for words only |
| `words` | string | the operator's words, verbatim; for `later`, `tell me` and `dig into` they are its `[when]` or `[what]`; empty when none |
| `rec` | string or null | the recommendation shown when they answered |
| `rev` | string | the card's `rev` when they answered: the revision this answer was given to |
| `at` | string | ISO-8601 time of the write, by the operator's browser clock: compared only with other `at` values for the same number, never with the agent's clock or with `rev` |

**Which answers count.** An answer counts only when its `rev` equals its card's current
`rev`: no clocks are compared, so a browser clock ahead of or behind the agent's makes no
difference. The collection outlives a republish, so a revised card under the same number still
has the answer given to its earlier version; that answer carries the old `rev`, the page shows
it as *open*, unticked, and the read-back skips it. The operator's next click on the revised
card replaces it. A format-only upgrade keeps every `rev`, so answers given before it keep
counting. Answers to numbers not on the current `cards.json` are skipped too. The page
reads the collection live, so an answer set in the owner's other tab shows at once.

**Already handed over.** The read-back compares a counting answer's `at` with the `at` it last
handed over for that number. Equal: the same answer, unchanged. Different: the operator changed
it since. Both values come from the operator's browser, so this too needs no shared clock.
The `at` is the read-back's marker only: it is never handed over as the time a card was shown
or seen (SKILL.md steps 3 and 6 use your clock for those).
