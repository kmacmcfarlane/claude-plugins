# Storage, shapes and the knowledge base

Loaded from `research` Step 4 and Step 10. This file owns where a research run lands, what
the four output shapes are, the run-record layout, and the knowledge-base rules: the
charter, the organising schemes, the fit check that runs every time a KB grows, and the
rebalance mechanism `research-prune` executes. Nothing here is restated in a SKILL.md.

## The principle

The **artifact** and the **workspace** are different things. Scratch, intermediate fetches,
scripts under test and half-written drafts go in the session scratchpad; the artifact goes
to exactly one resolved destination; nothing else on disk changes. A run never creates a
tracked file in a repo unless that repo has said, with a marker or a flag, that it wants
research checked in.

**Staging.** Everything drafted from fetched pages — lane findings, a report draft, a quick
run's `--to` file — lands first in `<scratchpad>/research/<run>/`, the run's staging area,
named in the brief's frontmatter, and is scanned there by the verifier. The verifier's sheet,
the synthesis and `sources.md` are written after that scan, from scanned files, into the
same staging area, and the whole record is copied to the destination only on a clean scan.
The brief is the one file written at the destination before that, because the orchestrator
authors it and it carries no fetched text. A run held on a security concern moves to
`.claude-sandbox/research/_held/<run>/` when the held-path check (§ The ignore check) says
that path is ignored, else it is lost with the session and the brief says so.

## The ignore check

Two questions, asked with the same command, answered at different depths.

- **Clean runs (rules 4 and 5)** — ask the **host repo**: `git check-ignore -q <path>` from
  the working directory. Ignored → the sidecar is usable. The sidecar being its own git
  repository in claude-sandbox's sidecar mode is not a problem here: that repo exists to
  commit verified runs, exactly as it commits investigations.
- **Held runs (`_held/`)** — unverified content must be ignored at **every level**, because
  the sidecar repo tracks what the host ignores. **First**, when `.claude-sandbox/` exists,
  create `.claude-sandbox/research/_held/` and write `_held/.gitignore` containing `*`, so
  every repo that could see the directory ignores its contents by construction. **Then** run
  the check: from the nearest *existing* parent of the candidate path, run
  `git -C <parent> check-ignore -q <rest>` (the remainder of the path, relative to that
  parent); then, while that parent's repo root is itself inside another repo, repeat from
  that root's parent for the remainder. Ignored at every level → usable. Any level still
  tracked, or `.claude-sandbox/` absent, or the nearest parent not in a repo at all → the
  held run stays in the scratchpad and is declared lost with the session.

## Destination resolution

Resolve in this order and stop at the first hit. Say which rule fired, in one line.

| # | Rule | Destination |
|---|---|---|
| 1 | The invocation names a path (`--to <path>`, "write it to …") | that path |
| 2 | The invocation says ephemeral ("scratch", "throwaway", "just tell me") | the session scratchpad; shape `answer` or `report` |
| 3 | A **KB root** is in scope: a directory at or above the working directory containing `KB.md` whose frontmatter says `kind: research-kb`, or a path named under a `research:` key in the repo's `CLAUDE.md` | that KB; shape `kb` |
| 4 | The session is inside an `investigate` series (the working thread has a `.claude-sandbox/investigations/<slug>/` it is writing to) | `<series>/research/<run>/`; shape `run`; the series' `INDEX.md` gets one line; `investigation-format.md` governs the series, this file governs the run dir |
| 5 | Otherwise | the sidecar `.claude-sandbox/research/<run>/`; shape `run` |

Rules 4 and 5 are **untracked-only**. Whether `.claude-sandbox/` is ignored is a per-repo
choice (some repos commit their investigations, and in sidecar mode it is a repo of its own),
so before either fires run the clean-run check (§ The ignore check) on the candidate
directory: ignored by the host repo → use it; tracked, or not a git repo → the path counts
as checked-in, and with no marker or flag the run goes to the scratchpad instead (shape
`run`, in staging), with a line saying why. Never assume the sidecar is untracked.

When two KB roots are in scope (a repo-level one and a subdirectory one), prefer the nearer.
When rule 5's path does not exist yet, create it only if the clean-run check (§ The ignore
check) reports the host repo would ignore it; otherwise the untracked-only rule sends the run
to the scratchpad. Never create a tracked path.

**Promotion out of the sidecar** — "this was worth keeping, check it in" — is a separate,
explicit step, and it is gated: it refuses unless the run's `verification.md` exists and its
security section is clean (a run that was never verified is verified first). Then copy the
run to `docs/research/<run>/` (or the path the operator names), add frontmatter
`promoted_from:`, and leave the sidecar copy in place. If the repo would benefit
from a KB, offer to establish one (below) rather than accumulating loose run dirs under
`docs/`.

## Shapes

| Shape | What lands | When |
|---|---|---|
| `answer` | the reply only, in the `question-research` writeup form (Answer with confidence · Question recap · Findings per sub-question with confidence and sources · Conflicting or discarded material · Bottom line · Open questions); nothing on disk | `quick`, ephemeral, "just tell me" |
| `report` | one file: the same form plus frontmatter and a Sources section | a single spike whose result someone will read once; the operator's most common historical shape |
| `run` | a run record directory (below) | any fan-out preset outside a KB |
| `kb` | a run record inside the KB's `runs/`, plus promotion into `notes/` and an `INDEX.md` update, after the fit check | a KB root resolved |

An `answer` never silently becomes a `report`: if the orchestrator wants to keep something, it
says so and names the path.

## The run record

```
<destination>/runs/<YYYY-MM-DD>-<slug>/      (or <destination>/<slug>/ for rules 1, 4, 5)
  00-brief.md          question, decision, sub-questions, criteria, lanes, routing, ledger
  findings/<lane>.md   flat — one file per lane, the agent's fixed shape, ≤300 lines
  01-synthesis.md      the one-pass synthesis, with the verification table
  verification.md      the verifier's score sheet
  sources.md           one line per source across the run: URL/path · tier · retrieved · used by
  tools/               scripts a toolkit lane built, when any
```

Runs are **append-only**: once `01-synthesis.md` is written, nothing in the directory is
edited — with one permitted exception, `superseded_by:` added to the brief's frontmatter when
a later run supersedes it. A refinement is a new run that names the old one in `supersedes:`;
a correction is a new run. This is what makes a run citable.

`findings/` is flat, always. Nesting under a run is the failure mode the ≤300-line contract
exists to prevent — the synthesis has to read every file in one pass.

Slug: kebab-case, 2–5 words, what the question *is*, not the file it touches and not a date
(the date is the prefix). Before creating one, list the destination for an existing slug on
the same question; extending beats near-duplicating.

## Frontmatter — every landed file

```yaml
---
question: <the one-line question>
run: <YYYY-MM-DD>-<slug>
date: <ISO date written>
retrieved: <ISO date of the newest source retrieval>
intensity: quick | standard | deep | exhaustive
shape: report | run | kb
confidence: established | well-supported | contested | uncertain
supersedes: [<run or note path>, …]   # or []
volatile: true | false                # true when any load-bearing claim can go stale
audience: operator | team | agents
---
```

`volatile` and `retrieved` are reserved now for a later `--refresh` that re-runs only the
claims that can go stale. `audience: agents` changes the writing: stable headings, a TL;DR
that reads correctly out of context, no pronouns without antecedents — a later agent will
grep this, not read it top to bottom.

## The knowledge base

A knowledge base is a directory that accumulates research over many runs and is read far
more than it is written. It has four parts and a charter that says how they fit together.

```
<kb-root>/
  KB.md            the charter (below) — its presence is the marker that makes this a KB
  INDEX.md         one row per note and one per run; the entry point a reader greps
  notes/           the durable, edited layer, laid out per the charter's scheme
  runs/            immutable run records, one per research run
```

### Establishing a KB — the charter

The first time a run resolves to a repo that wants research kept but has no `KB.md`, or when
the operator asks for one, the orchestrator **establishes the KB before landing anything**.
This is a conversation, not a template fill: the charter records what the KB is *for*, and
everything else follows from that.

Ask, in one round, with a recommendation on each:

1. **Purpose** — what decisions or work will this KB feed? One sentence.
2. **Audiences** — the operator, a team, future agent sessions, or all three. Agents as an
   audience changes the writing (above).
3. **Access patterns** — the three to five questions people will ask *of* the KB. "Which
   tool do we use for X?" "What did we decide about Y and why?" "What is the current state
   of Z?" These are the test the fit check runs later: every one must be answerable by
   navigating `INDEX.md` in at most two hops.
4. **Information type**, which selects the **organising scheme** (below). Recommend from the
   access patterns.
5. **Growth thresholds** — defaults below; adjust when the operator knows the KB will be
   large.
6. **Checked-in?** — whether the KB is tracked (default yes: a KB exists to be shared) and
   any privacy rule that binds what may be written into it.

Write `KB.md`:

```yaml
---
kind: research-kb
established: <ISO date>
scheme: by-question | by-entity | topic-tree | timeline | diataxis | mixed
audiences: [operator, team, agents]
thresholds:
  notes_per_dir: 12
  index_rows: 60
  hops_to_answer: 2
  orphan_notes: 0
  stale_days: 180
last_fit_check: <ISO date>
last_rebalance: <ISO date or none>
---
# <KB name>

## Purpose
## Audiences
## Access patterns
- Q: … → expected path: INDEX → <section> → <note>
## Organising scheme
<the scheme, and the one paragraph saying why it fits this information type>
## Privacy and check-in rules
## Rebalance log
- <date> — established.
```

### Organising schemes — chosen by information type

The right shape for `notes/` depends on what kind of information the KB holds. Pick one; say
why; `mixed` is allowed when the access patterns genuinely split, and then each top-level
directory under `notes/` names its own scheme in its `README.md`.

| Scheme | Fits when the information is… | `notes/` layout | Note grain |
|---|---|---|---|
| **by-question** | decisions and answers: "should we…", "which…", "is it true that…" | `notes/<question-slug>.md`, flat, grouped in `INDEX.md` by decision area | one note = one question with its current answer, confidence, and the runs behind it |
| **by-entity** | things that get compared and revisited: tools, vendors, libraries, models, products | `notes/<entity>.md` + `notes/comparisons/<a-vs-b>.md` | one note = one entity's current profile (version, licence, maintenance, verdicts); comparisons are separate notes that cite entity notes |
| **topic-tree** | a domain being learned: concepts with a natural taxonomy | `notes/<area>/<topic>.md`, depth ≤ 3, every directory with a `README.md` that is its local index | one note = one concept, linked to neighbours |
| **timeline** | events, changes, history, changelogs, incidents | `notes/<YYYY>/<YYYY-MM-DD>-<event>.md` + `notes/threads/<thread>.md` for the through-lines | one note = one dated event; threads tie events together |
| **diataxis** | operational knowledge someone will *use*: how-tos, references, explanations | `notes/how-to/`, `notes/reference/`, `notes/explanation/` (tutorials rarely belong in a research KB) | one note = one task, one reference surface, or one explanation |

Whatever the scheme, notes are **atomic and evergreen**: one idea per note, written so it
stands alone, edited in place as understanding improves, with `supersedes:` and a `## History`
section pointing at the runs that changed it. Runs are the provenance; notes are the
knowledge. A KB that has only runs is a graveyard; a KB that has only notes has no evidence.

### Landing a run into a KB — the fit check

Every time a run lands in a KB, before promotion, the orchestrator runs the fit check and
reports its result in one block in the run's ledger and in `KB.md`'s `last_fit_check`.

1. **Counts** — notes per directory, `INDEX.md` rows, orphan notes (not linked from any
   index), notes older than `stale_days` with `volatile: true`.
2. **Access-pattern walk** — for each question in the charter, walk from `INDEX.md` to the
   note that answers it and count the hops. Record any that exceed `hops_to_answer` or dead-
   end.
3. **Scheme fit** — does the new run's material fit the scheme? A by-entity KB receiving a
   "should we…" question, or a by-question KB accumulating entity profiles, is a scheme drift,
   not a filing problem. Say which.
4. **Verdict** — `FITS` (promote now), `STRAINED` (promote now, and file a rebalance
   proposal in `KB.md`'s rebalance log with the counts), or `REBALANCE FIRST` (a threshold is
   past by half again or an access pattern dead-ends: propose the rebalance, and in an
   interactive run ask before promoting; unattended, promote to a `notes/_inbox/` directory
   and record the proposal — nothing is lost, and the tree is not made worse).

### Promotion

For each finding that changes what the KB knows: create or edit the note it belongs to under
the scheme; add the run to the note's `## History`; set `supersedes:` where an older note or
run is now wrong; add or update the `INDEX.md` row (one line: path · one-clause summary ·
confidence · date · run). Findings that do not change what the KB knows stay in the run and
are not promoted — promotion is curation, not copying.

Never promote a findings file wholesale. A note is written for the KB's audiences in the KB's
scheme; a findings file is written for a synthesis.

### Rebalancing — the mechanism

A rebalance is a **proposal first, then a move**. The proposal (written by the fit check, or
by `research-prune` on request) is a table: current path → new path, or merge A+B → C, or
split A → A1, A2, with the reason from the fit check's counts and the access-pattern walk.
`research-prune` executes an approved proposal: moves with history preserved (`git mv` in a
tracked KB), every `INDEX.md` and directory `README.md` rewritten wholesale, every link that
pointed at a moved note updated, a `## Moved` note left at old paths that were linked from
outside the KB, and a line in `KB.md`'s rebalance log. A scheme change (by-question →
topic-tree, say) is a rebalance whose proposal also rewrites the charter's scheme section;
it is never done silently.

Pruning, the same skill's other half: notes whose every claim is superseded are merged into
their successor or moved to `notes/_archive/` with the reason; runs are never deleted (they
are the evidence), but a run whose findings are entirely superseded gets `superseded_by:` in
its brief's frontmatter and drops out of `INDEX.md`'s default view.

### Key junctures — when to revisit the charter

The charter is re-read, and the operator asked whether it still holds, at these points and
no others (asking on every run trains people to stop reading the question):

- the fit check returns `REBALANCE FIRST`;
- a run's material does not fit the scheme (a scheme-drift verdict) for the second time;
- the KB passes 3× any threshold it was established with;
- the operator says the KB is hard to use — that sentence is a fit-check failure whatever the
  counts say.
