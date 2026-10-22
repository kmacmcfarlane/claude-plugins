# Writer digest

What a writer of `cards.json` needs, in one read: the fields, the level shapes, the floor's
must-haves, the refusals and the lints. Read this instead of `cards-schema.md` and
`assets/cards.example.json`; open the schema only for a case this does not settle (older
data, a republish migration, the answers collection). The schema is the authority where they
differ; the plugin's `tests/test_digest.py` keeps this digest naming every field with its
Required cell, every lint key with its line start, and the runner's thresholds.

## The floor, per card

Each card meets the `decisions` skill's floor: what is decided in plain words, every term
glossed; its Impact (effect, wait, reach, cost, and undo only where an option is one-way
or costly to undo), its Effect and Reach about the system the work builds, never the
process (that is its Wait); Why now and what it blocks; Why ask;
the options, each with its consequence by its mechanism: how it happens, who meets it and
when, and the before and after; decide later as `(z)`; the recommendation, or the
labelled reason there is none. Keep the caller's numbers. No ids anywhere on the page: a
decision by its slug `[[N]]`, an item, series, branch or commit by its short name; a fact
only an id carries goes in backticks in `act` or `evidence`. A decision raised from one
labelled item of a source carries `label`, and that label passes anywhere with its short name
beside it: *F7 (oversize upload)*.

## Text

Every text field is plain text: the page escapes it, and only two marks render: `` `code` ``
in backticks, and `[[N]]`, a decision slug (a decision on the page, or a `refs` key; the page
refuses any other N). Links
(`https://` only) are clickable in the medium and high levels, in the fold parts at every
level and in an option's **More** detail; nowhere else (not a heading, a visible part's
summary, an option's `impact`, `act`, a tooltip or a slug). `page.doc.url`
must start `https://`, or it is not shown.

## Top level

| Key | Required | Shape |
|---|---|---|
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

## A card

| Key | Required | Shape and rule |
|---|---|---|
| `n` | yes | whole number, unique, the caller's own |
| `L` | yes | a `layers` key |
| `t` | yes | short name, 2–6 words, a noun phrase |
| `label` | no | `{id, name}`, when the decision is raised from one labelled item of a source (a finding, a plan's question or feature; never a work item, ticket or commit): `id` one word (`F7`), `name` its short name, 2–6 plain words, from the source where it has one; shown after the title, muted: `t` · **F7** (oversize upload) |
| `rev` | yes | non-empty: the UTC time you write it, by convention. New on any change to the card, Context included, since answers given to an old `rev` stop counting |
| `context` | yes | 1–2 sentences, ~30–60 words: introduces every count, named mode, setting, review, plan, document, item or label the flat part uses; then the resume cue. Does not repeat the TLDR. Its high level holds the facts a cold reader has lost |
| `impact` | yes | `{effect, wait, reach}` as text; `undo` only when some option is one-way or costly to undo, naming that option (`(b) none — …`), left out when every option is reversible at little cost; `cost` optional (leave it out when none); across all options, favouring none; `effect` and `reach` about the thing the work builds, never the process (that is `wait`). Write `effect` from the card's own option effects (`blocks`, each option's `impact`), copying a stored Effect only when it names each option's outcome or the card was stored or revised on or after 2026-10-14; otherwise write it from the option effects (the pre-publish check's rec-only lint backs this); under ~10 words, `(a) …; (b) …` where outcomes differ |
| `tldr` | yes | 1–2 bullets, each one sentence of about 14 words or fewer: what is decided, what rides on it; never the recommendation |
| `ifleft` | no | **If left:** on an ask for another round |
| `roundcosts` | no | **A round costs:** on an ask for another round |
| `ifunanswered` | no | **If unanswered:** a status-quo default |
| `why` | yes | Why now, and what it blocks |
| `whyask` | yes | what goes wrong if the recommendation were taken alone |
| `class` | no | the class that opens Why ask, when the caller names classes |
| `warn` | no | `true` for ⚠ one-way |
| `blocks` | expected on every card; required when `warn` | `{letter: {happens, who, undo, cost, oneway}}` for every option but `z`, each cell ~5–25 words, `happens` the effect by its mechanism, never a bare label; `undo` only on an option one-way or costly to undo, `cost` optional; `oneway: true` on each option one-way or costly to undo, which then needs its `undo`; a ⚠ card flags its one-way rows; shown in the option's **More** |
| `act` | when an option asks the operator to act; optional otherwise | `{letter: ["step", …]}`, not `z`; each list non-empty, each step text on one line, no `<placeholder>`; a step names where a secret goes, never its value; a paste text holding an angle-bracketed word, or of more than one line, goes in a file named by its `/…` path |
| `dep` | no | usually slugs with the answer that matters (`[[41]] (b)`); leave it out when there is none |
| `rec` | yes | an option letter, or `null` |
| `norec` | when `rec` is null | `your preference — no recommendation`, or `no recommendation — outside my authority` and why |
| `o` | yes | `[[letter, full, impact, title, oneLine], …]`, `a`… in order, ending `z` (decide later) |
| `basis` | yes | `strong`, `partial`, `thin` or `none` |
| `reason` | yes | one clause: the rec's reason, or, with no rec, the reason for the basis word |
| `unknown` | yes | what is not known, or `none` |
| `evidence` | no | text, or a list of tagged claims (*Observed: …*) with the paths and links behind each |
| `detail` | no; its levels scale with the decision | the levels, below |

Do not set `what`: it is older data only.

**None is not shown.** A field, facet or `blocks` Effect, Reach or Cost cell that is blank or
says only `none`, `n/a` or a dash is left off the page (a `dep`, a `cost`, an `evidence`, such a
cell, an Unknown in the Evidence fold): leave it out rather than write none. The required Impact
facets, an undo when given, `basis` and the rec line's *unknown: none* are statements, and stay
shown. Leave undo out on an option reversible at little cost: no undo shown reads as that. There is no Options
in full fold: each option's **More** shows its text at its fullest (a click steps through its
levels), its `impact` and its `blocks` row.

An option: `title` at most six words, verb first; `oneLine` reads after the page's label
(`because:` on the rec, `not recommended because:` on the others, `if left:` on `z`,
`if chosen:` with no rec); `full` and `impact` are the option and its consequence, by its mechanism, not a label.

## An excerpt

Verbatim multi-line text (code, a log, a diff, test output), drawn as a code block. No card
field carries one yet; the finding and the excerpt attachment will.

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
`whyask`, `dep`, `evidence`, and `o: {letter: [medium, high]}` (not `z`). A bullet is
`"text"` or `{"t": "text", "sub": ["text"]}`; a section is `{"h": "heading", "b": [bullets]}`.
`impact` levels are facet objects: `{"effect": bullet, …}` at medium, `{"effect": [bullets],
…}` at high.

| Level | Shape |
|---|---|
| summary (the field itself) | 1–2 sentences; the TLDR 1–2 bullets, each one sentence of about 14 words or fewer; the Impact one facet a line |
| medium | terse bullets, one sentence of about 14 words or fewer each, at most 6, each with at most 2 sub-bullets; the Impact one bullet per facet, the options in its sub-bullets |
| high | headed sections with bullets and sub-bullets; full sentences allowed |

Levels scale with the decision: a small call carries none; a wide or ⚠ one-way card carries
medium and high on its visible parts and on the fold items with depth to give. Each level is
longer than the one below. Soft sizes at a part's top level: Background (`why` + `whyask`)
~150 words; each option's text plus its `blocks` row ~60–120; `evidence` ~150; the card in
all ~600–900. Never pad: a fact no source holds goes under `unknown`.

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

## The checks

**Refusals** (the page renders nothing; `scripts/check_cards.js` prints them first, exit 1):
a bad or duplicate `n`; option letters not single `a`–`z`, out of order, or not ending `z`;
a `rec` not among them, or null without `norec`; a missing required field; empty `rev`; blank
`context`; a TLDR bullet, at any level, opening on Rec or Recommend… or saying I or we
recommend; an `impact` missing effect, wait or reach, or with an undo or cost not text; a
`label` not `{id, name}`; a layer's `shared` not text; a `refs` entry still open (`when`
`open`, or `a` not yet answered) or for a card on the page; a `[[N]]` neither a card nor a
`refs` entry (an excerpt is not read); a `basis` outside the four; a `follow` other than the
six; a non-number `refs` key; a ⚠ card without `blocks`, or a `blocks` key not a letter but
`z`, or a row without its text, or a `oneway` not true or false; a row flagged `oneway: true`
without its `undo`; an `act` not keyed by letters but `z`, a list empty or
holding anything but text, a step with a fill-in placeholder (an angle-bracketed word with no
spaces) or a line break; an excerpt (once a field carries one) not `{text, lang, src}`, with blank `text`, a `lang`
off its label shape or a `src` of more than one line; `evidence` neither text nor a
non-empty list of text; a malformed
`detail` (a bullet neither text nor `{t, sub}`, a section not `{h, b}`, both `t` and `h`,
bullets and sections mixed), or a `detail.o` key not a letter but `z`.

**Lints** (exit 2; each line says how to fix it, or leave it knowingly; never pad). A card's
lint prints `lint: card N:`, then the start below (— is none); a page-wide one prints
`lint: page:`.

| Key | Line starts | Fires on |
|---|---|---|
| `page` | `page:` | an id in the page title, the lede, a layer's title, note or shared context, or a `refs` short or question |
| `group` | `page:` | a bundle (a layer with `shared`) holding fewer than two cards |
| `refs` | `page:` | a `refs` answer holding an id (left as given when it is the operator's words) |
| `id` | — | an id in any card text: a hash, an item tag, a ticket key, a label like OQ3, decision N; a label a card declares passes with its short name beside it |
| `count` | — | a count in the flat part or a visible level that Context (with its bundle's `shared`) does not name |
| `named` | — | a named mode, setting, review, plan, document, … not glossed in Context |
| `tldr` | — | a TLDR bullet, at any level, that may carry the recommendation |
| `what` | — | a leftover `what`: move it into `context` |
| `shape` | `shape:` | a level off its shape, Context past its size, a long Impact facet, a label's short name past 6 words |
| `rec-only` | `impact:` | an Impact effect that reads as the recommended option's alone |
| `mech` | `impact:` | an option's effect, but `z`'s (its `blocks` row's `happens`, else its `impact`), of 4 words or fewer that does not open on no, nothing, none or unchanged: a label, not the mechanism |
| `process` | `impact:` | a process phrase (a review comment, another round, your time, a blocked session) in an Effect or Reach at any level, a `blocks` row or an option's `impact` but `z`'s; never the wait, never a round ask |
| `grow` | `depth:` | a level not longer than the one below it |
| `bg` | `depth:` | Background thin (where levelled) or long |
| `row` | `depth:` | an option but `z` with no `blocks` row |
| `opt` | `depth:` | an option's detail thin (where levelled) or long |
| `ev` | `depth:` | evidence thin (where levelled) or long |
| `all` | `depth:` | the card long in all |
| `key` | `depth:` | a `detail` key the page does not show |
| `oneway` | `oneway:` | a ⚠ card with no `blocks` row flagged one-way; a flagged row while the Impact carries no undo |

Then the cold read: list each noun phrase in the Impact, TLDR, option titles and one lines
that names a specific thing, and point to its gloss in `context`. Of each effect, ask: does
it name what happens to the thing being built? Could you say how it happens, not only that
it does?
