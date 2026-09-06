# Spec layer format

**This file is the single owner of the on-disk spec format.** The `spec` skill defers to it; other
skills that touch a spec directory (`investigate`, `implement`, `work-items`) read it rather than
restating it. Do not restate these rules in a SKILL.md body — restated rules drift.

## Layout

```
spec/
  README.md            # short: what each file is, and the propose -> groom -> apply -> archive loop
  constitution.md      # principles, each with its source; rarely changes; gates plans
  requirements.md      # the living spec: sectioned, permanent ids, status, source, verification
  changes/
    NNN-<slug>/
      proposal.md      # why now, scope, what decision it needs, what it does not touch
      delta.md         # ## ADDED / ## MODIFIED / ## REMOVED Requirements
    archive/
      YYYY-MM-DD-NNN-<slug>/    # applied changes, verbatim, never rewritten
```

Nothing else belongs in `spec/`. In particular **no** `plan.md`, `tasks.md`, `research.md`,
`data-model.md`, `contracts/`, and **no per-feature spec directories**. Those layers are owned by
`investigate` (design, research, data model), `work-items` (tasks) and the project's own research
tree (evidence). A spec tree that grows them accumulates duplicate and contradicting statements of
the same requirement — the documented failure mode of per-feature spec toolkits.

### Change numbering

`NNN` is zero-padded from `001`, allocated in order, **never reused**, expanding past three digits
when it must. The slug is kebab-case, 2–5 words, describing what the change *is* — not the file it
touches and not a date. Before opening one, list `spec/changes/` and `spec/changes/archive/` and
extend an open change rather than opening a near-duplicate.

## The three rules

### 1. `requirements.md` is never edited directly

Every change enters as a delta and is merged on apply. This is what makes each change a reviewable
diff instead of an untraceable mutation, and it is the difference between a spec that compounds and
one that drifts.

### 2. Requirement ids are permanent

`R<n>` (or a section-prefixed `R<section><n>` if the project prefers). Once allocated, an id is
never renumbered, never reused after retirement, and never deleted. A requirement that is wrong is
**superseded**; a requirement that is unwanted is **rejected**. Both stay in the file, at the bottom,
with a reason and a pointer.

### 3. Applied changes are archived verbatim

On apply the folder moves to `changes/archive/YYYY-MM-DD-NNN-<slug>/` with its content untouched.
The living spec carries the current statement; the archive carries why it says that. Neither is a
substitute for the other, and neither is rewritten to agree with hindsight.

## The requirement record

```markdown
### R7 — Contention resolution
Competing asks are ranked by thread priority x next-turn characterization x age, quantized to bands.

- Status: agreed
- Source: operator 2026-09-06 ("the key is characterizing the expected nature of the next turn"); e2
- Acceptance: WHEN two asks are pending on different threads, the scheduler SHALL present the
  higher-band ask first, and SHALL break ties by age.
- Verify: pocs/priority-engine replay test `ranks_by_band_then_age`
- Trace: change 003-scheduler-inputs -> investigation `attention-scheduler` -> wi `sched-4c1e`
```

Every field is load-bearing:

- **Status** — one of `open` · `agreed` · `built` · `verified` · `superseded` · `rejected`
  (see below). One value, never a mix.
- **Source** — an operator quote with a date, a finding id, or an ADR number. A requirement with no
  source is an invention; do not write one.
- **Acceptance** — EARS, once the requirement is `agreed` or beyond (see below). Omit while `open`;
  prose is fine for something still being argued about.
- **Verify** — the name of a check that actually runs: a test, a replay fixture, a manual UAT note
  with a date. Required to claim `verified`. Its absence at `built` is what `audit` reports.
- **Trace** — the downstream ids: change number, investigation slug, `wi` item ids. Ids only. Never
  copy plan text or task lists into the spec; they are owned elsewhere and will go stale here.

### Statuses

| Status | Means | Entry condition |
| --- | --- | --- |
| `open` | stated, but a decision blocks specifying it | has a Source and a named blocking question |
| `agreed` | specified and accepted; not built | has EARS acceptance |
| `built` | code exists | has a Trace |
| `verified` | a named check passes | has a Verify that runs |
| `superseded` | replaced by another requirement | points at the id that replaces it and the change |
| `rejected` | deliberately not doing it | carries the reason and the change that rejected it |

`superseded` and `rejected` requirements live in `## Superseded` and `## Rejected` sections at the
bottom of the file. They are never removed — the value of keeping them is that the same idea does
not get re-proposed every quarter.

## EARS acceptance criteria

EARS (Easy Approach to Requirements Syntax; Mavin et al., RE'09) constrains an acceptance sentence
enough that it converts mechanically into a test name. General form:

```
WHILE <optional precondition>, WHEN <optional trigger>, the <system> SHALL <response>.
```

The five patterns:

| Pattern | Shape |
| --- | --- |
| Ubiquitous | The `<system>` SHALL `<response>`. |
| Event-driven | WHEN `<trigger>`, the `<system>` SHALL `<response>`. |
| State-driven | WHILE `<state>`, the `<system>` SHALL `<response>`. |
| Optional-feature | WHERE `<feature is included>`, the `<system>` SHALL `<response>`. |
| Unwanted-behaviour | IF `<undesired condition>`, THEN the `<system>` SHALL `<response>`. |

Rules of use:

- One SHALL per sentence. Two SHALLs is two requirements — split it.
- Observable behaviour only. "SHALL be maintainable" is not verifiable and is not a requirement.
- Apply EARS to **acceptance criteria only**, not to the requirement's prose statement, and not to
  requirements still `open`. Blanket EARS on everything is ceremony that buys nothing.
- Gherkin GIVEN/WHEN/THEN scenarios are an acceptable alternative *where the project's tests are
  already written that way*. Do not run both notations in one spec.

## Delta format

`delta.md` contains only requirement blocks under exactly these three headings, in this order.
Omit a heading with no blocks rather than writing "none".

```markdown
## ADDED Requirements

### R24 — Away-window launch
Long-running unattended work is launched into known away windows.
- Status: agreed
- Source: operator 2026-09-05; a2
- Acceptance: WHEN an away window of at least 30 minutes begins, the scheduler SHALL start the
  highest-value unattended item queued for it.

## MODIFIED Requirements

### R4 — Ask
Previous: "an ask carries kind (permission / decision / missing-resource / review / fyi)."
New: "an ask carries kind and a next-turn characterization: expected duration, cognitive load,
context to load, modality, interruptibility, deadline + default."
- Status: agreed
- Source: operator 2026-09-05
- Acceptance: WHEN an ask is emitted, the agent SHALL populate every next-turn field, and IF a
  field is unknown THEN the agent SHALL emit its declared default rather than omitting it.

## REMOVED Requirements

### R11 — Automatic switch detection
Reason: violates constitution principle 6 (manual switch, automatic capture).
Superseded by: R6.
```

- A MODIFIED block **quotes the previous text verbatim** before the new text. Without the quote a
  reviewer cannot see what changed, and an apply cannot be checked.
- A REMOVED block carries a reason, and a `Superseded by:` pointer when the behaviour moved rather
  than vanished.
- Unresolved points are marked inline as `[NEEDS DECISION: <the specific question>]`. A delta may
  be groomed with markers present; it may **not** be applied with any remaining.

## Applying a delta

1. ADDED → append to the matching section of `requirements.md`, allocating the next permanent id.
2. MODIFIED → replace the body of the existing id in place. The id, and its section, do not move.
3. REMOVED → move the record to `## Superseded` (or `## Rejected`), keeping the id, adding the
   reason and the change number.
4. Move the change folder to `changes/archive/YYYY-MM-DD-NNN-<slug>/` unmodified.

Post-apply check, every time: each delta id appears exactly once in `requirements.md`; no id
changed number; the file's requirement count changed by exactly the number of ADDED blocks.

## Constitution

`constitution.md` is a numbered list of principles, each one sentence plus a source. It changes
rarely and only by an explicit change folder — a constitution amendment is the highest-ceremony
edit in the layer, and usually accompanies an ADR.

Its function is a **gate**: before an investigation's plan is accepted, check it against the
articles and say which ones it engages. A principle no requirement cites is either dead or being
violated silently; `audit` reports both.

## Relationship to investigation serials

The two formats are deliberately parallel and must not be merged:

| | investigation series | spec layer |
| --- | --- | --- |
| Unit | one problem, followed to completion | one product, followed indefinitely |
| Change | new serial `NN_*.md` + `Supersedes` block | new change folder + delta |
| Current view | `INDEX.md`, rewritten wholesale | `requirements.md`, merged in place |
| Lifetime | closed when implemented | never closed |

An investigation's Proposed Fix may *imply* a spec change; it does not *make* one. Open a change
folder. Conversely, a spec requirement at `open` or `agreed` that needs design is the normal input
to `/investigate` — pass the requirement id and let the series own the how.
