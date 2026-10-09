# Moves

Loaded from `foundation` when a move is taken. SKILL.md carries the moves table; this file
holds the full rows and the reopen procedure. A move is named and recorded, never an
exception handled in passing: a later phase never edits an earlier serial (the series is
append-only) and never absorbs a requirement change silently. That is the failure the
moves exist to prevent: a requirement change travelling as a plan fix, so that each review
round finds its next consequence.

## The rows

| Move | When | What is recorded, and where | Effect on gates |
|---|---|---|---|
| **Raise** | any phase, any time a question appears | triaged as the `investigate` skill's `references/open-question-sweep.md` triages: verifiable → verified now; a decision → asked; external → an Open Question with its owner and whether it blocks | none by itself |
| **Answer locally** | the answer touches no phase-1 or phase-2 artifact | in the current phase's serial (Confirmed Assumptions) | none |
| **Reopen architecture** | the answer changes any phase-2 artifact (an ADR, a contract, the threat and privacy model, context and containers, the strategy or traceability, a risk) and no phase-1 artifact | a serial `NN_reopen-<what>.md`: `Supersedes` names the changed artifact; a superseding ADR when an ADR changes; an impact list (the features, contracts and other phase-2 artifacts it touches) | gate G2 re-runs on the delta; the operator approves any one-way ADR change; gate G3 re-runs only for the features the impact list names |
| **Reopen requirements** | the answer adds or changes any phase-1 artifact (the intent, a goal or non-goal, a requirement, a quality scenario, a constraint, a glossary meaning, the claim or the neighbours table) | a serial `NN_reopen-<what>.md`: `Supersedes` names the changed requirement; an impact list read off the traceability table (the ADRs, contracts and features it touches); the touched artifacts revised in the same serial or the next | gate G1 re-runs on the delta only, and the operator approves the change; G2 and G3 re-run only for what the impact list names |
| **Hold** | a question the current phase does not need | a Held row: question, needed by, owner; with a store, a `decision N:` line on the foundation item, so `wi needs-input` lists it | a gate passes with holds when nothing it approves depends on one (the reviewer checks this). The wake is the phase or feature named in "needed by"; a feature filed with a hold on it is put to `wi groom` until the hold is answered |
| **Factor out** | an aspect with its own aim, another repo's claim, or a later horizon | a non-goal or a Later row; a follow-up work item (`--parent` the foundation item, or `--ref` the series); the seam kept for it, as a constraint | none; the seam is checked at gate G2 |
| **Probe ahead** | a risk or held question only building can answer, or data that must start accruing now because it cannot be rebuilt later | a timeboxed spike as its own work item; its result recorded as evidence in the phase that needed it. A probe that ships freezes its contract on purpose, with an ADR | none; never a substitute for a gate |
| **Re-size** | the problem is bigger or smaller than the size chosen | one line in Confirmed Assumptions; lite → full splits the next serial into phases | the new size's gates apply from here |

The three answer tiers partition the artifacts of `references/artifacts.md`: an answer that
touches a phase-1 artifact reopens requirements; one that touches a phase-2 artifact and no
phase-1 one reopens architecture; one that touches neither is answered locally. Phase-3
artifacts (features, roadmap, factored out) are revised inside the plan phase, or through
gate G3's re-run. The tier is set by the artifact the answer touches, never by a judgement
of how big the change feels.

## The reopen procedure

1. **Name the trigger.** The answer, its source (the operator and the date, a probe's
   result, a review finding), and the artifact it touches, which sets the tier.
2. **Read the impact off the traceability table.** For a requirement or quality scenario,
   every mechanism, ADR, contract and feature its row reaches; for a phase-2 artifact,
   every feature and contract that cites it. That list is the impact list.
3. **Write the reopen serial** at the next free number: `NN_reopen-<what>.md`, its
   `Supersedes` block naming each changed artifact by serial, section and id, then the
   change, then the impact list. Revise the touched artifacts in the same serial, or in the
   next when the revision is large. An ADR is never edited: a new ADR supersedes it, and the
   old one's Status line is restated as superseded in the new serial.
4. **Re-run the gate on the delta.** The reviewer gets the reopen serial and the impact
   list, not the whole phase (`references/gates.md` § 2). The operator approves per the
   gate's rule; a requirements reopen always comes to them.
5. **Re-run later gates only for what the impact list names.** A later gate already passed
   stays passed for everything the list leaves out.
6. **Regenerate `INDEX.md`**, its Foundation block naming the reopen and the gates it
   re-ran (`references/state.md`).

A reopen after gate G3, once features are filed, is the same procedure; the features its
impact list names are the ones to revise, and `F0`'s re-run is filed as a new item under
the foundation item, by `dev-cycle` or the standalone session, so the living docs follow
(`references/state.md` § The work item).
Raising one from inside a feature's build is done by hand, by the operator or a session
that sees the finding; dev-cycle's build does not raise it on its own.

Under the claim convention, a change to the claim's substance (an area, a Not-ours line, a
boundary rule, which side defines an interface) is a requirements reopen, and comes to the
operator; upkeep that changes no substance is reported.
