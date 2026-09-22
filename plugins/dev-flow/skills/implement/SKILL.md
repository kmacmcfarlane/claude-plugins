---
name: implement
description: Implement an investigation produced by the investigate skill — read the whole series from .claude-sandbox/investigations/{slug}/, triage its open questions, plan the work, build it (in isolated git worktrees when the plan fans out), verify with the project's own tests, then record the outcome and update the docs. Use when the user says "implement", "build the plan", "do the investigation", "carry out {slug}", or asks to act on a completed investigation.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, TaskCreate, TaskUpdate, TaskGet, TaskList, AskUserQuestion
argument-hint: "<investigation-slug>"
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

`/implement <investigation-slug>` — e.g. `/implement flaky-upload-retry`. With no argument,
resolve the series from the conversation, or list what is available.

---

## Step 1 — Resolve the series

The argument is a slug under `.claude-sandbox/investigations/` (`ls` it).

**No argument**: if the conversation just produced an investigation, use that slug. Otherwise
list the available series with their INDEX.md status lines and ask which. Never guess.

**No match**: stop.

> `Error: No investigation series '<slug>'. Run /investigate first, or pick from: <list>`

**Nothing at all in `.claude-sandbox/investigations/`**: stop.

> `Error: No investigations found. Run /investigate <description> first.`

---

## Step 2 — Read the whole series

**Read every `NN_*.md` in serial order, lowest to highest, applying each `Supersedes` block as
you go.** The composition of all files, in order, is the plan. Read `INDEX.md` first for
orientation, but it is a summary and **never a substitute for the files**. This is not a skim:
a run that reads only the index, or only the newest serial, implements superseded decisions.

Extract: the root cause or analysis; the **Proposed Fix / Implementation Approach**
(required); files to modify with their `file:line` citations; patterns to follow; blast
radius; risks; the base branch per repo (Confirmed Assumptions / Deployment & Rollout Notes);
the open questions, honouring every `Supersedes` — a question a later pass closed is not open,
and re-asking it shows you did not read the record; and the index's **provenance SHAs**, which
say what each citation was true at.

A series whose conclusion is a **Recommendation** not to write code is complete, not
defective: land whatever it does call for — usually the documentation recording why — and set
the row to `no code`.

Stop if the composed plan has **no Proposed Fix, Implementation Approach or Recommendation**:

> `Error: The investigation on '<slug>' has no proposed fix or implementation approach. Run /investigate <slug> to complete it.`

---

## Running non-interactively

When the invocation says to run without stopping, the gates change form rather than
vanishing. **Read `references/run-modes.md` § Running non-interactively before Step 2**; in
short: gate 1 (Step 6) is decided by you, each decision recorded under **Confirmed
Assumptions** as overturnable; gate 2 approves only on a passing verification at the planned
tier — failing or incomplete is still a stop, the work left uncommitted; 10a does the least
irreversible thing authorised (commit locally, leave the push); at Step 4 the recorded base
holds, and leaving it, adopting an unrecorded non-default base or meeting an unresolved repo
is a blocking stop, never a silent clone; at Step 7 a plan revision takes the least
irreversible choice under Confirmed Assumptions and a missed in-scope issue becomes a
non-blocking **Open Question**; at Step 8 a step needing human action is manual, deferred, so
gate 2's stop applies. A **blocking** open question still blocks. Report every recorded
decision together at the end.

---

## Running under an orchestrator

When another skill dispatches this one as a sub-agent (`dev-cycle`'s implementer, a
`deep-investigation` POC break-out), the orchestrator owns git, landing, the work item and
every dialog. It gives the **series** (a directory, anywhere, or a single plan file), the
**worktree** and the **base**, and its brief sets the commit. **Read
`references/run-modes.md` § Running under an orchestrator before Step 2**: it lists the
changes step by step, and the return shape. In short: run non-interactively; skip Step 1 and
Step 4 (no fetch, branch or worktree — every edit in the given worktree); gate decisions go
under DEVIATIONS; Step 7 is inline only — no fan-out, no merge — after regenerating stale
checked-in artifacts; a verification step gated on a human is committed around and listed
under COULD NOT DO, while a failing one is still a stop; of Step 10 only 10d runs, inside the
change; no report, no retro; never `AskUserQuestion`. Return STATUS, CHANGED, VERIFIED,
DEVIATIONS, COULD NOT DO, OPEN QUESTIONS (a brief that adds fields wins).

---

## Step 3 — Triage open questions

An investigation ships with open questions by design. Triage them before any code.

**1. Re-check staleness first — implement's advantage over investigate.** Time has passed and
some questions have answered themselves: a dependency merged, a resource now exists, a config
changed. Before asking the user anything, re-verify whatever the plan recorded as pending; the
provenance SHAs scope code questions cheaply (`git -C <repo> log --oneline <sha>..HEAD`). A
question you can close from evidence is not a question — close it and record what closed it.

**2. Classify what remains** — agent-verifiable / user decision / external-blocked, the same
taxonomy as `investigate`.

**3. Launch ONE background `general-purpose` agent for the verifiable batch — now**, before
Steps 4–6, so its answers are back by the gate. Brief it
self-contained: the questions, repo paths, SHAs, what counts as verified. It reports **answer /
evidence / confidence**, and says "could not determine" rather than guess. When `investigate`
already closed everything, skip it and say so.

**4. Blockers must be resolved or explicitly waived before Step 7.** Honour the investigation's
per-question blocks-or-not marking; never write code with an unresolved blocker. A question
with no marking: decide whether the implementation can be correct without it, and **say which
way you called it**.

**5. Decision-class questions go to the review gate** (Step 6), not a gate of their own.

---

## Step 4 — Resolve repos and re-verify the base branch

Resolve the plan's repos; ask for a path or clone URL for any unresolved — never clone
silently.

**Honour the base branch the investigation recorded — then re-verify it:**

```bash
git -C <repo> fetch --prune
git -C <repo> remote show origin | grep 'HEAD branch'          # detect, don't assume
git -C <repo> log --oneline <recorded-base>..origin/<default>  # has the dependency merged?
```

If the recorded non-default base is no longer right, say so and get agreement before
deviating. Adopting a non-default base the investigation did *not* record needs the same
explicit consent `investigate` requires. Branch naming and worktree layout are in
`references/worktree-orchestration.md`; the integration branch is `worktree-<slug>`.

---

## Step 5 — Plan the work and check for drift

**Reconcile the plan against current code first.** Re-verify every `file:line` citation
against current `HEAD`, scoped by the provenance SHAs rather than re-reading everything.
Record any drift — a fix that already landed, a function that moved, a file that is gone — for
gate 1, where the user decides whether the plan still holds.

Then decompose the approach into tasks and identify which are genuinely independent. Read
`references/worktree-orchestration.md` and decide **inline or fan-out**, stating which and why.

Establish the verification commands now, not after writing code: the repo's test target,
build/typecheck and lint. Record the **verification tier** they represent (the table is in
`investigation-format.md`). If the best available tier is 3 or 4, say so here — it changes
what "done" can mean, and it rules out fan-out.

---

## Step 6 — Review gate 1: the plan

**If there are decision-class questions, ask them first**, per the `investigate` skill's §
Asking at a gate — a numbered list answered free-form while scope is open, `AskUserQuestion`
for a closed choice late in the task. Each carries the evidence and the recommendation it rests
on. End the turn there. Keep the defer option either way:

> **Leave open and record in the investigation** — defer this; it stays under Open Questions
> with its owner and whether it blocks implementation.

A blocking question's defer option must say plainly that deferring means **not implementing
yet** — a legitimate outcome, never a slip.

**With none, go straight to the plan.** Once each decision question is answered or
deferred, present:

1. **The composed plan** — approach, files, patterns, risks — and that you read the full
   series.
2. **Drift findings** from Step 5, or "no drift".
3. **Task breakdown**, inline or fan-out, with the reason.
4. **Branch strategy per repo**, including whether the recorded base still holds.
5. **Verification plan** — the exact commands and the tier they reach.
6. **Open-question status** — what staleness closed, what the background agent verified with
   evidence, what still **blocks**, and how each decision question was resolved.

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

Material re-planning is a new investigation pass: invoke the `investigate` skill, which owns
the format, to write the next serial and rewrite the index. A minor correction can wait for the
outcome file in Step 10.

**Before writing code**, load the project's conventions — root and nested `CLAUDE.md`, and the
plugin skills matching the stack.

**Inline** (the default): create the integration branch off the verified base in the main
checkout, then work the tasks in dependency order in the session's own worktree
(`EnterWorktree`, no per-task fan-out), verifying as you go; from the main checkout, merge the
worktree's branch into `worktree-<slug>` when done.

```bash
git -C <repo> fetch origin
git -C <repo> checkout -b worktree-<slug> origin/<base>
```

Immediately after entering the worktree, regenerate anything checked in that the base may
carry stale (codegen, mocks, generated clients). No diff means the artifacts were correct; a
diff means the base shipped stale ones — reconcile before proceeding.

**Fan-out**: follow `references/worktree-orchestration.md` — worktree per task, vanilla
`general-purpose` subagents, dependency-ordered dispatch, test-gated merge, full verification
re-run after **every** merge.

In both modes:

- Read each file to modify **in full** before changing it.
- Make only the changes the approach describes; no unrelated refactors. Add the tests the plan
  calls for.
- **Delegate context-heavy work to subagents** — long logs, broad exploration, mechanical
  edits across many files. Keep your context for the plan and the diff.
- **An in-scope issue the investigation missed** is neither silently fixed nor silently
  ignored: surface it via `AskUserQuestion` and let the user decide whether it belongs here.

---

## Step 8 — Verify

Run the verification established at Step 5 and record the results honestly.

**State the tier you actually reached** — "tests pass" when only the build ran is the failure
the tier table exists to prevent; with no tests the tier is build-only — do not imply
behavioural coverage you do not have. Where the plan calls for it and the project supports it,
exercise the change by running the app (the `run` skill knows how).

**Do not defer a verification step just because it needs a human action.** When a person must
do something first — seed a record, flip a setting, provide a credential — surface the concrete
task, ask the user to do it, and finish the verification in this run. Reserve "manual,
deferred" for steps genuinely undriveable from here, and record those explicitly.

Record: command, outcome, and what it does **not** cover.

---

## Step 9 — Review gate 2: the diff

Present `git diff` per repo — all changes — and the verification results, with the tier
reached and its gaps.

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
  `bumped`, `fixed`. One such entry per line for a commit spanning distinct changes.
- Write multi-line messages to a temp file and use `git commit -F <file>`. Never HEREDOC or
  `$()` in git commands.

### 10a½ — Update the work item

When the repo has a work-item store (`.work/` or `.claude-sandbox/work/`) and this run
implements a claimed item: `wi done <id> --note <sha-or-branch>` on completion, or
`wi handoff <id> --doing … --next …` when the run ends with the item still open. A repo
without a store: skip silently. This is the only step that closes an item — nothing else does.

### 10b — Write the outcome

Write `NN_implementation.md` at the next free serial, per the outcome outline in the
`investigate` skill's `references/investigation-format.md`, with a `Supersedes` block naming
each plan statement the build overturned, or `Nothing — the plan held`. What it captures is in
`references/finalize.md` § 10b. Skip it only when the plan held exactly and there were no gate
decisions — and **say so in the report**.

### 10c — Rewrite the index

Regenerate `INDEX.md` wholesale — row statuses (`implemented <YYYY-MM-DD>` with Branches,
`no code`, `superseded by NN`), the outcome's TOC row, the reconciled sections, the provenance
SHAs delivered against — per `references/finalize.md` § 10c. **Revisit every deferred question
there**: close what the build answered, with evidence in the outcome file; bring the
still-open ones back to the user once, with the defer option; offer to spin out one deferred
twice with no movement. Open Questions end up listing **only** what is genuinely unresolved.

### 10d — Documentation follow-ups

Derive the documentation the change requires and apply it — part of the work, not an
afterthought. The full list is in `references/finalize.md` § 10d; its rules: any config or code
sample written into docs must be **valid in its target format** — parse it, or pin it with a
test (a fence label is not evidence); update the CHANGELOG (if kept), README, `docs/*` and
inline docs the change affects; present what you will update and skip, with reasons, then
apply. A doc the change made **wrong** is a defect; do not leave it for later.

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

Offer a quick retrospective, with the prompt in `references/retrospective.md`. On **Yes**,
note the friction — deriving each finding from the skill files in the **checkout**, not the
lagging plugin cache — present it, and **ask the user to run `/kit-dev:update-kit`**: it is
user-invoked only, so it cannot be launched from here, and its workflow is not replicated by
other means.

---

## Edge Cases

Read `references/edge-cases.md` when a run goes off the main path. Most entries restate a
step's rule; a few live only there — a `Supersedes` block naming a file that does not exist
(report it and ask; never pick an interpretation), a fan-out merge that goes red (stop merging;
report which task broke it), a worktree with uncommitted changes at cleanup (never remove it
automatically; ask), two worktrees needing docker compose with no scoping variable (serialize
them).

---

## Quality Criteria

The checklist a finished run is held to is in `references/quality-criteria.md` — each step's
rule restated as an outcome, plus one that lives only there: the series is re-read after any
pause. Hold the run to it before the Step 11 report.
