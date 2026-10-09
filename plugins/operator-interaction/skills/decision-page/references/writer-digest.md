# Writer digest

What a writer of `cards.json` needs, in one read: the fields, the level shapes, the floor's
must-haves, the refusals and the lints. Read this instead of `cards-schema.md` and
`assets/cards.example.json`; open the schema only for a case this does not settle (older
data, a republish migration, the answers collection). The schema is the authority where they
differ; the plugin's `tests/test_digest.py` keeps this digest naming every field with its
Required cell, every lint key with its line start, and the runner's thresholds.

## The floor, per card

Each card meets the `decisions` skill's floor: what is decided in plain words, every term
glossed; its Impact (effect, wait, reach, undo, cost); Why now and what it blocks; Why ask;
the options, each with its consequence; decide later as `(z)`; the recommendation, or the
labelled reason there is none. Keep the caller's numbers. No ids anywhere on the page: a
decision by its slug `[[N]]`, an item, series, branch or commit by its short name; a fact
only an id carries goes in backticks in `act` or `evidence`.

## Text

Every text field is plain text: the page escapes it, and only two marks render: `` `code` ``
in backticks, and `[[N]]`, a decision slug (a decision on the page, or a `refs` key). Links
(`https://` only) are clickable in the medium and high levels, in the fold parts at every
level and in an option's **More** detail; nowhere else (not a heading, a visible part's
summary, the Impact table, an option's `impact`, `act`, the popup or a slug). `page.doc.url`
must start `https://`, or it is not shown.

## Top level

| Key | Required | Shape |
|---|---|---|
| `page` | no | `{title, lede, doc: {name, url}}`; `url` must start `https://` |
| `layers` | yes | `[[key, title, note], …]`, the groups in display order |
| `follow` | yes | copied from below as it stands |
| `cards` | yes | one per decision, in the `decisions` skill's order |
| `refs` | no | `{"N": {short, q, a, when}}` for a slugged decision not on the page |

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
| `rev` | yes | non-empty: the UTC time you write it, by convention. New on any change to the card, Context included, since answers given to an old `rev` stop counting |
| `context` | yes | 1–2 sentences, ~30–60 words: introduces every count, named mode, setting, review, plan, document, item or label the flat part uses; then the resume cue. Does not repeat the TLDR. Its high level holds the facts a cold reader has lost |
| `impact` | yes | `{effect, wait, reach, undo}` as text, `cost` optional; across all options, favouring none. Write `effect` from the card's own option effects (`blocks`, each option's `impact`), never copying a stored Effect line, which is the recommendation's; under ~10 words, `(a) …; (b) …` where outcomes differ |
| `tldr` | yes | 1–2 bullets, each one sentence of about 14 words or fewer: what is decided, what rides on it; never the recommendation |
| `ifleft` | no | **If left:** on an ask for another round |
| `roundcosts` | no | **A round costs:** on an ask for another round |
| `ifunanswered` | no | **If unanswered:** a status-quo default |
| `why` | yes | Why now, and what it blocks |
| `whyask` | yes | what goes wrong if the recommendation were taken alone |
| `class` | no | the class that opens Why ask, when the caller names classes |
| `warn` | no | `true` for ⚠ one-way |
| `blocks` | expected on every card; required when `warn` | `{letter: {happens, undo, who, cost}}` for every option but `z`, each cell ~5–25 words |
| `act` | when an option asks the operator to act; optional otherwise | `{letter: ["step", …]}`, not `z`; each list non-empty, each step text on one line, no `<placeholder>`; a step names where a secret goes, never its value; a paste text holding an angle-bracketed word, or of more than one line, goes in a file named by its `/…` path |
| `dep` | no | usually slugs with the answer that matters (`[[41]] (b)`) |
| `rec` | yes | an option letter, or `null` |
| `norec` | when `rec` is null | `your preference — no recommendation`, or `no recommendation — outside my authority` and why |
| `o` | yes | `[[letter, full, impact, title, oneLine], …]`, `a`… in order, ending `z` (decide later) |
| `basis` | yes | `strong`, `partial`, `thin` or `none` |
| `reason` | yes | one clause: the rec's reason, or, with no rec, the reason for the basis word |
| `unknown` | yes | what is not known, or `none` |
| `evidence` | no | text, or a list of tagged claims (*Observed: …*) with the paths and links behind each |
| `detail` | no; its levels scale with the decision | the levels, below |

Do not set `what`: it is older data only.

An option: `title` at most six words, verb first; `oneLine` reads after the page's label
(`because:` on the rec, `not recommended because:` on the others, `if left:` on `z`,
`if chosen:` with no rec); `full` and `impact` are the option and its consequence.

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

The lints fire past these (`scripts/check_cards.js`):

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

## The checks

**Refusals** (the page renders nothing; `scripts/check_cards.js` prints them first, exit 1):
a bad or duplicate `n`; option letters not single `a`–`z`, out of order, or not ending `z`;
a `rec` not among them, or null without `norec`; a missing required field; empty `rev`; blank
`context`; a TLDR bullet, at any level, opening on Rec or Recommend… or saying I or we
recommend; an `impact` missing a facet; a `basis` outside the four; a `follow` other than the
six; a non-number `refs` key; a ⚠ card without `blocks`, or a `blocks` key not a letter but
`z`, or a row without its text; an `act` not keyed by letters but `z`, a list empty or
holding anything but text, a step with a fill-in placeholder (an angle-bracketed word with no
spaces) or a line break; `evidence` neither text nor a non-empty list of text; a malformed
`detail` (a bullet neither text nor `{t, sub}`, a section not `{h, b}`, both `t` and `h`,
bullets and sections mixed), or a `detail.o` key not a letter but `z`.

**Lints** (exit 2; each line says how to fix it, or leave it knowingly; never pad). A card's
lint prints `lint: card N:`, then the start below (— is none); a page-wide one prints
`lint: page:`.

| Key | Line starts | Fires on |
|---|---|---|
| `page` | `page:` | an id in the page title, the lede, a layer's title or note, or a `refs` short or question |
| `refs` | `page:` | a `refs` answer holding an id (left as given when it is the operator's words) |
| `id` | — | an id in any card text: a hash, an item tag, a ticket key, a label like OQ3, decision N |
| `count` | — | a count in the flat part or a visible level that Context does not name |
| `named` | — | a named mode, setting, review, plan, document, … not glossed in Context |
| `tldr` | — | a TLDR bullet, at any level, that may carry the recommendation |
| `what` | — | a leftover `what`: move it into `context` |
| `shape` | `shape:` | a level off its shape, Context past its size, a long Impact facet |
| `rec-only` | `impact:` | an Impact effect that reads as the recommended option's alone |
| `grow` | `depth:` | a level not longer than the one below it |
| `bg` | `depth:` | Background thin (where levelled) or long |
| `row` | `depth:` | an option but `z` with no `blocks` row |
| `opt` | `depth:` | an option's detail thin (where levelled) or long |
| `ev` | `depth:` | evidence thin (where levelled) or long |
| `all` | `depth:` | the card long in all |
| `key` | `depth:` | a `detail` key the page does not show |

Then the cold read: list each noun phrase in the Impact, TLDR, option titles and one lines
that names a specific thing, and point to its gloss in `context`.
