---
name: foundation
description: Lay a project's foundation before its first feature — frame what the operator already wants, then requirements (intent, goals and non-goals, requirements, quality scenarios, constraints, glossary, scope and claim), architecture (context, strategy, traceability, contracts, ADRs, risks and spikes) and a phased plan, each phase ending in a review gate, with named moves to reopen a phase, hold a question, factor an aspect out or probe ahead. Use when the user says "foundation", "green-field", "new project", "requirements and architecture", "what should we build first", or when a new repo or a large new aim has no requirements yet; also to retrofit an existing plan series. Not for a scoped bug or feature (investigate) or a broad landscape question (deep-investigation).
argument-hint: "[wi-id | slug | description] [requirements | architecture | plan | all] [--lite | --full] [--retrofit]"
---

# Foundation

A foundation session settles what a new project, or a large new aim inside an existing repo,
must do and how it will be built, before its first feature: requirements, then
architecture, then a phased plan. Each phase writes one serial of an investigation series
and ends in a **gate** that blocks the next phase. The **moves** let a later phase reopen an
earlier one, hold a question, factor an aspect out or probe ahead, so the run is not a
waterfall: questions are raised in any phase, and where an answer lands is a rule, not a
judgement.

The series format is the `investigate` skill's `references/investigation-format.md`,
including its § Foundation series. **Read it before writing anything.** The artifacts and
their templates are in `references/artifacts.md`.

## Usage

`/dev-flow:foundation [<wi-id> | <slug> | <description>] [<phase>] [--lite | --full] [--retrofit]`

- No phase runs the whole session, Steps 0–5, stopping at each gate the operator owns.
- A phase (`requirements`, `architecture`, `plan`, or `all` for a lite run) runs that one
  phase and its gate: the form an orchestrator dispatches (§ Running under an orchestrator).
- An existing foundation slug resumes it: read the whole series and its `INDEX.md`
  Foundation block, and take up the first gate not passed.

**The floor.** When the result could be described in one sentence, this is not a foundation
session: use `investigate`, or no plan at all.

## The moves

Any step may take a move. The full rows and the reopen procedure are in
`references/moves.md`.

| Move | When | Effect on gates |
|---|---|---|
| **Raise** | any time a question appears; triaged first (verify, ask, or record as external) | none by itself |
| **Answer locally** | the answer touches no phase-1 or phase-2 artifact | none |
| **Reopen architecture** | the answer changes a phase-2 artifact and no phase-1 one | gate G2 re-runs on the delta; G3 only for the features the impact list names |
| **Reopen requirements** | the answer changes any phase-1 artifact | gate G1 re-runs on the delta, with the operator; later gates only for what the impact list names |
| **Hold** | a question the current phase does not need | a gate passes with holds when nothing it approves depends on one |
| **Factor out** | an aspect with its own aim, another repo's claim, or a later horizon | none; its seam is checked at gate G2 |
| **Probe ahead** | only building can answer it, or data must start accruing now | none; a spike item, never a substitute for a gate |
| **Re-size** | the problem is bigger or smaller than the size chosen | the new size's gates apply from here |

A reopen is a serial of its own, `NN_reopen-<what>.md`, with an impact list read off the
traceability table. A later phase never edits an earlier serial and never absorbs a
requirement change as a plan fix.

---

## Step 0 — Frame

1. **The target.** The repo (the working directory's git root, confirmed). When the owning
   repo does not exist yet, point to the create-repo skill and keep the series in the
   current repo until it does (the format's § A repo not yet created).
2. **The item.** In a repo with a work-item store, resolve or `wi add` the foundation item
   and `wi claim` it (standalone only).
3. **The series.** A new slug (kebab-case, 2–5 words, what the project is), or an existing
   foundation series to resume. Nothing is written until the first serial.
4. **The mode**: `new`, `retrofit` (`references/retrofit.md`) or `resume`.
5. **The size**: `full` (three phases, three gates) or `lite` (one serial, one gate, the core
   artifacts only), from the flags, else proposed with a reason and confirmed.
6. **What exists.** Read `CLAIM.md`, `CLAUDE.md`, `README.md`, `docs/` and any prior series.
   Quote the operator's words verbatim, and list what is stated against what is inferred.
7. **Where the living docs live**, asked once per repo (`references/state.md` § Living docs).

## Step 1 — Requirements

Draft the phase-1 artifacts: intent, goals and non-goals, requirements, quality scenarios,
constraints, glossary, scope and context, held. Then question rounds: at most five questions
a round, ranked by impact × uncertainty, each triaged first and each with a hold option,
asked per the `operator-interaction:decisions` skill when the session lists it, else as a
numbered list. Run the prompt list (`references/prompt-list.md`): it always runs. Loop until
the operator has nothing left to add, or holds the rest.

**Research is optional per phase**: the `research` skill (quick by default) for a fact a
requirement rests on, landing in `<series>/research/`; `deep-investigation` when the
landscape itself is the question.

Write `00_initial.md` (`references/state.md` § The series), regenerate `INDEX.md` with its
Foundation block, then **gate G1** (§ The gates).

## Step 2 — Architecture

Draft the phase-2 artifacts: context and containers, solution strategy, traceability,
contracts and the threat and privacy model (or their one-line skips), an ADR for each one-way
decision, risks with a spike for each H risk the design cannot retire. Research for a vendor
or protocol fact; a probe-ahead spike for a risk only building answers. Write
the architecture serial at the next free number (`NN_architecture.md`, `references/state.md`
§ The series), regenerate the index, then **gate G2**.

## Step 3 — Phased plan

Features with acceptance traced to ids, a test plan and deps: `F0` (land the view) first,
then a walking skeleton. A roadmap when there is more than one horizon; the factored-out
table. Write the plan serial (`NN_plan.md`) with an **Implementation Approach** holding the
Features table, so `implement` and `dev-cycle` accept the series. Regenerate the index, then
**gate G3**.

## Step 4 — File the work

After the operator approves gate G3, with a store: file the features, groom the ones a hold
blocks, file the factored-out aspects still unfiled, and close the foundation item, exactly
as `references/state.md` § The work item says. Without a store, the Report lists the
features to file.

## Step 5 — Report

```
## foundation complete

**Series:** <slug> (<size>, <mode>)
**Gates:** G1 <approved date> · G2 <approved date | reported> · G3 <approved date>
**Held:** <n, each with what needs it | none>
**Factored out:** <aspect → item, each | none>
**Filed:** <F0 … Fn as items | listed for filing>

Next:
- /dev-flow:dev-cycle <F0 item> — then the walking skeleton
```

A run that stops at a gate (decide later, an unattended run at gate G1) reports the same
shape with the gates not passed marked `open`, and its handoff names the next phase.

---

## The gates

Every gate has three parts, in order (`references/gates.md`):

1. **The exit checklist**, run by this session.
2. **A fresh review**: one `dev-flow:reviewer`, `model: opus`, that never saw the drafting,
   briefed with the phase's checklist and the bar (only what affects correctness or the
   stated requirements). The fix loop and its cap are the `dev-cycle` skill's
   `references/fix-loop.md` and its SKILL.md § Step 4.3; each revision is a new serial.
3. **The operator's approval**: gate G1 always; gate G2 only for a one-way ADR or a change
   to the repo's `CLAIM.md`, the rest reported; gate G3 always, with a short architecture
   summary when G2 was reported. One decision per gate:
   approve, approve with holds, revise, reopen an earlier phase, or decide later.

A gate after a reopen runs on the delta only. The lite size runs one gate: G3's checklist,
plus G1's lines for requirements, quality scenarios and inferred lines, and the operator's
approval.

---

## Running unattended

Requirements belong to the operator. An unattended run drafts phase 1 with every question
held, writes `00_initial.md`, runs the checklist and the review, and stops at gate G1 with
the approval asked as a `decision N:` line on the item (or in the Report). It never approves
a gate itself.

## Running under an orchestrator

When `dev-cycle` (its foundation plan variant) or `librarian-mode` dispatches this skill as
a sub-agent, it runs **one phase per dispatch**: the phase the brief names, at the Series
home the brief gives. The orchestrator owns git, the work item, the review and every dialog.
Run as the `investigate` skill's `references/run-modes.md` § Running under an orchestrator
says, with these changes:

- Write only the phase's serial and the regenerated `INDEX.md`, with its Foundation block,
  at the Series home. Run the exit checklist; dispatch no reviewer (the orchestrator's
  plan review is the gate's review).
- Ask nothing. Each question you would ask is an Open Question marked blocking or not;
  the prompt list still runs, its unanswered prompts held.
- From the second phase on, the brief carries the previous gate's verdict, its `CLEAR`
  round, and whether it was approved (with the answer) or reported; record them in the
  serial's Confirmed Assumptions and in that gate's row of the Foundation block
  (`references/state.md` § The Foundation block).
- Fill the Foundation block's Operator cell for this gate (`references/gates.md` § 3), so
  the orchestrator knows whether to ask.
- A fix round, or a reopen the brief names, is a new serial with a `Supersedes` block.

Return `STATUS`, `SERIES` (absolute path), `OPEN QUESTIONS` (each blocking or not),
`DEVIATIONS`.

## Composition

`investigate` owns the series format and the open-question triage; `research` and
`deep-investigation` feed a phase; `dev-cycle` reviews each gate under an orchestrator and
builds each feature; the `operator-interaction:decisions` skill, when loaded, shapes every
question and gate decision; the `work-items` skill carries the item, holds and features.
Each is used by pointer, nothing copied. A repo's `CLAIM.md` is read and proposed as a
file; no claim skill is required.
