---
name: spec
description: The durable requirements layer for a project — a living spec/ directory with a constitution, numbered requirements carrying source and verification, and change folders that are proposed, groomed, applied and archived rather than edited in place. Use when the user says "spec", "requirements", "groom the spec", "write a spec for", "propose a change to the spec", "what are the requirements", or when a project needs a spec-driven (spec-kit / OpenSpec / Kiro-style) workflow. Not for the design of a single fix — that is investigate; not for task tracking — that is work-items.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
argument-hint: [init | groom | propose <what> | apply <NNN> | audit]
---

# Spec

The spec layer holds the durable **what** and **why** of a project: the requirements that outlive
any one investigation, branch, or agent session. It does not hold the plan and it does not hold the
tasks — `investigate` owns the how, `work-items` owns the work.

The on-disk format — layout, requirement record, id rules, statuses, delta syntax, archive naming —
is canonical in `references/spec-format.md`. **Read it before writing or editing any spec file.**
It is the single owner of those rules; this file does not restate them.

## Critical

- **Never edit `spec/requirements.md` directly.** Every change enters through a change folder under
  `spec/changes/` and is merged on apply. Direct edits destroy the review surface and are the
  documented cause of spec drift.
- **Requirement ids are permanent.** Never renumber, never reuse a retired id, never delete a
  requirement — reject and supersede in place.
- **A requirement is not `verified` until it names a check that runs.** Prose with no `Verify:`
  line is spec-first, the level that rots. Everything here exists to keep the project spec-anchored.
- **Right-size.** A one-line fix does not get a change folder. The spec layer earns its cost on
  requirements that several sessions will argue about; below that, go straight to `investigate`.

## Where it fits

```
research / investigations   evidence        ->  append-only serials, never groomed
spec/constitution.md        principles      ->  rarely changes; gates plans
spec/requirements.md        the WHAT        ->  this skill; the grooming surface
spec/changes/NNN-<slug>/    the diff        ->  this skill; proposed, groomed, applied, archived
decisions/NNNN-*.md         ratified choice ->  ADR; closes an `open` requirement
investigate series          the HOW         ->  investigate skill
wi items                    the WORK        ->  work-items skill
tests / replays / UAT       the PROOF       ->  named on the requirement's Verify: line
```

Do not create `spec/plan.md`, `spec/tasks.md`, per-feature spec directories, or per-feature
`research.md` / `data-model.md` / `contracts/`. Each of those duplicates a layer above and is where
spec-kit-shaped trees are reported to accumulate contradictions.

---

## Step 1 — Resolve the mode

The argument selects the verb. With no argument, infer from the conversation and say which you chose.

| Argument | Do |
| --- | --- |
| `init` | Step 2 — create the directory |
| `propose <what>` | Step 3 — open a change folder |
| `groom` | Step 4 — walk the operator through an open change |
| `apply <NNN>` | Step 5 — merge and archive |
| `audit` | Step 6 — find the drift |
| none | read `spec/requirements.md` for orientation, then ask which |

If `spec/` does not exist and the mode is not `init`, say so and offer `init` — do not create the
directory as a side effect of another verb.

---

## Step 2 — `init`

Create only these:

```
spec/README.md          # a short pointer: what each file is and the four-step loop
spec/constitution.md    # principles; seed from any existing ADRs and research conclusions
spec/requirements.md    # sectioned by domain; may start with the sections and no requirements
spec/changes/           # empty
spec/changes/archive/   # empty
```

Seed `constitution.md` from what the project has already ratified — ADRs, research conclusions, an
existing README's stated non-negotiables. **Every principle carries its source.** A principle with
no source is an opinion; ask the user whether to keep it or drop it.

If the project already has ad-hoc spec-shaped files, do not rewrite them in place. Read them, keep
the ids, and land the reshape as change `001-spec-layer` so the first act of the loop is the loop.

Expected output: the directory, and a one-paragraph report naming the sections in `requirements.md`.

---

## Step 3 — `propose`

A change folder is opened by anything that would alter the spec: an operator statement, a research
finding, a landed ADR, a discovery made during `implement`.

1. Pick the next free `NNN` (zero-padded, never reused) and a kebab slug for **what the change is**.
2. Write `spec/changes/NNN-<slug>/proposal.md` — why now, scope, what decision it needs, what it
   does *not* touch. Short: a screen, not a document.
3. Write `spec/changes/NNN-<slug>/delta.md` with only `## ADDED Requirements`, `## MODIFIED
   Requirements`, `## REMOVED Requirements` — format per `references/spec-format.md`. MODIFIED
   quotes the previous text verbatim before the new text.
4. Mark anything you are unsure of `[NEEDS DECISION: <the specific question>]` rather than guessing.
   Those markers are what Step 4 exists to clear.

**Never invent a requirement the project has not said out loud.** Every ADDED requirement carries a
`Source:` — an operator quote with a date, a finding id, or an ADR number. If you cannot source it,
it is a proposal note, not a requirement.

---

## Step 4 — `groom` (blocking)

Grooming is the operator reading a delta line by line and ruling on each block. This is the whole
point of the layer; do not shortcut it.

- Present one change folder at a time, ADDED first, then MODIFIED, then REMOVED.
- For each block, offer the four rulings: **accept** · **split** (too big to verify as one) ·
  **defer** (`open`, needs a decision first) · **reject** (with a reason; moves to the Rejected
  section, never deleted).
- Clear every `[NEEDS DECISION]` marker. A decision that is architectural, not just a wording
  choice, becomes an ADR in `decisions/` — the requirement then reads `decided`, pointing at it.
- Use `AskUserQuestion` in rounds of 2–4, with your recommendation on each, so confirming is cheap.

**Running non-interactively:** do not silently accept. Rule on each block yourself, record every
ruling under a `## Grooming decisions (unreviewed)` heading in the proposal, and leave anything
genuinely blocking as `[NEEDS DECISION]`. Report them together at the end for one review pass.

---

## Step 5 — `apply`

Run when the change's work has landed, or when the requirements are agreed and routed.

1. **Route before merging.** Each accepted requirement gets its downstream ids on its `Trace:` line:
   a requirement needing design becomes an `investigate` series (record the slug); a requirement
   ready to build becomes `wi` items (`wi add`, record the ids). The spec records the ids and
   nothing more — never copy the plan or the task list into the spec.
2. **Merge the delta into `spec/requirements.md`.** ADDED blocks append to their section with fresh
   permanent ids; MODIFIED blocks replace the body of the existing id in place, keeping the id;
   REMOVED blocks move to `## Superseded` with a pointer to the change. Ids never move sections.
3. **Archive** the folder to `spec/changes/archive/YYYY-MM-DD-NNN-<slug>/`, verbatim. Nothing is
   rewritten on archive; the reasoning is preserved out of the way of the living spec.
4. **Verify the merge**: every id in the delta appears exactly once in `requirements.md`; no id
   changed number; no requirement lost. Say so in the report.

---

## Step 6 — `audit`

The only enforcement that scales at small size. Report, do not fix:

- Requirements at `built` with no `Verify:` line — **this list is the drift**.
- Requirements at `agreed` older than the last two changes with no `Trace:` — specified and dropped.
- `open` requirements whose blocking question has since been answered by a landed ADR.
- Change folders in `spec/changes/` whose work has landed but which were never applied.
- Constitution principles no requirement cites — either dead, or being violated silently.

Hand the operator the lists and ask which to turn into a `propose`. Never auto-apply an audit.

## Examples

**Example 1 — a new operator statement.**
User: *"asks need to carry how long the next turn will take."*
Actions: `propose next-turn-characterization` → `002-next-turn-characterization/delta.md` with one
MODIFIED block on the existing Ask requirement (quoting its current text) and one ADDED block for
the new field, each with `Source: operator <date>` and an EARS acceptance line → groom → route to an
investigate series because the scale is undesigned → apply on landing.
Result: one reviewable diff, an unchanged requirement id, and a preserved rationale.

**Example 2 — implement discovers a missing rule.**
Actions: do not edit `requirements.md` from the implementation session. Open a change folder with
the discovered rule as ADDED, `Source:` the investigation serial, `Verify:` the test just written,
status `built`. Groom and apply in the same pass — the proof already exists.

## Troubleshooting

**Two change folders touch the same requirement.** Apply in NNN order; the second's MODIFIED block
now quotes stale previous text. Re-groom the second delta against the merged spec before applying —
never apply a MODIFIED whose quoted "previous" no longer matches the file.

**`requirements.md` is being edited directly by hand.** Expected occasionally. Do not revert it;
open a change folder that records what was changed and why, so the next reader sees a diff rather
than a mutation, then continue the loop.

**The spec and the code disagree.** The code wins as a description of reality; the spec wins as a
description of intent. Record the divergence as a MODIFIED requirement (reality) or as a `built`
requirement failing its `Verify:` line (a bug) — never quietly rewrite the spec to match the code.

**The layer feels like overhead.** It probably is, for that work. The spec layer is for requirements
several sessions will revisit. Use `investigate` alone for anything smaller and say so.
