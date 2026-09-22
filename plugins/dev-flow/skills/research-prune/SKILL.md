---
name: research-prune
description: Curate a research knowledge base — run the fit check against its charter, propose and on approval execute a rebalance (moves, merges, splits, a scheme change), archive notes whose every claim is superseded, mark runs superseded, and rewrite INDEX.md and directory indexes wholesale. Use when the user says "prune the knowledge base", "rebalance the KB", "the research KB is hard to navigate", "tidy up the research notes", "archive stale research", or when a research run's fit check returned STRAINED or REBALANCE FIRST. Not for gathering new research (research, research-refine).
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion
argument-hint: "[kb root] [--fit-check-only | --execute]"
---

# Research — prune

The knowledge base's gardener. No research happens here: this skill reads a KB, measures it
against its own charter, proposes how to restructure it, and — only on approval — moves,
merges, splits, archives and re-indexes. The rules it applies are owned by the `research`
skill's `references/storage-and-knowledge-base.md` (§ The knowledge base, § Landing a run
into a KB, § Rebalancing, § Key junctures); **read that file first**. This file is the
procedure.

`disable-model-invocation` is `true`: restructuring a shared knowledge base is an operator
decision, every time.

## Usage

- `/research-prune` — the nearest KB root
- `/research-prune docs/research --fit-check-only` — measure, propose, change nothing
- `/research-prune --execute` — execute the proposal currently logged in `KB.md`

## Steps

### Step 1 — Find the KB and read the charter

Resolve the root (an argument, or the nearest directory at or above the working directory
with `KB.md` whose `kind` is `research-kb`). No root → say so and stop; this skill does not
create knowledge bases (the `research` skill's Step 4 does, with the charter conversation).

Read `KB.md` in full: purpose, audiences, access patterns, scheme, thresholds, the rebalance
log. Read `INDEX.md`. Do not read the notes yet.

### Step 2 — Fit check

Run the fit check from the reference exactly, and write its result as a block:

1. **Counts** — notes per directory against `notes_per_dir`; `INDEX.md` rows against
   `index_rows`; orphan notes (present on disk, absent from every index); notes past
   `stale_days` whose frontmatter says `volatile: true`; runs with no note citing them.
2. **Access-pattern walk** — for each question in the charter, the path from `INDEX.md` to
   the answering note and the hop count; any over `hops_to_answer`, any dead end.
3. **Scheme fit** — sample ten notes across directories: does each belong where the scheme
   says? Count the misfits; name the pattern (entity profiles in a by-question KB, and so on).
4. **Verdict** — `FITS`, `STRAINED`, or `REBALANCE FIRST`, with the numbers.

Record the block in `KB.md`'s rebalance log with today's date and set `last_fit_check`.
With `--fit-check-only`, print the block and stop.

### Step 3 — Propose

When the verdict is `STRAINED` or `REBALANCE FIRST`, or the operator asked for a prune
regardless, write the proposal as a table in `KB.md`'s rebalance log:

| Action | From | To | Reason (from the fit check) |
|---|---|---|---|
| move | `notes/vendors/acme.md` | `notes/vendors/storage/acme.md` | `notes/vendors` at 19/12 |
| merge | `notes/q-hybrid-search.md` + `notes/q-bm25-plus-vectors.md` | `notes/q-hybrid-search.md` | same question, second supersedes first |
| split | `notes/observability.md` | `notes/observability/{otel,hooks,transcripts}.md` | 3 access patterns dead-end here |
| archive | `notes/q-old-limit.md` | `notes/_archive/` | every claim superseded by 2026-09-20 run |
| supersede-run | `runs/2026-08-01-limits/` | — | findings entirely superseded; drops from INDEX default view |
| scheme | by-question | mixed (by-question + by-entity under `notes/entities/`) | 8 of 10 sampled misfits are entity profiles |

Rules: a **scheme** row is a charter change and is always its own decision; runs are never
deleted (archive or supersede only); a note is archived only when *every* claim in it is
superseded and the successor is named; moves preserve history (`git mv` in a tracked KB).

Then present the proposal to the operator as a numbered decision list — one row per number,
recommended action first, with what each does to the access-pattern walk. Do not pair the
list with the fit-check analysis in the same turn; show the analysis, then ask. Unattended,
stop here with the proposal logged and `STATUS: BLOCKED — proposal awaits approval`.

### Step 4 — Execute (approved rows only)

In this order, so nothing dangles:

1. Moves and splits (`git mv`; a split writes the new notes, then reduces the original to a
   `## Moved` stub if anything outside the KB linked to it, else removes it).
2. Merges — the surviving note absorbs the other's `## History`, sets `supersedes:`, and the
   absorbed note becomes a `## Moved` stub or is removed by the same rule.
3. Archives — move to `notes/_archive/<original path>` with a one-line `archived:` reason in
   frontmatter.
4. Run supersedes — `superseded_by:` in the run brief's frontmatter; nothing else in a run
   changes.
5. Charter — when a scheme row was approved, rewrite `KB.md` § Organising scheme and
   `scheme:`; adjust thresholds only when the operator said to.
6. **Indexes, wholesale** — regenerate `INDEX.md` and every directory `README.md` from disk;
   never patch them by hand. One row per note (path · one-clause summary · confidence · date
   · last run) grouped per the scheme; a `## Runs` section listing every run not superseded;
   a `## Archived` section.
7. **Links** — grep the KB (and the repo, for a tracked KB) for every old path and update
   it; list any link outside the KB you could not update.
8. Re-run the access-pattern walk and print the before/after hop counts.
9. Log the execution in `KB.md`'s rebalance log; set `last_rebalance`.

A tracked KB gets one commit per approved proposal, staged path by path (never `add -A`),
with the proposal table in the message; the operator lands it.

### Step 5 — Report

```
STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED
KB: <root> — verdict before: <…>, after: <…>
EXECUTED: <n> moves, <n> merges, <n> splits, <n> archives, <n> run supersedes, scheme <changed|unchanged>
ACCESS PATTERNS: <n>/<n> within <hops_to_answer> hops (before <n>/<n>)
LINKS NOT UPDATED: <list or none>
NEXT: <the threshold nearest to tripping, or "charter revisit due: <reason>">
```

## Running non-interactively

Fit check and proposal only; execution needs an approval the run cannot give. `--execute`
in an unattended run executes exactly the proposal logged by a prior interactive turn and
nothing newer.

## Edge Cases

- **Two KB roots in scope** — the nearer one; say so.
- **A note is linked from outside the repo** (a wiki, a ticket) — it gets a stub, never a
  removal; list it.
- **The charter's access patterns are stale** (nobody asks those questions any more) — that
  is a key-juncture signal from the reference; ask about the charter before proposing moves
  that optimise for the wrong questions.
- **`_inbox/` has accumulated** from unattended landings — inbox triage is part of the
  proposal: each inbox note gets a move row.
- **A run directory was edited after its synthesis** — a rule was broken upstream; note it
  in the report, do not "fix" the run.

## Quality Criteria

The charter was read before any note; the fit check ran in full and was logged; the proposal
is a table with a fit-check reason per row; scheme changes were their own decision; nothing
executed without approval; runs were never deleted; indexes were regenerated wholesale, not
patched; links were updated and the leftovers listed; the access-pattern walk was re-run and
its before/after is in the report.
