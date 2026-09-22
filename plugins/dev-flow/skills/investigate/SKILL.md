---
name: investigate
description: Investigate a problem before implementing it — resolve repos, survey branches, load project context, search and read the code, gather requirements with the user, then write a reviewed plan to .claude-sandbox/investigations/{slug}/ for the implement skill to consume. Use when the user says "investigate", "look into", "research this issue", "figure out how to fix", "plan this work", or picks an item off TODO.md. Also use to re-investigate an existing series. For a scoped bug or feature, one session can read its way to a plan; a broad, open-ended landscape question — three to five categories of evidence, no single one enough — escalates to the deep-investigation skill.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, WebSearch, WebFetch, AskUserQuestion
argument-hint: "<issue description | wi item id | TODO item>"
---

# Investigate

Investigate a problem: understand what it is, read the code, settle the requirements with the
user, and synthesize a plan that `implement` can act on directly.

The output is a markdown file in `.claude-sandbox/investigations/<slug>/`, not a ticket. The
on-disk format — layout, serials, `Supersedes`, `INDEX.md`, the standard outline, the writing
rule — is canonical in `references/investigation-format.md`. **Read it before writing
anything.** It is the single owner of those rules; this file does not restate them.

Every investigation ends with a concrete **Proposed Fix** (bugs), **Implementation Approach**
(features), or **Recommendation** — when no code should be written (it exists, it is not worth
it, the premise fails); a Recommendation still says what to do, usually document why, and
`implement` lands that. `implement` refuses a series with none of the three.

## Usage

`/investigate <issue description | wi item id | TODO item | existing slug>` — an existing slug
re-investigates; with no argument the problem comes from the conversation, or is asked for.

---

## Step 1 — Resolve the issue

Resolve the argument per `references/resolving-the-issue.md`: a **work-item** id or title
fragment (in a repo with a `.work/` or `.claude-sandbox/work/` store) → `wi show` or `wi ls
--plain`, start from its description and `## Handoff` block, and `wi claim` it once the
investigation begins — with no argument in such a repo, offer `wi next --plain` first; a
**TODO.md** item only when no store exists — a `TODO.md` carrying the work-items deprecation
notice means use `wi`, a missing one means treat the argument as ad hoc text, and `TODO.md` is
never created; an **existing slug** → Step 1a; **ad hoc text** as given; **no argument** → the
problem from the conversation. **A thin description is expected** — filling it in is the job;
what you need is *something to anchor on* (a symptom, a component, a file, a goal), else ask.

## Step 1a — Resolve or create the series

Check `.claude-sandbox/investigations/` for a series that already covers this problem.
**Extending one**: read the whole series first, per
`references/investigation-format.md` — every `NN_*.md` in serial order, applying each
`Supersedes` block — since you extend a record, not start over; confirm a new pass with the
user unless the invocation already states that intent. **New**: propose and state a slug
(kebab-case, 2–5 words, what the work *is*); create nothing until Step 13. An absent
`.claude-sandbox/config.yaml` means warn once and continue (the wording is in
`references/investigation-format.md`).

---

## Asking at a gate

A blocking gate (Steps 2, 9, 11) blocks on the user's answer, not on a widget; either form
carries your recommendation on each question. While scope is still open, **prefer a numbered
list in your reply**, answered free-form: the honest answer is often "none of these, and here
is why", which fixed options fight, and an answer that redefines the problem is one to
re-scope from. Keep `AskUserQuestion` for a closed choice late in a task, never in the same
turn as heavy analysis.

**End the turn on the list.** Your recommendation is not the answer, and a background agent's
return is not either: fold it in and keep waiting.

---

## Running non-interactively

When told to run without stopping, the blocking gates (Steps 2, 9, 11, 12) change form, not
vanish. **Read `references/run-modes.md` § Running non-interactively before Step 1**; in
short: decide each gate yourself and record it under **Confirmed Assumptions** as
overturnable; a **relayed** decision (peer session, message, secondhand notes) that would change
behaviour or a default for people not present is a **blocking Open Question**, never a
Confirmed Assumption; anything you would have asked is an Open Question with an owner and a
blocks-or-not marking, and a genuine blocker stops the run; Step 12 is Save. Report every
recorded decision together at the end.

---

## Running under an orchestrator

When another skill dispatches this one as a sub-agent (`dev-cycle`'s plan agent or
implementer, a `deep-investigation` POC spec), the orchestrator owns git, the work item and
every dialog, and gives a **Series home** (absolute), the **base** and maybe a **worktree**.
**Read `references/run-modes.md` § Running under an orchestrator before Step 1.** In short: run
non-interactively; the brief is the description and a work item is read, never claimed; the
series lives at the Series home, never in a repo or worktree; Steps 2, 9, 11 ask nothing (the
verification agent still runs); Step 3a is skipped; Step 6 creates no branch or worktree; no
report or retro; never ask the user — each gate decision is a Confirmed Assumption and a
DEVIATION. Return `STATUS`, `SERIES` (absolute path), `OPEN QUESTIONS` (each blocking or not),
`DEVIATIONS`.

---

## Step 2 — Scoping gate (blocking)

**A short round to make the problem investigable**, not the requirements gate (Step 9). Ask
only what you cannot answer yourself and what changes *where you look*:

- What is the observable symptom, or the goal? (What happens now vs what should happen.)
- Where does it show up — which command, endpoint, screen, file?
- Which repo owns this work? If the target may not exist yet — a new plugin, repo, or tool —
  say so and point to the create-repo skill.
- What does "done" look like?
- Is anything explicitly out of scope?

One round of 2–4 questions, per **Asking at a gate** — scope is open, so a numbered list. Then
**wait**. **Skip it only when the description already answers it**, saying why. Never ask what
the code will tell you — that's Step 6.

---

## Step 3 — Resolve repositories

Usually the working directory's git root: confirm it and move on. Resolve more when the
problem spans repos (a library and its consumers, code and infrastructure), preferring local
checkouts — glob for siblings before proposing a clone.

**Never clone silently.** A repo with no local checkout: ask — provide a path, clone it, or
exclude it. Record each repo's resolved path and, where known, its remote.

---

## Step 3a — Survey open branches and choose the base

Run this for every resolved repo. The
commands, what makes a strong candidate and how to vet one are in `references/branch-survey.md`.

**The default branch is the base unless proven otherwise.** With no overlap, say so in one line
— no empty branch-strategy table. Only when branching off the default would not build do you
consider an alternative, and **a non-default base requires explicit `AskUserQuestion` consent**
with the genuine options laid out: base off the in-flight branch and accept the rebase risk,
make this work self-contained, or wait for the dependency to merge.

Record the per-repo base in **Confirmed Assumptions** and **Deployment & Rollout Notes**;
`implement` still re-verifies it.

---

## Step 4 — Load project context

Before searching, load the project's conventions: root and nested `CLAUDE.md` for the areas
you will touch; `README.md` and `docs/`; `.claude-sandbox/CLAUDE.md` when present; the plugin
skills matching the stack. State each and why, one line apiece. **Trim to what the problem can
use, with a reason per omission**.

**Before defining any new convention, look for an existing one.** If the work will introduce a
path, a directory layout, a naming scheme, a branch pattern or a file format, grep the loaded
skills, the project's scaffolding and sibling projects for one already in use. Adopt or extend
the existing one; diverging is a decision to state and justify in the plan.

---

## Step 5 — Build a search strategy

Build a prioritised list of search terms:

- **Bugs** — exact strings first: error messages, exception types, stack frames, log lines,
  function names, file paths, endpoints. Then domain terms.
- **Features** — entity names, concepts, API endpoints, component names.
- **Tasks** — component names, config areas, file paths.

List external subjects too (part and model numbers, spec and API versions) for Step 6d.

**Search for the whole class of issue, not one idiom**: for a *category* (insecure randomness,
a deprecated call, a missing guard), grep every way it can appear, not just the preferred
wrapper.

---

## Step 6 — Explore and read the code

**Delegate context-heavy searching to subagents** — broad greps, call-chain tracing, external
research: `Explore` to locate code, `general-purpose` to read and reason, a **fork** when the
sub-task needs this session's context. **Bring back `file:line` findings and cited claims, not
file dumps.**

Per repo:

**6a — Orientation.** Read `README.md` / `CLAUDE.md`; glob for build config and structure;
note what kind of repo it is and how it is built, run and tested.

**6b — Targeted search.** Exact strings first, then domain terms; note `file:line` and context
for each hit.

**6c — Deep read.** Read in full any file with two or more hits, with its callers, imports and
tests, following the call chain both ways; cap at roughly 20 files per repo. **Validate by
building, not just reading**: run the repo's build, tests, codegen and lint. A
codegen step the change needs is called out in **Files to Modify**.

Investigation stays in the checkout; a probe needing substantive repo edits gets its own
worktree (a fresh checkout — untracked `.env`, `node_modules` absent unless `.worktreeinclude`
or the worktree symlink setting covers them; the sandbox skill's worktree-mode section owns
the details). Two rules for probes are in `references/probe-discipline.md`: **a probe that
reproduces a symptom has its own parameters as suspects** — vary the harness and re-run
without anything present in every run before recording a root cause; and **when the plan turns
on a low-level nuance of a tool's behaviour, read the tool's source** and cite it, or mark the
claim documentation-only for `implement` to re-verify.

A repo that yields nothing: record "no relevant code found" and move on.

**6d — External research**, when the plan rests on a fact the codebase cannot answer (a
vendor spec, a price, a third-party behaviour); one line to skip it otherwise. Per
`references/external-research.md`: **get the primary** — search results and vendor guides
only look authoritative; **reconcile against the live system** — prefer the observation and say
which source lost; expect fetch-blocking. Record per the citation rule in
`references/investigation-format.md`.

---

## Step 7 — Blast radius

Identify what else the change can reach: callers of changed functions and types; public API
(exports, routes, CLI flags, config keys, event payloads); persisted shapes (schemas,
migrations, serialized formats, on-disk layouts); anything downstream of those.

**For any contract change, verify both ends exist and are wired** — grep both sides. If the
change is genuinely self-contained, **say so explicitly**: a missing Blast Radius reads as "not
checked".

---

## Step 8 — Infrastructure and operational scope (conditional)

Only when the change plausibly touches deployment, configuration or runtime resources (one
line to skip): new or changed artifacts, containers, services, scheduled jobs; config or env
vars that must exist somewhere; migrations, backfills, one-off jobs; manual deploy steps.
**Read the thing that actually defines the deployed state**, not a build file resembling it.

---

## Step 9 — Requirements gate (blocking)

This sits **after** exploration on purpose: the code answers many questions, so ask only what
it cannot. **Do not begin the plan until this gate completes.** Present all three together:

1. **The core problem**, in 1–2 sentences, as you now understand it from the code.
2. **Your assumptions**, as an explicit list — scope, expected behaviour, compatibility, what
   is out of scope — including any **external** fact the plan depends on (Step 6d).
3. **Your open questions** — ambiguities, missing acceptance criteria, edge cases, anything
   Step 7 raised — asked per **Asking at a gate**.

Then **wait**. This is a loop, and one round is rarely enough. Each round:

1. Incorporate the answers, and restate any assumption that changed.
2. **Go and answer what the answers made answerable** — an answer often opens a question the
   *code* settles; return to Steps 4–8 for it. Exploration and requirements interleave.
3. Ask the next round, in batches of related questions, saying where you are so a multi-round
   gate reads as progress.

**Keep looping until the user confirms there is nothing left to clarify** — never on "probably
enough". Apply the
triage rule for what may become an Open Question (in `references/investigation-format.md`)
now, not after the plan is written.

---

## Step 9a — Measure before choosing (conditional)

**When the plan will offer genuinely-open alternatives, take the cheapest measurement that
discriminates between them — before you recommend one**; one line to skip otherwise. The rules
are in `references/measure-before-choosing.md`:
measure the worst thing you already own; bound the blast radius (idle capacity first — loading
a production path needs explicit consent, a time cap and a health check after); two instruments
beat one; record the command, conditions and number as evidence and as `implement`'s baseline.
If the measurement cannot be taken, say which option the decision rests on and mark it for
`implement` to settle.

---

## Step 10 — Build the plan

Compose the file locally; nothing is written yet. Follow the standard outline, the section
naming (`Root Cause Analysis` / `Proposed Fix` for bugs), and the writing rule in
`references/investigation-format.md`. All code references carry `file:line`. If no relevant
code was found anywhere, say so in Existing Architecture and suggest where else to look.

---

## Step 11 — Open-question sweep (loop)

The plan exists but **nothing is on disk** — the last point where a question is cheap to close.
Follow
`references/open-question-sweep.md`: **sweep your own draft** (hedges, claims with no
`file:line` or command, implicit choices, thin sections); **classify each** — agent-verifiable,
user decision, or external/blocked (straight to Open Questions with owner and blocks-or-not),
a both-kind going to the user first; **launch ONE background agent for the whole verifiable
batch — first**; meanwhile **ask the decision questions**, per **Asking at a gate**, each with a
defer option; **fold in and loop** until a round yields nothing new or all that remains is
deferred or external. Report the outcome in one line at the Step 12 gate — e.g. *"Sweep: 5
candidates → 2 verified, 2 decided by you, 1 deferred."*

---

## Step 12 — Review gate

Hold the plan to `references/quality-criteria.md` first — the last point before anything is
written. Display the full plan, then output this **verbatim**:

```
---
**Plan ready. What would you like to do?**

1. **Save** — write the investigation and update the index, as-is
2. **Discuss** — refine the plan before saving
3. **Reject** — discard, write nothing

Reply with 1, 2, or 3.
---
```

**Save** → Step 13.

**Discuss** → free-form; after each exchange re-display the **full updated plan**, then:

```
---
Ready to save, continue discussing, or reject? (1 = Save / 2 = Discuss / 3 = Reject)
---
```

Loop until Save or Reject.

**Reject** → print `Investigation cancelled. Nothing was written.` and stop.

---

## Step 13 — Write the investigation

`mkdir -p` the series directory and `ls` it: the serial is the highest existing `NN` plus
one, `00` for a new series. **Never reuse a serial and never overwrite a file** — one at your
intended serial means you misread the directory; re-read it. Write `NN_<name>.md` with the
Write tool, per `references/investigation-format.md`; on `01`+ the `Supersedes` block comes
first, always.

---

## Step 14 — Rewrite the index

Regenerate `INDEX.md` wholesale from all serials, per `references/investigation-format.md`.
Capture the provenance SHAs now (`git -C <repo> rev-parse --short HEAD`). Add a TOC row for the
new file with status `pending`; leave existing rows' Status and Branches untouched, except
`superseded by NN` on any row this pass supersedes. The reconciled sections reflect **all**
passes, not a copy of the new file's.

---

## Step 15 — Report

```
## investigate complete

**Series:** <slug>
**Wrote:** .claude-sandbox/investigations/<slug>/NN_<name>.md
**Index:** updated (N investigations, M open questions)
**Repos:** <repo> @ <sha>
**Base branch:** <per repo, or "default everywhere">
**Blast radius:** <self-contained | reaches: ...>
**Sweep:** <N candidates → X verified, Y decided, Z deferred>

Next:
- /dev-flow:implement <slug>
- /context-guard:checkpoint, /clear, then /dev-flow:implement <slug> in the fresh session
- /dev-flow:dev-cycle <slug> — a sub-agent builds it in a worktree, reviewed before merge
```

Print the checkpoint line only when `context-guard:checkpoint` is in this session's list of
available skills — that list, not a config path, which can go stale.

---

## Step 16 — Retrospective (optional, user-gated)

Offer a lightweight retrospective, with the prompt in `references/retrospective.md`. On
**Yes**, note the friction — a missed search idiom, an undocumented step, a wrong assumption —
present it, and **ask the user to run `/kit-dev:update-kit`**: it is user-invoked only, and its
workflow is not replicated here.

---

## Edge Cases

Read `references/edge-cases.md` when a run goes off the main path. Most entries restate a
step's rule; a few live only there — a path the user names that is missing inside a container
(check the `mounts:` cascade before calling it unreachable), a user who defers every question
(legitimate; record each and do not re-ask), a sweep with no candidates (say so in one line), a
problem that turns out to be several (propose one series each, cross-referenced).

---

## Quality Criteria

The checklist a finished run is held to — every gate, sweep, citation and serial rule
restated as an outcome — is in `references/quality-criteria.md`. Hold the run to it before
the Step 15 report.
