# Writer digest

What a writer of `cards.json` needs, in one read: the fields, the level shapes, the floor's
must-haves, the refusals and the lints. Read this instead of `cards-schema.md`, the
`decisions` skill's `references/card-record.md` and `assets/cards.example.json`; open those
only for a case this does not settle (an older `cards.json`, the answers collection). The
schema and the record are the authority where they differ; the plugin's `tests/test_digest.py`
keeps this digest naming every field with its Required cell, every lint key with its line
start, and the runner's thresholds.

**Write only `decision-page/5`, each card a `decision-card/5` record plus `L` and `dep`.** A
`cards.json` in an older format is upgraded first: `node scripts/upgrade_cards.js IN OUT
--questions QMAP` (format only, every `rev` kept byte for byte), then written on.

## The floor, per card

Each card meets the `decisions` skill's floor: what is decided in plain words, in `what`, and
for a set every item it acts on, in `items`, every term glossed; its Impact (wait, reach, cost, and undo only where an option is one-way or costly to
undo), its Reach about the system the work builds, never the process (that is its Wait); Why
now and what it blocks; Why ask; the options, each with its consequence by its mechanism: how
it happens, who meets it and when, and the before and after, in its own `effect`, and its main
upside and downside in one line each, `pro` and `con`; decide later
as `(z)`; the recommendation, or the labelled reason there is none; its basis, and the
assumptions it rests on, each with its tripwire, in `assume`; what is still open, in `open`. There is no card-level effect: each option carries its own. Keep the caller's numbers.
No ids anywhere on the page: a decision by its slug `[[N]]`, an item, series, branch or commit
by its short name; a fact only an id carries goes in backticks in an option's `act` or in
`evidence`. A decision raised from one labelled item of a source carries `label`, and that
label passes anywhere with its short name beside it: *F7 (oversize upload)*.

## Text

Every text field is plain text: the page escapes it, and only two marks render: `` `code` ``
in backticks, and `[[N]]`, a decision slug (a decision on the page, or a `refs` key; the page
refuses any other N). Links
(`https://` only) are clickable in the medium and high levels, in the fold parts at every
level and in an option's **More** detail; nowhere else (not a heading, a visible part's
summary, `act`, a tooltip or a slug). `page.doc.url` must start `https://`, or it is not shown.

## Top level

| Key | Required | Shape |
|---|---|---|
| `format` | yes | `"decision-page/5"` |
| `page` | no | `{title, lede, doc: {name, url}}`; `title` is `(<owner>) <session name>`, else `<repo>: open decisions` (SKILL.md step 2), the `<title>` set to match; `url` must start `https://` |
| `layers` | yes | `[[key, title, note, shared], …]`, the groups in display order; `shared` optional: a bundle's shared context, the terms and source every card in it uses, in plain words, which a card's Context may lean on; `note` then says what the cards share. A bundle holds two or more whole item cards |
| `follow` | yes | copied from below as it stands |
| `cards` | yes | one per decision, in the `decisions` skill's order |
| `refs` | no | `{"N": {short, q, a, when}}` for a slugged decision not on the page, answered only: one still open goes on the page as a card; never a number that is a card |

`follow`, exactly:

```json
[["later","later","[when]","When should it come back? Blank means the next report."],
 ["tell me","tell me","[what]","What should the card add?"],
 ["expand","expand","","Anything in particular to show in more detail?"],
 ["dig into","dig into","[what]","What should I look into first?"],
 ["you decide","you decide","","Anything I should weigh?"],
 ["drop","drop","","Why drop it? (optional)"]]
```

## A page card

| Key | Required | Shape and rule |
|---|---|---|
| `L` | yes | a `layers` key |
| `dep` | no | usually slugs with the answer that matters (`[[41]] (b)`); leave it out when there is none |

## A card

*To render*: the page refuses the card without it. *Of a new card*: the runner lints it; leave
it knowingly only on a card upgraded from an older format.

| Key | Required | Shape and rule |
|---|---|---|
| `format` | to render | `"decision-card/5"` |
| `n` | to render | whole number, 1 or more, unique, the caller's own |
| `rev` | to render | the UTC time you write it, `YYYY-MM-DDTHH:MM:SSZ`. New on any change to the card, Context included, since answers given to an old `rev` stop counting; kept only by a format-only upgrade |
| `raised` | optional | UTC, when the decision was first raised |
| `upgraded` | optional; written by the upgrader only | `{from, rev}`: the shape a card was carried over from (`legacy`, `kit` or `kit (v4)`; the page refuses any other) and the `rev` it carries after the upgrade. Never write it; a revision gives a new `rev`, so it no longer matches. **The trust boundary:** the runner is the writer's self-check, not a gate, and the marker is the upgrader's alone: a writer who forges it only skips their own check |
| `t` | to render | short name, 2–6 words, a noun phrase |
| `q` | to render | the question as asked, one line (the headline's) |
| `label` | optional | `{id, name}`, when the decision is raised from one labelled item of a source (a finding, a plan's question or feature; never a work item, ticket or commit): `id` one word (`F7`), `name` its short name, 2–6 plain words, from the source where it has one; shown after the title, muted: `t` · **F7** (oversize upload) |
| `oneway` | optional | `true` for ⚠ one-way: every option but (z) then gives its `reach` |
| `class` | optional | the class that opens Why ask, when the caller names classes |
| `tldr` | to render | 1–2 bullets, each one sentence of about 14 words or fewer: what is decided, what rides on it; never the recommendation |
| `context` | to render | 1–2 sentences, ~30–60 words: introduces every count, named mode, setting, review, plan, document, item or label the flat part uses; then the resume cue. Does not repeat the TLDR. Its high level holds the facts a cold reader has lost |
| `what` | optional | one sentence: what is decided, in plain words; shown as the **What** part after Context, never folded |
| `items` | optional; a card that counts a set where it says what is decided is refused with none, or too few | `[{name, where, about, per}, …]`, one per item of a set, every item listed: `name` its plain name (never an id), `where` where it lives when that helps, `about` what it is in a few words, `per` `{"a": "…", "b": "…"}`, its outcome under each option, keyed by the card's letters, only where the options treat it differently (left out, it reads the same under every option); the part reads *What · N items* |
| `open` | optional | a list of text: what is not known yet, one question each; shown folded above the Impact |
| `impact` | to render | `{wait, reach}` as text; `undo` only when some option is one-way or costly to undo, naming that option (`(b) none — …`), left out when every option is reversible at little cost; `cost` optional (leave it out when none); across all options, favouring none; `reach` about the thing the work builds, never the process (that is `wait`). No `effect`: each option carries its own |
| `options` | to render | the options, below, `a`… in order, ending `z` (decide later) |
| `rec` | to render | an option letter, or `null` |
| `norec` | to render when `rec` is null | `your preference — no recommendation`, or `no recommendation — outside my authority` and why |
| `basis` | to render | `strong`, `partial`, `thin` or `none`: the Assumptions fold's summary opens on it, `basis: partial · 2 assumptions with tripwires` |
| `reason` | of a new card | one clause: the rec's reason, or, with no rec, the reason for the basis word; shown after the basis word in the Assumptions fold |
| `evidence` | optional | text, or a list of tagged claims (*Observed: …*) with the paths and links behind each; shown in the Assumptions fold, after the Basis line |
| `assume` | optional; a card with a recommendation and none is linted | `[{rests, tw}, …]`: each thing the recommendation rests on and its tripwire, the sign that would change the call, both text; shown in the closed Assumptions fold above the Impact, after Open questions, with the basis word, `reason` and `evidence`. Never an unknown: that is `open` |
| `why` | of a new card | Why now, and what it blocks: shown in the Background fold, the first of the bottom folds; closed, its summary is *why now:* and the first sentence of `why`, about 25 words at most (rewrite a longer one, never cut it) |
| `whyask` | of a new card | what goes wrong if the recommendation were taken alone: shown in the Background fold, after Why now |
| `ifleft` | optional | **If left:** on an ask for another round |
| `roundcosts` | optional | **A round costs:** on an ask for another round |
| `ifunanswered` | optional | **If unanswered:** a status-quo default |
| `detail` | optional | the levels, below |

`what` is the What part: what is decided, in plain words, after Context. A count of two or
more in `t`, the first TLDR bullet, or an option's title or line (but (z)'s) names a set: list
every item in `items`, or the runner refuses the card. A set named by a rule that picks out its members (*the pages that cite the retired setup guide*) keeps its count out of the checked places (the title, the first TLDR bullet, the option titles and lines), or lists its items. A count in `what`
itself with no `items` of its length is the `count` lint.

## An option

| Key | Required | Shape and rule |
|---|---|---|
| `k` | to render | one letter |
| `title` | to render | at most six words, verb first |
| `line` | optional | one line read after the page's label (`because:` on the rec, `if chosen:` on the others, `if left:` on `z`): write it to follow *if chosen:*; the downside goes in `con` |
| `text` | optional | the option in full: an older card's view, shown in the plan's place only when it has no `plan`; a new card writes `plan` |
| `plan` | of a new card | **Plan in brief**, 2–4 sentences on one line, at most ~100 words: what choosing the option sets in motion; (z) too, what deciding later sets in motion. Its view opens on it |
| `effect` | to render, but on (z) | its own effect by its mechanism, how it happens, who meets it and when, the before and after; never a bare label; on (z), what waiting does |
| `reach` | of a new card; to render on a ⚠ card, but (z) | who or what it reaches; ~5–25 words |
| `undo` | with `oneway` | only on an option one-way or costly to undo: how it is undone and at what cost, or that it cannot be |
| `oneway` | optional | `true` on each option one-way or costly to undo, which then needs its `undo`; a ⚠ card flags its one-way options |
| `cost` | optional | its cost, where it has one |
| `pro` | of a new card, but on (z) | one line, about 25 words at most, the main upside: shown under the option as its **Pros** row, always visible; none on `z`, which shows no rows |
| `con` | of a new card, but on (z) | one line, about 25 words at most, the main downside or risk: its **Cons** row; the recommended option always gives one; none on `z` |
| `pros` | optional | `["point", …]`, 1–5 upsides in full (0–5 on `z`), weightiest first: the Pros column of the option's view, its **Pros \| Cons** table |
| `cons` | optional | `["point", …]`, 1–5 downsides in full (0–5 on `z`), weightiest first: the table's Cons column |
| `act` | optional | `["step", …]`, when the option asks the operator to act; not on `z`; each step text on one line, no `<placeholder>`; a step names where a secret goes, never its value; a paste text holding an angle-bracketed word, or of more than one line, goes in a file named by its `/…` path |
| `detail` | optional | `[medium, high]` levels of its `plan` (of its `text` on an older option with none), each longer than the one below |

**None is not shown.** A field, facet or option field that is blank or says only `none`, `n/a`
or a dash is left off the page (a `dep`, an `open`, a `cost`, an `evidence`, an option's reach
or cost): leave it out rather than write none. The required Impact facets, an undo when given
and `basis` are statements, and stay shown. Leave undo out on an option reversible at little
cost: no undo shown reads as that. A none `pro` or `con` has no row, and a none `plan` is no plan. There is no
Options in full fold: each option's **view**, closed until the option is picked or its **More**
pressed (picking one closes the card's other open view; every view starts closed, a ⚠ card's
too), shows in this order: its **Plan in brief** (a click steps through its levels), then its
**Pros | Cons** table, two columns side by side, then its effect, reach, undo and cost. An
older option with no `plan` shows its `text` at its fullest in the plan's place. Its
**To act on (x):** stays under the option, outside the view.

## An excerpt

Verbatim multi-line text (code, a log, a diff, test output), drawn as a code block. No card
field the page shows carries one yet; the finding and the excerpt attachment will.

| Key | Required | Shape |
|---|---|---|
| `text` | yes | the lines verbatim, non-blank, with no fence around them (the page draws the block); about 80 lines or 4 KB, a longer one cut with the cut said in the text |
| `lang` | no | a short label (`python`, `diff`, `log`): letters, digits and `+ # . _ -`, 24 at most |
| `src` | no | where it came from, one line: a path and line range at a commit, or the command and when it ran |

Nothing in an excerpt renders as a mark: backticks, `[[N]]`, links, HTML tags and fences show
as typed. Never a secret's value (`[redacted: key <name> in <path>]`), personal data, or
another party's private material.

## Levels and their shapes

`detail` holds `[medium, high]` per part: `context`, `impact`, `tldr`, `rec`, `why`,
`whyask`, `dep`, `evidence`; an option's levels are its own `detail`. A bullet is `"text"` or
`{"t": "text", "sub": ["text"]}`; a section is `{"h": "heading", "b": [bullets]}`. `impact`
levels are facet objects, `{wait, reach, undo, cost}`: `{"wait": bullet, …}` at medium,
`{"wait": [bullets], …}` at high.

| Level | Shape |
|---|---|
| summary (the field itself) | 1–2 sentences; the TLDR 1–2 bullets, each one sentence of about 14 words or fewer; the Impact one facet a line |
| medium | terse bullets, one sentence of about 14 words or fewer each, at most 6, each with at most 2 sub-bullets; the Impact one bullet per facet, the options in its sub-bullets |
| high | headed sections with bullets and sub-bullets; full sentences allowed |

Levels scale with the decision: a small call carries none; a wide or ⚠ one-way card carries
medium and high on its visible parts and on the fold items with depth to give. Each level is
longer than the one below. Soft sizes at a part's top level: Background (`why` + `whyask`)
~150 words; each option's plan (or older text) plus its effect, reach, undo and cost ~60–120; `evidence` ~150;
the card in all ~600–900, the What part (`what` and `items`), each option's `pro` and `con` and its table's `pros` and `cons` counted in it; a set still lists every item. Never pad: a fact no source holds goes under `open`.

## The runner's thresholds

The lints fire past these values, except `mech`, which fires at or under its value
(`scripts/check_cards.js`):

| Threshold | Value |
|---|---|
| words in a summary or medium bullet | 14 |
| sub-bullets on one bullet | 2 |
| bullets in a medium level | 6 |
| sentences in Context's summary | 2 |
| words in Context's summary | 60 |
| bullets in the TLDR | 2 |
| words in a summary Impact facet | 16 |
| words in the card in all | 1350 |
| words in an option's effect, at or under which mech fires | 4 |
| words in the Background fold's summary | 25 |
| words in a pro or con | 25 |
| words in a plan in brief | 100 |

## The checks

`node scripts/check_cards.js cards.json` checks a page; `node scripts/check_cards.js --record
FILE` checks one record (no layer, no slug check, and `L` and `dep` refused in it), before it
is raised. Exit codes are the same.

**Refusals** (the page renders nothing; the runner prints them first, exit 1): a `what` not
text; an `items` not a non-empty list of objects with a `name`, an item's `where` or `about`
not text, a `per` not an object of text keyed by the card's option letters; no
`decision-page/5` stamp, or a newer one; a card with no `decision-card/5` stamp, or a newer
one; a field the record no longer has (`o`, `blocks`, a card-level `act`, `warn`, `unknown`,
`stakes`, `detail.o`); a bad or duplicate `n`; a `rev` or `raised` not a UTC time; a `q` on
more than one line; options not objects with a single `a`–`z` letter and a title, out of
order, or not ending `z`; a `rec` not among them, or null without `norec`; a missing field
required to render; blank `context`; a TLDR bullet, at any level, opening on Rec or
Recommend… or saying I or we recommend; an `impact` missing wait or reach, or with an undo or
cost not text; an `open` not a list of text; an option but (z) with no effect; on a ⚠ card an
option but (z) with no reach; an option field not text; a `plan`, `pro` or `con` holding a line break
(CR, LF, NEL, a line or paragraph separator, a vertical tab or form feed); a `pros` or `cons`
not a list of text, over five points, a point holding a line break, or empty but on `z`; a `oneway` not true or false; an option
flagged `oneway: true` without its `undo`; an `act` on (z), not a non-empty list of text, or a
step with a fill-in placeholder (an angle-bracketed word with no spaces) or a line break; a
`label` not `{id, name}`; a layer's `shared` not text; a `refs` entry still open (`when`
`open`, or `a` not yet answered) or for a card on the page; a `[[N]]` neither a card nor a
`refs` entry (an excerpt is not read); a `basis` outside the four; a `follow` other than the
six; a non-number `refs` key; an excerpt (once a field carries one) not `{text, lang, src}`,
with blank `text`, a `lang` off its label shape or a `src` of more than one line; `evidence`
neither text nor a non-empty list of text; a malformed `detail` (a bullet neither text nor
`{t, sub}`, a section not `{h, b}`, both `t` and `h`, bullets and sections mixed, an Impact
level with none of its four facets), or an option's `detail` not `[medium, high]`.

**The set refusal** (the runner's alone, exit 1, after the page's own; the page never refuses
it, so an older published page still renders): a card whose `t`, first TLDR bullet, or an
option's title or line (but (z)'s) counts two or more things, with no `items`, or fewer items
than the largest count. A list of another length is the `set` lint. **A card the upgrader
carried over** (its `upgraded.rev` equal to its `rev`) gets the set check as the `set` lint,
never a refusal: the upgrade is lazy and keeps every `rev`. A writer who revises it gives it a
new `rev`, and from then it is refused like any card until its items are listed. A count of
100 or more is the `set` lint, never a refusal. A set named by a rule that picks out its members (*the pages that cite the retired setup guide*) keeps its count out of the checked places (the title, the first TLDR bullet, the option titles and lines), or lists its items. Not a set's
count: a four-digit year; a numeral right after a capitalised word inside the text (*Python 2*, *Node 22*, *HTTP 404*); a date (*26 October*); a list of labels (*findings 3, 4 and 7*); a numeral right after a label noun from a closed list (principle, step, tier, option, rule, finding, item, section, …) and before the text's end, punctuation, a function word or a verb and its object (*principle 3*, *step 2 of the guide*, *tier three*); after a verb or any other word it counts (*Retire 3 plugins this quarter*), *N times*, a
range, a number after a slash, *N of the …* (but not after *all*, *both* or *each*), a quantity of a unit (*2 spaces*, *600 words*),
and a count equal to the real options' in a sentence about them (*choose between the two
options*).

**Lints** (exit 2; each line says how to fix it, or leave it knowingly; never pad). A card's
lint prints `lint: card N:` (a record's `lint: record N:`), then the start below (— is none); a
page-wide one prints `lint: page:`.

| Key | Line starts | Fires on |
|---|---|---|
| `page` | `page:` | an id in the page title, the lede, a layer's title, note or shared context, or a `refs` short or question |
| `group` | `page:` | a bundle (a layer with `shared`) holding fewer than two cards |
| `refs` | `page:` | a `refs` answer holding an id (left as given when it is the operator's words) |
| `id` | — | an id in any card text, the What part's `what` and `items` included: a hash, an item tag, a ticket key, a label like OQ3, decision N; a label a card declares passes with its short name beside it |
| `count` | — | a count in the flat part or a visible level that Context (with its bundle's `shared`) and the What part (`what`, `items` and their number) do not name; one where the card says what is decided points to `items` |
| `named` | — | a named mode, setting, review, plan, document, … not glossed in Context or What |
| `set` | `shape:` | a set's `items` list of another length than its count (not short of the largest); a set on a card the upgrader carried over, its `rev` kept (refused once a writer revises it) |
| `tldr` | — | a TLDR bullet, at any level, that may carry the recommendation |
| `shape` | `shape:` | a level off its shape, Context past its size, a long Impact facet, a label's short name past 6 words |
| `rec-only` | `impact:` | an Impact reach, at any level, that shares 40% or more of its words with the recommended option and none with any other option (the v5 form: with no card-level effect, the reach is what it reads; a reach naming two or more options is the decision's); an item's `per` that names the recommended option and no other |
| `mech` | `impact:` | an option's effect, but `z`'s, of 4 words or fewer that does not open on no, nothing, none or unchanged: a label, not the mechanism |
| `process` | `impact:` | a process phrase (a review comment, another round, your time, a blocked session) in an option's effect or reach but `z`'s, or the Impact's reach at any level; never the wait, never a round ask |
| `grow` | `depth:` | a level not longer than the one below it |
| `bg` | `depth:` | `why` or `whyask` missing (owed by a new card); Background thin (where levelled) or long |
| `bgsum` | `shape:` | the Background fold's summary (the first sentence of why) past its words |
| `reason` | `depth:` | `reason` missing (owed by a new card) |
| `assume` | `depth:` | a card with a recommendation and no `assume` (a small call may leave it knowingly; an upgraded older card holds none) |
| `row` | `depth:` | an option but `z` with no reach |
| `opt` | `depth:` | an option's detail thin (where levelled) or long |
| `ev` | `depth:` | evidence thin (where levelled) or long |
| `all` | `depth:` | the card long in all |
| `key` | `depth:` | a `detail` key the page does not show |
| `oneway` | `oneway:` | a ⚠ card with no option flagged one-way; a flagged option while the Impact carries no undo |
| `tradeoffs` | `shape:` | an option but `z` with no shown `pro` or `con`; a recommended option with no `con`; a card with two or more options but `z` and none (an upgraded older card may leave it knowingly); a `pro` or `con` past its words |
| `plan` | `depth:` | an option, `z` included, with no shown `plan` (one line when no option has one; an upgraded older card may leave it knowingly, its view showing its `text`); a `plan` past its words; an option with both `plan` and `text`, whose text is not shown |

Then the cold read: could you name every item the card acts on, from its What part alone? List
each noun phrase in the Impact, TLDR, option titles and one lines,
and each option's `pro` and `con` (visible rows, linted by `count` and `named` though outside
the flat part's size) and its view's `plan`, `pros` and `cons`, that names a specific thing, and point to its gloss in `context`. Over the view the `named` lint reads qualified names only ("content mode"); a bare noun, a phrase opening on a function word ("to plan") or on a verb form ("reaches review") is yours to check here. Of each effect, ask: does
it name what happens to the thing being built? Could you say how it happens, not only that
it does?
