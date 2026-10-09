# Artifacts

Loaded from `foundation` before drafting any phase. Each artifact is one page or less.
**Core** artifacts are written in every full run. **Conditional** ones have a trigger;
skipping one is a recorded one-line choice in the serial ("no data leaves the process: no
contracts"), never a silent omission.

## The set

| Artifact | Class | Phase | Minimal form |
|---|---|---|---|
| Intent | core | 1 | 3–5 lines; the operator's words quoted, every inferred line marked `(inferred)` |
| Goals and non-goals | core | 1 | `G<n>` one-liners with their source; `NG<n>`: something that could reasonably be a goal and was chosen not to be, with why |
| Requirements | core | 1 | `R<n>` one-liners, each tracing to a goal; EARS phrasing ("When <trigger>, <system> shall <response>") optional |
| Quality scenarios | core | 1 | the top 3–5, prioritised: quality, stimulus (with its source and environment), response, measure |
| Constraints | core | 1 | `C<n>`: the constraint and who or what imposes it |
| Glossary | core when non-empty | 1 | terms used in two senses, or that collide with a neighbour's: term, meaning, not to be confused with |
| Scope and context | core | 1 | the repo's `CLAIM.md` (written or proposed through the `ownership:claim-md` skill when the session lists it, else proposed as a file, unchecked) plus a neighbours table: neighbour, interface, direction, which side defines it |
| Context and containers | core | 2 | a table or a small text diagram; containers only when there are several deployables |
| Solution strategy and traceability | core | 2 | 5–10 bullets, then a table mapping each quality scenario and requirement to the mechanism that meets it |
| ADRs | core, one-way calls only | 2 | Title, Status, Context, Decision, Alternatives considered, Consequences; kept, never edited, superseded by a later one |
| Risks and spikes | core | 2 | `K<n>`: risk, likelihood and impact (H/M/L), the mitigation or the spike that retires it |
| Data contracts | conditional: the system publishes data or an API others read | 2 | contract, producer, consumers, versioning and compatibility rule |
| Threat and privacy model | conditional: a trust boundary, credentials, personal or account data | 2 | the four threat-modelling questions as headings (what are we working on, what can go wrong, what are we going to do about it, did we do a good job); a pass over LINDDUN's seven privacy categories |
| Features | core | 3 | `F<n>`: requirements served, acceptance, test plan, deps, horizon; a walking skeleton first |
| Roadmap | conditional: more than one horizon | 3 | Now / Next / Later, no dates |
| Test strategy | folded into Features | 3 | one paragraph of levels, then a test plan per feature |
| Factored out | core when non-empty | any | aspect, where it went (an item), the seam kept for it |
| Held | core when non-empty | any | question, needed by (a phase or a feature), owner |

The ids are per series and never reused. `G<n>` ids name goals only; the three gates are
written "gate G1", "gate G2", "gate G3", or by name (the requirements gate), so the two
never read alike in prose.

A **one-way** decision is one that is costly to reverse once built on: a storage format, a
public name, a protocol, a boundary with another repo. It gets an ADR. A two-way decision
is a line in the strategy.

**Folded or skipped:** a PRD (its areas are the intent, requirements, quality scenarios and
roadmap), a design doc or RFC (the architecture serial is the design doc), full arc42 (the
skeleton above covers its §§ 1–4 and 9–12), C4's component and code levels, and dated
roadmaps. Product-management artifacts with no agent use (market requirements, pricing,
launch plans) are out of scope.

## Templates

Phase 1, in the first serial (`00_initial.md`):

```markdown
## Intent
<3-5 lines. Quote the operator; mark each inferred line "(inferred)".>

## Goals
- G1 <goal> — operator <YYYY-MM-DD> | inferred
## Non-goals
- NG1 <something that could reasonably be a goal> — <why not>

## Requirements
| Id | Requirement | Goal | Source |
|---|---|---|---|
| R1 | When <trigger>, <system> shall <response>. | G1 | operator <date> |

## Quality scenarios
| Id | Quality | Stimulus (source, environment) | Response | Measure | Priority |
|---|---|---|---|---|---|
| Q1 | modifiability | a second agent harness is added (maintainer, after release) | a new adapter, no data migration | 0 schema majors bumped | 1 |

## Constraints
| Id | Constraint | Imposed by |
|---|---|---|

## Glossary
| Term | Means | Not to be confused with |
|---|---|---|

## Scope and context
Claim: CLAIM.md — <approved <date> | proposed | proposed, unchecked (no claim tool)>
| Neighbour | Interface | Direction | Defined by |
|---|---|---|---|

## Held
| # | Question | Needed by | Owner |
|---|---|---|---|
```

Phase 2, in the architecture serial (`NN_architecture.md`):

```markdown
## Context and containers
## Solution strategy
## Traceability
| Scenario or requirement | Mechanism | Where |
|---|---|---|
## Contracts            (or one line: why none)
## Threat and privacy   (or one line: why none)
## Decisions            (one line per ADR: id, title, one-way or not)
## Risks
| Id | Risk | L/I | Mitigation or spike |
|---|---|---|---|
```

One ADR per one-way decision, in the architecture serial under `## Decisions`, each in this
shape (the living-docs feature later copies each to `docs/adr/NNNN-<title>.md`):

```markdown
# ADR-<nnnn>: <short noun phrase>
Status: proposed | accepted <YYYY-MM-DD> | superseded by ADR-<nnnn>
## Context
## Decision
## Alternatives considered
## Consequences
```

Phase 3, in the plan serial (`NN_plan.md`), under its `Implementation Approach`:

```markdown
## Features
| Id | Feature | Serves | Acceptance | Test plan | Deps | Horizon |
|---|---|---|---|---|---|---|
| F0 | land the view: regenerate the living docs from the series | — | the docs match the approved serials | read against the series | — | now |
| F1 | walking skeleton: <thinnest end-to-end slice> | R1, Q1 | … | … | — | now |
## Factored out
| Aspect | Went to | Seam kept |
|---|---|---|
```

`F0` is always the first feature: the living docs are a repo change, so they are built like
any other feature, never written by the foundation session itself (`references/state.md`
§ Living docs).

Each serial still follows the series format's standard outline (Summary, Confirmed
Assumptions, Risk Assessment, Open Questions and the rest, per the `investigate` skill's
`references/investigation-format.md`); the artifacts above are sections inside it, placed
after Existing Architecture (or after Summary when nothing exists yet).
