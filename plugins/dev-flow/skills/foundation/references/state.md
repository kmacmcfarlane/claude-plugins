# State across sessions

Loaded from `foundation` at Frame (to resume) and whenever a serial, the index, the item or
the living docs are written. The skill keeps no state of its own: no hooks, no settings, no
directory outside the series, the work item and the repo's own docs.

| Layer | Holds | Read by |
|---|---|---|
| **The series** | one serial per phase pass, append-only; `INDEX.md` regenerated with a Foundation block | a resumed session, which reads the whole series as the format requires; `dev-cycle` and `implement` for the plan serial |
| **One work item** (when a store exists) | the foundation as one item: its handoff (`doing`, `next`), the gate approvals and holds as `decision N:` / `answer N:` lines; factored-out aspects and the plan's features as items with `--parent` it and real deps | `wi prime`, `wi needs-input`, the `work-review` skill |
| **The repo's living docs** | the current view, regenerated from the series by feature `F0` | every later session; humans |

The serials keep how understanding changed; the regenerated docs show the current rationale
as if it had been reached in order. When the two disagree, the series wins until the next
approved gate.

## The series

The format is the series format, owned by the `investigate` skill's
`references/investigation-format.md` (its § Foundation series names these serials and the
block). Read it before writing anything. The series lives at
`.claude-sandbox/investigations/<slug>/`, or at the Series home an orchestrator gives.

| Serial | Phase | Written at |
|---|---|---|
| `00_initial.md` | frame and requirements | phase 1 (lite: all three phases) |
| `01_architecture.md` | architecture | phase 2 |
| `02_plan.md` | the phased plan, with `Implementation Approach` | phase 3 |
| `NN_reopen-<what>.md` | a reopen | any time after the phase it reopens |
| `NN_<what>.md` | a gate's fix round: the revision the review asked for | inside a gate |

The serial numbers above hold for a run with no fix rounds; each serial takes the next free
number, so a fix round at gate G1 makes the architecture serial `02_architecture.md`. The
name, not the number, says which phase a serial is.

**Implementation Approach** appears only in the plan serial. `implement` and dev-cycle's
build refuse a series with none, so they refuse a foundation series before gate G3: that is
the guard. No phase-1 or phase-2 serial carries a placeholder section.

## The Foundation block

`INDEX.md`, regenerated wholesale on every pass, carries this block after its TOC:

```markdown
## Foundation

Size: full | lite · Mode: new | retrofit · Item: <wi id | none>

| Phase | Serial | Gate | Operator | Approved |
|---|---|---|---|---|
| requirements | 00_initial.md | G1 CLEAR round 2 | needed | 2026-10-09 |
| architecture | 01_architecture.md | G2 in review | reported (no one-way ADR, no claim change) | — |
| plan | — | not started | needed | — |

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
- **Approved**: the date the operator approved, or `—`. A gate counts as passed when it is
  `CLEAR` and its Operator cell is `reported`, or its Approved cell is a date.
- Under an orchestrator the planner writes the block, filling an Approved date from the
  answer its brief carries; the orchestrator writes nothing in the series.

A series is a foundation series when its `INDEX.md` carries this block; `dev-cycle` reads
it to know which gate a `CLEAR` was for.

## The work item

When the repo has a work-item store (the `work-items` skill), one item carries the run:

- **Claim** it at Frame when standalone; an orchestrator claims it under its own rules.
- **Handoff** after every gate: `$WI handoff <id>` naming the series, the gate passed and
  the next phase (`--next "phase 2: architecture"`). The item stays open until gate G3.
- **Decisions**: each gate approval the operator owes, and each hold, is a `decision N:`
  line (`$WI note <id> --raw -- "decision N: …"`), answered by an `answer N:` line. N is the
  next number on the channel's counter (a librarian's counter under `librarian-mode`).
- **After gate G3 is approved**: file each feature as an item, `--parent` the foundation
  item and `--dep` each feature it depends on, in the Features table's order; put a feature
  that a hold blocks to `wi groom` with the hold as its question. Then `$WI done <id>
  --note <series path>`.
- **Factored-out aspects** are filed when factored out, `--parent` the item (or `--ref` the
  series for an aspect that belongs to another repo).

With no store, the Held and Factored out tables in the Foundation block are the record, and
the Report lists the features to file by hand.

## Living docs

Feature `F0` regenerates the current view from the series: `docs/requirements.md` (the
phase-1 artifacts), `docs/architecture.md` (the phase-2 artifacts), `docs/adr/NNNN-<title>.md`
(one per ADR, append-only: a superseded ADR keeps its file and gains its Status line), and
the repo's `CLAIM.md` through a claim skill when one is installed. `F0` re-runs after every
reopen that passes its gates.

Where the docs live is asked once per repo, at the first run's Frame, and recorded in
Confirmed Assumptions; the recommendation is tracked `docs/` and `docs/adr/`. In a public
repo the docs carry no estate detail (no host names, private paths or other repos' internals);
the series keeps those.
