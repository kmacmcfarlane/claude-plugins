# Legacy cards: reading a card with no format

The frozen reference for every card written before `decision-card/5` (answer 343 (a)): a page
card in a `cards.json` with no `decision-page/5` stamp, and the older working shape of the
answer page (the kit). It holds the reader rules, the map from each older shape to the record
(`card-record.md`), and the dated reader clauses that left the skills when the record came
in: the page's, and the chat card's (§ Older stored cards, in chat). Writers never write these
shapes; they read them, and upgrade on a touch.

*Frozen:* nothing here changes for a new card format. A rule that changes what a current card
holds goes in `card-record.md`; a ruling stays in `rulings.md`, the record of what was decided.

## The six reader rules

1. **Read it as written.** An older card renders by the rules of its era, below.
2. **Never rewrite at render time.** Showing a card does not change it.
3. **Upgrade only on a touch**: a card or block showing, a page publish, a revision. Never on
   an answer, a list line, a tag-size mention, a sweep or a ref.
4. **An answered card is never rewritten.** It stays as written; its answer named its `rev`.
5. **A newer card is never downgraded.** A reader that meets a format newer than it knows
   shows the headline alone and says to update the plugins.
6. **A missing fact is absent, never invented.** What the older card did not hold, the
   record leaves out; the runner's lints for a new card are left knowingly on it.

What v5 removed from every view stays removed on a legacy card: its card-level effect (the
page's `impact.effect`, a stored `impact:` line's `→ …`) is not shown; its options' own
effects are. Nor is a stored Rec line shown as written: its basis and reason show in the
Assumptions fold (**A stored Rec line**, below).

## The upgrader

The `decision-page` skill's `scripts/upgrade_cards.js` moves a `cards.json` to
`decision-page/5`, format only, every `rev` kept byte for byte (an answer counts only when its
`rev` equals its card's exactly, so a minute-form `rev`, `…T09:30Z`, stays as it is; a `rev`
that is no UTC time at all gets a new one, reported *new rev*). It tells the shapes apart card by card and refuses, all or nothing, any card it
cannot fully map: no question (`--questions`), a field the shape does not have, an unknown
scope level, unequal assumption lists, a writer marker, a newer stamp. `--only` limits it to a
set of decisions; `--records` also writes one record per card, without `L` and `dep`. Each card
it writes carries `upgraded`, `{from, rev}`: the shape it came from and the `rev` it kept. Beside
`rev`, never touching it, it marks the card as carried over: until a writer revises it with a new
`rev`, the pre-publish runner lints its set check rather than refusing it. **A gap:** data
upgraded by an earlier upgrader, before the marker, carries none, so its set check is a
refusal. Re-upgrade it from its kit or legacy source, which this upgrader marks, or list its
items. The live answer page is still in the kit shape, so the migration pass runs this
upgrader and its cards carry the marker.

## Legacy shipped → `decision-card/5`

| Legacy page card | Record |
|---|---|
| `o[i] = [k, full, impact, title, oneLine]` | `options[i] = {k, title: title, line: oneLine, text: full, effect: blocks.k.happens, else impact}`; (z)'s `impact` is its `effect`, what waiting does |
| `blocks.k.who` | `options[k].reach` |
| `blocks.k.undo`, `blocks.k.cost`, `blocks.k.oneway` | `options[k].undo`, `.cost`, `.oneway` |
| `act.k` | `options[k].act` |
| `detail.o.k` | `options[k].detail` |
| `warn` | `oneway` |
| `unknown` | `open: [unknown]`; none when it says `none` |
| `impact.effect`, `detail.impact[*].effect` | dropped: no card-level effect. An option with no effect of its own takes its clause of the old effect (`(b) …`) |
| `stakes` | dropped: the Impact's undo and reach carry it |
| `what` | `what`, as written |
| every other field | kept as it is |

## The kit → `decision-card/5`

The answer page's working kit, in its v4 and its v5 layouts, holds options as objects with no
stamp.

| Kit card | Record |
|---|---|
| option `text` | option `title` |
| option `pros`, `cons` (the one-line texts) | option `pro`, `con` |
| option `prosT`, `consT` (the table's rows) | option `pros`, `cons` |
| `act.k` | `options[k].act` |
| `assume {basis, reason, assumptions[], tripwires[]}` | `basis`, `reason`, `assume[{rests: assumptions[i], tw: tripwires[i]}]` (unequal lists refused) |
| `assume.unknown` (v4 layout), `open` (v5 layout) | `open` |
| `background {why, whyask}` | `why`, `whyask` |
| an `evidence` attachment | `evidence`, one flat list: a text body is one item `<title> — <text>`; a list body one item per entry, the first prefixed `<title> — ` |
| any other attachment | `attached`, as it stands, shown as the Attached fold; a kind the record has not (`excerpt`, `summary`, `link`, `example`, `preview`, `table`, `matrix`, `steps`, `checks`, `depmap`), or an `attached` that is not a list, refused; a null `attached` is none |
| an `example` attachment's `mode` | its `form`: `mock` or `narrative` as written; `invented to illustrate`, or none, `narrative` (the kit drew every example as paragraphs); any other word refused |
| `scope {k, text}` | `scope {level, says}`: `shapes the work` → `shapes`, `required` → `required`, `outside the criteria` → `outside`; any other refused |
| `likelihood {basis, text}` | `likelihood {kind, seen}`: `observed` → `observed`; any other word → `evidence`, the word kept at the head of `seen` as `(<word>) ` |
| `what` text; a list; `{intro, items[{name, is, per}]}` | `what`; `items[{name}]`; `what: intro`, `items[{name, about: is, per}]` |
| `finding {what, where, code}` | `finding {mechanism: what, where, excerpt: code}` |
| `rejected [{bold, bullets}]` | `rejected [{t: bold, why: bullets}]`, shown as the Rejected alternatives fold; a `bold` or a bullet that is not one line of text, or no bullets, refused |
| `dep {n, letters}` | `dep` as text: `only if [[N]] is (a) or (b)`; no letters: `after [[N]] is answered, whatever its answer` |
| `impact.effect` | dropped |

## Older page data, by era

What each older `cards.json` held, and how a reader shows it. On a republish, the upgrader
moves every card to `decision-page/5` first; then a card with no counting answer, or one
revised anyway, gets what its era lacked, each with a new `rev`, handed over as shown again.
A card the operator has answered stays as it is, its lints left knowingly.

- **A `cards.json` written before `impact` existed** carries a `stakes` field and no `impact`.
  An older `stakes` field is ignored: Undo and Reach carry it. On a republish, each kept card
  gets `impact` from the caller's stored Impact line, backfilled as the decisions skill's
  re-show says when the store has none.
- **A `cards.json` written before Context came first** has either no `context` or a cue-only
  one with its `what` after the cue. The one-time Context migration kept its `rev`: a card
  whose own `what` and resume cue moved into `context`, its terms glossed from its own folds
  alone. A gloss drawn from outside the card was new information: a new `rev`. A `what` such a
  card still holds shows as its What part, after Context (F6), never at the end of Context.
- **A `cards.json` written before `detail` existed** renders with **More** buttons and no
  toggles; it is thin until rewritten. A card that gets `detail` gets a new `rev`.
- **A `cards.json` written before undo went optional** (answer 260, 2026-10-20) carries
  `undo` on the Impact and on every row, and no `oneway` flag. It renders as written, with the
  plain Undo label; a ⚠ card of it lints `oneway:`. On a republish of a card with no counting
  answer, drop the undo of each option reversible at little cost, flag each one-way option,
  keep the Impact's undo only for that option, and give the card a new `rev`.
- **A `cards.json` written before the level shapes** renders its text levels as paragraphs;
  nothing is refused. An older level written as one string, `<reason> · unknown: <unknown>`,
  showed its reason and its unknown as the summary showed the two.
- **A `cards.json` written before bundle groups (2026-10-22)** has layers of three elements:
  each is a plain group. On a republish, a bundle whose items need different answers becomes a
  layer with its `shared` context; a card moved into it whose own text is unchanged keeps its
  `rev`, one whose Context is shortened to lean on the shared context gets a new one.
- **A `cards.json` written before the reference rule (2026-10-22)** may hold a `refs` entry
  for a decision still open, or a `[[N]]` that is neither a card nor a ref (it rendered bare):
  the page refuses it on a republish. Add the open decision as a card, or a ref with its
  answer.
- **A stored Effect** was copied into a page card's `impact.effect` only when it named each
  option's outcome or the card was stored or revised on or after 2026-10-14; otherwise it was
  written from the option effects. The record has no card-level effect: it is dropped.

## Older stored cards, in chat

What a caller's stored card held in earlier forms, and how the decisions skill's chat card and
block show it (`rendering.md`). Each renders as stored, never recomposed at render time, apart
from what v5 removed from every view (a stored effect, a stored Rec line); a revision for any other reason writes it to the current
rules.

- **Older stored lines read as written**, all but the effect. A stored `impact:` line's
  effect, the `→ …` before its `later:`, is not shown in any era: the card's **Impact:** line
  starts at its wait, and the options' own lines say what each does. That holds for an
  Impact line stored before Effect covered the options (2026-10-14), which gave the
  recommended option's effect alone. A revision writes the line with no effect.
- **An option stored on one line**, its impact after a dash (a caller's store form included),
  renders in the current form: its facets on the line under the option.
- **A card stored in the older form** may carry a plain `undo:` on every option and on its
  Impact line, from before undo was shown only where it bites (answer 260, 2026-10-20). It
  renders as stored, and an undo there that says the option cannot be undone, or only at real
  cost, is read as the marker, the read-back included (`replies.md`). A revision rewrites its
  undos to the rule (`rendering.md` § Impact).
- **Older stored cards render as before.** A stored Context holding the cue alone, from before
  Context took the terms, is the card's **Context:** line as it stands. A stored card with no
  Context at all renders as it did before Context existed: the **Impact:** line directly
  under the title, then **What:**, **Why now:**, **Why ask:** and the options, with no Context
  section; a block stored with no Context keeps the older order the same way. A cold re-show
  still backfills the cue (`rendering.md` § Re-show with what changed): a stored card from
  before the cue existed is revised, its cue backfilled from the record, *not recorded* when
  no record holds it, and stored as its Context, and renders in the current order from then
  on.
- **A stored unknown** (a Rec line's `· unknown: …`, or an `unknown` field) shows as the
  card's ▸ Open questions line (`rendering.md` § Folds), one open question; `unknown: none`
  shows no fold.
- **A stored Rec line** (`Rec (x) · basis word — reason`, or a `rec:` line with its basis and
  reason) shows as the card's ▸ Assumptions line (`rendering.md` § Folds): its basis word the
  summary, its reason inside the fold, and no assumption invented; the recommendation is the
  bold option. A card stored with none of its assumptions shows the basis alone.

## A headline with no card

A `decision N:` headline whose only indented lines are `raised:` (and `revised:`) is a
headline-only decision, never a stored card to backfill as one.

## The cut

When no open decision anywhere in the estate has a stored legacy card (an unanswered decision
on an item not done, with indented card lines and no current record), this reference is cut
to reading a headline and an answer line, which is all a ref or a tooltip of an answered card
needs. The stores are found by discovery, the decision store in each repo checkout beside this
one, never by a written path.
