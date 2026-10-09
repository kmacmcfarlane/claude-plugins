# Gates

Loaded from `foundation` at the end of every phase. A gate blocks the next phase until its
three parts hold, in order: the exit checklist, a fresh review returning `CLEAR`, and the
operator's approval where the gate is theirs. A gate after a reopen runs on the delta only
(`references/moves.md`).

## 1. The exit checklists

Run by the session itself, before any reviewer is dispatched. A failed line is fixed in the
draft, or recorded as a hold the checklist allows, before the review.

**Gate G1 — requirements**

- Every goal has a requirement or a quality scenario.
- Every requirement has an id and a goal, and is testable.
- 3–5 quality scenarios, each with a measure.
- At least one non-goal.
- Every constraint names its source.
- Every term used in two senses is in the glossary.
- Scope is written as a claim (or proposed), and is consistent with the neighbours' claims
  where they have them.
- Every inferred line is confirmed by the operator, or held.
- Every held question names what it is needed by.
- The prompt list was run (`references/prompt-list.md`).

**Gate G2 — architecture**

- Every quality scenario and requirement appears in the traceability table, or was moved
  to a non-goal or to Later with the operator's answer.
- Every one-way decision is an ADR with its alternatives.
- The contracts match the claim's boundaries.
- The threat and privacy model ran, or its one-line skip is recorded.
- Every H risk has a mitigation or a spike.
- The pre-mortem prompt ran (`references/prompt-list.md` § Pre-mortem).
- Every factored-out aspect's seam is a constraint the architecture keeps.

**Gate G3 — the phased plan**

- Features are independently landable, `F0` (land the view) first, then a walking
  skeleton.
- Every requirement is served by a feature, or listed Later or as a non-goal.
- Every feature has acceptance traced to ids, a test plan and deps.
- Every held question is mapped to the feature that needs it.
- The plan serial carries `Implementation Approach`, holding the Features table.

**The lite size** runs one gate: G3's checklist, plus G1's lines for requirements, quality
scenarios and inferred lines.

## 2. The fresh review

One `dev-flow:reviewer` agent, `model: opus`, that never saw the drafting: never a fork,
never this session. Brief it with the plan-review variant of the `dev-cycle` skill's
`references/review-brief.md`, which already names the gate checklists for a foundation
series, plus:

- the phase's checklist above, pasted in full;
- the bar: flag only what affects correctness or the stated requirements; style, wording
  and preference are not findings;
- for a gate after a reopen, the reopen serial and its impact list, and "review the
  change and what the impact list names, not the whole phase".

The verdicts, the severity scale and the fix loop are dev-cycle's: medium and above must
be fixed. The `dev-cycle` skill's `references/fix-loop.md` says who is resumed and who is
re-dispatched, and its SKILL.md § Step 4.3 sets the cap. A revision is a new serial with a
`Supersedes` block, never an edit. Under `dev-cycle` or `librarian-mode` this whole part is
theirs: the skill writes the phase and returns, and the orchestrator reviews it.

## 3. The operator's approval

Who approves which gate (operator decision 195, answered (a) on 2026-10-09):

| Gate | The operator approves | Reported only |
|---|---|---|
| G1 requirements | always | — |
| G2 architecture | each one-way ADR, and any change to the repo's `CLAIM.md` (its areas, Not-ours lines, boundaries, which side defines an interface) | everything else in the phase |
| G3 the plan | always, since it files work | — |

A G2 with no one-way ADR and no claim change passes on the reviewer's `CLEAR` and is
reported to the operator in the Report, not asked. The G3 decision then carries a short
architecture summary (the strategy bullets, the ADRs and the H risks, a few lines), so the
operator has read the architecture before approving the plan built on it.

**The decision**, one per gate, put to the operator per the `operator-interaction:decisions`
skill when the session lists it, else as a plain lettered list in prose:

- (a) approve;
- (b) approve with holds — name the held rows; the gate passes when nothing it approves
  depends on one (the reviewer checked this);
- (c) revise — the operator's words go into a new serial and the gate re-runs on it;
- (d) reopen an earlier phase — a move (`references/moves.md`);
- (z) decide later — the run stops at this gate; with a store, the question is a
  `decision N:` line on the foundation item, so `wi needs-input` lists it.

The approval is recorded where the next writer reads it: in the next serial's Confirmed
Assumptions ("Gate G1 approved by the operator <YYYY-MM-DD>"), and in `INDEX.md`'s
Foundation block (`references/state.md`). G3 has no next serial: its approval is the
item's `answer N:` line, and a standalone run also writes it into the Foundation block when
it regenerates `INDEX.md`. Under an orchestrator, which writes nothing in the series, the
block keeps the gate's `CLEAR` and the item's line is the record: a done foundation item,
or that `answer N:` line, marks gate G3 passed (`references/state.md` § The Foundation
block).

**Unattended runs.** Requirements belong to the operator, so an unattended run drafts phase 1
with every question held and stops at gate G1. It never approves a gate itself.
