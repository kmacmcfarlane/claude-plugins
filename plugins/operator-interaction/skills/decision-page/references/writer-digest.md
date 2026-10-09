# Writer digest

What a writer of `cards.json` needs, in one read: the fields, the level shapes, the floor's
must-haves and the lints. Read this instead of `cards-schema.md` and
`assets/cards.example.json`; open the schema only for a case this does not settle (older
data, a republish migration, the answers collection). The schema is the authority where they
differ; `tests/test_digest.py` keeps this digest naming every required field and every lint.

## The floor, per card

Each card meets the `decisions` skill's floor: what is decided in plain words, every term
glossed; its Impact (effect, wait, reach, undo, cost); Why now and what it blocks; Why ask;
the options, each with its consequence; decide later as `(z)`; the recommendation, or the
labelled reason there is none. Keep the caller's numbers. No ids anywhere on the page: a
decision by its slug `[[N]]`, an item, series, branch or commit by its short name; a fact
only an id carries goes in backticks in `act` or `evidence`.

## Top level

| Key | Required | Shape |
|---|---|---|
| `layers` | yes | `[[key, title, note], …]`, the groups in display order |
| `follow` | yes | copied from the example as it stands (below) |
| `cards` | yes | one per decision, in the `decisions` skill's order |
| `page` | no | `{title, lede, doc: {name, url}}` |
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
| `n` | yes | whole number, unique |
| `L` | yes | a `layers` key |
| `t` | yes | short name, 2–6 words, a noun phrase |
| `rev` | yes | non-empty; UTC time written; new on any change to the card |
| `context` | yes | 1–2 sentences, ~30–60 words: introduces every count, named mode, setting, review, plan, document, item or label the flat part uses; then the resume cue. Does not repeat the TLDR |
| `impact` | yes | `{effect, wait, reach, undo}` as text, `cost` optional; across all options, favouring none; `effect` under ~10 words, `(a) …; (b) …` where outcomes differ; each facet ~16 words |
| `tldr` | yes | 1–2 terse fragment bullets: what is decided, what rides on it; never the recommendation |
| `why` | yes | Why now, and what it blocks |
| `whyask` | yes | what goes wrong if the recommendation were taken alone |
| `rec` | yes | an option letter, or `null` |
| `norec` | when `rec` is null | `your preference — no recommendation`, or `no recommendation — outside my authority` and why |
| `o` | yes | `[[letter, full, impact, title, oneLine], …]`, `a`… in order, ending `z` (decide later) |
| `basis` | yes | `strong`, `partial`, `thin` or `none` |
| `reason` | yes | one clause, the rec's reason |
| `unknown` | yes | what is not known, or `none` |
| `blocks` | required when `warn`; expected on every card | `{letter: {happens, undo, who, cost}}` for every option but `z`, each cell ~5–25 words |
| `act` | when an option asks the operator to act | `{letter: ["step", …]}`, not `z`; one line per step, no `<placeholder>`, no line break (a multi-line paste goes in a `/…` file) |
| `warn` | no | `true` for ⚠ one-way |
| `class`, `dep`, `evidence`, `ifleft`, `roundcosts`, `ifunanswered` | no | `dep` usually slugs (`[[41]] (b)`); `evidence` text or a list of tagged claims with paths and links |
| `detail` | no | the levels, below |

An option: `title` at most six words, verb first; `oneLine` reads after the page's label
(`because:` on the rec, `not recommended because:` on the others, `if left:` on `z`,
`if chosen:` with no rec); `full` and `impact` are the option and its consequence.

## Levels and their shapes

`detail` holds `[medium, high]` per part: `context`, `impact`, `tldr`, `rec`, `why`,
`whyask`, `dep`, `evidence`, and `o: {letter: [medium, high]}` (not `z`). A bullet is
`"text"` or `{"t": "text", "sub": ["text"]}`; a section is `{"h": "heading", "b": [bullets]}`.
`impact` levels are facet objects (`{"effect": bullet, …}` at medium, `{"effect": [bullets], …}`
at high).

| Level | Shape |
|---|---|
| summary (the field itself) | 1–2 sentences; TLDR 1–2 bullets; Impact one facet a line |
| medium | at most ~6 terse bullets (≤ ~14 words, one sentence), ≤ 2 sub-bullets each; the Impact one bullet per facet, options in its sub-bullets |
| high | headed sections with bullets and sub-bullets; full sentences allowed |

Levels scale with the decision: a small call carries none; a wide or ⚠ one-way card carries
medium and high on its visible parts and on the fold items with depth to give. Each level is
longer than the one below. Soft sizes at a part's top level: Background (`why` + `whyask`)
~150 words; each option's text plus its `blocks` row ~60–120; `evidence` ~150; the card in
all ~600–900. Never pad: a fact no source holds goes under `unknown`.

## The checks

**Refusals** (the page renders nothing; `scripts/check_cards.js` prints them first, exit 1):
a bad or duplicate `n`; option letters not single `a`–`z`, out of order, or not ending `z`;
a `rec` not among them, or null without `norec`; a missing required field; empty `rev`; blank
`context`; a TLDR bullet, at any level, opening on Rec or Recommend… or saying I or we
recommend; an `impact` missing a facet; a `basis` outside the four; a `follow` other than the
six; a non-number `refs` key; a ⚠ card without `blocks`, or a `blocks` key not a letter but
`z`, or a row without its text; a malformed `act` (above); `evidence` neither text nor a
non-empty list; a malformed `detail` (a bullet neither text nor `{t, sub}`, a section not
`{h, b}`, both `t` and `h`, bullets and sections mixed), or a `detail.o` key not a letter
but `z`.

**Lints** (exit 2; each line says how to fix it, or leave it knowingly; never pad). By the
runner's key:

| Key | Fires on |
|---|---|
| `page` | an id in the page title, the lede, a layer's title or note, or a `refs` entry |
| `refs` | a `refs` answer holding an id (left as given when it is the operator's words) |
| `id` | an id in any card text: a hash, an item tag, a ticket key, a label like OQ3, decision N |
| `count` | a count in the flat part or a visible level that Context does not name |
| `named` | a named mode, setting, review, plan, document, … not glossed in Context |
| `tldr` | a TLDR bullet, at any level, that may carry the recommendation |
| `what` | a leftover `what`: move it into `context` |
| `shape` | a level off its shape (table above), Context past 2 sentences or ~60 words, a long Impact facet |
| `rec-only` | an Impact effect that reads as the recommended option's alone |
| `grow` | a level not longer than the one below it |
| `bg` | Background thin (where levelled) or long |
| `row` | an option but `z` with no `blocks` row |
| `opt` | an option's detail thin (where levelled) or long |
| `ev` | evidence thin (where levelled) or long |
| `all` | the card long in all |
| `key` | a `detail` key the page does not show |

Then the cold read: list each noun phrase in the Impact, TLDR, option titles and one lines
that names a specific thing, and point to its gloss in `context`.
