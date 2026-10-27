# cards.json and the answers collection

The page (`assets/index.html`) renders whatever `cards.json` beside it holds, and writes one
answer document per decision to the artifact's `db`. This file is the schema for the page's
envelope, a page card, an excerpt and the answers collection. **Each card is a card record**,
`decision-card/5`, whose fields are the `decisions` skill's `references/card-record.md`; a
page card adds its layer `L` and its dependency line `dep`. `assets/cards.example.json` is a
complete, invented example: three decisions, each opening on its TLDR, then its Context, then
its What (one with its Scope, one with its Likelihood and Best response?, one with its Finding), then its Open questions fold, then its Assumptions fold, then its Impact; the wide card carries three attachments (an excerpt, a table and check results, one named by a link in its evidence) and ends on a Rejected alternatives fold. Its levels scale with the decision: a wide card with
every part a click from more detail, a ⚠ one-way card (every option with its reach, its
one-way option flagged) levelled too, and a small call raised from a source's labelled item
with no recommendation and no levels, whose Finding shows its excerpt. One option carries the steps the operator takes to act
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
an `assume` that is not a list of `{rests, tw}`, each non-empty text; a `finding` that is not
an object, has no `mechanism` as text, or one holding a line break, a `title` or `where` that is
not one line of text, a `label` that is not `{id, name}` or, on a card that carries a `label`, is
not that same label, or an `excerpt` the excerpt rules refuse (§ An excerpt); a `scope` that is
not an object, has a `level` other than `required`, `shapes` or `outside`, a `says` that is not
one line of text, or none on a `required` or `shapes` scope; a `likelihood` that is not an
object, has a `kind` other than `observed` or `evidence`, or a `seen` that is not one line of
non-blank text; a `best` that is not one line of text, or one on a card with no `likelihood`;
a `rejected` that is not a list of `{t, why}`, an alternative with no `t` as text or one holding a
line break, or a `why` that is not a list of one or more reasons, each one line of text;
an `attached` that is not a list, or an attachment the attachment rules refuse (§ An
attachment);
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

Text fields are plain text: the page escapes them. Three marks are rendered:

- `` `code` `` in backticks shows as code;
- `[[N]]` is a **decision slug**: it renders as *N · short name*; a click opens its card when
  it is on the page, and hovering or focusing it shows its tooltip (its Context and each
  option, the recommended one marked, and your answer; for a decision not on the page, the
  question, the answer and when), which a tap or click pins on a decision not on the page and
  a second tap, a tap elsewhere or Escape closes. N must be a card or a `refs` entry (its card's `t`, or the entry's
  `short`, is the short name): the page refuses any other N. Use a slug wherever a card
  mentions another decision by number;
- `[[att:id|label]]` is a **link to an attachment** (F3): it shows `label` with a dotted
  underline, and a click opens the card's Attached fold and the attachment `id`, scrolls to it
  and marks it briefly. `id` must be one of the card's own attachments: the pre-publish runner
  refuses any other, and the page shows its label as plain text, so an older or hand-edited
  page still reads. Anywhere off a card (the lede, a layer's note) it is its label.

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
| `page` | object | no | `title` (the heading and tab title; set by SKILL.md step 2's title rule), `lede` (one or two sentences: what this set of decisions is about; slugs allowed; when any card carries an excerpt, an excerpt-shaped attachment or a Finding's excerpt, it names the repos they come from, so the operator knows what a share would expose: the runner's `lede` lint), `doc` (`{name, url}`, a reading copy; `url` must start `https://`, otherwise it is not shown) |
| `layers` | array | yes | the groups, in display order: `[key, title, note, shared]` each, `shared` optional. `note` is one sentence under the group heading, after *What they share:*. `shared`, text, marks a **bundle** (the `decisions` skill's `references/rendering.md` § A bundle as a group): the shared context, the terms and the source every card in it uses, in plain words, shown in a closed **Shared context** fold under the heading; each item is a whole card, whose Context may lean on it (the runner reads a card's Context with its bundle's shared context). A bundle holds two or more cards; one answer for every item stays one card naming each |
| `follow` | array | yes | the six follow-ups, exactly as in the example, in that order: `[key, label, placeholder, words prompt]`. Keys `later`, `tell me`, `expand`, `dig into`, `you decide`, `drop`; placeholders `[when]` on `later`, `[what]` on `tell me` and `dig into`, empty on the rest |
| `cards` | array | yes | one card per decision, in list order (the `decisions` skill's order: inside a layer, each card after every card in its layer that its `dep` names, then the precedence; the runner's `deporder` lint flags a card placed before one in its own layer that its `dep` names, a pair in a dependency cycle skipped) |
| `refs` | object | no | decisions mentioned by slug that are not on the page, keyed by number as a string: `{short, q, a, when}` — short name, the question as asked, the answer as given, when. Answered decisions only; one still open goes on the page as a card; a number that is a card is not a ref |

## A page card

A page card is a card record (`decision-card/5`, the `decisions` skill's
`references/card-record.md`: its fields, what each requires, an option, the levels) plus two
fields only a page has, never written into a record:

| Key | Type | Required | What |
|---|---|---|---|
| `L` | string | yes | its group: a `layers` key |
| `dep` | string | no | what it depends on, one line in the dependency line's sentence form, each decision a slug: `only if [[41]] is (a) or (c), and after [[47]] is answered, whatever its answer` (*The dependency line*, below). Shown as the dependency line, after the TLDR; it has no levels, and an older `detail.dep` is not shown. Leave it out when the card depends on nothing: a card with no `dep`, or a none one, has no line |

Each record field maps to a part of the `decisions` skill's card (its `references/rendering.md`
§ Card); the floor is met by the card. Where a page shows each:

- `t`, then `label` after it, muted, in every view: `t` · **F7** (oversize upload); a slug shows `t` alone;
- `tldr` first on the open card; then, on a card with a `dep`, the dependency line (*The
  dependency line*, below); then `context`; then the **What** part, never folded: `what`,
  what is decided in plain words, and for a set its `items`, every one listed, each its `name`, its
  `where` (muted), its `about`, and its `per` (its outcome under each option, in letter order, on a
  muted line under it; none when it fares the same under every option), the part labelled
  *What · N items* (F6, answer 290 (a)); then, on a card raised from a finding, the **Finding**
  part, never folded (F7, answer 337 (a)): its head, the `finding`'s `label` with its short name
  and its `title` after a colon, then ` — ` and its `where` (mono), then its `mechanism`, then its
  `excerpt` drawn as a code block (§ An excerpt); then, where the work states requirements, the
  **Scope** part, never folded, one line (F8, answer 266 (b)): the `scope`'s `level` as a small
  boxed word (*required*, *shapes the work*, *outside the criteria*), then its `says`, the
  criterion it rests on or what in the work it decides; then, on a risk decision, the
  **Likelihood** part, never folded (F9, answers 267 (a) and 339 (a)): the `likelihood`'s `kind`
  as a small boxed word (*observed*, *evidence*), then its `seen`, then **Best response?** and
  `best` on a line of its own; then `open` in a closed **Open questions**
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
  number, which the runner's `bgsum` lint keeps to about 25 words), then **Attached**
  (`attached`; F3, answers 264 (a), 291 (a) and 286 (b)): closed, its summary the count and the
  titles, *2: title · title*; open, each attachment its own entry, closed, showing its title, a
  kind pill and its source line, and opening on a click to its body in its kind's shape
  (§ An attachment), then **Rejected alternatives** (`rejected`; F2, answer 286 (b)), the last: closed,
  its summary the count and the titles, *2: title · title*, a slug as its number; open, each
  alternative's `t` on a bold line with its `why` reasons as bullets under it. The evidence is
  in the Assumptions fold, above.

**The dependency line.** A card that waits on another decision's answer says so on one line,
second on the card, after the TLDR and before Context, labelled *depends:* (03ab F3; the v4 layout, answer 313; the chat
card's line is the `decisions` skill's `references/rendering.md` § Card). `dep` is written at
page time from the caller's stored dependency (a librarian's `depends N:` lines, read as each
decision's `depends` targets `{n, repo, letter}`), never from the card record, which holds no
`dep`:

- a target with a letter: `only if [[M]] is (x)`; letters on the same M are alternatives, `is
  (a) or (c)`, three or more `is (a), (b), or (c)`;
- a target with no letter: `after [[M]] is answered, whatever its answer`;
- different Ms all apply, joined by `, and `;
- a target in another repo (`<repo>#M`) has no slug: it is named in words, `<repo>'s M (name)`
  where the caller knows its name, else `<repo>'s decision M`, as the chat card names it;
- a target that is open goes on the page as a card; an answered one not on the page gets a
  `refs` entry (§ Top level), as every slug does.

The page escapes the line and draws each slug in it by the reference rule: a decision on the
page reads `M (name)`, the line's own wording and its one exception to *N · short name*, as a
link that opens that card, with the card's tooltip; a decision in `refs` keeps its slug,
*N · short name*, and its tooltip. An older `dep` (`[[41]] (b)`) renders as written after
*depends:*. A `dep` that is not one line of text is refused.

**The closed row's effect** (answer 340 (a)): the recommended option's own `effect`, its letter
first, `→ (b) …`; with no recommendation, each option's in a few words, `(a) …; (b) …`.

**Context introduces every specific thing the card names.** Every label, number, acronym,
term of art or item that the flat part (`t`, the Impact, `tldr`, the option titles and one
lines) uses is introduced in `context`, or in the What part after it, as the `decisions` floor
requires: the flat part is what the operator reads, and an option's `plan` (or older `text`)
sits in its view. Two shapes need it most:

- **A count** ("four changes", "the three"). Where the card says what is decided (`t`, the
  TLDR's first bullet, an option's title or line but (z)'s), a count names a set: list every
  item in `items`, the What part, one each with its name (*the four changes*: four items). The
  pre-publish runner **refuses** a card that counts two or more things there with no `items`,
  or fewer than the largest count (the set refusal; the page's `check()` never does, so an
  older published page still renders); a list of another length is the `set` lint. **A card the
  upgrader carried over**, its `upgraded` marker naming the `rev` it still has, gets the set
  check as the `set` lint, never a refusal: the upgrade is lazy and seamless, and every `rev` is
  kept. Once a writer revises it, with a new `rev`, it is refused like any card until its items
  are listed. A count of 100 or more is the `set` lint, never a refusal. A set named by a rule that picks out its members (*the pages that cite the retired setup guide*) keeps its count out of the checked places (the title, the first TLDR bullet, the option titles and lines), or lists its items.
  Not a set's count: a four-digit year; a numeral right after a capitalised word inside the text (*Python 2*, *Node 22*, *HTTP 404*; a text that opens on the name counts it, so write *Support Python 3 only*); a date (*26 October*); a list of labels (*findings 3, 4 and 7*); a numeral right after a singular label noun from a closed list (principle, step, tier, option, rule, finding, item, section, …), or after a plural one before the text's end, punctuation, a function word or a verb and its object (*principle 3*, *step 2 of the guide*, *tier three*); after a verb or any other word it counts (*Retire 3 plugins this quarter*), *N
  times*, a range, a number after a slash, a sum of money (*$30*), a count of rounds, a setting's value after *to* or *at* (*set the timeout to 30*), *N of the …* (but not after *all*, *both* or *each*), a quantity of a unit (*600 words*),
  and the options themselves counted (*choose between the two options*). Elsewhere, Context says what the things are, or lists them: *the review asked for four
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
(SKILL.md step 2) lints counts and named things missing from `context` and the What part (the
Finding's `title` and `mechanism`, the Scope's `says`, the Likelihood's `seen` for named things
and `best`, included), and ids wherever they are (the What part and its items, the Finding but
its excerpt, the Scope, the Likelihood and Best response?, and each rejected alternative's `t` and
`why`, and each attachment's title, source line and text but an excerpt-shaped body,
included); each rejected alternative's `t` and each attachment's `title` are read for counts
and named things too, as their folds' summaries show them (the rest sits in the closed folds,
as the other folds' text does); an observed count in
`seen` is the fact the line gives, so the count lint leaves it; those lints are proxies, and plain-word terms stay the cold read's. The same holds for
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
| The Finding: its `title`, `where` and `mechanism` (one to three sentences) | counts in the card in all; its `excerpt` does not, and has its own size (§ An excerpt) |
| The Scope: its `says`, one line | counts in the card in all |
| The Likelihood: its `seen` and `best`, one line each | count in the card in all |
| Rejected alternatives: each `t` and its `why` reasons, a line each | count in the card in all |
| Attached: about six a card; an excerpt-shaped body about 80 lines or 4 KB | never in the card in all: an attachment is opened when needed (the runner's `attached` lint) |
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
muted, with its short name, in every view. It opens every card on its TLDR, then its dependency line when it waits on another decision, then its Context,
then its What, then its Finding when it has one, then its Scope and its Likelihood when it has them, then its Open questions, then its Assumptions, then its Impact: a page is read away from the conversation, so its
reader is treated as cold. After the Impact come the round lines (*If left:*, *A round costs:*, *If unanswered:*), then
the answer (each option with its line, its **Pros** and **Cons** rows and **More**; the follow-ups; the words), then
*Clear answer*, then the bottom folds (the v5 order, F11; `tests/test_layout.py` pins it). Any part with `detail` toggles its level on a click, on its button
or on its text (never on a link or a control, nor while text is selected, so it can be
copied); the folds (Open questions and Assumptions above the Impact, Background, Attached
and Rejected alternatives after the answer) keep their order and stay closed; each option has a **More** button at its right, outside its label, which opens or closes the
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
the page, by one test in the template: a `dep` (no dependency line), an `open` list (no Open
questions fold), a `what` and `items` (no What part), a `finding`'s `mechanism` (no Finding part)
and its `title` or `where`, a `scope`'s `says` (its level word alone), a `likelihood`'s `seen` (no
Likelihood part, and no Best response? with it), a `best` (no Best response? line), an `attached` list (no Attached fold) or an attachment's `title` (that attachment left out), a `rejected` list (no Rejected alternatives fold), an
alternative's `t` (that alternative left out) or a `why` reason, an item's `where`, `about` or `per` entry, an Impact `cost`, at every level, an option's effect, reach or cost, an
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
shown as a code block. The finding's `excerpt` carries one (F7), and so does the `body` of an
`excerpt` or `preview` attachment and of a `mock` example (F3); each checks and draws it the
same way. An excerpt is never read by the id lint or the cold
read: it is the source's text as it stands.

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
same way. **The characters the page tags**, in the text and in `src`, exactly: the C0 controls
U+0000–U+0008 and U+000B–U+001F (every C0 control but tab and line feed; a carriage return in
the text is read as a line break first), DEL and the C1 controls U+007F–U+009F, the soft
hyphen U+00AD, the Arabic letter mark U+061C, the Mongolian vowel separator U+180E,
U+200B–U+200F (the zero-width spaces and joiners and the directional marks), U+2028–U+202E
(the line and paragraph separators and the directional embeddings and overrides),
U+2060–U+2069 (the word joiner, invisible operators and the directional isolates), the byte
order mark U+FEFF, the tag characters U+E0000–U+E007F, the variation selectors
U+E0100–U+E01EF, the interlinear annotation marks U+FFF9–U+FFFB, the combining grapheme
joiner U+034F, the Hangul fillers U+115F, U+1160, U+3164 and U+FFA0, the Khmer inherent
vowels U+17B4 and U+17B5, and the Mongolian free variation selectors U+180B–U+180F.

**The page refuses**, wherever a field carries one, an excerpt that is not an object, one holding a key
other than `text`, `lang` and `src`, with blank `text`, a `lang` outside its
label shape, or a `src` that is not one line of text.

**Size.** About 80 lines or 4 KB. Cut a longer one and say so where the cut is, in the text
(`… lines 40–120 left out; full at <where> …`). Long lines scroll inside the block, never
the page.

**Safety.** Never a secret's value: the line shows `[redacted: key <name> in <path>]`. Never
personal data from any source (logs, fixtures, configs, test output), and nothing from a third
party's private source. Never Claude Code's source, prompts or internal names.

## An attachment

Material a decision rests on, carried with the card in `attached` and opened when needed (F3;
answer 264 (a) adopted the attachments draft as written; 291 (a), with the operator's words,
folds them closed with links to them; 286 (b), with the operator's words, set the kinds below).
It keeps the card short and puts what the card talks about one step away. Nothing the decision
needs moves into one: an attachment never counts in the card in all, and the floor stays on the
card.

| Key | Type | Required | What |
|---|---|---|---|
| `id` | string | no | lower-case letters, digits and `-`, each its own on the card: what a `[[att:id\|label]]` link names |
| `kind` | string | yes | one of the kinds below; the page refuses any other, `evidence` included (it is the card's own `evidence`, in the Assumptions fold) |
| `title` | string | yes | one line: what it shows on this card |
| `src` | string | no | one line, its source line: where it came from; a `preview` needs one |
| `body` | by kind | yes but on `link` | its content, in the shape of its kind |
| `url` | string | on `link` | one `https://` address, shown as the link |
| `pointer` | string | no; `summary` only | one line: where the full text lives, shown as *Full text:* |
| `form` | string | on `example` | `mock` (drawn as a code block) or `narrative` (drawn as prose) |

| Kind | Carries | `body` | Drawn as | Source line |
|---|---|---|---|---|
| `excerpt` | verbatim lines (code, a log, a diff, a config block, test output, a quoted draft) | an excerpt (§ An excerpt) | a code block | a path and range at a commit, or the command and when it ran |
| `summary` | a few lines in the writer's words, and a `pointer` | text or a list of paragraphs | prose, then *Full text:* and the pointer | the full text's place |
| `link` | a public page (vendor docs, a changelog, a standard) and why it matters | its note: text or paragraphs, optional | the `url` as a link, then the note | where it was cited |
| `example` | invented text showing what an option would mean in a case | `mock`: an excerpt; `narrative`: text or paragraphs | a code block, or prose | always *invented to illustrate*: the page shows it, then any `src` |
| `preview` | a text mock of the changed card or output, never HTML or an image | an excerpt | a code block | *invented to illustrate*, or the command that produced it |
| `table` | a comparison grid | `{cols, rows}`: `cols` one-line headings, each row a list of one-line cells, one per column | a table, scrolling sideways in its own box | its sources |
| `matrix` | who is affected | `{cols, rows}`, as `table` | a table | its sources |
| `steps` | a runbook | a non-empty list of `{t, d}`: `t` one line, `d` text, optional | a numbered list, each step bold with its detail under it | the plan section |
| `checks` | check results | a non-empty list of `{s, t, d}`: `s` `pass`, `fail` or `pending`, `t` one line, `d` text, optional | a tally (*2 pass · 0 fail · 1 pending*), then a status list, each led by its status | how and when they ran |
| `depmap` | how decisions wait on each other | a non-empty list of nodes `{n, name, rel, note, self, kids}`: `n` a decision number, `name` its short name, one line; `rel` and `note` one line, optional; `self` true on this card's own node; `kids` a non-empty list of nodes | a tree: each node its relation, then *N · name* (a card on the page opens on a click), then its note, its children nested under it | the store or the series |

Alternatives considered and assumptions with tripwires, which 286 (b) also named, are card
folds (Rejected alternatives, Assumptions), not attachment kinds. A new kind that fits a shape
above is one row here and in the writer digest, one value in the page's list (`ATT_KINDS`) and
the upgrader's, its chat line in the `decisions` skill's `references/rendering.md` § Folds,
and one test case; one that needs a new shape (an image, a chart) is a page change through the
`artifact-design` skill, with its own escaping tests.

**The page refuses** an `attached` that is not a list, and an attachment that is not an object;
whose `kind` is not in the list; that holds a field its kind does not have; whose `id` is off its
shape or used twice on the card; whose `title` is not one line of text or whose `src` is not one
line; and whose `body` is off its kind's shape: an excerpt the excerpt rules refuse (§ An
excerpt), a `preview` with no source line in its `src` or its excerpt's `src`, an `example` with no
`form` of the two, a `summary` or `narrative` body that is not text or a non-empty list of
paragraphs, a `pointer` of more than one line, a `link` with no `https://` `url`, a table with
no headings or no rows or a row of another width or a cell holding a line break, a step or a
check with no one-line `t` or a field it does not have, a status not one of the three, and a
node with no decision number or name.

**Every text is escaped** (the title, the source line, the pointer, prose, cells, steps,
statuses and nodes, through the same escaping as every field, the marks above rendered in
them); an excerpt-shaped body is drawn by the code-block renderer, verbatim and never parsed.
**Safety:** what a private page may carry is the attachments draft's rule: excerpts of code,
configs, test output and logs from the repos its decisions are about; never a secret's value
(where it is kept and under which key, `[redacted: key api_token in /etc/app/env]`), never
personal data from any source (logs, fixtures, configs, test output), never material from a
third party's private source, never Claude Code's source, prompts or internal names. The
pre-publish runner refuses a line in an attachment, or in the Finding's excerpt, that looks
like a secret, naming where it is and its key, never the value; without node, SKILL.md step 2's
grep step runs the same patterns over `cards.json`. The patterns are a net, not a proof: a value holding a backslash, quote or space in its first 16 characters, a key running more than 80 characters past its keyword, or more than 80 spaces around its `=` or `:` passes both; the cold read's item 6 is the check for those.

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
