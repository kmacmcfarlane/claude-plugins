# The research strategy doc

Loaded from `deep-investigation` Step 4. This file owns the format of
`<series>/00_research-strategy.md` — the canonical state of a fan-out run.

The series layout around it (serials, `Supersedes`, `INDEX.md`, the writing rule) is owned by
`investigate`'s `references/investigation-format.md`. This file does not restate it. The
strategy doc takes serial `00`; the synthesis takes `01`.

## Why it exists

Three things read this file that cannot read your conversation:

1. **Cron wakeups and scheduled turns.** Their prompt should be *"read
   `<series>/00_research-strategy.md` and launch wave N"* and nothing more. A wakeup prompt that
   restates the lanes goes stale the first time the plan changes.
2. **A resumed or compacted session.** Rehydration reads this doc, not the transcript.
3. **The operator.** It is the one place that answers "what is this run doing and where is it".

Consequence: **when the plan changes, the doc changes.** A superseded schedule stays in place
with a ledger entry marking it superseded — supersede, do not rewrite.

## Required sections

### `# 00 — Research strategy: <question>`

Opening paragraph: when it was written, by which session, and one sentence saying this document
is the canonical brief and the rehydration point.

### `## Problem statement`

The question, what decision it feeds, and the costs of not answering it. Include any framing
analogies the operator supplied — they are lane seeds, and they justify the odd lanes to a
reviewer who would otherwise cut them.

### `## Research lanes`

Grouped under `### <Category letter> — <category name>`, 3–5 categories. One paragraph per lane,
opening in bold with the lane id and its wave and model:

```
**a1-log-toolkit** (wave 1, sonnet) — <mission in one sentence>. Corpora: <paths, with the
sizes recon measured>. <What is already known about the format, from recon.> Deliverables:
(1) …; (2) …; (3) a mining plan for a2/a3 documenting exactly how to detect <X> in the data.
Siblings: a4 covers the estate survey — do not chase it.
```

Required per lane: **id**, **wave**, **model**, **mission**, **scope** (paths for local lanes,
subject list for web lanes), **numbered deliverables**, and the **sibling-territory line**.

Lane ids are `<category letter><n>-<slug>` and are used verbatim as findings filenames.

### `## Output contract (every lane)`

The contract from `lane-contract.md`, reproduced in full — the doc must be self-sufficient for a
session that rehydrates from it. Immediately after it, the privacy rule and which lane ids it
binds.

### `## Wave schedule and usage budget`

The pacing constraint **and its reason**, in one sentence. Then either "all lanes launch in
parallel" or a table:

| Wave | When (UTC) | Lanes |
|---|---|---|

Followed by the two rules, stated explicitly:

- **Idempotence** — a wave's lanes launch only if their findings files do not exist and the
  ledger does not mark them launched.
- **Overrun** — synthesis starts no later than `<T>` with whatever findings exist; hard stop
  `<T+1h>`.

### `## Meta-deliverables`

Numbered: the synthesis, the SOP pointer, the retro, and the POC break-out. Each with its target
path.

### `## Parked threads`

One line per thread deliberately not actioned in this run — an unfinished handoff, a queued
item, a rehydration hook you saw and skipped. Omitting this section makes a resuming session
re-litigate decisions you already made. Write "none" rather than dropping the heading.

### `## Status ledger`

Append-only, oldest first, updated **in place as things happen** — not reconstructed afterwards.

```
- 2026-09-01 07:40Z — wave 1 LAUNCHED (a1, a4, a5 on sonnet). One-shot crons armed: wave 2 @09:03Z…
- 2026-09-01 07:52Z — a1 DONE (findings/a1-log-toolkit.md + tools/{…}.py, validated on both
  stores). Notable: <2–3 results, a clause each>. First numbers: <n> (unsampled).
- 2026-09-01 08:05Z — PLAN CHANGE (operator): usage window is fresh, stagger dropped. All 10
  remaining lanes launched NOW in parallel. Wave schedule table above is superseded by this entry.
- 2026-09-01 09:15Z — SYNTHESIS DONE: 01_synthesis.md written (headline: …). RUN COMPLETE.
```

Entry kinds: `LAUNCHED`, `DONE`, `FAILED`, `PLAN CHANGE`, `SYNTHESIS DONE`, `RUN COMPLETE`.

A `DONE` line carries the findings path plus the two or three results a reader would want if
they read nothing else — this is what makes the ledger a usable rehydration point rather than a
list of checkmarks. Mark any number that has not been validated by sampling as unsampled, right
there in the line.

## Anti-patterns

- **A ledger written at the end.** Its whole value is being correct at the moment the session
  dies.
- **Lane descriptions that restate the category.** A lane whose mission is "research X" gives the
  subagent nothing recon did not already give you.
- **Editing the schedule in place after a plan change.** The superseded plan plus a `PLAN CHANGE`
  entry is the record; a silently-edited table loses the fact that a decision was made.
- **Findings filenames that drift from lane ids.** Synthesis and the ledger both index by id.
