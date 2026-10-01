# cards.json and the answers collection

The page (`assets/index.html`) renders whatever `cards.json` beside it holds, and writes one
answer document per decision to the artifact's `db`. This file is the schema for both.
`assets/cards.example.json` is a complete, invented example: three decisions, one ⚠
one-way, one with no recommendation, one reference to a decision not on the page.

Text fields are plain text: the page escapes them. Two marks are rendered:

- `` `code` `` in backticks shows as code;
- `[[N]]` is a **decision slug**: it renders as `[N · short name]` and opens decision N in a
  popup on hover or click. N is a decision on the page (its card's `t` is the short name) or a
  key of `refs`; any other N renders bare. Use a slug wherever a card mentions another
  decision by number.

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
| `tldr` | array of strings | yes | 2–3 fragment bullets: the decision at a glance | flat |
| `context` | string | no | **Context:** where the operator left it · what they decide now | flat |
| `what` | string | yes | **What:** in plain words, items by plain name | Background fold |
| `why` | string | yes | **Why now:** and what it blocks | Background fold |
| `whyask` | string | yes | **Why ask:** what would go wrong if the recommendation were taken alone | Background fold |
| `class` | string | no | the class that opens Why ask, when the caller names classes | a pill, and the Background fold |
| `stakes` | string | yes | reversibility and breadth, as the stakes slot | Stakes fold |
| `warn` | boolean | no | `true` for ⚠ one-way (one-way and high impact) | a ⚠ pill |
| `dep` | string | no | what it depends on, usually slugs with the answer that matters (`[[41]] (b)`) | summary line, Stakes fold |
| `rec` | string or null | yes | the recommended option's letter; `null` with no recommendation | the one bold option, the rec line |
| `norec` | string | when `rec` is null | the labelled exception: `your preference — no recommendation`, or `no recommendation — outside my authority` and why | in place of the rec |
| `o` | array | yes | the options, in letter order, `(z)` decide later last: `[letter, full text, impact, title, one line]` each | see below |
| `basis` | string | yes | the basis word: `strong`, `partial`, `thin` or `none` | rec line, Evidence fold |
| `reason` | string | yes | the one-clause reason for the rec (or for the basis word, with no rec) | rec line |
| `unknown` | string | yes | what is not known, or `none` | Evidence fold |
| `evidence` | string | no | the basis drill-down: what was observed, inferred, assumed | Evidence fold |

An option `[letter, full, impact, title, oneLine]`:

- `title` — at most six words, verb first where it reads naturally; shown flat.
- `oneLine` — one line shown flat after a label the page picks: `because:` on the
  recommended option, `not recommended because:` on the others, `if left:` on `(z)`, and
  `if chosen:` on every option of a card with no recommendation. Write it to follow its label.
- `full` and `impact` — the option and its consequence as the card states them; shown in the
  Options in full fold.

**Size.** The flat part of a card (title, TLDR, context, option titles and one-liners, rec
line) stays near 150 words; the folds carry the rest.

**What the page adds.** It shows the context cue on every card that has one: a page is read
away from the conversation, so its reader is treated as cold. A `⚠ one-way` card gets no
special control: the read-back happens in chat, when the answers are read back.

## The answers collection

The page writes collection `answers`, one document per decision, id the decision number as a
string. Written on every click, and 600 ms after typing stops; a cleared answer deletes the
document.

| Field | Type | What |
|---|---|---|
| `n` | integer | the decision number |
| `choice` | string or null | an option letter, a follow-up key (`later`, `tell me`, `expand`, `dig into`, `you decide`, `drop`), or null for words only |
| `kind` | string or null | `option`, `follow-up`, or null for words only |
| `words` | string | the operator's words, verbatim; for `later`, `tell me` and `dig into` they are its `[when]` or `[what]`; empty when none |
| `rec` | string or null | the recommendation shown when they answered |
| `at` | string | ISO-8601 time of the write |

The page reads the collection live, so an answer set in another tab or by another viewer
shows at once. The collection outlives a republish: answers to decisions on an earlier
version stay, and the read-back keeps only the numbers on the current `cards.json`.
