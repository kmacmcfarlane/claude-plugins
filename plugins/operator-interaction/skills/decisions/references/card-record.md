# The card record (`decision-card/5`)

One record for a decision's card, whichever surface shows it: the answer page (the
`decision-page` skill, where a page card is this record plus its layer `L` and its dependency
line `dep`), and a caller's stored card. It is this skill's card, written as data: each field
is a part of the card in `rendering.md`, and the floor in SKILL.md is met by the record. The
record is versioned by its `format` stamp (answer 343 (a)); a card with no stamp is in an
older format, read by `legacy-cards.md` and upgraded before it is shown again.

**Writers write only `decision-card/5`.** A record is JSON. Every text field is plain text:
the page escapes it, and only two marks render, `` `code` `` in backticks and `[[N]]`, a
decision slug. A part, facet or field that is missing, blank or says only `none`, `n/a` or a
dash is not shown (*none is not shown*, 2026-10-14), except where its none is a statement (the
Impact's `wait` and `reach`, an `undo` when given, the `basis` word).

## Required: to render, and of a new card

Two kinds of required:

- **To render**: a reader refuses the card without it (the page's check names the field).
- **Of a new card**: what a writer owes on every card it writes now, linted by the
  pre-publish runner (the `decision-page` skill's `scripts/check_cards.js`), never refused.
  A card upgraded from an older format may lack it, knowingly: the split is what lets an
  upgraded card render with nothing invented. A missing fact is absent, never invented.

## A card

| Key | Type | Required | What |
|---|---|---|---|
| `format` | `"decision-card/5"` | to render | the stamp. A reader refuses a newer number, naming it, and never downgrades it |
| `n` | integer | to render | the decision number, 1 or more: the caller's own, never reused |
| `rev` | `YYYY-MM-DDTHH:MM:SSZ` | to render | the card's revision. Any change to a card gets a new `rev`, Context included: an **Added:** line after `tell me`, more detail after `expand`, a `dig into` finding, a corrected fact, a re-ask. Only a format-only upgrade keeps it: an older card moved to `decision-card/5` by the `decision-page` skill's `scripts/upgrade_cards.js`, its fields moved and none added. A fact drawn from anywhere outside the card is new information: a new `rev`. A new card writes it to the second; a minute-form `rev` (`…T09:30Z`) from older data is read, and an upgrade keeps it byte for byte, since an answer counts only when its `rev` equals the card's exactly. It is compared only for equality, never as a time |
| `raised` | `YYYY-MM-DDTHH:MM:SSZ` | optional | when the decision was first raised |
| `t` | text | to render | the short name, 2–6 words, a noun phrase: what a slug shows |
| `q` | text, one line | to render | the question as asked, the headline's |
| `label` | `{id, name}` | optional | the source label, when raised from one labelled item of a source (a review's finding, a plan's question): `id` one word (`F7`), `name` its short name, 2–6 plain words (the `plain-names` skill's § Source labels) |
| `oneway` | boolean | optional | `true` on a ⚠ one-way card (one-way and high impact). Each option of a ⚠ card but (z) then gives its `reach` |
| `class` | text | optional | the why-ask class, when the caller names classes: shown first in Why ask |
| `tldr` | list of text | to render | one or two terse bullets: what is decided and what rides on it, never the recommendation (the options mark it) |
| `context` | text | to render | **Context:** one or two sentences introducing every term, item, count and named thing the card uses, by name, never by id; then where the operator left it |
| `open` | list of text | optional | **Open questions**: what is not known yet, one question each (it was `unknown`). Empty or none: no fold |
| `impact` | `{wait, reach, undo?, cost?}` | to render | the **Impact**, across all the options, favouring none: `wait` (what waiting costs, what it holds up) and `reach` (who or what any option reaches), each non-empty text; `undo` only when some option is one-way or costly to undo, naming that option (*(b) none — lost search ranking does not come back*); `cost` when it is what the operator weighs. There is **no card-level effect**: each option carries its own (the operator's v5 ruling, 2026-10-22). Effect and Reach describe the system the work builds, never the process, which is the Wait |
| `options` | list of options | to render | the options in letter order, (z) decide later last, each letter once (§ An option) |
| `rec` | a letter, or `null` | to render | the recommended option's letter |
| `norec` | text | to render when `rec` is null | the labelled exception: `your preference — no recommendation`, or `no recommendation — outside my authority` and why |
| `basis` | `strong`, `partial`, `thin` or `none` | to render | the basis word (`evidence-basis.md`): the **Assumptions** fold's summary opens on it, `basis: partial`, and its Basis line shows it, every card |
| `reason` | text | of a new card | one clause: the rec's reason, or the basis word's with no rec; shown after the basis word, inside the Assumptions fold |
| `evidence` | text, or a list of text | optional | the basis drill-down: what was observed, inferred and assumed, with the paths and `https://` links behind each claim; inside the Assumptions fold, after the Basis line |
| `assume` | list of `{rests, tw}` | optional; a card with a recommendation and none is linted | **Assumptions**: each thing the call rests on (`rests`) with its tripwire (`tw`), the sign that would change it; both non-empty text. Shown in the closed Assumptions fold after Open questions and before the Impact, each assumption in bold with its *tripwire:* under it; the fold's summary counts them, `basis: partial · 2 assumptions with tripwires`. What is not known yet is never an assumption: it is `open` |
| `why` | text | of a new card | **Why now:** and what it blocks. Its first sentence must stand alone, about 25 words at most: it is the Background fold's summary on every surface (rewrite a longer one, never cut it) |
| `whyask` | text | of a new card | **Why ask:** what would go wrong if the recommendation were taken alone |
| `ifleft` | text | optional | **If left:** on an ask for another round: each leftover finding and what it would break |
| `roundcosts` | text | optional | **A round costs:** on an ask for another round |
| `ifunanswered` | text | optional | **If unanswered:** a status-quo default |
| `detail` | object | optional | the card parts' fuller renditions, `[medium, high]` each (§ Levels) |
| `what` | text | optional | older data: shown at the end of Context; a new card does not set it (the runner lints it) |

## An option

| Key | Type | Required | What |
|---|---|---|---|
| `k` | one letter `a`–`z` | to render | its letter; `z` is decide later |
| `title` | text | to render | at most six words, verb first where it reads naturally |
| `line` | text | optional | one line shown after the label the page picks: `because:` on the recommended option, `not recommended because:` on the others, `if left:` on (z), `if chosen:` on every option of a card with no recommendation |
| `text` | text | optional | the option in full, its summary level |
| `effect` | text | to render, but on (z) | its own effect, by its mechanism: how it happens, who meets it and when, the before and after; never a bare label. On (z), what waiting does |
| `reach` | text | of a new card; to render on a ⚠ card, but (z) | who or what it reaches |
| `undo` | text | with `oneway` | how it is undone and at what cost, or that it cannot be; given only on an option one-way or costly to undo |
| `oneway` | boolean | optional | `true` on an option one-way or costly to undo; it then needs its `undo` |
| `cost` | text | optional | its cost, where it has one |
| `act` | list of text | optional | **To act on (x):** the steps the operator takes, one line each, in order; never on (z), never a fill-in placeholder (`<dir>`), never a secret's value |
| `detail` | `[medium, high]` | optional | the levels of `text` |

The option's own levels, steps and facets live in it, never in letter-keyed maps beside it.

## Levels

`detail` holds the fuller renditions of a card's parts, `[medium, high]` each: `context`,
`tldr`, `impact` (each level `{wait, reach, undo, cost}`, a facet text, a bullet or a list of
bullets), `rec` (the basis line's reason), `why`, `whyask`, `evidence`. An option's own levels are its
`detail`. A bullet is `"text"` or `{"t": "text", "sub": ["text"]}`; a section is
`{"h": "heading", "b": [bullets]}`; a rendition is text, a list of bullets, or a list of
sections. Levels scale with the decision: a small call may carry none; a wide or one-way
decision carries the most. Each level has its shape: summary one or two sentences (the TLDR
one or two bullets, the Impact one facet a line), medium terse bullets with a sub-bullet or
two, high headed sections. The shapes and sizes are the `decision-page` skill's
`references/cards-schema.md` § Size and `references/writer-digest.md` § Levels and their
shapes.

## Fields an upgraded card may already carry

The upgrader maps the answer page's working kit into the record, and some of the kit's parts
have no row above yet: `what` as the What part with its `items`
(`[{name, where?, about?, per?}]`), `finding` (`{label?, title?, where?, mechanism, excerpt?}`),
`scope` (`{level, says}`), `likelihood` (`{kind, seen}`) and `best`, `attached`, `rejected`
(`[{t, why}]`), and on an option `pro`, `con`, `pros`, `cons` and `plan`. A reader keeps them as
data and does not show them; each joins the tables above when the page and the chat card show
it. In the kit, `pros` and `cons` were the one-line texts and `prosT` and `consT` the table's
rows; the record names the one-line texts `pro` and `con` and the rows `pros` and `cons`. The
kit's `evidence` attachments become the record's `evidence`, a flat list of text: their ids are
dropped (the upgrader reports each, and refuses a card whose text links to one).

## Older cards

A card with no `format` is legacy: `legacy-cards.md` reads it, and a writer upgrades it
before showing it at card or block size (a format-only upgrade, `rev` kept). An answered card
is never rewritten.
