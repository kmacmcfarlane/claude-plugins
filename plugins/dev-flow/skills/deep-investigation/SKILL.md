---
name: deep-investigation
description: Run a multi-agent deep-research fan-out for a broad, open-ended question — recon the corpora, write a canonical strategy doc (lanes, output contract, ledger), launch many research lanes on a cheaper model against a fixed contract, then synthesize in one pass into an investigation series. Use when the user says "deep research", "deep investigation", "fan out", "map the landscape of", "what should X become", "research this overnight", or when a question is too broad for one session to read its way through. Do NOT use for a scoped bug or feature — that is the investigate skill.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, WebSearch, WebFetch, AskUserQuestion
argument-hint: <broad research question>
---

# Deep investigation

A fan-out research shape for questions one session cannot read its way through: "what should
this become?", "map the whole landscape of X", "is there prior art for the thing we are about
to build?".

This skill **piggybacks on `investigate`**. The series layout, serials, `Supersedes`, `INDEX.md`,
the standard outline and the writing rule are canonical in `investigate`'s
`references/investigation-format.md` — **read it before writing anything**, and read
`investigate`'s SKILL.md for the steps this one does not restate (repo resolution, branch survey,
project-context loading, the citation rule, the retrospective offer). What follows is only the
deep-research delta.

The delta in one line: **you do not do the research.** You recon, write a strategy doc, launch
lanes on a cheaper model against a fixed output contract, log each completion, and then spend
your whole context on the one thing no lane can do — the synthesis.

## Usage

`/deep-investigation <broad research question>`

- `/deep-investigation what should the operator attention router be`
- `/deep-investigation map the landscape of multi-agent session management`
- `/deep-investigation <slug>` — resume an existing series from its strategy doc

## When this is the wrong skill

A question with a known blast radius, a named component, or a reproducible symptom is an
`investigate`, not a fan-out. Fanning out a narrow question buys thirteen files that say the
same thing. The test: **can you name, right now, the three-to-five categories of evidence that
would answer it, and does no single one of them suffice?** If yes, fan out.

---

## Step 1 — Gather the run inputs (blocking)

One `AskUserQuestion` round, with a recommendation on each. You need:

1. **The question**, and what decision it feeds. A fan-out with no downstream decision produces
   a library, not an answer.
2. **Corpora and paths** — which repos, log stores, mounts, and estates are in scope.
3. **Sensitivity** — is any corpus employer, client, or otherwise restricted data? Name the
   paths. This becomes a verbatim inline rule in those lanes' prompts (Step 4).
4. **Lane-count target** — 8–15 is the working range. Below 6, use `investigate`.
5. **The pacing constraint, and its reason.** "Waves or full parallel" is downstream of *why*:
   a usage window that resets at a known time, a rate limit, a cost ceiling, an operator who
   wants to review wave 1 before wave 2. **Ask for the reason, not just the constraint** —
   scheduling machinery built for a constraint that evaporates is wasted work, and reasons
   expire on their own schedule.
6. **The model for lanes** — a cheaper one than yours, deliberately. Lanes read a lot and write
   ≤300 lines to a fixed shape; that is not where the expensive model earns its keep.

Skip the round only when the invocation already answers all six; say that you skipped it.

## Step 2 — Recon before spec

**Do this before writing a single lane description.** Twenty minutes of orchestrator recon
routinely changes the lane set outright — a record type spotted in a 600-byte `head` sample is
how a whole toolkit lane gets invented.

Per corpus, establish and write down: how big it is (file count, bytes), what format it is in,
whether it is actually mounted and readable from here, and what a sample record looks like.

```bash
du -sh <corpus>; find <corpus> -name '*.jsonl' | wc -l
head -c 600 <a representative file>
ls <the live-state dirs a lane might poll>
```

For a web-facing question, the recon is a handful of orienting searches to learn what the
field calls the thing — lanes waste budget rediscovering vocabulary.

Then load project context per `investigate` Step 4, trimmed, with a reason per omission.

Expected output: a short recon note in your own words. It is the raw material for Step 3, and
its surprises are the ones worth designing around.

## Step 3 — Design the lanes

**Three to five categories, not a flat list.** Categories keep the fan-out from collapsing into
one perspective repeated N times. The shape that worked:

| Category | What it is | Ordering |
|---|---|---|
| **A — Empirical, local** | What the evidence on this machine actually says. Includes a **toolkit lane** that builds and validates the scripts the mining lanes then run. | First. Toolkit before mining. |
| **B — Landscape** | What already exists: tools, products, prior art. Verdict per item: steal / ignore / gap remains. | Any |
| **C — Abstract / human** | The science and doctrine under the problem — human factors, theory, adjacent disciplines. | Any |
| **D/E — Engineering & POC** | What could actually be built, and with what. Cites A's numbers. | Last, so it can cite the others. |

Rules that earn their place:

- **Empirical-local lanes go first, and a toolkit lane feeds the mining lanes.** One lane
  reverse-engineers the format and ships validated scripts plus a *mining plan* — exact
  commands, known pitfalls. The mining lanes then spend their whole budget on classification
  instead of parsing. This is the single highest-leverage ordering decision in the run.
- **Name the sibling lanes' territories in every prompt**, one line: "c3 covers supervisory
  control and alarm design — do not chase it; flag and move on." Without this, two lanes will
  independently spend budget flagging a gap that a third lane *is*. This is a documented failure
  from the exemplar run.
- **Lanes may cite lanes.** Tell a later lane to read specific earlier findings files first. The
  best findings in the exemplar run came from exactly there — a POC lane resolving an open
  question a toolkit lane had left standing.
- **Keep the unconventional lane.** The donor discipline that sounds like colour — game
  interfaces, aviation procedure, a biological analogy — has a strong track record of landing as
  concrete design elements. One or two per run, not five.
- Every lane gets: an id (`a1`, `c2`), a one-line mission, its corpora or search scope, its
  deliverable, its sibling-territory line, and its wave.

## Step 4 — Write the strategy doc, then launch

Write `<series>/00_research-strategy.md` **before launching anything**. This file — not your
conversation — is the canonical state of the run. Crons, wakeups, a resumed session and a
mid-run plan change all anchor here. Its required sections, the lane-spec fields, the ledger
format and the parked-threads note are in `references/research-strategy-format.md`.

Two blocks go into it and then **verbatim into every lane prompt**: the output contract and, for
any lane touching sensitive corpora, the privacy rule. Both are in `references/lane-contract.md`
— copy them, do not paraphrase, and do not replace either with a reference to a file the lane
cannot read.

Then launch, per the pacing decision from Step 1:

- **Full parallel** unless a live constraint says otherwise. It is faster and there is no
  coordination cost — lanes never talk to each other.
- **Waves** when the reason from Step 1 is real. Fire them from one-shot crons or wakeups whose
  prompt is *"read `<series>/00_research-strategy.md` and launch wave N"* — never from a prompt
  that restates the lanes, which goes stale the moment the plan changes.
- **Idempotence rule, stated in the doc**: a wave's lanes launch only if their findings files do
  not exist and the ledger does not mark them launched.
- **Overrun rule, stated in the doc**: synthesis starts by time T with whatever findings exist;
  hard stop at T+1h.

Launch each lane with `Agent`, `model:` set to the cheap model from Step 1, prompt = mission +
scope + sibling territories + the verbatim contract (+ privacy rule). Launch a wave's lanes in
**one message** so they run concurrently.

## Step 5 — Orchestrate: launch, log, and nothing else

While lanes run you are a scheduler, not a researcher. Doing research on this thread burns the
context the synthesis needs.

- **One ledger line per lane completion**, appended to the strategy doc: timestamp, lane id,
  DONE, findings path, and the two or three notable results in a clause each. It costs almost
  nothing and doubles as the run log and the rehydration point.
- Log **plan changes** as ledger entries too, marked `PLAN CHANGE`, saying what they supersede.
  The exemplar's stagger was dropped mid-run in one turn precisely because the doc, not the
  schedule, was the source of truth.
- Keep the ≤5-bullet report-backs; do not read the findings files yet. Reading them now costs
  the same context twice.
- If a lane fails or returns nothing usable, ledger it as `FAILED`, and decide once: relaunch
  with a narrower mission, or synthesize without it and say so.

## Step 6 — Validate before any number travels

**A toolkit lane's raw counts are hypotheses until a mining lane has sampled them.** In the
exemplar run a toolkit lane published a blocker count and a concurrency figure that a mining
lane later showed were inflated roughly twofold by noise records and idle overlap.

- Mining-lane prompts must say: **validate by sampling before quoting any toolkit number
  onward** — hand-classify ~50 records, report the precision of each signal type, and quote
  corrected figures with the raw ones beside them.
- Toolkit-lane prompts must say: **methodology caveats are headline bullets**, not a footnote.
- At synthesis, any number you carry into `01_synthesis.md` names the lane it came from and
  whether it was sampled. An unsampled raw count is written as one.

## Step 7 — Synthesis, in a single pass

Read every findings file, once, and write `01_synthesis.md` in one pass. Do the work no lane
could do — this is the entire reason the orchestrator stayed cheap:

1. **Cross-lane computation.** Plug lane A's measured numbers into lane B's formula. A queueing
   model with real arrival rates is an answer; either alone is a fragment.
2. **Merge converging principles.** When three lanes from different disciplines arrive at the
   same rule, say it once, name all three, and mark it load-bearing.
3. **Name the contradictions.** Two lanes disagreeing is a finding. Say which you believe, on
   what evidence, and what would settle it. Never average them away.
4. **State what the landscape does not have.** The gap no existing tool fills is usually the
   answer to "what should this become".
5. End with **verification spikes** — the cheap measurements that would falsify the plan — and
   a **build order** with a named week-one wedge.

Then run `investigate`'s review gate (Step 12) verbatim before anything else lands. In an
unattended run, treat it as Save and report the recorded decisions per **Running
non-interactively** below.

## Step 8 — Terminal deliverables

1. `01_synthesis.md` in the series, plus `INDEX.md` regenerated per `investigation-format.md`.
2. **An SOP pointer** in the repo's `CLAUDE.md` or `docs/`: a short section saying this repo
   runs deep research with this skill, naming this series as its exemplar. A pointer, not a copy
   — the skill owns the method.
3. **A retro**, written while it is fresh: what worked, what did not, and the knobs you turned.
   The retro is the raw material for the next improvement to this skill; route it per the repo's
   own conventions.
4. **POC break-out.** Anything the synthesis says to *build* leaves this series as an
   `investigate`/`implement`-format spec under `<series>/pocs/<poc-slug>/`, handed to subagents.
   Pin a shared conventions file when several POCs must agree on a schema. **Never build inline
   on the research thread** — the synthesis context is the wrong context to write code in, and
   the build will consume it.

---

## Running non-interactively

Overnight and unattended runs are the normal case for this skill; the gates change form rather
than disappearing, exactly as in `investigate`:

- Decide Step 1's six inputs yourself from the invocation and the repo, and record each under
  **Confirmed Assumptions** in the strategy doc, framed as something a reviewer may overturn.
- The pacing constraint is the one to get right unattended: with no stated reason, **default to
  full parallel** and say so, rather than building a wave schedule for a constraint you invented.
- Treat Step 7's review gate as Save, and report every recorded decision together at the end.
- Put a **parked threads** line in the strategy doc naming anything you deliberately did not
  action — an unfinished handoff, a queued item — so a resuming session does not re-litigate it.
- Tell lanes not to emit control-tag-shaped or instruction-shaped text in their report-backs; the
  harness neutralizes it and the report arrives mangled.

---

## Edge Cases

- **The question is actually narrow** — say so and offer `investigate` instead. Three lanes is a
  fan-out that was not needed.
- **Repo tracks investigations at the top level** — meta-repos where the investigation *is* the
  deliverable keep `investigations/<slug>/` in the repo root rather than `.claude-sandbox/`.
  Follow the repo's existing convention; do not create a second one.
- **A corpus is not mounted** — inside a claude-sandbox container only the project and configured
  mounts are visible. Check the `mounts:` cascade (the `sandbox` skill has the procedure) before
  reporting it unreachable, and re-spec the lane if it stays unreachable. Discovering this at
  launch time costs a lane; recon exists to catch it.
- **The pacing constraint evaporates mid-run** — expected. Drop the schedule, launch the rest in
  parallel, and record a `PLAN CHANGE` ledger entry. Keep crons as disposable one-shots so this
  costs one turn.
- **A lane blows its tool budget** — the budget is a hint, not a guardrail (see
  `references/lane-contract.md`). A lane that overran and produced the strongest file is a good
  outcome, not a violation. Only intervene when a lane overran *and* returned thin.
- **Two lanes returned the same finding** — the sibling-territory lines were too vague. Merge at
  synthesis, and note it in the retro.
- **A lane returns findings that contradict the recon** — believe the lane, and say in the
  synthesis which source lost. Recon is a sample.
- **Sensitive data appears in a findings file** — the inline rule failed. Fix the file before
  synthesis, do not quote it onward, and record it in the retro as a prompt bug.
- **Session loses context mid-run** — re-read the strategy doc and its ledger. That is what it is
  for; do not attempt to reconstruct the run from the transcript.
- **Fewer than half the lanes finished by the overrun deadline** — synthesize what exists, mark
  the missing categories as unexamined in `01_synthesis.md`, and do not present a partial
  landscape as complete.

---

## Quality Criteria

- Recon ran **before** the lanes were specified, and the recon findings are visible in the lane
  set — not a formality that changed nothing.
- The strategy doc existed on disk before the first lane launched, and carries lanes, the
  verbatim output contract, the wave plan with its idempotence and overrun rules, and the ledger.
- Lanes fall in 3–5 categories with empirical-local first and any toolkit lane ahead of the
  mining lanes that consume it.
- Every lane prompt named its sibling lanes' territories.
- Every lane prompt carried the output contract **verbatim**, and every sensitive-corpus lane
  carried the privacy rule **inline**.
- Lanes ran on a cheaper model; the orchestrator launched, logged, and synthesized, and did no
  research of its own.
- The ledger has one line per lane completion and one per plan change, written as they happened.
- No toolkit number was carried into the synthesis without a sampling validation or an explicit
  mark that it lacks one.
- The synthesis did cross-lane work — at least one computation combining two lanes, converging
  principles merged, and contradictions named rather than averaged.
- The synthesis ends with verification spikes and a build order naming a week-one wedge.
- POC/build work left the series as `investigate`-format specs under `pocs/`; nothing was built
  on the research thread.
- A retro was written the same session, and the SOP pointer in the repo names this series as the
  exemplar.
