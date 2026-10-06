# cards.json and the answers collection

The page (`assets/index.html`) renders whatever `cards.json` beside it holds, and writes one
answer document per decision to the artifact's `db`. This file is the schema for both.
`assets/cards.example.json` is a complete, invented example: three decisions, each with its
impact, one ⚠ one-way (with its Impact table rows), one with no recommendation, one reference
to a decision not on the page.

**The page checks the data before it renders anything** and, when a check fails, shows *The
decisions can't be shown: cards.json is not valid* with the first problems found, and renders
nothing else. It refuses: an `n` that is not a whole number or is used twice; an option letter
that is not a single `a`–`z`; options out of letter order or not ending in `z`; a `rec` that is
not one of the card's letters (or null without `norec`); a missing required field; an empty
`rev`; an `impact` without its effect, wait, reach and undo as text; a `basis` word outside
the four; a `follow` list other than the fixed six; a `refs` key that is not a number; a ⚠
card without its `blocks`; a `blocks` entry that is not an option letter other than `z`, or
lacks its text. Every text field is
escaped wherever it reaches the page, attributes and ids included.

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
| `rev` | string | yes | the card's revision: a label that changes whenever the card does (a `tell me` answer added, a re-ask, a reframe kept under its number). An ISO-8601 UTC time when you write it (`2026-01-12T09:30:00Z`) is the convention, but it is only ever compared for equality, never as a time | not shown; the page copies it into each answer, and it decides which answers count (below) |
| `impact` | object | yes | the **Impact:** line (the `decisions` skill's `references/rendering.md` § Impact): `effect` (what changes if the recommendation is taken; with no recommendation, each option's in a few words), `wait` (what waiting costs, what it blocks), `reach` (who or what is affected), `undo` (how it is reversed, or one-way), each non-empty text; `cost` optional. Copied from the caller's stored Impact line where it keeps one, never composed again | `effect` at tag size (after an arrow) in the map, on the closed card and in the popup; the whole line flat at the top of the open card; `wait` as the Impact table's Wait row |
| `tldr` | array of strings | yes | 2–3 fragment bullets: the decision at a glance | flat |
| `context` | string | no | **Context:** where the operator left it · what they decide now | flat |
| `ifleft` | string | no | **If left:** an ask for another round: each leftover finding and what it would break | flat |
| `roundcosts` | string | no | **A round costs:** an ask for another round: time, quota, the operator's attention | flat |
| `ifunanswered` | string | no | **If unanswered:** a status-quo default (`I leave X as it is …`) | flat |
| `what` | string | yes | **What:** in plain words, items by plain name | Background fold |
| `why` | string | yes | **Why now:** and what it blocks | Background fold |
| `whyask` | string | yes | **Why ask:** what would go wrong if the recommendation were taken alone | Background fold |
| `class` | string | no | the class that opens Why ask, when the caller names classes | a pill, and the Background fold |
| `warn` | boolean | no | `true` for ⚠ one-way (one-way and high impact) | a ⚠ pill |
| `blocks` | object | when `warn`; optional otherwise | the block's Impact table row per option: keyed by letter, every option but `z` on a ⚠ card (any of them otherwise), each `{happens, undo, who, cost}` — the Effect, Undo (plainly: it decides the read-back) and Reach cells, and Cost, optional | the Impact table in Options in full, which opens unfolded on a ⚠ card; an option with no entry shows its `impact` as the Effect and `—` in the rest |
| `dep` | string | no | what it depends on, usually slugs with the answer that matters (`[[41]] (b)`) | summary line, Dependencies fold |
| `rec` | string or null | yes | the recommended option's letter; `null` with no recommendation | the one bold option, the rec line |
| `norec` | string | when `rec` is null | the labelled exception: `your preference — no recommendation`, or `no recommendation — outside my authority` and why | in place of the rec |
| `o` | array | yes | the options, in letter order, `(z)` decide later last: `[letter, full text, impact, title, one line]` each | see below |
| `basis` | string | yes | the basis word: `strong`, `partial`, `thin` or `none` | rec line, Evidence fold |
| `reason` | string | yes | the one-clause reason for the rec (or for the basis word, with no rec) | rec line |
| `unknown` | string | yes | what is not known, or `none` | rec line, Evidence fold |
| `evidence` | string | no | the basis drill-down: what was observed, inferred, assumed | Evidence fold |

An option `[letter, full, impact, title, oneLine]`:

- `title` — at most six words, verb first where it reads naturally; shown flat.
- `oneLine` — one line shown flat after a label the page picks: `because:` on the
  recommended option, `not recommended because:` on the others, `if left:` on `(z)`, and
  `if chosen:` on every option of a card with no recommendation. Write it to follow its label.
- `full` and `impact` — the option and its consequence as the card states them; shown in the
  Options in full fold.

**Size.** The flat part of a card (title, Impact line, TLDR, context, option titles and
one-liners, rec line) stays near 150 words; the folds carry the rest. The `effect` stays
under about 10 words: it is shown alone, at tag size, in the map.

**What the page adds.** Every view shows the impact: the map and a closed card the effect, an
open card the Impact line, and its Options in full fold the Impact table (a row per option,
then the Wait row; Effect, Reach, Undo, Cost). It shows the context cue on every card that
has one: a page is read away from the conversation, so its reader is treated as cold. A
`⚠ one-way` card is the decisions skill's block: the card's essentials plus its Impact table,
unfolded. An older `stakes` field is ignored: Undo and Reach carry it.

**Republishing older data.** A `cards.json` written before `impact` existed is refused by the
current template. On a republish, add `impact` to each kept card (a `stakes` field may stay,
ignored); the impact comes from the caller's stored Impact line, backfilled as the decisions
skill's re-show says when the store has none. It gets no special
control: the read-back of a one-way pick happens in chat, when the answers are read back.

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
