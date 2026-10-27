# Putting decisions to the operator

Loaded from SKILL.md § Intake step 3, `cycle-bindings.md` § Decision channel and
`report.md`. This file binds the librarian to the `operator-interaction` plugin's
`decisions` skill, a soft dependency (README principle 4). It says only what the
librarian supplies to that skill and what the store records. How a decision is written,
ordered and answered is the skill's, and is not restated here.

## When it applies

The skill is available when the session's skill listing carries `operator-interaction:decisions`
(the `operator-interaction` plugin is installed). Then:

- **Load it at Rehydrate** (`rehydrate.md` § Step 2) with the Skill tool, and again after
  every `/clear` or compaction. It is knowledge only: it asks nothing and writes nothing.
- **Every decision the librarian raises follows it:**
  - an Intake ask (step 3);
  - anything dev-cycle raises through the decision channel;
  - a Groom row that needs the operator (`idle-turn.md`);
  - every decision a Report carries.

  It covers the content floor, the impact every view shows (tag size, list line, card,
  block), the order, the layout, the hint, reading replies with an echo, the read-back on a one-way choice in a ⚠ decision, and
  "decide later" with a wake.
- **Never through AskUserQuestion.** That is the librarian's own rule (SKILL.md § Intake
  step 3), and the skill agrees. The opt-in dialog is the one exception (`opt-in.md`).

Without the skill, nothing here applies but the `closed N:` line, the `<repo>#N` form and
the verbatim rule on every answer line (§ What the store records, **Answered**):
`decisions needed:`, its store lines and the replies are as SKILL.md § Report and
`report.md` give them. Without the skill there is no card-record reference, so no card is
stored: each decision is raised headline-only, `$WI raise <id> -- '<question>'`.

## What the librarian supplies to the skill

| The skill asks for | The librarian's binding |
|---|---|
| the caller's numbering | the store counter, the one counter for every question put to the operator (`report.md` § The counter): `decision N:` continues from the highest N (`rehydrate.md` § Step 3); a number is never reused. A source label (a review's F7, a series' OQ3, a gate's G5) is never a number: a decision raised from one labelled item carries it, with its short name, first in the headline's question (§ What the store records) |
| the default wake ("the next time I finish a piece of work and report") | **the next Report**; a `later` with no time or event wakes there |
| the operator's expected return | what the operator said ("back tomorrow morning"), in the item or the transcript; when they said nothing, the return is unknown and every stated deadline goes first |
| who is reading, and how warm | after Rehydrate the operator is **cold** on every decision raised before the reset; the first Report after it re-shows them per the skill, with what changed since each was raised. Between resets: a decision shown in a Report written after the operator's last turn has **not been seen** — background returns can write several Reports while the operator is away — so the next Report shows it at its level again, not *(shown before)*. Your own transcript tells you: has the operator taken a turn since that Report? The store records the same thing (§ What the store records, **Shown** and **Seen**): a reader without the transcript — after a reset, or another session — reads the last showing as unseen when no `seen N:` line follows the last `shown N:` line, and as not recorded (cold) when there is no `shown N:` line |
| related decisions (groups) | the stored group: the decision's last `group N:` member line, read through its group's entity line (§ What the store records, **Grouped and depends**); with none, the item's short name. The stored group's name is chosen at raise: decisions on one item, or on sibling items (one parent) about the same plugin, share one; a decision with no item groups by plugin or files. Never transitive: two groups that share a file stay two groups |
| named templates | none: the librarian names no template, so every decision carries the floor on its own card |
| classes of decision (the class in *why ask* and on the list line) | the reasons in `decide-alone.md` § Class names, the first that applies in § The line's order, picked when the decision is raised; `unclassed` when in doubt whether one applies, which raises |
| a decide-alone class the caller's rules define (the FYI rule's authority) | the kinds `decide-alone.md` § The line lets be decided alone once no reason applies, cited as `class <kind>` on the `decided:` line; beside them, the FYI authority is an answered decision or the task the item carries |
| the record of what was decided alone | the `decided:` line and the Report's **Done alone** group (`decide-alone.md`) |

## What the store records

The store stays the source of truth, and it keeps the **card**, so a re-show after a reset
renders what the operator read instead of composing it again. The card is a **card record**
(`decision-card/5`): one immutable JSON file per revision, `cards/<item id>/<N>/<rev>.card<k>.json`,
written by `$WI raise --record` and named by the indented `card:` line `wi` writes under the
headline (the `work-items` skill's format reference, § Card records). What each field holds is
the `decisions` skill's card-record reference (`references/card-record.md`); this file says only
how the librarian raises, revises and reads a record, and what it binds in one.

- **Raised:** write the card the decisions skill renders as its record, a JSON file in the
  session's scratchpad, by the card-record reference; check it; then raise it:

  ```bash
  node <decision-page skill dir>/scripts/check_cards.js --record <file>
  $WI raise <id> --record <file> [--lines <lines file>]
  ```

  The check is the `decision-page` skill's checker in record mode (its `scripts/check_cards.js`),
  run from that skill's base directory as the session's skill list gives it (the directory
  holding its `SKILL.md`), the way that skill's own pre-publish check runs it; fix what it
  refuses, then raise. `$WI raise` prints N. It writes the record once, then appends the
  headline it builds from the record, `raised:` and the `card:` line; machine lines may ride
  this first raise with `--lines` (**Machine lines**, below). The decision's `group N:` and
  `depends N:` lines are written after the raise (**Grouped and depends**, at raise).
  **Without the checker** (no node, or no `decision-page` skill), the record is stored after
  `wi`'s own checks only (it parses, its headline fields, its secrets), and the Report says so
  in one clause: *card records not schema-checked: no decision-page skill* (or *no node*).
  Without the `decisions` skill as well there is no card-record reference: the librarian raises
  headline-only decisions, `$WI raise <id> -- '<question>'` (§ When it applies, *Without the
  skill*).
- **The headline** is `wi`'s, built from the record's `label` and `q`, never typed:

  ```
  decision N: [<label.id> (<label.name>) · ]<q>[ ⚠ one-way] — options: (a) <title> [recommended] | (b) <title> | … | (z) <title>[ — <norec>]
  ```

  The headline is as the `dev-cycle` skill's `references/record-lines.md` gives the
  `decision:` line, so `wi needs-input` and the counter grep (`^decision [0-9]`) read it
  unchanged; the `card:` line, indented, matches neither `^decision` nor `^answer`.
  `[recommended]` closes the `rec` option's title; with `rec` null, ` — <norec>` follows the
  last option; `⚠ one-way` follows the question when the card's `oneway` is true. When the
  decision is raised from one labelled item of a source (a review's finding F7, a series'
  OQ3, a gate's G5), its record carries that label and its short name, `label {id, name}`, so
  its headline's question opens on them, then ` · `, as the card's title shows it:

  ```
  decision 41: F7 (oversize upload) · Cap the upload size? — options: (a) cap at 25 MB [recommended] | (b) no cap | (z) decide later
  ```

- **What the librarian binds in the record**, beyond the card-record reference:
  - **`q`** is a question, as the card's title shows it, and the question alone: a round
    ask's justification goes in `ifleft` and `roundcosts`, never in `q`. Every text field
    names items by plain name with the tag trailing, and glosses any other id (no bare item
    id, sha, series or finding number).
  - **The label.** Its short name is plain words, taken from the source or written where it
    has none, and kept for as long as the operator sees the label; `what` names the source by
    plain name (*… from the upload review*). The number stays the handle: the headline still
    opens `decision N:`, so the counter grep and `wi` read it unchanged, and a reply by the
    label is stored as `answer N:`. Any other label a card names (a decision covering several
    labelled items) is written label first with its short name where it stands, never a bare
    label and never a number. Tracker ids (items, tickets, commits) are not source labels:
    they keep the tag trailing, above.
  - **The options** are every option the source offered (a series, a dispatch's `decision:`
    line), one choice per letter: a compound choice gets its own letters, never `(a)+…`. They
    stay in letter order, (z) decide later last, `rec` the recommended letter. A preference or
    an outside-authority decision has `rec` null and its label as `norec` (*your preference —
    no recommendation*), which `wi` writes after the last option, so a reader of the headline
    alone can show it.
  - **⚠ one-way**, or any decision shown as a block: the card's `oneway` is true when it is
    ⚠, every option but (z) gives its `reach`, and the `evidence` drill-down is required: they
    fill the block's Impact table, with `cost` where the option has one.
  - **Each option holds its own impact**: its `effect`, then `reach`, `undo` and `cost` where
    they apply, a facet that does not apply left out; the card shows it on the italic line
    under the option (the `decisions` skill's rendering reference, § Impact). Effect and Reach
    are about the thing the work builds, never the process, which is Wait (rule 259); each
    option's `effect` gives it by its mechanism, how it happens, who meets it and when, and
    the before and after (rule 268).
  - **Undo is stored only where it bites** (answer 260 (a)): an option that is one-way or
    costly to undo carries `oneway: true` and its `undo`, how it is reversed and at what cost,
    or that it cannot be and why, and never one without the other, since the marker decides
    the read-back (below). An option with no `undo` is reversible at little cost, and is read
    that way; in a block its Undo cell shows `—`, and with no marked option the column is
    dropped. The marker marks the option, never the decision: only the card's `oneway` makes a
    decision ⚠, and a ⚠ one-way decision has at least one marked option.
  - **The Impact** (`impact`), across all its options, favouring none: `wait` (what waiting
    costs, what it blocks), `reach`, and `undo` only when some option is one-way or costly to
    undo, naming that option and its undo, not only the recommended option's; with every
    option reversible at little cost, it carries no undo. There is no card-level effect: each
    option carries its own. What the decision blocks is its `wait`, so `why` drops its
    *blocks* when the wait carries it.
  - **`class`** is the reason from `decide-alone.md` § Class names, picked when the decision
    is raised, and `whyask` its text (`decide-alone.md` § Raised).
  - **`context`** is written when the decision is raised: the terms the card uses, then the
    cue last — where the operator left it (what they last saw or decided on this subject) ·
    what they decide now — never what changed since, which *while it waited* carries at the
    re-show. A block's further facts are its levels (`detail`). The Context is shown every
    time a card or block is shown, to a warm reader as to a cold one (the `decisions` skill's
    rendering reference, § Context).
  - **An ask for another round** — the dev-cycle cap, most often — fills `ifleft` and
    `roundcosts` from the reviewer's `findings:` block and the run's record; any other
    decision leaves both out.
  - **An option that asks the operator to act** carries its `act`, the steps one line each,
    written when the decision is raised (what each step holds is the skill's rendering
    reference, § Card).
- **Machine lines** (`delegation:`, `terms:`, `act:`, `grant:`) go under the card's
  **current** `card:` line with `$WI raise <id> --revise N --why '<why>' --lines <lines file>`
  and no `--record`: the record and its `rev` stay unchanged, so its page answers keep
  counting. `wi` refuses it once N is answered, as it refuses any revision. They may also ride
  the first raise (`--record <file> --lines <lines file>`). A signed grant names the card's
  current revision, `card: <record path> rev <rev> sha256:<hex>` as `$WI show <id> --card N`
  prints it; how a card shows its grants (a `grant: <id>` line under its current `card:`
  block, added while N is open) is an input for the signed-grants build, which settles it. A
  card a live grant names is never upgraded or revised while the grant runs.
- **Revised:** `$WI raise <id> --revise N --why '<why>' --record <file>`, the new record
  checked as at the raise: when the options or the recommendation really change, when the
  skill's re-show check finds a stored field stale, or when a fact is added (an **Added:**
  line, a `dig into` finding). A new record carries a **new** `rev` for new content; the same
  `rev` only for a format-only upgrade (**A legacy card**, below). An answered card is never
  revised: `wi` refuses it. `wi` writes `revised: <time> — <why>` and the new `card:` line;
  the last `card:` line names the current record. A revised card keeps the first card's
  `raised:` (`wi` reads the first one per N), so its age and its order still count from the
  ask. A decision with no `raised:` line yet (a headline-only one getting its card) takes
  `--raised <UTC>`: the time the headline was committed — the commit time, not the ask time,
  the closest the record holds — to the second, `TZ=UTC git -C "$MAIN" log --reverse
  --date=format-local:%Y-%m-%dT%H:%M:%SZ --format=%cd -S'decision N:' -- <item file>`, first
  hit.
- **Reading a card:** `$WI show <id> --card N --json` reads the current record (`record`, with
  its `rev` and `sha256`). Every view reads it: a card or block renders it by the card-record
  reference; the list line reads its wait; where a view shows one effect — the Report's
  `decisions needed:` at tag size, the list line, the Groom row (`idle-turn.md`) — it is the
  recommended option's own `effect` (the option whose `k` is the record's `rec`), its letter
  first, and with no recommendation each option's in a few words, so the report line never
  has to open the card. Its exit 2 says *decision N has no card record*: a legacy card or a
  headline only (below). An exit 2 that says *unrecognized arguments* is an older `wi`
  (below), told apart by the message.
- **A legacy card**, a decision with no `card:` line: legacy cards are read by the decisions
  skill's legacy reference (`references/legacy-cards.md`), as written, its indented lines by
  that reference's § Stored card lines, its effect for a view from the recommended option's
  line. It is **upgraded on its next touch** — a card or block showing, a page publish, a
  revision; never an answer, a list line, a Groom row, a tag-size mention, an estate sweep
  or a ref — into a record by that reference's map, checked, and stored with `$WI raise <id>
  --revise N --why 'format upgrade to decision-card/5, rev kept' --record <file>` (with
  `--raised` where N has no `raised:` line): a format-only upgrade keeps the `rev` the
  reference gives; a fact drawn from outside the card gives a new one. **An answered card is
  never upgraded.** A headline whose only indented lines are `raised:` (and `revised:`) is a
  headline-only decision, never a stored card to backfill as one: at its next touch it gets
  its card from the durable record (the item, its series, its commits), with a new `rev`, a
  fact no record holds written *not recorded*, never invented.
- **The v5 reader rule:** a legacy block for N after a `card:` line for N, in file order (an
  older session's backfill), is compared with the record. A backfill, or nothing the record
  lacks: the record stays current, and `revised: <UTC> — legacy backfill after v5 ignored` is
  appended under that block. A real revision: it is upgraded into a new record with a **new**
  `rev`.
- **A missing or mismatched record file** (`$WI show --card` exits 3): show the headline, and
  say *card record missing (`<path>`); restore it from the store's history*; never backfill
  it.
- **An older `wi`** (no `--record`): the record stays in the session's scratchpad, the
  headline is raised headline-only (`$WI raise <id> -- '<question>'`; with no `raise` at all,
  `invalid choice: 'raise'`, N is one more than the last decision number the counter grep
  prints, and the headline is written with `$WI note <id> --raw`), the card is shown from the
  scratchpad copy, and `--revise N --record` follows once `wi` updates. Never legacy lines in
  its place.
- **Grouped and depends:** which group each decision is in, and which decision it waits
  on, are column-0 lines: a group's entity line `group g-<MMDD>-<hhh>: <plain name>` (a
  bundle's adds ` · shares: <what its members share> · context: <shared context>`, written
  once there), a member line `group N: g-<MMDD>-<hhh>` per decision, and `depends N:
  <target>[, …][ — <why>]`, whose targets on the same M are alternatives. Their grammar, the
  id and the line that makes it, the check that an id is not taken, the store-wide lookup
  and how a duplicate id is fixed are the `work-items` skill's format reference, § Groups and
  dependencies. Group ids are not numbers and take nothing from the counter. Only this
  session, the store's writer, writes them; a dispatched agent (planner, reviewer) never
  does, and returns a link in words for the librarian to write. They are appended with one
  `$WI note <id> --raw -- '<line>' ['<line>' …]` per item (one lock, so one commit in a
  store that commits its own changes), and ride the next store commit otherwise; never
  through `raise --lines`.
  - **At raise:** right after `$WI raise` prints N, in the same turn, the new decision joins
    a group, `group N: <id>`, or a new group is made: draw an id, check it is not taken,
    then write the entity line, then the member line. The name is the item's short name, or
    the parent's or the series' short name for a group spanning sibling items about one
    plugin. When its question or options presuppose another decision's answer — its text
    says *only if*, *given* or *after* another decision; a planner's question names
    another's answer ("only on OQ1 (b)", mapped to that question's decision number); a
    restate cites one — write `depends N:` too. A stop between the raise and these lines is
    caught by the back-fill below.
  - **At a reframe** (N reframed as M): `group M: <N's id>`; `depends M:` copies N's set,
    rechecked against M's options; each open K whose set names N gets a new `depends K:`
    line, its whole set again with N replaced by M (the last line is the whole set), the
    letter kept only when an option of M carries the same meaning, else no
    letter, and K is re-shown, since its premise changed.
  - **A rename** is one new entity line, the members unchanged. **A regroup** is one new
    member line. **A revision** that changes what a decision presupposes appends a new
    `depends N:` line; the card is never rewritten for a line.
  - **The id is never shown to the operator**, in chat or on a page: the group goes by its
    plain name. Store lines and briefs carry it.
  - **Back-fill is lazy.** When this session next shows an open decision that has no member
    line (at card, block or page level, when it writes `shown N:`), revises one, or raises a
    new decision in its item, it writes in the same store commit: member lines for **every**
    open decision of that item that lacks one, so the item never splits between an id and
    the default, making a group when none fits; `depends N:` lines where the record states a
    dependency in words; and, for a legacy `withdrawn K: reframed as M` there with no
    `closed K:` line, `closed K: superseded by M`. Building an answer page is a showing, so
    every card has its lines before the page's writers are split. Only in this session's
    own store; a `<repo>#N` decision gets none. A decision that none of these moments
    reaches keeps none: there is no back-fill pass.
- **Shown:** right before a message goes out that renders decisions at card or block
  level, append `shown N: <UTC time> chat` for each decision it renders that way, with
  `rev <rev>` from its last `card:` line when it has one, the time
  from `date -u +%Y-%m-%dT%H:%M:%SZ`: a Report's decisions block, an Intake ask, a
  decision raised between Reports, a re-show, a `tell me` or `dig into` re-render. A list
  line, a tag-size mention or a Groom row writes none. For an answer page, append one
  `shown N: <time> page rev <rev>` line per card the `decision-page` skill hands over (its
  number, publish time and `rev`), never one note for the page; after writing, count the
  lines against the hand-over's count (*N cards handed over*) and write any missing one
  before the Report. A republish that keeps a card's `rev` hands nothing over for it, so a
  kept card writes no line: the `rev` is what the operator read, and an unchanged card was
  already shown. For a tick-box doc, append `shown N: <time> doc` for each number and time
  the skill hands over, with `rev <rev>` when the hand-over names one. Only this session,
  the one the operator reads, writes it; a dispatched agent never does.
- **Seen:** at the operator's next turn in this session, append `seen N: <UTC time> turn`
  for every decision this session showed in chat since the operator's previous turn,
  answered or not. For each new page or doc answer the `decision-page` skill hands over,
  append `seen N: <time> page` (or `doc`) at the time it hands over; it hands over new
  answers only, so an unchanged one writes nothing. A chat turn never sees a page or doc
  card. **Held:** while the hold in the `work-items` skill's format reference, § Shown and
  seen, stands, write no `seen N:` line; `shown N:` lines are written as above.

  Both lines are column 0, appended, never inside a card, and ride the next store commit
  like every other record line: commit the store with `$WI commit -m "<message>"` (the
  `dev-cycle` skill's `references/bindings.md`, the store lookup). Their shape and how they
  are read (first and last by position; seen after the last showing by file order, never by
  the times) are the `work-items` skill's format reference, § Shown and seen.
- **Re-show:** render the current card record (**Reading a card**; a legacy card upgraded
  first, since a re-show is a touch), adding only what the skill allows, and append
  its `shown N:` line (above). *While it waited* is read from the record, never from
  memory. It opens at the last `shown N:` line that a `seen N:` line follows in file order —
  the showing the operator read — at that line's time; with no such line (never seen, or
  not recorded), at the card's `raised:` time. Find it with
  `grep -n '^shown N:\|^seen N:' <item>` and take the last `shown` hit with a `seen` hit
  below it. What changed is the item's lines written below that line (below the card, when
  it opens at `raised:`), and `git -C "$MAIN" log --since=<that time>` over the files the
  decision is about, and the answers to the decisions its `depends N:` set names; nothing
  there is *nothing changed*. Age and order still count from
  `raised:`.
- **Open question:** `open question: <text>` in the item body. It closes with a later line:
  `open question: <text> → decision N` when it gains options and is raised as `decision N:`,
  or `open question dropped: <text> — <why>` when retired. The open ones are the `^open
  question:` lines without `→` and with no later closing line for the same text, read from
  the record; each is listed under *Open questions* on every cold re-show.
- **Decided alone:** a `decided:` line, as `decide-alone.md` § The record gives it — never a
  `decision N:` or `answer N:` line.
- **Answered:** `answer N: <the reply> (read as: <the echo's reading>)`. The reading is
  recorded because a natural-language reply can be misread, and the echo is what the
  operator saw. **Every answer line keeps the operator's reply verbatim**, so the store
  is a source of truth to go back to: `<the reply>` is the operator's own words as
  written, never a summary.
  - **A letter reply** (an exact `N: letter`) keeps its letter, without the number it
    opens with. Any other reply keeps its words as written, its number included; a
    message with several replies gives each `answer N:` the part that answers N, the
    part its echo names, kept the same way.
  - **One physical line:** a reply over several lines has its line breaks written
    ` / `. Nothing in a reply is escaped — not a quote mark, not a ` / ` of its own.
  - **A reply that opens with a form word** (`drop`, `later`, `you decide`, `tell me`,
    `expand`, `dig into`) and is a plain answer — not that form — is written in double
    quotes, `answer 7: "drop the flag" (read as: (a) …)`, so an unquoted
    `answer N: drop` stays the drop form's key. Lines written before this rule are
    left as they are.
  - **The forms below** that open with their own wording (`you decide`, `drop`, a
    reframe) append ` — "<the reply>"` after that wording. A redirect is a plain
    answer. A hold is a follow-up, never an answer line (**`hold`**, below).
  - **On a ⚠ read-back** (below), the choice's words are the verbatim reply, and the
    confirmation appends ` — confirmed "<reply>"`.
  - **The read-as stays**, last on the line; a reader splits it off at the last
    ` (read as: `.
  - **A reply added after the fact** to an answer stored without it (one recorded
    before this rule, or as a summary) is one indented line under that `answer N:`
    line, the answer line itself kept as written:

    ```
    answer N: <as stored>
      verbatim N (added <UTC time>, from <source>): "<the reply>"
    ```

    Indented, it matches neither `^decision` nor `^answer`. Interim `verbatim N` lines
    written before this rule, in other shapes, are left as written; this shape applies
    from now on.
  - **A `later`, `hold` or `dig into` stored as an answer line** before the follow-up
    rule (below), on a decision with no later final answer, is rewritten as its `wake N:`
    line, the original kept whole on one indented line under it: `  verbatim N (moved <UTC
    time>, from its answer line): <the original line>`; one followed by a final answer is
    left as written.
- **A one-way choice on a ⚠ decision** (the chosen option carries `oneway: true` and its
  `undo` in the record; on a legacy card, what the legacy reference reads as the marker):
  repeat the choice back first. Record `answer N:` only when the operator confirms
  (`answer N: <the choice's words> — confirmed "<reply>" (read as: …)`).
  Nothing acts before that. A reversible choice on a ⚠ decision is echoed and recorded
  at once.
- **A follow-up is never an answer line.** An `answer N:` line holds a final answer only
  (an option, words, `you decide`, `drop`, a reframe); `later` (the `(z)` option too, by
  its letter or its words), `hold`, `dig into`, `tell me` and `expand` are recorded as the
  bullets below give, never as `answer N:`. `wi` reads any `answer N:` line as answered, so
  a follow-up stored as one drops the decision from `wi needs-input` while it is still
  open. A follow-up from an answer page or a tick-box doc is recorded by the same rule: the
  read-back hands it over as `kind: follow-up` (as it does `you decide` and `drop`, which
  are final answers and keep their answer lines), and it is recorded as the bullets below
  give: a `wake N:` line for `later` and `dig into`, nothing for `tell me` and `expand`;
  never an answer line.
- **`later [when]`:** `wake N: <time | event | next Report>`. There is no `answer N:`, so the
  decision stays open and `wi needs-input` keeps listing it. Deferred again, it gets another
  `wake N:`; the last one wins (`grep -n '^wake N:'`, last hit). At the wake, re-show it
  with what changed.
- **`hold`:** `wake N: <what it waits on>`, and no `answer N:`. Its form beyond that waits
  on OQ6 of the decision-lifecycle investigation (5140), which settles it.
- **`tell me`:** an `Added:` fact that changes an option's impact or the rec is a revision
  (above); otherwise nothing new in the store. **`expand`:** nothing new; the same number is
  shown a level higher next round. Neither writes an `answer N:` line.
- **`dig into [what]`:** a bounded investigation, dispatched like any other (a `dispatch:`
  line, routing and the quota sense apply), and `wake N: when the dig into returns
  (<what>)`, no `answer N:`; its result comes back on the same number.
- **`you decide`:** `answer N: you decide — chose (x), because … — "<the reply>"`. On ⚠,
  only a reversible option; when the only good answer is the one-way option, it is
  re-asked, as the skill says.
- **`drop`:** `answer N: drop — withdrawn — "<the reply>"`.
- **A reframe:** two lines, written together: `answer N: reframed as decision M — "<the
  reply>"` and `closed N: superseded by M`, and M is raised to the floor like any new
  decision. M copies N's group and its `depends` set, and every open decision that depends
  on N is repointed to M (**Grouped and depends**, at a reframe). A `withdrawn N:` line is
  never written; one already stored (`withdrawn N:
  reframed as M`) is read as those two lines.
- **A batch (`ok N-M`):** one `answer` line per accepted number, each keeping the batch
  reply verbatim (`answer 51: ok 51-53 (read as: …)`). The skipped ones stay open and are
  re-asked, as the skill says.
- **Closed:** once an answered decision's outcome has taken effect, one physical line in
  the same item's body, in one of three forms:

  ```
  closed N: acted <short sha | item id>
  closed N: rule <repo path>
  closed N: superseded by <M | <repo>#M>
  ```

  `acted` names the commit on main, or the item, that carried the answer out — written when
  that change lands, in the store commit that records the landing: commit the store with
  `$WI commit -m "<message>"` (the `dev-cycle` skill's `references/bindings.md`, the store
  lookup). The line is appended when the change lands either way. An answer carried out by
  several changes is closed when the last of them lands, and stays answered but not closed
  until then; an answer that changes nothing closes at once as `closed N: acted <the id of
  the item the answer was recorded on>`. `rule` names the file the answer became a standing
  rule in, written once the rule change lands. `superseded by` names the later decision that
  replaced it: a reframe is closed this way when M is raised, and an answer a later decision
  overturns when that one is answered. A `drop` needs none (its answer line is its close,
  and it counts as closed), and a `you decide` closes as any answer does. Any other answered
  decision with no `closed N:` line is answered but not closed. A later `closed N:` for the
  same N (an acted answer later made a rule, say) adds to the record; the last one is its
  state (`grep -n '^closed N:'`, last hit). Its shape, and the reader's split, are the
  `work-items` skill's format reference, § Closed.
- **Another repo's decision:** `<repo>#N` — `<repo>` the name of that repo's `origin`
  remote (its last path part, without `.git`), else its main checkout's directory name —
  in any line of this store that names one (a card's `basis:`, a `wake N:` event, a
  `superseded by`). A bare N, or `decision N`, always means this store's counter.
- **Writer runs:** every answer page built through the `decision-page` skill's writer split
  records each writer's run, to tune the split's card cap, a run of one writer included:
  one column-0 line per writer, appended to the body of the open item whose acceptance asks
  for `writer-run:` lines, from the first page written after the split lands and while that
  item stays open; a store with no such item records none:

  ```
  writer-run: <UTC time> <page short name> w<k>/<K> — cards <n> · tokens <input>/<output> · lints <n> [<keys>]
  ```

  `w<k>/<K>` is writer k of K. **Tokens** are that writer's input and output, from the
  dispatch result's usage; without it, the line says `tokens not recorded` in their place. **Lints** count the `lint:` lines `check_cards.js` prints for
  that writer's cards on the first merged check, before any fix, with their keys. The
  line is neither `decision N:` nor `answer N:`, and `wi` does not read it.

## The Report

The four lines per landed change stay exactly as SKILL.md § Report gives them. With the
skill, the decisions come **last in the turn**, where the operator's eye is when you stop:

1. Each change's `decisions needed:` names that change's decision numbers, each with the
   recommended option's effect at tag size, its letter first, from its card record
   (§ What the store records, **Reading a card**; a legacy card's option line) —
   `46 (→ (a) preview up in about 4 minutes)` — or `none`. An
   item blocked or declined since the last Report — `report.md` § Batching's "goes under
   `decisions needed` of the next" (a forward excepted, as there) — is raised as its own
   decision and carried in the block, not on another change's line.
2. Then the **Done alone** group (`decide-alone.md` § The Report), each line in the skill's
   FYI form, with no group when nothing was decided alone since the last Report; then the
   push outcome, any `incoming:` lines, and the team summary, as `report.md` gives
   them.
3. Then **one decisions block**, the last thing written in the turn — when the push outcome
   and team summary go out as a follow-up message (`report.md` § The push), the block moves to
   the end of that follow-up — laid out as the skill says: the decisions shown in full
   first, in list order, then the compact list of every open decision (a deferred one also
   shows its wake), then the hint when it carries two or more.
4. Shown in full, at the level the skill gives them:
   - those raised since the last Report;
   - those whose wake has come;
   - those shown in a Report the operator has not had a turn since (not yet seen; after a
     reset, readable from the store as a last `shown N:` line with no `seen N:` line below
     it);
   - after Rehydrate, every open one (the cold re-show, paged as the skill says — paging is
     provisional);
   - a ⚠ one-way decision on its first showing and whenever the operator is cold on it;
   - any the operator raised with `expand`, which stays raised.

   Every other open decision is a list line only, ending *(shown before)* or *(line only)*,
   as the skill says. A deferred one stays a list line with its wake until the wake comes —
   on a cold re-show, a card showing its wake, as the skill says.

A decision raised between Reports (an Intake ask, a blocked item) is put to the operator in
the message that raises it, per the skill — last in that message. It is carried in every
later Report per items 3 and 4 until it is answered.
