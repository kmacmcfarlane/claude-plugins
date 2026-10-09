# cards.json and the answers collection

The page (`assets/index.html`) renders whatever `cards.json` beside it holds, and writes one
answer document per decision to the artifact's `db`. This file is the schema for both.
`assets/cards.example.json` is a complete, invented example: three decisions, each opening on
its TLDR, then its Context, then its Impact across all its options. Its levels scale with the
decision: a wide card with every part a click from more detail, a ⚠ one-way card (with its
Impact table rows) levelled too, and a small call with no recommendation and no levels. One
option carries the steps the operator takes to act on it, and one slug names a decision not on
the page.

**The page checks the data before it renders anything** and, when a check fails, shows *The
decisions can't be shown: cards.json is not valid* with the first problems found, and renders
nothing else. It refuses: an `n` that is not a whole number or is used twice; an option letter
that is not a single `a`–`z`; options out of letter order or not ending in `z`; a `rec` that is
not one of the card's letters (or null without `norec`); a missing required field; an empty
`rev`; a missing or blank `context`; a TLDR bullet that carries the recommendation (one that
opens with Rec, Recs, Recommend, Recommended or Recommendation followed by a colon, a dash (a
hyphen only with a space after it), a full stop, a bracket or nothing, unless *by* follows;
or one that says `rec (b)`, I or we recommend, my or our recommendation, `(recommended)`, or
`(b) is recommended`); an
`impact` without its effect, wait, reach and undo as text; a `basis` word outside
the four; a `follow` list other than the fixed six; a `refs` key that is not a number; a ⚠
card without its `blocks`; a `blocks` entry that is not an option letter other than `z`, or
lacks its text; an `act` that is not keyed by option letters other than `z`, a key whose list
of steps is empty or holds anything but text, a step holding a fill-in placeholder (an
angle-bracketed word with no spaces, such as `<dir>` or `<path>`), or a step holding a line
break; an `evidence` that is neither text nor a non-empty list of text; a `detail` that is not
an object, or a malformed `detail` entry (a bullet that is neither text nor `{t, sub}`, a
section that is not `{h, b}`, an object holding both `t` and `h`, a sub-bullet that is not
text, a list mixing bullets and sections); a `detail.o` key that is not an option letter other
than `z`; a `detail.tldr` bullet that carries the recommendation, at either level, its
headings, bullets and sub-bullets counted in reading order. Every text field is escaped
wherever it reaches the page, attributes and ids included.

Text fields are plain text: the page escapes them. Two marks are rendered:

- `` `code` `` in backticks shows as code;
- `[[N]]` is a **decision slug**: it renders as `[N · short name]` and opens decision N in a
  popup on hover or click. N is a decision on the page (its card's `t` is the short name) or a
  key of `refs`; any other N renders bare. Use a slug wherever a card mentions another
  decision by number.

**No ids on the page.** The page is the reader's only context: they are not in the
conversation. Refer to another decision by its slug, and to an item, a series, a branch or a
commit by its short name or title, with no id after it, in every field, titles included (the
page title, the layer titles). A fact that only an id carries (a commit hash the operator must
check out, say) goes in backticks in `act` or `evidence`, where it is something to type or
open. The runner lints an id anywhere the page shows text (SKILL.md step 2).

## Top level

| Key | Type | Required | What |
|---|---|---|---|
| `page` | object | no | `title` (the heading and tab title), `lede` (one or two sentences: what this set of decisions is about; slugs allowed), `doc` (`{name, url}`, a reading copy; `url` must start `https://`, otherwise it is not shown) |
| `layers` | array | yes | the groups, in display order: `[key, title, note]` each. `note` is one sentence under the group heading |
| `follow` | array | yes | the six follow-ups, exactly as in the example, in that order: `[key, label, placeholder, words prompt]`. Keys `later`, `tell me`, `expand`, `dig into`, `you decide`, `drop`; placeholders `[when]` on `later`, `[what]` on `tell me` and `dig into`, empty on the rest |
| `cards` | array | yes | one card per decision, in list order (the `decisions` skill's order) |
| `refs` | object | no | decisions mentioned by slug that are not on the page, keyed by number as a string: `{short, q, a, when}` — short name, the question as asked, the answer as given, when |

## A card

Each field maps to a part of the `decisions` skill's card (its `references/rendering.md`
§ Card); the floor is met by the card, so a field the floor needs is required here.

| Key | Type | Required | Card part | Shown |
|---|---|---|---|---|
| `n` | integer | yes | the decision number, the caller's own, never reused | everywhere |
| `L` | string | yes | its group: a `layers` key | groups the map and the cards |
| `t` | string | yes | the short name, 2–6 words, a noun phrase (it is what a slug shows) | title |
| `rev` | string | yes | the card's revision: a label that changes whenever the card does. Any change to a card gets a new `rev`, Context included: an **Added:** line after `tell me`, more detail after `expand`, a `dig into` finding, a corrected fact, a re-ask. Only the one-time format migration keeps it: a card written before Context existed, whose own `what` and resume cue move into `context`, and whose terms are glossed from its own folds alone. A gloss drawn from anywhere outside the card is new information: a new `rev`. An ISO-8601 UTC time when you write it (`2026-01-12T09:30:00Z`) is the convention, but it is only ever compared for equality, never as a time | not shown; the page copies it into each answer, and it decides which answers count (below) |
| `context` | string | yes | **Context:** one or two sentences: the terms, items and concepts the rest of the card uses, each introduced in plain words, by name and never by id; then where the operator left it (the `decisions` cue), when there is one. The TLDR says what is decided, so Context does not repeat it. Context introduces every specific thing the card names. Two shapes need it most: a count ("four changes", "the three"), for which Context says what the things are, or lists them; and a named mode, setting, review, plan or document ("content mode", "the review"), which Context gives a one-line gloss: what it is, and where it comes from. Written from the caller's stored What, its cue and the card's terms, with the cold read (below) run on it | flat on the open card, under the TLDR and above the Impact, and the same in the popup; not counted in the flat part's size (below); its medium and high in `detail` |
| `impact` | object | yes | the **Impact** (the `decisions` skill's `references/rendering.md` § Impact), across all the decision's options, favouring none: `effect` (what the decision changes and settles, whichever option is taken: *sets where the docs build runs, and who can publish*; where two or three outcomes fit, *(a) …; (b) …*), `wait` (what waiting costs, what it blocks), `reach` (who or what any option reaches), `undo` (each option's undo where they differ), each non-empty text; `cost` optional (the range across the options, when it is what the operator weighs). Its `effect` is written from the card's own option effects (`blocks`, each option's `impact`), never copied from a stored line's Effect, which is the recommendation's; its `wait`, `reach` and `undo` are copied from the caller's stored line where it keeps one and they hold across the options. Each option's own effect lives in its `blocks` row and its **More** detail | `effect` at tag size (after an arrow) in the map, on the closed card and in the popup; on the open card one facet a line, under Context; `wait` as the Impact table's Wait row; its medium and high in `detail` |
| `tldr` | array of strings | yes | one or two terse fragment bullets: the choice and what rides on it, no recommendation: the options mark it; the check refuses a bullet that opens with Rec or Recommend…, or says I or we recommend | first on the open card and in the popup; its medium and high in `detail` |
| `ifleft` | string | no | **If left:** an ask for another round: each leftover finding and what it would break | flat |
| `roundcosts` | string | no | **A round costs:** an ask for another round: time, quota, the operator's attention | flat |
| `ifunanswered` | string | no | **If unanswered:** a status-quo default (`I leave X as it is …`) | flat |
| `what` | string | no | Older data only. Shown at the end of the Context block, after the resume cue: the reverse of the new order (terms, then what is decided, then the cue). That is accepted for older data, since nothing is lost. On a republish, move it into `context` and delete it; a new card does not set it | at the end of the Context block |
| `why` | string | yes | **Why now:** and what it blocks | Background fold; its medium and high in `detail` |
| `whyask` | string | yes | **Why ask:** what would go wrong if the recommendation were taken alone | Background fold; its medium and high in `detail` |
| `class` | string | no | the class that opens Why ask, when the caller names classes | a pill, and the Background fold |
| `warn` | boolean | no | `true` for ⚠ one-way (one-way and high impact) | a ⚠ pill |
| `blocks` | object | expected on every card; required when `warn` | the block's Impact table row per option: keyed by letter, a row for every option but `z` (the check refuses a ⚠ card without them; on any other card a missing row is a runner lint), each `{happens, undo, who, cost}` — the Effect, Undo (plainly: it decides the read-back) and Reach cells, and Cost, optional; each cell a table cell's length (about 5–25 words) | the Impact table in Options in full, which opens unfolded on a ⚠ card, and each option's **More** detail; an option with no entry shows its `impact` as the Effect and `—` in the rest |
| `act` | object | when an option asks the operator to act; optional otherwise | the **To act on (x):** part (the `decisions` skill's floor, what it takes to act; its specifics in that skill's `references/rendering.md` § Card): keyed by option letter other than `z`, each a non-empty array of steps as text, in order; backtick code renders as code. A step names where a secret goes, never its value. A paste text that legitimately holds an angle-bracketed word (`<br>`, a tag in an HTML snippet) goes in a file named by its `/…` path in the step: the check refuses it inline, as it refuses a fill-in placeholder. The page renders no fenced block and folds line breaks: a paste text of more than one line goes in a file named by its `/…` path in the step, never inline; the check refuses a step with a line break | flat, as a numbered list under its option in the open card, never folded; not counted in the flat part's size (below) |
| `dep` | string | no | what it depends on, usually slugs with the answer that matters (`[[41]] (b)`) | summary line, Dependencies fold; its medium and high in `detail` |
| `rec` | string or null | yes | the recommended option's letter; `null` with no recommendation | the one bold option, the rec line |
| `norec` | string | when `rec` is null | the labelled exception: `your preference — no recommendation`, or `no recommendation — outside my authority` and why | in place of the rec |
| `o` | array | yes | the options, in letter order, `(z)` decide later last: `[letter, full text, impact, title, one line]` each | see below |
| `basis` | string | yes | the basis word: `strong`, `partial`, `thin` or `none` | rec line, Evidence fold |
| `reason` | string | yes | the one-clause reason for the rec (or for the basis word, with no rec) | rec line; its medium and high in `detail.rec` |
| `unknown` | string | yes | what is not known, or `none` | rec line, Evidence fold; its medium and high in `detail.rec` |
| `evidence` | string, or array of strings | no | the basis drill-down: what was observed, inferred, assumed, with the paths (in backticks) and `https://` links behind each claim; a list holds one tagged claim per item (*Observed: … (path or link)*) | the Evidence part in the Evidence and unknowns fold, a list as bullets; its medium and high in `detail.evidence` |
| `detail` | object | no; its levels scale with the decision | each part's **medium and high renditions** (below); `null` is absent | in place of the part's text, a click away |

An option `[letter, full, impact, title, oneLine]`:

- `title` — at most six words, verb first where it reads naturally; shown flat.
- `oneLine` — one line shown flat after a label the page picks: `because:` on the
  recommended option, `not recommended because:` on the others, `if left:` on `(z)`, and
  `if chosen:` on every option of a card with no recommendation. Write it to follow its label.
- `full` and `impact` — the option and its consequence as the card states them; shown in the
  Options in full fold (`full` steps to its medium and high in `detail.o`; `impact` is static),
  and in the option's **More** detail.

**`detail`, the levels.** The existing fields are each part's summary. `detail` holds the
fuller renditions, `[medium, high]` per part, written from the same sources; a click on the
part steps it summary → medium → high → summary, and the level replaces the part's text. A
part steps alone, only through the levels it has: `[medium]` alone toggles between the two,
and a part with no entry has no toggle. Every part opens at its summary.

Each level has its own shape, so each is clearly sparser than the next:

| Level | Shape | Words |
|---|---|---|
| summary | one or two sentences; the TLDR one or two bullets; the Impact one facet a line | terse |
| medium | a list of bullets, each with an optional sub-bullet or two | terse fragments |
| high | headed sections, each with bullets and sub-bullets | full sentences allowed |

A summary or medium bullet is a fragment: a subject and its point, no connective clauses
(*Stale cache broke two publishes this month*). Full sentences belong at high. A part with no
levels is its own full text, and a small call stays short.

```json
"a bullet":  "text"  |  {"t": "text", "sub": ["text", "text"]}
"a list":    ["a bullet", …]                            (non-empty)
"sections":  [{"h": "heading", "b": "a list"}, …]       (non-empty)
"rendition": "text" | "a list" | "sections"

"detail": {
  "context": [medium, high],
  "impact":  [{"effect": a bullet, "wait": a bullet, …}, {"effect": "a list", "wait": "a list", …}],
  "tldr":    ["a list", "sections"],
  "rec":     ["a list", "sections"],
  "why":     [medium, high],
  "whyask":  [medium, high],
  "dep":     [medium, high],
  "evidence":[medium, high],
  "o":       {"a": [medium, high], "b": [medium, high]}
}
```

The structure comes from the JSON, never from parsing the text, so every string is escaped on
its own and no data byte becomes markup. Text is still valid at any level, so older data
renders; the runner lints a level whose shape is off (SKILL.md step 2).

- A rendition is text, a list of bullets, or a list of sections, shown as a paragraph, bullets
  with their sub-bullets nested, or a heading over its bullets. Links (`https://` only) are
  clickable in the medium and high renditions, in the fold parts at every level and in the
  **More** detail; never in a heading, a visible part's summary, the Impact table, an option's
  `impact` line, `act`, the popup or a slug.
- `context`: Context at more detail, under the same label. Its high holds the facts a cold
  reader has lost (the decisions block's *Context you may have lost*: what was tried, what was
  answered before, where a list or number came from). The tick-box doc, which cannot toggle,
  shows Context at its high (`references/fallback.md`).
- `impact`: facet objects in the decisions skill's one vocabulary, `effect` required, across
  all the options as the summary is. At medium, one terse bullet per facet, shown with its
  label (→, later, reach, undo, cost); where the options differ on a facet, its sub-bullets
  carry them, lettered, one or two, grouping the options when a facet differs across more than
  two. At high, a short section per facet, headed Effect, Wait, Reach, Undo, Cost, each value
  text or a list of bullets.
- `tldr`: bullets or sections, with no recommendation at any level (the check refuses one, as
  it does in `tldr`).
- `rec`: bullets or sections, shown after `Rec (b) · basis word —`: the reason, then the
  unknown (*unknown: …*), or a Reason and an Unknown section. An older level written as one
  string, `<reason> · unknown: <unknown>`, shows as the summary shows the two.
- `why`, `whyask` (its class still first), `dep`, `evidence`: the fold items at more detail.
- `o`: keyed by option letters other than `z`: each option's paragraph in Options in full, at
  more detail. **More** shows its high (else its medium, else `full`), then its Effect, Reach,
  Undo and Cost from `blocks`.
- **Which parts carry levels.** Levels are optional on every part, and scale with the
  decision: a small call may carry none; a wide or one-way decision carries the most, a medium
  and a high for its visible parts (`context`, `impact`, `tldr`, `rec`) and for the fold items
  with depth to give. A part with levels has its depth sized at its top level (§ Size).
- The page ignores a `detail` key it does not know; the runner lints it.

**Context introduces every specific thing the card names.** Every label, number, acronym,
term of art or item that the flat part (`t`, `impact`, `tldr`, `title`, `oneLine`, the rec
line) uses is introduced in `context`, as the `decisions` floor requires: the flat part is what
the operator reads, and `full` sits in a fold. Two shapes need it most:

- **A count** ("four changes", "the three"). Context says what the things are, or lists them:
  *the review asked for four changes: X, Y, Z and W*.
- **A named mode, setting, review, plan or document** ("content mode", "the review"). Context
  gives it a one-line gloss: what it is, and where it comes from.

An item, a commit or a series is named by its short name or title, never by its id (§ No ids
on the page, above).

**The cold read** (the `decisions` skill's `references/worksheet.md` § The cold read, applied
to the flat part). Before publishing, list each noun phrase in the card's Impact line, TLDR,
option titles and one lines that refers to a specific thing: a count, a named mode, setting,
review, plan or document, an item or a label. For each one, point to its gloss in
`context`. A phrase with no gloss gets one before the page goes out. The pre-publish runner
(SKILL.md step 2) lints counts and named things missing from `context`, and ids wherever they
are; those lints are proxies, and plain-word terms stay the cold read's. The same holds for
the medium and high renditions of the Impact line, the TLDR and the rec line, checked against
Context's **summary** only: each part steps alone, so the Context beside a TLDR at full detail may be at
its summary. A term a level introduces needs its gloss in Context's summary, or in the level
itself.

**Size.** The flat part of a card (title, Impact line, TLDR, option titles and one-liners, rec
line) stays near 150 words; the folds carry the rest. `context` and an `act` list are outside
that budget: what the operator needs to read the card, and to act on it, is never folded away.
Context's summary is one or two sentences, typically 30–60 words (the runner lints past ~60);
a term that needs a paragraph has its detail in its levels or a fold, with its one-line gloss
kept in Context. The `effect` stays under about 10 words: it is shown alone, at tag size, in
the map.

Every card carries the decisions block's depth (decision 198), scaled to the decision, with
levels where the decision calls for them (decision 201). Each size is read at the
part's top level, its high when it has one, else its summary; words are counted as
whitespace-split:

| What | Size |
|---|---|
| Background: `why` + `whyask`, each at its top level | ~150 |
| Each option but `z`: its top text + its `blocks` cells | ~60–120 |
| Evidence, at its top level | ~150, with the paths and links behind each claim |
| The card in all: the flat part and Context at their summary, the fold parts at their top level, each option's `impact`; not `act` | ~600–900 |
| A fold part's medium | between its summary and its high, about half its high |

The levels' own sizes are their shapes (§ A card, `detail`), linted as clear misses:

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
sources (SKILL.md step 2), and a fact no source holds goes under `unknown`, never into the
depth to fill a size. **The cost** falls on the cards that carry levels: the example's small
call (card 43) carries none, so it costs nothing extra: about 424 words in its flat part,
Context and folds; a card with every part levelled (card 41) writes about 1134 words of
levels, about 674 of them for its visible parts, against its fold depth alone of about 386,
about 2.9 times. The pre-publish
runner lints only clear misses: thin (about 40% of a size) only on a part that carries levels,
long (1.5 times) on any.

**What the page adds.** Every view shows the impact across the options: the map and a closed
card the effect, beside the rec pill and the recommended option's title, which mark the
recommendation; an open card the Impact, one facet a line; and its Options in full fold the
Impact table (a row per option, each option's own effect, then the Wait row; Effect, Reach,
Undo, Cost). It opens every card on its TLDR, then its Context, then its Impact: a page is
read away from the conversation, so its reader is treated as cold. Any part with `detail`
toggles its level on a click, on its button or on its text (never on a link or a control, nor
while text is selected, so it can be copied); the folds keep their order and stay closed, with
Options in full open on a ⚠ card; each option but `z` has a **More** button at its right,
outside its label, which shows the option in full. The Impact table, each option's `impact`
line, the Basis and Unknown lines, the titles, the one lines, `act`, and the round and default
lines are static. A
`⚠ one-way` card is the decisions skill's block: the card's essentials plus its Impact table,
unfolded. It gets no special control: the read-back of a one-way pick happens in chat, when
the answers are read back. An older `stakes` field is ignored: Undo and Reach carry it.

**Republishing older data.** A `cards.json` written before `impact` existed is refused by the
current template. On a republish, add `impact` to each kept card (a `stakes` field may stay,
ignored); the impact comes from the caller's stored Impact line, backfilled as the decisions
skill's re-show says when the store has none.

A `cards.json` written before Context came first has either no `context` (refused) or a
cue-only one, which passes and shows its `what` after the cue (§ A card, `what`). On a
republish, give each kept card a `context`: the terms its Impact line, TLDR and options use,
each glossed; then its `what`, moved in (delete `what`); then its cue. That is the format
migration (the `rev` rule above). Any change to a card gets a new `rev`, Context included: an
**Added:** line after `tell me`, more detail after `expand`, a `dig into` finding, a corrected
fact, a re-ask. Only the one-time format migration keeps it: a card written before Context
existed, whose own `what` and resume cue move into `context`, and whose terms are glossed from
its own folds alone. A gloss drawn from anywhere outside the card is new information: a new
`rev`.

A `cards.json` written before `detail` existed renders as it did, with **More** buttons added
and no toggles; it is thin until rewritten. On a republish, write the depth (§ Size) and the
`detail` levels its decision calls for into each card with no counting answer, and into each
card revised anyway, each with a new `rev`. A card the operator has answered keeps its depth
as it stands, unless it is revised for another reason. A card that gets `detail` gets a new
`rev`, so the republish hands it over as shown again (SKILL.md § Hand over what was shown),
with the publish time.

A `cards.json` written before the level shapes renders TLDR first, the Impact one facet a
line, and its text levels as paragraphs; nothing is refused. The runner lints its shapes, its
ids and an effect that reads as the recommendation's. On a republish, each card with no
counting answer, and each card revised anyway, gets its `impact` across the options, its
levels in their shapes and its ids replaced by names, each with a new `rev`, handed over as
shown again. A card the operator has answered stays as it is, its lints left knowingly,
unless it is revised for another reason; its effect may still read as the recommendation's.

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
card replaces it. Answers to numbers not on the current `cards.json` are skipped too. The page
reads the collection live, so an answer set in the owner's other tab shows at once.

**Already handed over.** The read-back compares a counting answer's `at` with the `at` it last
handed over for that number. Equal: the same answer, unchanged. Different: the operator changed
it since. Both values come from the operator's browser, so this too needs no shared clock.
The `at` is the read-back's marker only: it is never handed over as the time a card was shown
or seen (SKILL.md steps 3 and 6 use your clock for those).
