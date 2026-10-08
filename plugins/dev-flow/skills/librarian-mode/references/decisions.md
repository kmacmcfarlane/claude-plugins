# Putting decisions to the operator

Loaded from SKILL.md § Intake step 3, § The cycle (Decision channel) and § Report. This
file binds the librarian to the `operator-interaction` plugin's `decisions` skill, a soft
dependency (README principle 4). It says only what the librarian supplies to that skill and
what the store records. How a decision is written, ordered and answered is the skill's, and
is not restated here.

## When it applies

The skill is available when the session's skill listing carries `operator-interaction:decisions`
(the `operator-interaction` plugin is installed). Then:

- **Load it at Rehydrate** (SKILL.md § Rehydrate step 2) with the Skill tool, and again after
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
`decisions needed:`, its store lines and the replies are as SKILL.md § Report gives them.

## What the librarian supplies to the skill

| The skill asks for | The librarian's binding |
|---|---|
| the caller's numbering | the store counter, the one counter for every question put to the operator (SKILL.md § Report): `decision N:` continues from the highest N (SKILL.md § Rehydrate step 3); a number is never reused. A source's own label (a series' OQ3, a gate's G5) rides in the card's `what:` line, never as a number |
| the default wake ("the next time I finish a piece of work and report") | **the next Report**; a `later` with no time or event wakes there |
| the operator's expected return | what the operator said ("back tomorrow morning"), in the item or the transcript; when they said nothing, the return is unknown and every stated deadline goes first |
| who is reading, and how warm | after Rehydrate the operator is **cold** on every decision raised before the reset; the first Report after it re-shows them per the skill, with what changed since each was raised. Between resets: a decision shown in a Report written after the operator's last turn has **not been seen** — background returns can write several Reports while the operator is away — so the next Report shows it at its level again, not *(shown before)*. Your own transcript tells you: has the operator taken a turn since that Report? The store records the same thing (§ What the store records, **Shown** and **Seen**): a reader without the transcript — after a reset, or another session — reads the last showing as unseen when no `seen N:` line follows the last `shown N:` line, and as not recorded (cold) when there is no `shown N:` line |
| related decisions (groups) | decisions on one item, or on sibling items (one parent) about the same plugin; a decision with no item groups by plugin or files. Never transitive: two groups that share a file stay two groups |
| named templates | none: the librarian names no template, so every decision carries the floor on its own card |
| classes of decision (the class in *why ask* and on the list line) | the class names in `decide-alone.md` § Class names, picked when the decision is raised; `unclassed` when none fits |
| a decide-alone class the caller's rules define (the FYI rule's authority) | the classes `decide-alone.md` § The line marks decided alone, cited as `class <class>` on the `decided:` line; beside them, the FYI authority is an answered decision or the task the item carries |
| the record of what was decided alone | the `decided:` line and the Report's **Done alone** group (`decide-alone.md`) |

## What the store records

The store stays the source of truth, and it keeps the **card**, so a re-show after a reset
renders what the operator read instead of composing it again.

- **Raised:** a headline line, then the card as indented lines under it:

  ```
  decision N: <question, one line> — options: (a) … [recommended] | (b) … | (z) decide later
    raised: <UTC time, e.g. 2026-09-24T14:05Z>
    what: <what is decided>
    why now: <why it is up now>
    why ask: <class> — <what would go wrong if the librarian took its recommendation alone>
    context: <where the operator left it · what they decide now> — then: <a block's lost-context facts, or none>
    impact: → <effect> · later: <wait> · reach: <reach> · undo: <undo>
    if left: <a round ask only: each leftover finding — what it would break>
    round costs: <a round ask only: time, quota, the operator's attention>
    (a) <option> — <its effect> [— reach: <who or what>] [— undo: <how, or cannot>] [— cost: <time, money, quota, attention>]
    (b) <option> — <its effect>
    (z) decide later — <what waiting costs; the deadline, if any>
    rec: (a) · basis <word> — <reason>
    basis: <per load-bearing claim: provenance — claim (link or pointer)> · …
    unknown: <what isn't known, or none>
  ```

  The headline is as the `dev-cycle` skill's `references/record-lines.md` gives the
  `decision:` line, so `wi needs-input` and the counter grep (`^decision [0-9]`) read it
  unchanged; the indented lines, `impact:` included, match neither `^decision` nor
  `^answer`. The question is a
  question, as the card's title shows it, and the question alone: a round ask's
  justification goes in `if left:` and `round costs:`, never in the headline. `raised:`
  carries the time, not a date alone (an existing date-only `raised:` is kept as
  written); every line names items by plain name with the tag trailing, and glosses any
  other id (no bare item id, sha, series or finding number).
  When the source numbered the question its own way (a series' OQ3, a gate's G5), the
  label rides at the end of `what:`, with the source by plain name — *… (was OQ3 of the
  decision-lifecycle investigation, 5140)* — and is never a bare number.
  The options are every option the source offered (a series, a dispatch's `decision:`
  line), one choice per letter: a compound choice gets its own letters, never `(a)+…`.
  When the decision is ⚠ one-way — or any decision shown as a block — write `⚠ one-way`
  after the question (⚠ only), and every option line carries its `reach:` and `undo:` (a
  card stored before this rule may carry `who:` in place of `reach:`, read as it), and
  the `basis:` drill-down line is required: they fill the block's Impact table, with
  `cost:` where the option has one. `why ask:` follows `why now:` on every card,
  one physical line, its class from `decide-alone.md` § Class names. `context:` follows
  `why ask:` on every card, one physical line, written when the decision is raised. Before
  its first ` — then: ` is the cue: where the operator left it (what they last saw or
  decided on this subject) · what they decide now — never what changed since, which *while
  it waited* carries at the re-show; the cue never contains ` — then: ` (reword it). After
  the separator are the facts a block's *Context you may have lost* adds, or `none` on a
  decision raised as a card. The separator is always written. A card shows the cue alone as
  its **Context:** for a cold reader; a block shows the cue, then the facts. An ask for
  another round — the dev-cycle cap, most often — requires the `if left:` and `round
  costs:` lines, in that order after `why now:`, `why ask:`, `context:` and `impact:` (the
  skill's floor), filled from the reviewer's `findings:` block and the run's record; any other
  decision leaves both out. The options stay in letter order, `[recommended]` on the
  headline marking the recommended one.
  `impact:` follows `context:` on every card, one physical line, written when the decision
  is raised: the skill's Impact line, its five facets in their order —
  Effect (the recommended option's; with no recommendation, each option's in a few words,
  `(a) …; (b) …`), Wait (what waiting costs, what it blocks), Reach, Undo — in the form
  above; Cost stays on the option lines. Its Undo names the one-way option's undo
  whenever any option is one-way, not only the recommended option's. What the decision
  blocks is its `later:`, so `why now:` drops `blocks:` when the `impact:` line's `later:`
  carries it. It replaces the `stakes:` line, which a card stored
  before it keeps as written. Every view reads it: the Report's `decisions needed:` and the
  Groom row (`idle-turn.md`) take its effect at tag size, the list line its effect and wait,
  the card the whole line, so the tightest view never opens the options. A card stored
  without it is backfilled under the rule below, from its recommended option's line and its
  `(z)` line (and an older `stakes:` line, for reach and undo), and written as a revised
  card `revised: <time> — backfilled impact` before it renders anywhere, the Groom row
  included; a facet no record holds is `not recorded`.
  **A card or block renders only from stored fields**: a field it needs that the store
  lacks — a headline-only entry, a block's missing `undo:`, a card stored before `why ask:`
  existed (in the one form `decide-alone.md` § Raised gives it), one stored before the cue
  existed (no `context:` line, or one with no ` — then: `, whose text is a block's facts
  and is kept as the part after it), a block whose facts read `none` (a decision raised as
  a card, rendered as a block by `expand` or as a wide one shown to a cold reader: `none`
  counts as missing), a card with no `impact:` line — is backfilled from the durable record
  (the item, its series, its commits) and written as a revised card with `revised: <time> — backfilled` before it
  renders; a field no record holds is written and shown as `not recorded`, never
  invented at render time. A card with no `raised:` takes it from the record: the time the
  headline was committed — the commit time, not the ask time, the closest the record holds
  — in the form `wi` parses (`TZ=UTC git -C "$MAIN" log
  --reverse --date=format-local:%Y-%m-%dT%H:%MZ --format=%cd -S'decision N:' -- <item
  file>`, first hit).
  A preference or an outside-authority decision writes its label on the `rec:` line, and
  on the headline after the last option in place of `[recommended]` — *your preference —
  no recommendation* — so a reader of the headline alone can show it.
- **Revised:** when the options or the recommendation really change, or the skill's re-show
  check finds a stored field stale, write `decision N:` again with the new card and a
  `revised: <time> — <why>` line under it; the last one wins. A revised or backfilled card
  keeps the first card's `raised:` (`wi` reads the first one per N), so its age and its
  order still count from the ask.
- **Shown:** right before a message goes out that renders decisions at card or block
  level, append `shown N: <UTC time> chat` for each decision it renders that way, the time
  from `date -u +%Y-%m-%dT%H:%M:%SZ`: a Report's decisions block, an Intake ask, a
  decision raised between Reports, a re-show, a `tell me` or `dig into` re-render. A list
  line, a tag-size mention or a Groom row writes none. For an answer page or a tick-box
  doc, append `shown N: <time> page` (or `doc`) for each number and publish time the
  `decision-page` skill hands over. Only this session, the one the operator reads, writes
  it; a dispatched agent never does.
- **Seen:** at the operator's next turn in this session, append `seen N: <UTC time> turn`
  for every decision this session showed in chat since the operator's previous turn,
  answered or not. For each new page or doc answer the `decision-page` skill hands over,
  append `seen N: <time> page` (or `doc`) at the time it hands over; it hands over new
  answers only, so an unchanged one writes nothing. A chat turn never sees a page or doc
  card. **Held:** while the hold in the `work-items` skill's format reference, § Shown and
  seen, stands, write no `seen N:` line; `shown N:` lines are written as above.

  Both lines are column 0, appended, never inside a card, and ride the next store commit
  like every other record line. Their shape and how they are read (first and last by
  position; seen after the last showing by file order, never by the times) are the
  `work-items` skill's format reference, § Shown and seen.
- **Re-show:** render the last stored card, adding only what the skill allows, and append
  its `shown N:` line (above). *While it waited* is read from the record, never from
  memory. It opens at the last `shown N:` line that a `seen N:` line follows in file order —
  the showing the operator read — at that line's time; with no such line (never seen, or
  not recorded), at the card's `raised:` time. Find it with
  `grep -n '^shown N:\|^seen N:' <item>` and take the last `shown` hit with a `seen` hit
  below it. What changed is the item's lines written below that line (below the card, when
  it opens at `raised:`), and `git -C "$MAIN" log --since=<that time>` over the files the
  decision is about; nothing there is *nothing changed*. Age and order still count from
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
    answer. A hold reply waits on OQ6 of the decision-lifecycle investigation (5140),
    which settles its form.
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
- **A one-way choice on a ⚠ decision** (the chosen option's `undo:` says it cannot be
  undone): repeat the choice back first. Record `answer N:` only when the operator confirms
  (`answer N: <the choice's words> — confirmed "<reply>" (read as: …)`).
  Nothing acts before that. A reversible choice on a ⚠ decision is echoed and recorded
  at once.
- **`later [when]`:** `wake N: <time | event | next Report>`. There is no `answer N:`, so the
  decision stays open and `wi needs-input` keeps listing it. Deferred again, it gets another
  `wake N:`; the last one wins (`grep -n '^wake N:'`, last hit). At the wake, re-show it
  with what changed.
- **`tell me`:** an `Added:` fact that changes an option's impact or the rec is a revision
  (above); otherwise nothing new in the store. **`expand`:** nothing new; the same number is
  shown a level higher next round.
- **`dig into [what]`:** a bounded investigation, dispatched like any other (a `dispatch:`
  line, routing and the quota sense apply); its result comes back on the same number.
- **`you decide`:** `answer N: you decide — chose (x), because … — "<the reply>"`. On ⚠,
  only a reversible option; when the only good answer is the one-way option, it is
  re-asked, as the skill says.
- **`drop`:** `answer N: drop — withdrawn — "<the reply>"`.
- **A reframe:** `answer N: reframed as decision M — "<the reply>"`, and M is raised to the
  floor like any new decision.
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
  that change lands, in the store commit that records the landing. An answer carried out
  by several changes is closed when the last of them lands, and stays answered but not
  closed until then; an answer that changes nothing closes at once as `closed N: acted
  <the id of the item the answer was recorded on>`. `rule` names the file the answer
  became a standing rule in, written once the rule change lands. `superseded by` names the
  later decision that replaced it: a reframe is closed this way when M is raised, and an
  answer a later decision overturns when that one is answered. A `drop` needs none (its
  answer line is its close, and it counts as closed), and a `you decide` closes as any
  answer does. Any other answered decision with no `closed N:` line is answered but not
  closed. A later `closed N:` for the same N (an acted answer later made a rule, say) adds
  to the record; the last one is its state (`grep -n '^closed N:'`, last hit). Its shape,
  and the reader's split, are the `work-items` skill's format reference, § Closed.
- **Another repo's decision:** `<repo>#N` — `<repo>` the name of that repo's `origin`
  remote (its last path part, without `.git`), else its main checkout's directory name —
  in any line of this store that names one (a card's `basis:`, a `wake N:` event, a
  `superseded by`). A bare N, or `decision N`, always means this store's counter.

## The Report

The four lines per landed change stay exactly as SKILL.md § Report gives them. With the
skill, the decisions come **last in the turn**, where the operator's eye is when you stop:

1. Each change's `decisions needed:` names that change's decision numbers, each with its
   effect at tag size from its stored `impact:` line — `46 (→ preview up in about 4
   minutes)` — or `none`. An
   item blocked or declined since the last Report — SKILL.md § Report's "goes under
   `decisions needed` of the next" — is raised as its own decision and carried in the
   block, not on another change's line.
2. Then the **Done alone** group (`decide-alone.md` § The Report), each line in the skill's
   FYI form, with no group when nothing was decided alone since the last Report; then the
   push outcome, any `incoming:` lines, and the team summary, as SKILL.md § Report gives
   them.
3. Then **one decisions block**, the last thing written in the turn — when the push outcome
   and team summary go out as a follow-up message (SKILL.md § Report), the block moves to
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
