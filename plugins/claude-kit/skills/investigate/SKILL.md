---
name: investigate
description: Investigate a problem before implementing it — resolve repos, survey branches, load project context, search and read the code, gather requirements with the user, then write a reviewed plan to .claude-sandbox/investigations/<slug>/ for the implement skill to consume. Use when the user says "investigate", "look into", "research this issue", "figure out how to fix", "plan this work", or picks an item off TODO.md. Also use to re-investigate an existing series.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, WebSearch, WebFetch, AskUserQuestion
argument-hint: <issue description | wi item id | TODO item>
---

# Investigate

Investigate a problem: understand what it is, read the code, settle the requirements with the
user, and synthesize a plan that `implement` can act on directly.

The output is a markdown file in `.claude-sandbox/investigations/<slug>/`, not a ticket. The
on-disk format — layout, serials, `Supersedes`, `INDEX.md`, the standard outline, the writing
rule — is canonical in `references/investigation-format.md`. **Read it before writing
anything.** It is the single owner of those rules; this file does not restate them.

Every investigation must end with a concrete **Proposed Fix** (bugs) or **Implementation
Approach** (features) section. `implement` refuses a series without one.

## Usage

`/investigate <issue description | TODO item>`

Examples:

- `/investigate the upload retry gives up after one attempt instead of three`
- `/investigate TODO.md item 3`
- `/investigate flaky-upload-retry` — re-investigate an existing series
- `/investigate` — no argument; the problem is taken from the conversation, or asked for

---

## Step 1 — Resolve the issue

The argument is a problem description, a pointer to one, or absent.

**A work-item reference** (an id like `etcd-alerting-3f9a`, or a title fragment, in a repo
with a `.work/` or `.claude-sandbox/work/` store): resolve it with the `work-items` skill's
CLI — `wi show <id>` for an id, `wi ls --plain` to match a fragment — and use the item's
description and `## Handoff` block as the starting description. `wi claim` it once the
investigation begins. With **no argument** in such a repo, offer `wi next --plain` (the
ready-ranked queue) before falling back to the conversation.

**A TODO.md reference** (`TODO.md item 3`, `the second TODO`, or just a phrase matching one) —
the fallback when no work-item store exists: read `TODO.md` from the repo root, find the
matching `- [ ]` item, and use its text as the starting description. A `TODO.md` that carries
the work-items deprecation notice means the store has moved — use `wi`, do not resurrect the
file. If `TODO.md` does not exist, say so and treat the argument as ad hoc text. Do not create
`TODO.md`.

**An existing slug** (matches a directory under `.claude-sandbox/investigations/`): this is a
re-investigation. Go to Step 1a.

**Ad hoc text**: use it as the starting description.

**No argument**: take the problem from the conversation so far — the error, the failure, the
finding that prompted this. If the conversation gives you nothing to anchor on, ask.

**The description you start with is expected to be thin.** Filling it in is the job, not a
precondition — Step 2 exists for exactly that. What you cannot proceed without is *something
to anchor on*: an observable symptom, a named component, a file, or a stated goal. If you have
none of those, ask for one before continuing.

## Step 1a — Resolve or create the series

List `.claude-sandbox/investigations/` and check whether a series already covers this problem.

**Extending an existing series** — read the whole thing first, per
`references/investigation-format.md`: every `NN_*.md` in serial order, applying each
`Supersedes` block. You are extending a record, not starting over. Then confirm with the user
that a new pass is wanted, unless the invocation already states the re-investigation intent
explicitly ("re-investigate with the new scope"), in which case treat that as the
confirmation and do not re-ask.

**New series** — propose a slug (kebab-case, 2–5 words, what the work *is*) and state it. Do
not create the directory yet; nothing is written until Step 13.

If `.claude-sandbox/config.yaml` is absent, warn once and continue — see
`references/investigation-format.md` for the exact wording and why this is not a hard stop.

---

## Step 2 — Scoping gate (blocking)

**A short round to make the problem investigable.** Not the requirements gate — that is Step 9,
after you have read the code. This gate exists so you do not spend an exploration pass on the
wrong subsystem.

Ask only what you cannot answer yourself and what would change *where you look*:

- What is the observable symptom, or the goal? (What happens now vs what should happen.)
- Where does it show up — which command, endpoint, screen, file?
- What does "done" look like, roughly?
- Is anything explicitly out of scope?

Keep it to one `AskUserQuestion` round with 2–4 questions. Give a recommendation on each where
you have one, so the cheap path is confirming rather than composing an answer.

**Skip this gate only when the description already answers all of it** — a well-specified
TODO item sometimes does. Say that you skipped it and why.

Do not ask here what the code will tell you. "Which function handles retries" is not a
scoping question; it is Step 6.

---

## Step 3 — Resolve repositories

Usually one repo: the current working directory's git root. Confirm it and move on.

Resolve more when the problem spans repos — a shared library and its consumers, code and
infrastructure, a tool and the project using it. Prefer existing local checkouts; glob for
them as siblings before proposing a clone.

**Never clone silently.** If a repo has no local checkout, ask: provide a path, clone it, or
exclude it.

Record the resolved path and, where known, the remote for each repo.

---

## Step 3a — Survey open branches and choose the base

Run this for every resolved repo. Discovering at implement time that the work should have been
based on an in-flight branch is expensive; the survey is cheap.

```bash
git -C <repo> fetch --prune
git -C <repo> remote show origin | grep 'HEAD branch'    # detect the default, don't assume
git -C <repo> branch -a --sort=-committerdate \
  --format='%(refname:short) %(committerdate:relative)' | head -30
```

A branch is a **strong candidate** when it touches the same area this work will target
(`git -C <repo> diff --stat origin/<default>...<candidate>`), or is a rebased variant of one
that does.

Vet each candidate before offering it as a base:

- **Not behind default** — `git -C <repo> log --oneline <candidate>..origin/<default>`. Any
  commits listed mean the candidate is missing default-branch work.
- Prefer the variant that is on current default and is the most complete superset.

**The default branch is the base unless proven otherwise.** When there is no overlap, say so
in one line and move on — do not emit an empty branch-strategy table. Only when branching off
the default would not build do you consider an alternative, and **a non-default base requires
explicit `AskUserQuestion` consent** with the genuine options laid out: base off the in-flight
branch and accept the rebase risk, make this work self-contained, or wait for the dependency
to merge.

Record the per-repo base in **Confirmed Assumptions** and **Deployment & Rollout Notes** so
`implement` does not re-derive it. It must still re-verify — a dependency can merge between
investigate and implement.

---

## Step 4 — Load project context

Ground the investigation in the project's own conventions before searching.

- `CLAUDE.md` at the repo root, and any nested `CLAUDE.md` in the areas you will touch
- `README.md`, and `docs/` if present
- `.claude-sandbox/CLAUDE.md` when it exists
- The plugin skills that match the stack — e.g. `goa` for a Goa API, `playwright` for E2E
  tests, `sandbox` for claude-sandbox configuration, `backlog-yaml` where a backlog is in play

State which you are loading and why, in one line each. **Trim to what the problem can actually
use, and give a reason per omission.** A skill that cannot apply is a real context cost, not a
free safety margin.

**Before defining any new convention, look for an existing one.** If the work will introduce a
path, a directory layout, a naming scheme, a branch pattern, or a file format, search for one
already in use before inventing a parallel one — skills routinely define these, and so do
scaffolds, sibling repos, and helper scripts. Grep the skills you loaded, the project's
scaffolding, and the sibling projects for the thing you are about to name.

Nothing errors when you invent a second convention alongside an existing one; it just
fragments the project quietly, and the cost lands on whoever finds both later. Adopting the
existing convention — or extending it — is almost always right. Diverging from one is a
decision to state and justify in the plan, not something to arrive at by not having looked.

---

## Step 5 — Build a search strategy

Build a prioritised list of search terms from the problem:

- **Bugs** — exact strings first: error messages, exception types, stack frames, log lines,
  function names, file paths, endpoints. Then domain terms.
- **Features** — entity names, concepts, API endpoints, component names.
- **Tasks** — component names, config areas, file paths.

When the problem touches anything outside the codebase — hardware, a vendor product, pricing,
a third-party service's behaviour — list the external subjects too: part and model numbers,
board or chip revisions, spec versions, API versions. Step 6d goes and gets them.

**Search for the whole class of issue, not one idiom.** When the problem is a *category* —
insecure randomness, a deprecated call, a missing guard — enumerate every way it can appear
and grep for all of them, not just the project's preferred wrapper. Missing an idiom means
missing an instance.

---

## Step 6 — Explore and read the code

**Delegate context-heavy searching to subagents.** Exploration reads a lot; preserve your
context for synthesis by handing off well-scoped, high-volume work and keeping only the
findings. Good candidates: broad multi-file or multi-repo greps, tracing a call chain,
external research (Step 6d) — reading a vendor manual or sweeping a market for prices is
high-volume and returns a short answer, so it belongs in a subagent. Use `Explore` for
locating code, `general-purpose` for anything that needs to read and reason, and a **fork**
when the sub-task genuinely needs this session's context. **Bring back `file:line` findings
and cited claims, not file dumps.**

Per repo:

**6a — Orientation.** Read `README.md` / `CLAUDE.md`. Glob for build config (`Makefile`,
`go.mod`, `package.json`, `pyproject.toml`, `docker-compose*.yml`) and for structure. Note
what kind of thing the repo is — service, CLI, library, infrastructure — and how it is built,
run, and tested.

**6b — Targeted search.** Exact strings first, then domain terms. Note `file:line` and
surrounding context for each hit.

**6c — Deep read.** Read in full any file with two or more hits. Read its callers, its
imports, and its tests. Follow the call chain both directions. Cap at roughly 20 files per
repo to stay practical.

**Validate by building, not just reading.** Investigation is mostly read-only, but you are
expected to run the repo's own tooling to confirm what the code does and that the approach is
viable — build, test, codegen, lint. This catches what a grep cannot: a generated artifact
that is stale, a test helper that does not exist yet, an interface that does not compile on
the base branch. If a codegen step is required for the change to build, call it out in **Files
to Modify** so the implementer expects it.

**When the plan depends on a low-level nuance of a tool's behaviour, read the tool's source.**
Not for ordinary usage — docs and `--help` are correct and cheaper for that. This is for the
narrow case where the answer turns on precisely *how* something behaves: whether a file is
overwritten or seeded once, whether a step runs on every invocation or only one subcommand,
what exactly gets written where, what happens when it runs twice. Documentation states intent
and rounds off edges; the plan may be resting on an edge.

Applies when the tool's source is reachable — a sibling repo, a vendored dependency, an
installed package. When it is not, say the claim is from documentation and mark it for
`implement` to re-verify. A verified nuance carries `file:line` like any other finding, and
frequently deletes a hazard outright rather than mitigating it.

If a repo yields nothing, record "no relevant code found" and move on.

**6d — External research.** Run this when the plan will rest on a fact the codebase cannot
answer: hardware topology, a vendor's specification, what a part costs or whether it is
obtainable, a third-party service's documented behaviour. Skip it with one line when the
problem is wholly internal.

- **Get the primary.** The manufacturer's manual, datasheet, or spec document; the project's
  own docs; the standards body's PDF. Search results and vendor guides arrive pre-formatted as
  findings and read as authoritative next to something you verified — that is the trap.
- **Reconcile against the live system.** An external fact that contradicts what the machine
  reports is a finding, not a footnote. Prefer the observation and say which source lost.
- Record per the citation rule in `references/investigation-format.md` — it owns how external
  and secondhand claims are written down. Do not restate it here.
- Fetch-blocking is normal, not exceptional, and the workarounds are worth knowing before you
  waste a pass on them: see `references/external-research.md`.

---

## Step 7 — Blast radius

Identify what else the change can reach:

- Callers of any function or type being changed
- Public API: exported symbols, HTTP routes, CLI flags, config keys, event payloads
- Persisted shapes: schemas, migrations, serialized formats, on-disk layouts
- Anything downstream that consumes the above

**For any contract change, verify both ends exist and are wired.** A producer with no consumer
— or a consumer with no producer — is a real failure mode: the feature silently never fires.
Grep both sides.

If the change is genuinely self-contained, **say so explicitly**. A missing Blast Radius reads
as "not checked", not "nothing to report".

---

## Step 8 — Infrastructure and operational scope (conditional)

Run this only when the change plausibly touches deployment, configuration, or runtime
resources. Skip it with one line when it does not.

- New or changed build artifacts, containers, services, scheduled jobs
- Config or environment variables that need to exist somewhere they do not
- Migrations, backfills, or one-off jobs
- Anything needing a manual step at deploy time

**Read the thing that actually defines the deployed state**, not a build file that resembles
it. Build manifests describe how an artifact is produced; they are not the source of truth for
what is running.

---

## Step 9 — Requirements gate (blocking)

This sits **after** exploration on purpose: the code answers many questions on its own, so ask
only what it cannot.

**Do not begin the plan until this gate completes.** Present all three together:

1. **The core problem**, in 1–2 sentences, as you now understand it from the code.
2. **Your assumptions**, as an explicit bullet list — scope boundaries, expected behaviour,
   compatibility expectations, what you are treating as out of scope. Include any **external**
   fact the plan depends on (Step 6d), so a wrong one is caught here rather than after money
   is spent or a migration is half done.
3. **Your open questions** — ambiguities, missing acceptance criteria, edge cases, anything
   Step 7 raised.

Then **wait**.

### This is a loop, and it runs until everything is settled

One round is rarely enough. Each round:

1. Incorporate the answers.
2. Restate any assumption that changed.
3. **Go and answer what the answers made answerable.** An answer routinely opens a question
   the *code* settles, not the user — a newly in-scope subsystem, a constraint that needs
   checking, a convention to find. Return to Steps 4–8 for it. This is the normal shape of the
   gate, not a failure of it: exploration and requirements interleave, and looping back is
   cheaper here than anywhere later.
4. Ask the next round.

**Keep looping until the user confirms there is nothing left to clarify.** Do not proceed on
"probably enough". Stopping early is how an unconfirmed assumption becomes shipped behaviour,
and the whole cost of this skill is paid on the assumption that this gate actually held.

Two practical notes:

- Ask in batches of a few related questions rather than one at a time, and give a
  recommendation with each where you have one.
- Say where you are — "that opens one more thing about X, checking the code now" — so a
  multi-round gate reads as progress rather than stalling.

The triage rule for what may become an Open Question rather than being answered here is in
`references/investigation-format.md`. Apply it now, not after the plan is written.

---

## Step 9a — Measure before choosing (conditional)

**When the plan will offer genuinely-open alternatives, take the cheapest measurement that
discriminates between them — before you recommend one.** Skip with one line when there is only
one viable approach, or when nothing measurable separates the candidates.

Specs and vendor numbers rank options; a measurement on the real system *eliminates* them. The
difference matters most where the alternatives differ by an order of magnitude in cost, because
that is exactly where reasoning from datasheets quietly picks the expensive one.

- **Measure the worst thing you already own.** A floor established on hardware or a
  configuration that is indisputably inferior to every option on the table often settles the
  question outright — if the worst candidate already clears the requirement by a wide margin,
  the differences above it are unobservable and the cheap option wins on evidence.
- **Bound the blast radius.** Measure idle or spare capacity first. Loading a production path
  needs explicit consent, a hard time cap, and a health check straight after — say plainly what
  could break and what it cost last time.
- **Two instruments beat one.** A synthetic benchmark that agrees with the system's own
  telemetry converts a plausible diagnosis into a confirmed one.
- Record the command, the conditions and the number. It goes in the investigation as evidence,
  and it is the baseline `implement` re-runs to prove the change worked.

If the discriminating measurement cannot be taken, say which option the decision rests on and
mark it for `implement` to settle.

---

## Step 10 — Build the plan

Compose the file locally; nothing is written yet. Follow the standard outline, the section
naming (`Root Cause Analysis` / `Proposed Fix` for bugs), and the writing rule in
`references/investigation-format.md`.

All code references carry `file:line`. If no relevant code was found anywhere, say so in
Existing Architecture and suggest where else to look.

---

## Step 11 — Open-question sweep (loop)

The plan exists but **nothing has been written to disk** — the last point where a question is
cheap to close. Step 9 caught what you could anticipate before writing; this catches what the
concrete plan surfaced, which is usually more and sharper.

**1. Sweep your own draft.** Look for hedged language ("likely", "presumably", "should be",
"may need"), any claim with no `file:line` or command behind it, a choice left implicit, a
section written thinly because you did not know, and anything already sitting in Open
Questions. Each is a candidate.

**2. Classify every candidate:**

| Class | Test | Handling |
|---|---|---|
| **Agent-verifiable** | The answer exists somewhere reachable — code, `git`, a config, a running system, docs | Batch into one background agent (step 3) |
| **User decision** | An opinion, a scope call, a preference. "Should we also…", "is X in scope", "which behaviour" | `AskUserQuestion` (step 4) |
| **External / blocked** | Depends on someone else's decision, or a system you cannot reach | Straight to Open Questions, with owner and blocks-or-not |

A question that is both — verifiable in principle, but only matters given a decision — goes to
the user first. Do not verify a branch that may be discarded.

**3. Launch ONE background agent for the verifiable batch — first**, so it works while the
user reads. One agent for the whole batch, not one per question; the point is to keep
high-volume tool output out of your context and return only findings. Use a fresh
`general-purpose` agent with a self-contained brief: the questions, the repo paths and their
SHAs, and what counts as verified (a command's output, a `file:line`, a doc quote). Require it
to report **answer / evidence / confidence** per question, and to say "could not determine"
rather than guess. Tell it to flag any *new* uncertainty it finds.

**4. Meanwhile, ask the user the decision-class questions.** Every one carries a defer option,
worded:

> **Leave open and record in the investigation** — defer this; it will be listed under Open
> Questions with its owner and whether it blocks implementation.

Deferring is one click, never a negotiation. Some questions genuinely need data nobody has
yet, and forcing an answer produces a worse record than an honest Open Question.

**5. Fold in and loop.** Verified facts become findings **with their evidence**; decisions
become **Confirmed Assumptions**; deferred and external items become **Open Questions** with
owner and blocks-or-not. If either source produced a *new* question, run another round —
verification frequently reveals a second-order question. **Stop** when a round yields nothing
new, or when everything remaining is deferred or external.

Report the outcome in one line at the Step 12 gate — e.g. *"Sweep: 5 candidates → 2 verified,
2 decided by you, 1 deferred."* — so the reviewer can see the section was earned.

---

## Step 12 — Review gate

Present the full plan and pause. Nothing has been written yet.

Display the plan, then output this **verbatim**:

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

**Discuss** → free-form: answer questions, incorporate corrections, update the plan. After
each exchange re-display the **full updated plan**, then:

```
---
Ready to save, continue discussing, or reject? (1 = Save / 2 = Discuss / 3 = Reject)
---
```

Loop until Save or Reject.

**Reject** → print `Investigation cancelled. Nothing was written.` and stop. Do not proceed to
any further step.

---

## Step 13 — Write the investigation

```bash
mkdir -p .claude-sandbox/investigations/<slug>
ls .claude-sandbox/investigations/<slug>/          # confirm the next free serial
```

Determine the serial from what is already there — the highest existing `NN` plus one, `00` for
a new series. **Never reuse a serial and never overwrite a file.** If a file at your intended
serial exists, you misread the directory; re-read it.

Write `NN_<name>.md` with the Write tool, per the outline in
`references/investigation-format.md`. On `01`+, the `Supersedes` block is the first section
after the heading and is never omitted.

---

## Step 14 — Rewrite the index

Regenerate `INDEX.md` wholesale from the composition of all serials — structure, provenance
line, TOC table and status values are canonical in `references/investigation-format.md`.

Capture the provenance SHAs now:

```bash
git -C <repo> rev-parse --short HEAD
```

Add a TOC row for the new file with status `pending`. Leave existing rows' Status and Branches
untouched, except to set `superseded by NN` on any row this pass supersedes. The reconciled
sections reflect the state after **all** passes, not a copy of the new file's sections.

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

Next: /implement <slug>
```

---

## Step 16 — Retrospective (optional, user-gated)

Offer a lightweight retrospective so the skills improve from real use:

```text
Run a quick retrospective on this investigate run and update the skill docs?
* Yes — capture stumbles, gotchas, and undocumented steps, then update the skills
* No — skip
```

If **Yes**: note where the run hit friction — a missed search idiom, an undocumented step, a
wrong assumption — then **read and follow `update-kit`'s SKILL.md**. It owns the mechanics:
locating the real checkout rather than the plugin cache, settling the branch, the staleness
check, and the context-cost bar for what earns a place in a skill. Do not re-derive any of
that here.

`update-kit` is `disable-model-invocation: true`, so it is **user-invoked only and cannot be
called through the Skill tool** — open its `SKILL.md` from the `claude-plugins` checkout and
follow it directly.

The likely targets are this skill, `investigation-format.md`, and any project skill whose gap
cost you time during the run.

---

## Edge Cases

- **No argument and nothing in the conversation to anchor on** — ask for an observable symptom,
  a component, or a goal. Do not guess a problem.
- **Description is thin** — expected. Step 2 fills it in. Only stop when there is nothing to
  anchor on at all.
- **`TODO.md` does not exist** — say so, treat the argument as ad hoc text, do not create it.
- **Slug already exists** — re-investigation. Read the whole series first, confirm intent, then
  write the *next* serial. Never edit an existing file.
- **`.claude-sandbox/` not scaffolded** — warn once, continue, recommend `claude-sandbox init`.
  Never create `.claude-sandbox/CLAUDE.md`.
- **Repo has no local checkout** — ask: path, clone, or exclude. Never clone silently.
- **Branch survey finds nothing** — one line saying every repo bases off its default. No empty
  table.
- **A non-default base looks right** — explicit `AskUserQuestion` consent, never silent.
- **Requirements gate unresolved** — do not build the plan. Loop until the user confirms.
- **An answer at the gate opens a question the code can settle** — go back to Steps 4–8 and
  settle it, then resume the gate. Interleaving is expected.
- **A path the user names does not exist** — inside a claude-sandbox container only the project
  and configured mounts are visible, and a symlinked host path appears elsewhere. Check the
  `mounts:` cascade before reporting it unreachable; the `sandbox` skill has the procedure.
- **Tempted to write an Open Question** — triage it first
  (`references/investigation-format.md`). Verifiable → verify it. Requirement → ask at Step 9.
- **Background agent returns "could not determine"** — that becomes an Open Question, or a user
  question if a decision would settle it. Never promote a guess to a finding.
- **User defers every question** — legitimate. Record each with owner and blocks-or-not, and
  do not re-ask on the next loop iteration.
- **Sweep finds no candidates** — say so in one line at the gate and move on.
- **No relevant code found anywhere** — still write the plan; say so in Existing Architecture
  and suggest where else to look.
- **User rejects at the gate** — nothing written. Confirm that to the user.
- **Problem turns out to be several problems** — say so, and propose one series each rather
  than one plan covering all of them. Cross-reference the sibling slugs in each Out of Scope.

---

## Quality Criteria

- The scoping gate ran before exploration, or its omission was stated and justified.
- Project context is loaded before searching, trimmed to what applies, with a reason per
  omission.
- Context-heavy exploration was delegated to subagents; `file:line` findings came back, not
  file dumps.
- Claims about what the code does are backed by having run the build or tests, not by reading
  alone, wherever running was possible.
- Where the plan rests on a low-level nuance of a tool's behaviour, the tool's **source** was
  read and cited — or the claim is marked as documentation-only for `implement` to re-verify.
- Where it rests on a fact outside the codebase, the **primary** source was opened and cited,
  or the claim is marked secondhand; and any such fact contradicted by the live system was
  reconciled rather than left standing.
- Where the plan offered genuinely-open alternatives, a discriminating measurement was taken
  before one was recommended — or its absence is stated and the dependent choice flagged.
- Any new convention the work introduces was checked against existing ones first; adopting an
  existing convention is the default, and diverging is stated and justified in the plan.
- The requirements gate **blocked** the plan and looped until the user confirmed there was
  nothing left — including looping back to exploration when an answer opened a question the
  code could settle.
- The sweep ran against the drafted plan before anything was written: candidates classified,
  the verifiable batch in **one** background agent launched *before* the `AskUserQuestion`,
  a defer option on every user question, looping until a round produced nothing new. Its
  outcome is reported at the gate.
- Open Questions contain **only** genuinely external or blocked items, each naming an owner
  and whether it blocks implementation.
- Findings cite `file:line`, and are flagged as point-in-time.
- Blast radius is assessed and stated — including an explicit "self-contained" when it is.
- The file follows the standard outline and the writing rule, and carries a concrete
  **Proposed Fix** or **Implementation Approach**.
- Serials are append-only: a re-investigation writes the next serial with a `Supersedes` block
  and edits nothing.
- `INDEX.md` was rewritten wholesale with a provenance line carrying per-repo SHAs.
- The review gate fired before anything was written to disk.
