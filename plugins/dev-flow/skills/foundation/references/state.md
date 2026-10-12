# State across sessions

Loaded from `foundation` at Frame (to resume) and whenever a serial, the index, the item or
the living docs are written. The skill keeps no state of its own: no hooks, no settings, no
directory outside the series, the work item and the repo's own docs.

| Layer | Holds | Read by |
|---|---|---|
| **The series** | one serial per phase pass, append-only; `INDEX.md` regenerated with a Foundation block, which records each gate's passing | a resumed session, which reads the whole series as the format requires; `dev-cycle` and `implement` for the plan serial |
| **One work item** (when a store exists) | the foundation as one item: its handoff (`doing`, `next`), the gate approvals and holds as `decision N:` / `answer N:` lines (a second source for gate status: it stays behind when the series moves to another repo); factored-out aspects and the plan's features as items with `--parent` it and real deps | `wi prime`, `wi needs-input`, the `work-review` skill |
| **The repo's living docs** | the current view, regenerated from the series by feature `F0` | every later session; humans |

The serials keep how understanding changed; the regenerated docs show the current rationale
as if it had been reached in order. The docs are written only by `F0`, built after gate G3
and re-filed after each later reopen (§ Living docs), so during a run, and while a reopen
is in flight, they lag the series: when the two disagree, the series wins.

## The series

The format is the series format, owned by the `investigate` skill's
`references/investigation-format.md` (its § Foundation series names these serials and the
block). Read it before writing anything. The series lives at
`.claude-sandbox/investigations/<slug>/`, or at the Series home an orchestrator gives.

| Serial | Phase | Written at |
|---|---|---|
| `00_initial.md` | frame and requirements | phase 1 (lite: all three phases) |
| `NN_architecture.md` | architecture | phase 2 |
| `NN_plan.md` | the phased plan, with `Implementation Approach` | phase 3 |
| `NN_reopen-<what>.md` | a reopen | any time after the phase it reopens |
| `NN_<what>.md` | a gate's fix round: the revision the review asked for | inside a gate |

Each serial takes the next free number: with no fix rounds the architecture serial is
`01_architecture.md` and the plan `02_plan.md`, and a fix round at gate G1 makes the
architecture serial `02_architecture.md`. The name, not the number, says which phase a
serial is.

**Implementation Approach** appears only in the plan serial. `implement` and dev-cycle's
build refuse a series with none, so they refuse a foundation series before gate G3: that is
the guard. No phase-1 or phase-2 serial carries a placeholder section.

## The Foundation block

`INDEX.md`, regenerated wholesale on every pass, carries this block after its TOC:

```markdown
## Foundation

Size: full | lite · Mode: new | retrofit · Item: <wi id | none>[ (was <old-repo>:<id>)]

| Phase | Serial | Gate | Operator | Approved |
|---|---|---|---|---|
| requirements | 00_initial.md | G1 CLEAR round 2 | needed | 2026-10-09 |
| architecture | 01_architecture.md | G2 in review | reported (no one-way ADR, no claim change) | — |
| plan | — | not started | needed | — |

### Gates passed
- G1 passed 2026-10-09 (claude-plugins#195)

### Held
| # | Question | Needed by | Owner |
|---|---|---|---|

### Factored out
| Aspect | Went to | Seam kept |
|---|---|---|
```

- **Gate**: `not started`, `in review`, `CLEAR round <n>`, `re-run after <reopen serial>`,
  or `retrofit` (a retrofit's gap decisions are still open, `references/retrofit.md`).
- **Operator**: `needed` or `reported`, per `references/gates.md` § 3; for gate G2, the
  reason when it is `needed` (the one-way ADR's id, the claim change).
- **Approved**: the date the operator approved, or `—`.
- **Gates passed** is the series' own record of each gate's passing, one line per pass,
  appended and never removed: `G<n> passed <YYYY-MM-DD> (<repo>#<N> | reported | in
  session)`. The ref is the decision that approved it as `<repo>#<N>` (the repo whose
  decision channel numbered it, so the ref still resolves after the series moves),
  `reported` for a gate G2 passed on its `CLEAR` alone, or `in session` for an approval
  with no numbered decision (no store, or an unnumbered channel). A gate that re-runs after
  a reopen gains a new line ending `after <reopen serial>`. Every regeneration of
  `INDEX.md` carries the list forward whole.
- **Who writes the line.** A standalone run writes it as soon as it records the approval
  (or, for a reported G2, the `CLEAR`), regenerating `INDEX.md` then rather than with the
  next serial. Under an orchestrator the orchestrator writes each gate's line itself, right
  after the approval (or a reported gate's `CLEAR`) and before any next dispatch, or with
  none to follow, as for a reopen's last re-run gate — its only writes in the series; the
  planner fills the gate's row. A gate a reopen re-ran gets its line ending
  ` after <reopen serial>`. For G3 that is step 1 of § The work item, After gate G3 is
  approved.
- **What marks a gate passed.** A resumed session reads the series first: a gate is passed
  when the block's Gates passed list holds its line — and, when its row's Gate cell reads
  `re-run after <reopen serial>`, a line ending `after <that serial>`. A row whose Gate
  cell reads `re-run after <reopen serial>` is passed only by a line ending
  `after <that serial>`, or by that re-run's own `answer N:` line: no earlier line of it,
  no later gate's line, no Approved date, no earlier answer and no done foundation item
  passes it. The foundation
  item, when the session can see it, is a second source: a done foundation item, or a gate
  approval's `answer N:` line, marks that gate passed too, and the session adds the missing
  line when it next regenerates `INDEX.md`. For a gate with neither, the table decides (it
  covers a series written before this list existed, and a pass whose line is not yet
  written): a gate is passed when it is `CLEAR` and its Operator cell is `reported`, or its
  Approved cell is a date. And a gate's line means every earlier gate passed, except a gate
  a reopen is re-running (above). A resume never re-runs a passed gate or re-files a
  feature already filed in this repo's store (a moved series past G3 files here, § The
  work item); a deliberate reopen is a move (`references/moves.md`).
- **Item**: the foundation item's id, or `none`. A reader takes the id from `Item:`'s first
  word; `(was …)` is a note, written when a moved series files under a new item here
  (§ The work item, A moved series past G3).
- **Moved from**: the note a moved series' `INDEX.md` carries under its provenance line
  (the `investigate` skill's `references/investigation-format.md`) is carried forward on
  every regeneration.
- Under an orchestrator the planner writes all of the block but the Gates passed lines.
  From the second phase on, the brief carries the previous gate's verdict, its `CLEAR`
  round, and whether it was approved (with the answer, its date and its decision ref) or
  reported; the planner fills that gate's Gate, Operator and Approved cells from it, and
  carries the Gates passed list forward whole.

**A lite run** has one row:

```markdown
| Phase | Serial | Gate | Operator | Approved |
|---|---|---|---|---|
| all (lite) | 00_initial.md | G3 CLEAR round 1 | needed | — |
```

Its single gate is recorded in that row, and its pass as one `G3 passed` line; Held and
Factored out are as in a full run.

A series is a foundation series when its `INDEX.md` carries this block; `dev-cycle` reads
it to know which gate a `CLEAR` was for.

## The work item

When the repo has a work-item store (the `work-items` skill), one item carries the run:

- **File** it at Frame with `--ref <series path>`, so a moved series still finds it.
- **Claim** it at Frame when standalone; an orchestrator claims it under its own rules.
- **Handoff** after every gate: `$WI handoff <id>` naming the series, the gate passed and
  the next phase (`--next "phase 2: architecture"`). The item stays open until gate G3.
- **Decisions**: each gate approval the operator owes, and each hold, is a `decision N:`
  line (`$WI note <id> --raw -- "decision N: …"`), answered by an `answer N:` line. N is the
  next number on the channel's counter (a librarian's counter under `librarian-mode`).
- **After gate G3 is approved** — this list is the one home for that filing, which a
  standalone run does at its Step 4 and `dev-cycle` does at its foundation bullet:
  1. Add the `G3 passed` line (ending ` after <reopen serial>` when a reopen re-ran G3) to
     the series' Foundation block (§ The Foundation block) before anything is filed (a
     file write; the series is committed only as its home's tracking mode says, the
     `investigate` skill's `references/investigation-format.md` § A repo not yet
     created). This step runs with no store too.
  2. File each feature of the plan serial's Features table as an item, in the table's
     order: `$WI add … --parent <id>`, with a `--dep` naming the filed item of each
     feature it depends on.
  3. Put each filed feature that a hold blocks to `$WI groom <feature-id> "<the hold>"`,
     so it waits for the answer.
  4. File each factored-out aspect that has no item yet: `$WI add … --parent <id>`, or
     `--ref <series path>` for an aspect that belongs to another repo.
  5. `$WI done <id> --note <series path>`.
- **A filing cut short.** A `G3 passed` line with the foundation item (the block's
  `Item:`, or in a moved series the item that refs the series path) not done means the
  list stopped after step 1: a resume continues it at step 2, filing only the features and
  aspects with no item whose `parent:` is the foundation item yet, then step 5. That
  finishes G3; it is not a re-run or a re-file.
- **A moved series past G3.** A resume that finds the `G3 passed` line in a series moved
  here (its `INDEX.md` has a `Moved from` note), when the block's `Item:` id (the field's
  first word) names no item in this repo's store (`$WI show <id>` exits 2) and no item
  here refs the series path (`$WI ls --status all --json`, which reads done and archived
  items too: an item whose `refs` holds the path as written), re-runs no gate and files
  nothing in the old repo. With a store:
  `$WI add` a new foundation item with `--ref <series path>`, its first note
  `G3 passed <date> (<ref>) carried from <old-repo>` quoting the Gates passed line, so the
  original approval stands and no second one is asked; the note also names the old repo's
  items the series records (the block's `Item:`, any filed feature) as `<old-repo>:<id>`.
  Regenerate `INDEX.md` then, its `Item:` the new id, followed by `(was <old-repo>:<id>)`
  only when the old `Item:` was an id, and run steps 2–5 above under the new item; a
  cut-short filing resumes as above. With no store, or with `no wi found`, the Report
  lists the features to file, naming those old items the same way.
- **Factored-out aspects** are filed when factored out where the run can (standalone);
  step 4 above files any that are still unfiled, which is every one under an orchestrator.
- **After a later reopen** passes its gates, the orchestrator (`dev-cycle`), or the
  standalone session, files `F0`'s re-run as a new item under the foundation item, beside
  the revised features the impact list names. A reopen a feature's build raised is itself
  filed as an item under the foundation item when the operator takes it
  (`references/moves.md`). A G3 re-run takes step 1 alone; its filing is this bullet's
  (`F0`'s re-run and the revised features the impact list names).

With no store, the Foundation block's Gates passed, Held and Factored out sections are the
record, and the Report lists the features to file by hand.

## Living docs

Feature `F0` regenerates the current view from the series: `docs/requirements.md` (the
phase-1 artifacts), `docs/architecture.md` (the phase-2 artifacts), `docs/adr/NNNN-<title>.md`
(one per ADR, append-only: a superseded ADR keeps its file and gains its Status line), and
the repo's `CLAIM.md`, through the `ownership:claim-md` skill's write mode when the
session lists it, landing the draft that gate G1 (or a reopen's G1 re-run) approved, with
no second decision: its Status line and Amendments line name that approval's date and its
`decision N:` line on the foundation item (with no store, the date alone); else as the file
the series approved. After every reopen that passes its gates, `F0`'s re-run is filed as a
new item under the foundation item (§ The work item) and built like any feature.

Where the docs live is asked once per repo, at the first run's Frame, and recorded in
Confirmed Assumptions; the recommendation is tracked `docs/` and `docs/adr/`. In a public
repo the docs carry no estate detail (no host names, private paths or other repos' internals);
the series keeps those.
