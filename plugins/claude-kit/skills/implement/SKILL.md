---
name: implement
description: Implement an investigation produced by the investigate skill — read the whole series from .claude-sandbox/investigations/<slug>/, triage its open questions, plan the work, build it (in isolated git worktrees when the plan fans out), verify with the project's own tests, then record the outcome and update the docs. Use when the user says "implement", "build the plan", "do the investigation", "carry out <slug>", or asks to act on a completed investigation.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, TaskCreate, TaskUpdate, TaskGet, TaskList, AskUserQuestion
argument-hint: <investigation-slug>
---

# Implement

Take an investigation through to working, verified code.

The record format — layout, serials, `Supersedes`, `INDEX.md`, the standard outline, the
writing rule, verification tiers — is canonical in the `investigate` skill's
`references/investigation-format.md`. **Read it before reading or writing any investigation
file.** This file does not restate those rules.

Worktree isolation, fan-out criteria, dispatch and consolidation are in
`references/worktree-orchestration.md`. Read it before fanning out.

## Usage

`/implement <investigation-slug>`

Examples:

- `/implement flaky-upload-retry`
- `/implement` — no argument; resolve the series from the conversation, or list what is
  available

---

## Step 1 — Resolve the series

The argument is a slug under `.claude-sandbox/investigations/`.

```bash
ls .claude-sandbox/investigations/
```

**No argument**: if the conversation just produced an investigation, use that slug. Otherwise
list the available series with their INDEX.md status lines and ask which.

**No match**: stop.

> `Error: No investigation series '<slug>'. Run /investigate first, or pick from: <list>`

**Nothing at all in `.claude-sandbox/investigations/`**: stop.

> `Error: No investigations found. Run /investigate <description> first.`

---

## Step 2 — Read the whole series

**Read every `NN_*.md` in serial order, lowest to highest, applying each `Supersedes` block as
you go.** The composition of all files, in order, is the plan. Read `INDEX.md` first for
orientation, but it is a summary and **never a substitute for the files**.

This is not optional and it is not a skim. A run that reads only the index, or only the newest
serial, will implement superseded decisions.

Extract:

- Root cause or analysis
- **Proposed Fix / Implementation Approach** — required
- Files to modify, with their `file:line` citations
- Patterns to follow
- Blast radius
- Risk assessment
- Base branch per repo, from Confirmed Assumptions / Deployment & Rollout Notes
- Open questions, honouring every `Supersedes` — a question a later pass closed is not open,
  and re-asking it signals you did not read the record
- The **provenance SHAs** from the index, which say what each citation was true at

Stop if the composed plan has **no Proposed Fix or Implementation Approach**:

> `Error: The investigation on '<slug>' has no proposed fix or implementation approach. Run /investigate <slug> to complete it.`

---

## Step 3 — Triage open questions

An investigation ships with open questions by design. **Implementing while they sit untouched
is how a known unknown becomes a shipped assumption.**

**1. Re-check staleness first — this is implement's advantage over investigate.** Time has
passed; some questions have answered themselves. Before asking the user anything:

- A dependency may have merged, a resource may now exist, a config may have changed. Re-verify
  anything the plan recorded as pending.
- The provenance SHAs settle code questions cheaply:
  `git -C <repo> log --oneline <sha>..HEAD` scopes the check to what actually moved.

A question you can close from evidence is not a question. Close it and record what closed it.

**2. Classify what remains** — agent-verifiable / user decision / external-blocked, the same
taxonomy as `investigate`.

**3. Launch ONE background `general-purpose` agent for the verifiable batch — now**, before
Steps 4–6. That work is genuine dead time for verification, so the answers are usually back by
the review gate. Self-contained brief: the questions, repo paths, SHAs, and what counts as
verified. It must report **answer / evidence / confidence**, and say "could not determine"
rather than guess.

**4. Blockers must be resolved or explicitly waived before Step 7.** The investigation states
per question whether it blocks. Honour it: never start writing code with an unresolved
blocker. If a question carries no blocks-or-not marking, decide yourself whether the
implementation can be correct without it, and **say which way you called it**.

**5. Decision-class questions go to the review gate** (Step 6), not a second gate of their own.

---

## Step 4 — Resolve repos and re-verify the base branch

Resolve the repos named in the plan. Ask for a path or a clone URL for anything unresolved;
never clone silently.

**Honour the base branch the investigation recorded — then re-verify it.** The picture moves
between investigate and implement:

```bash
git -C <repo> fetch --prune
git -C <repo> remote show origin | grep 'HEAD branch'          # detect, don't assume
git -C <repo> log --oneline <recorded-base>..origin/<default>  # has the dependency merged?
```

If the recorded non-default base is no longer the right choice, say so and get agreement
before deviating. Adopting a non-default base the investigation did *not* record needs the
same explicit consent `investigate` requires.

Branch naming and worktree layout are in `references/worktree-orchestration.md`. The
integration branch is the bare slug.

---

## Step 5 — Plan the work and check for drift

**Reconcile the plan against current code first.** The investigation may be days old. Re-verify
every `file:line` citation against current `HEAD`. Use the provenance SHAs to scope it rather
than re-reading everything. Record any drift: a fix that already landed, a function that moved,
a file that no longer exists.

Then decompose the approach into tasks and identify which are genuinely independent — the
dependency-aware plan that the fan-out decision rests on. Read
`references/worktree-orchestration.md` and decide **inline or fan-out**, stating which and why.

Establish the verification commands now, not after writing code: the repo's test target, its
build/typecheck, its lint. Record which **verification tier** they represent (the table is in
`investigation-format.md`). If the best available tier is 3 or 4, say so here — it changes what
"done" can mean and it rules out fan-out.

---

## Step 6 — Review gate 1: the plan

Present:

1. **The composed plan** — approach, files to modify, patterns, risks — and that you read the
   full series.
2. **Drift findings** from Step 5, or "no drift".
3. **Task breakdown**, and whether you will work inline or fan out, with the reason.
4. **Branch strategy per repo**, including whether the recorded base still holds.
5. **Verification plan** — the exact commands, and the tier they reach.
6. **Open-question status** — what staleness closed, what the background agent verified with
   evidence, what still **blocks**, and what you need decided now.

**Ask the decision-class questions here**, via `AskUserQuestion`, each with the defer option:

> **Leave open and record in the investigation** — defer this; it stays under Open Questions
> with its owner and whether it blocks implementation.

A blocking question's defer option must say plainly that deferring means **not implementing
yet**. That is a legitimate outcome, never a slip.

Then output **verbatim**:

```
---
**Review: implementation plan**

1. **Proceed** — approve and begin implementation
2. **Discuss** — talk through the plan first
3. **Reject** — cancel, nothing will be changed

Reply with 1, 2, or 3.
---
```

**Discuss** → free-form, then re-display the full plan and re-prompt. Loop until Proceed or
Reject.

**Reject** → print `Implementation cancelled. No changes have been made.` and stop.

Do not proceed with an unresolved **blocking** question. If the user defers a blocker,
implementation waits — say so rather than continuing.

---

## Step 7 — Implement

**If the plan changed materially at the gate**, ask whether to record the revision:

```text
The plan changed at the review gate. Record the revision on the investigation?
* Yes — write the next serial with a Supersedes block naming what the gate overturned
* No — carry it into the outcome file instead
```

Material re-planning is a new investigation pass: invoke the `investigate` skill so it writes
the next serial and rewrites the index. `investigate` owns that format. A minor correction can
wait for the outcome file in Step 10.

**Before writing code**, load the project's conventions — root and nested `CLAUDE.md`, and the
plugin skills matching the stack. The investigation names the patterns to follow; the project
docs say how the code is actually written.

**Inline** (the default): create the branch off the verified base, work the tasks in dependency
order in the main checkout, running the verification as you go.

```bash
git -C <repo> fetch origin
git -C <repo> checkout -b <slug> origin/<base>
```

Immediately after checkout, regenerate anything checked in that the base may carry stale
(codegen, mocks, generated clients). A no-op diff means the artifacts were correct; a diff
means the base shipped stale ones — reconcile before proceeding.

**Fan-out**: follow `references/worktree-orchestration.md` — worktree per task, vanilla
`general-purpose` subagents, dependency-ordered dispatch, test-gated merge, full verification
re-run after **every** merge.

In both modes:

- Read each file to modify **in full** before changing it.
- Make only the changes the approach describes. Do not refactor unrelated code.
- Add the tests the plan calls for.
- **Delegate context-heavy work to subagents** — long logs, broad exploration, mechanical
  fan-out edits across many files. Keep your context for the plan and the diff.
- **If you find an in-scope issue the investigation missed** — another instance of the same
  bug class, say — do **not** silently expand scope and do **not** silently ignore it. Surface
  it via `AskUserQuestion` and let the user decide whether it belongs in this run.

---

## Step 8 — Verify

Run the verification established at Step 5 and record the results honestly.

**State the tier you actually reached.** Reporting "tests pass" when only the build ran is the
specific failure the tier table exists to prevent. If the tests do not exist, say the tier is
build-only — do not imply behavioural coverage you do not have.

Where the plan calls for it and the project supports it, exercise the change by running the
app — the `run` skill knows how to launch this project.

**Do not defer a verification step just because it needs a human action.** If a step is blocked
because a person must do something first — seed a record, flip a setting, provide a
credential — surface the concrete task, ask the user to do it, and finish the verification in
this run. Reserve "manual, deferred" for steps genuinely undriveable from here, and record
those explicitly rather than silently.

Record: command, outcome, and what it does **not** cover.

---

## Step 9 — Review gate 2: the diff

Present:

1. `git diff` per repo — all changes
2. Verification results, with the tier reached and its gaps

**If verification passed at the planned tier**, output **verbatim**:

```
---
**Review: implementation diff**

1. **Approve** — finalize the work
2. **Discuss** — request changes first
3. **Reject** — discard all changes and stop

Reply with 1, 2, or 3.
---
```

**If verification failed or could not be completed**, output this instead — Approve must not be
offered:

```
---
**Review: implementation diff**

⚠️ Verification is failing or incomplete. Approve is not available until it passes.

2. **Discuss** — resolve the failures
3. **Reject** — discard all changes and stop

Reply with 2 or 3.
---
```

**Discuss** → make the changes, re-verify, re-display the diff and results, re-prompt with the
appropriate menu. Loop until Approve or Reject.

**Reject** → discard uncommitted changes, remove any worktrees, delete the branches, print
`Changes discarded. Nothing was committed.`, and stop.

---

## Step 10 — Finalize

### 10a — Terminal action

Ask which, via `AskUserQuestion`:

```text
How should this land?
* Merge to base, stop before push — worktrees removed, branches merged locally, nothing leaves this machine
* Merge, commit, and push the branch — also pushes to origin, no PR
* Something else — tell me what
```

Then do exactly that and no more. Do not push, tag, or open anything the user did not choose.

Commit hygiene:

- Stage specific files. Never `git add .` or `git add -A`.
- Message format `<verb>: <aspect> - <description>`, verb one of `added`, `updated`, `removed`,
  `bumped`. One such entry per line for a commit spanning distinct changes.
- Write multi-line messages to a temp file and use `git commit -F <file>`. Never HEREDOC or
  `$()` in git commands.

### 10b — Write the outcome

Write `NN_implementation.md` at the next free serial, per the outcome outline in the
`investigate` skill's `references/investigation-format.md`. Its `Supersedes` block names each
plan statement the build overturned, or `Nothing — the plan held`.

Capture: decisions locked at the gates, deviations from the plan (including files that turned
out to be no-ops), the verification outcome **with its tier**, any new analysis the run
produced, the branches delivered, and follow-ups spun out.

Skip this file only when the run produced nothing worth recording — the plan held exactly and
there were no gate decisions. **Say so in the report when you skip it.**

### 10c — Rewrite the index

Regenerate `INDEX.md` wholesale:

- Set each implemented row's Status to `implemented <YYYY-MM-DD>` and fill its Branches column.
  Rows that needed no code get `no code`; rows a later serial invalidated get `superseded by NN`.
- Add the TOC row for the outcome file.
- Refresh the reconciled sections — Deployment & Rollout Notes especially, since deploy reality
  is now known. Update the provenance line to the SHAs actually delivered against.
- **Revisit every deferred question — this is where answers are most likely to exist.**
  Building the change answers questions that reading the plan could not. For each: did the
  implementation settle it? Has anything changed externally? Close what you can, recording the
  evidence in the outcome file, and drop it from the index's Open Questions. Bring the still-open
  ones back to the user once, briefly, with the same defer option. A question deferred twice
  with no movement belongs on its own investigation — offer to spin it out.

  Open Questions must end up listing **only** what is genuinely still unresolved.

### 10d — Documentation follow-ups

Derive the documentation the change requires and apply it — this replaces the release/change-
management step it was adapted from, and it is part of the work, not an afterthought:

- `CHANGELOG.md` — an entry, if the project keeps one, in its existing style
- `README.md` — when behaviour, flags, config, or setup changed
- `docs/*` — when the change contradicts something written there
- Inline docs — package docs, help text, comments that the change made wrong

Present what you propose to update and what you are skipping, with reasons, then apply. A doc
the change made **wrong** is a defect; do not leave it for later.

---

## Step 11 — Report

```
## implement complete

**Series:** <slug>
**Repos:** <repo> @ <sha>
**Mode:** <inline | fan-out: N tasks across N worktrees>
**Branches:** <branch> (<merged | pushed | local>)
**Verification:** tier <N> — <command> — <result>. Not covered: <...>
**Outcome:** .claude-sandbox/investigations/<slug>/NN_implementation.md (or: skipped — plan held exactly)
**Index:** updated — <N> implemented, <M> open questions
**Docs:** <files updated, or "none needed">
**Follow-ups:** <spun out, or "none">
```

---

## Step 12 — Retrospective (optional, user-gated)

```text
Run a quick retrospective on this implement run and update the skill docs?
* Yes — capture stumbles, gotchas, and undocumented steps, then update the skills
* No — skip
```

If **Yes**: note where the run deviated from these steps or hit friction — an undocumented
workflow, a wrong assumption, a gotcha that cost time — then **invoke the `update-kit` skill
and follow it**. It owns locating the real checkout rather than the plugin cache, settling the
branch, the staleness check, and the bar for what earns a place in a skill. Do not re-derive
any of that here.

Likely targets: this skill, `worktree-orchestration.md`, `investigation-format.md`, and any
project skill whose gap cost you time.

---

## Edge Cases

- **No slug given** — use the series the conversation just produced, else list what exists and
  ask. Never guess.
- **Slug not found / no investigations at all** — stop with the error in Step 1.
- **No Proposed Fix in the composed plan** — stop; point at `/investigate <slug>`.
- **Only `INDEX.md` was read** — a bug in the run, not a shortcut. Read the serials.
- **A `Supersedes` block names a file that does not exist** — the series is inconsistent.
  Report it and ask before proceeding; do not silently pick an interpretation.
- **An open question is marked blocking** — resolve or explicitly waive before Step 7. If the
  user defers a blocker, implementation waits.
- **A question carries no blocks-or-not marking** — decide yourself and state which way you
  called it.
- **A deferred question is answerable by the end of the build** — close it at Step 10c with its
  evidence. A resolved question must not survive into the record.
- **A question deferred twice with no movement** — offer to spin it onto its own investigation.
- **The recorded base branch has merged** — say so and get agreement before switching to the
  default.
- **Code drifted since the investigation** — record the drift, present it at gate 1, let the
  user decide whether the plan still holds.
- **An in-scope issue the investigation missed** — surface via `AskUserQuestion`. Never
  silently expand or silently ignore.
- **The project has no tests** — verification is build-only or run-only. State the tier, and do
  not fan out (the merge gate is missing).
- **Fan-out merge goes red** — stop merging. Report which task broke it and what you tried.
- **A worktree has uncommitted changes at cleanup** — never remove it automatically. Surface it
  and ask.
- **Two worktrees need docker compose and the project has no scoping variable** — serialize
  those tasks; do not run compose concurrently.
- **Verification blocked on a human action** — ask the user to do it and finish the check in
  this run. Do not mark it deferred for convenience.
- **User rejects at gate 1** — nothing changed, clean stop.
- **User rejects at gate 2** — discard changes, remove worktrees, delete branches, clean stop.

---

## Quality Criteria

- **The entire series was read in serial order with every `Supersedes` applied** before any
  code was written, and again after any pause.
- Open questions were triaged before code: staleness re-checked first, the verifiable batch in
  **one** background agent launched before Steps 4–6, decisions asked at gate 1 with a defer
  option, and **no blocking question left unresolved** at Step 7.
- Deferred questions were revisited at Step 10c and closed where the build answered them.
- The recorded base branch was re-verified, not trusted blindly; a non-default base was never
  adopted without explicit consent.
- `file:line` citations were re-verified against current `HEAD`, scoped by the provenance SHAs.
- Fan-out happened only with three or more independent tasks **and** a working merge gate;
  otherwise the work was inline, and the choice was stated.
- Every worktree merge was gated on that task's verification, and the **full** verification was
  re-run on the integration branch after each merge.
- **The verification tier reached is stated explicitly**, with its command and its gaps. A lower
  tier is never reported as a higher one.
- Both review gates fired before any commit, push, or write to the investigation record.
- Files were staged specifically; commit messages follow `<verb>: <aspect> - <description>`.
- The terminal action is exactly what the user chose — nothing pushed, tagged, or opened beyond
  it.
- The outcome file was written at the next free serial with a `Supersedes` block, and existing
  serials were neither edited nor deleted.
- `INDEX.md` was rewritten wholesale, with no row left `pending` that was actually implemented.
- Documentation the change made wrong was fixed, not deferred.
- Worktrees were cleaned up, or their retention was reported with a reason.
