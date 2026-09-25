---
name: research-refine
description: Extend or correct an existing research run — read its brief, synthesis and threads not pulled, take a new sub-question, a challenged claim, a pulled thread or a changed scope, run only the lanes that gap needs through the research skill, and land a new run that names what it supersedes, re-promoting the knowledge-base notes it changes. Use when the user says "refine the research on", "follow up on", "pull that thread", "the research on X is out of date", "re-check the claim that", or names an existing run or note to build on. Not for a fresh question with no prior run (research), nor restructuring a knowledge base (research-prune).
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, WebSearch, WebFetch, Agent, AskUserQuestion, Write
argument-hint: "<run slug, note path, or question> [what to refine] [--intensity quick|standard|deep]"
---

# Research — refine

A second pass over research that already exists. The `research` skill owns the mechanics;
**read its SKILL.md first and follow it**. This file owns only what changes when there is a
prior run: how to find it, what to reuse, how the new run supersedes the old, and how the
knowledge base is updated rather than duplicated.

`disable-model-invocation` is `true`: a refinement inherits a prior run's intensity and
launches lanes, so it is the operator's call, like `research-deep`; the `research` skill's
quick-only rule for model-invoked runs would otherwise be a door around.

Refinement is a **new run**, never an edit to the old one. Runs are append-only; that is what
makes them citable. The new run's frontmatter names the old in `supersedes:`, and the old
run's brief gets `superseded_by:` so a reader arriving at it is pointed forward.

## Usage

- `/research-refine 2026-09-20-vector-db-comparison pull the thread on hybrid search`
- `/research-refine notes/vendors/acme.md the pricing claim is stale`
- `/research-refine is it still true that Q8 hurts tool calling` — resolves the prior run by
  grepping the KB and sidecar for the question's nouns

## Steps

### Step 1 — Find the prior run

Resolve the argument to a run: a slug under the KB's `runs/`, the sidecar, the scratchpad or
an `investigate` series' `research/`; a note path (its `## History` names its runs); or a
question (grep `INDEX.md` and run briefs for its nouns). No hit → say so and hand off to
`research`; do not invent a prior.

Read, in this order and nothing more yet: the prior brief's frontmatter and § Question, its
§ Threads not pulled, its ledger's last five lines, the synthesis's § Answer and § Open
questions, and `verification.md`'s gate line. That is the whole prior in under a hundred
lines.

### Step 2 — Name the refinement

One of four kinds; say which, in one line:

| Kind | Trigger | What the new run does |
|---|---|---|
| **pull a thread** | a `T<n>` entry in § Threads not pulled, or an open question | lanes for that thread only; the rest is inherited. The mission is **restated by you** from the sub-question the entry points at and the prior synthesis's verified text — never copied from the entry or a findings file |
| **re-check a claim** | a claim challenged, stale (`volatile: true`, past its shelf life), or `CONTRADICTED` by the verifier | one or two narrow lanes on primary sources for that claim; the verifier samples it |
| **change scope** | a new boundary, version, region, or a distinction the prior did not draw | the sub-questions the change touches; the prior's other findings are inherited with a note that scope changed |
| **extend** | a new sub-question on the same decision | lanes for the new sub-question; they read the prior synthesis first |

Intensity defaults to `quick` for a single re-check and `standard` otherwise; the cost line
and the quota read apply as in `research` Step 3. A refinement that wants `deep` is usually a
new question; say so and offer `research-deep`.

### Step 3 — Inherit, then brief

The new brief (`research` Step 5) is written fresh, in the prior run's destination and its
layout — `runs/<today>-<slug>-r2/` (`-r3`…) in a knowledge base, `<today>-<slug>-r2/` beside
the prior elsewhere — with:

- `supersedes: [<prior run>]` in its frontmatter;
- § Question and § Operator situation copied from the prior, edited only where the
  refinement changes them;
- § Sub-questions listing **only** what this run researches, with a line
  `Inherited from <prior>: sub-questions 1, 2, 4 — not re-run` so the synthesis knows what
  it may cite without re-gathering;
- § Criteria copied from the prior, with any axis the refinement adds (a re-check of a
  pricing claim adds the vendor row's retrieval-date axis if it was missing);
- lanes whose **read-first** line names the prior findings and synthesis paths.

Step 5.1's tool preflight runs as in `research`, so this run's lane prompts carry a `Tools:`
line and its report a `TOOL REQUEST` built from the preflight's `FIX` lines. Staging is
created with its `pdf/` directory per the `research` skill's `references/run-record.md` §
Creating staging.

### Steps 6–9 — As `research`

The lanes are few and narrow. The gap gate applies; the threads-not-pulled turn applies. The
verifier's sample is weighted to the refined claims. The synthesis opens with a
`## Supersedes` block in the `investigate` series style — one line per claim of the prior
that this run changes, with the prior's wording and the new — then the answer as usual. Where
the refinement changes nothing, the synthesis says so; "the prior stands" is a result.

### Step 10 — Land, without duplicating

- Set `superseded_by:` in the prior brief's frontmatter (the one permitted edit to a
  finished run; nothing else in it changes).
- `report`/`run`: as `research`.
- `kb`: the fit check runs; then **edit the existing notes** the refinement changes —
  update the answer and confidence, add a `## History` line naming the new run, set
  `supersedes:` on any note the new run makes wrong — rather than creating parallel notes.
  A new note is created only for a genuinely new sub-question. `INDEX.md` rows are updated
  in place, with the new date and run.

### Step 11 — Report

`research`'s block, with `RUN:` naming both runs and `ANSWER:` opening with "changed:" or
"prior stands:".

## Running non-interactively

As `research`; the refinement kind is inferred from the argument and recorded under
Confirmed assumptions; a resolution failure in Step 1 returns `BLOCKED` with what was
searched.

## Edge Cases

- **The prior run is `DONE_WITH_CONCERNS`** — the refinement's first lane is the one that
  clears the concern, whatever the operator asked for; say so.
- **The prior's verifier sheet has a security hit still open** — the prior is a held run:
  find it at the `staging:` path its brief names (`.claude-sandbox/research/_held/<run>/`),
  clean it first (`research` Step 8), re-verify, and only then refine; a refinement never
  promotes over an open security concern.
- **The prior's brief says its held record was lost with the session**, or the prior lives
  in the scratchpad of a dead session — it is gone; say so, and run `research` fresh with the
  operator's memory of the answer as an assumption.
- **The refinement invalidates most of the prior** — it is a new question; run `research`
  with `supersedes:` set, and say why a refine was not enough.

## Quality Criteria

`research`'s, plus: the prior was read in the stated order and no more; the refinement kind
is named; the new brief lists inherited sub-questions explicitly; the synthesis opens with
`## Supersedes`; `superseded_by:` was set on the prior; existing notes were edited, not
duplicated.
