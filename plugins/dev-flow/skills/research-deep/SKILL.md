---
name: research-deep
description: Run the research skill at deep or exhaustive intensity for a subject too broad for one round — two or three rounds of research lanes on a cheaper model, a gap gate between rounds, an adversarial lane at exhaustive, a larger verifier sample, and a synthesis that may run in a fork; lands as a run record or knowledge-base notes. Use when the user says "research this thoroughly", "exhaustive research on", "research this from every angle", "thorough sourced research", or when the research skill proposes it after a quick run finds its core claim contested or thin. Not for a fan-out that writes an investigation series' plan — "deep research", "map the landscape of", "research this overnight" for a build decision are deep-investigation — nor a bug or feature in this repo (investigate).
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, WebSearch, WebFetch, Agent, AskUserQuestion, Write
argument-hint: "<broad question> [--intensity deep|exhaustive] [--shape run|kb] [--to <path>]"
---

# Research — deep

The `research` skill run at `deep` (default) or `exhaustive`, with the parts that only matter
at that scale spelled out. **Read the `research` skill's SKILL.md first and follow it
verbatim**; this file is the delta, not a restatement. Everything about destinations,
criteria, the brief, the verifier and the landing is owned there and in its `references/`.

`disable-model-invocation` is `true` here on purpose: a deep run is roughly fifteen to thirty
chat turns of usage, and it is launched by a person, or by `research` proposing it and the
operator saying yes — never by a model that loaded a skill on a keyword.

## Usage

- `/research-deep what should our observability stack look like for a hundred agent sessions`
- `/research-deep map the landscape of local-first sync engines --intensity exhaustive --shape kb`
- `/research-deep <slug>` — resume a deep run from its brief

## The delta

### Step 1 — Inputs

`research` Step 1, plus: ask for the **pacing constraint and its reason** if the operator
has one (a usage window resetting at a known time, a review they want between rounds). The
reason matters more than the constraint — scheduling machinery built for a constraint that
evaporates is wasted work, and it has been. Without a stated reason, every round launches
its lanes in full parallel.

### Step 3 — Intensity

`deep` unless the invocation says `exhaustive`. The quota table still applies: a hot
five-hour window downgrades to `standard` or defers to `resets_at`, and says so. Print the
cost line.

### Step 5 — Lanes

At this scale the lane set is 8–15 (deep) or 15+ (exhaustive) in three to five categories,
and the ordering rules earn their place:

- **Empirical-local first, toolkit ahead of mining.** A toolkit lane reverse-engineers a
  format, ships validated scripts under `tools/` and a *mining plan* (exact commands, known
  pitfalls); the mining lanes in the same round read it first and spend their budget on
  classification, not parsing. Mining-lane prompts say: validate by sampling before quoting
  any toolkit number onward.
- **Landscape lanes** carry a verdict per item found: steal / ignore / gap remains.
- **At least one unconventional lane** — a donor discipline that sounds like colour.
- **At `exhaustive`, one adversarial lane** (`a1-…`, launched with `model: opus` on the call)
  whose mission is to break the answer forming in the round-1 TL;DRs: find the strongest
  evidence against it, the premise it rests on, the case it does not cover. It reads round 1
  first, so it runs in round 2.
- **Siblings lines are not optional at this scale.** With fifteen lanes, two will otherwise
  spend their budget flagging a gap that a third lane *is*.

Search budget: divide the preset's budget across the round's web lanes in each prompt as a
hint; local lanes cost none. Expect exhaustion at `exhaustive`; brief lanes to fetch known
URLs and primary documents rather than search for summaries.

### Step 7 — Rounds

The gap gate runs after each round; the cap is 3. Round 2 is expected at `deep` and
mandatory at `exhaustive` (the adversarial lane). Round 3 launches only on a gap condition
and never on "it might find more". The threads-not-pulled turn runs after every round: in an
interactive run the operator decides whether to spend round 3 on them; in a chained or
unattended run the run continues and the report carries them.

Waves *within* a round exist only for the pacing reason from Step 1, fired from a one-shot
wakeup whose prompt is "read `<brief>` and launch round N wave M" and nothing more — never a
prompt that restates the lanes. The wakeup acts on the brief's § Lanes and ledger status
lines, which the orchestrator wrote; it never reads a findings file to decide what to launch. State the idempotence rule in the brief (a wave launches only
if its findings files do not exist and the ledger does not mark them launched) and the
overrun rule (synthesis starts by time T with whatever exists; hard stop T+1h). When the
constraint evaporates mid-run — it usually does — drop the schedule, launch the rest, ledger
`PLAN CHANGE`.

### Step 8 — Verify

Sample size 20 (deep) or 30 (exhaustive); the verifier prompt says so. At `exhaustive` the
adversarial lane's findings are in the sample by construction.

### Step 9 — Synthesis

Assume the fork. Fifteen findings files at ≤300 lines are up to 4,500 lines; that is past the
fallback threshold, so plan for a forked synthesis unless `context-guard` says the window is
fresh. The fork's prompt is the brief path, the findings paths, `verification.md`, and
`research` Step 9's list. Its output is `01-synthesis.md`; you read that, not the findings.

The synthesis at this scale ends with two extra sections: **verification spikes** — the
cheap measurements that would falsify the answer — and, when the question was "what should X
be", a **build order** naming a week-one wedge. Anything the synthesis says to *build* leaves
the run as an `investigate`-format spec; nothing is built on the research thread.

### Step 10 — Land

As `research`. A deep run into a KB is the case most likely to return `STRAINED` from the fit
check — fifteen lanes produce many notes — so read the fit-check verdict before promoting,
and prefer fewer, denser notes over one per lane.

### After

Write a **retro** while it is fresh: what worked, what did not, which knobs you turned
(rounds, waves, budgets, lanes that overran and were worth it). Route it per the repo's
convention (a `retro/` dir when there is one; otherwise `<run>/retro.md`). The retro is the
raw material for the next change to these skills.

## Running non-interactively

As `research`, plus: the pacing constraint defaults to none (full parallel per round) and is
recorded; round 3 needs a gap condition, not a preset; the retro is still written.

## Edge Cases

- **The question is narrow** — this skill was the wrong call; say so, run `research` at
  `standard` and note the downgrade in the report.
- **The fan-out is meant to write an investigation series' plan** — `deep-investigation`.
- **Fewer than half the lanes finished by the overrun deadline** — synthesize what exists,
  mark the missing categories unexamined in the synthesis, and do not present a partial
  landscape as complete.
- **A lane blew its budget and produced the strongest file** — a good outcome, not a
  violation; the budget is a hint. Intervene only when a lane overran *and* returned thin.

## Quality Criteria

`research`'s, plus: the pacing reason (or its absence) is in the brief; empirical-local and
toolkit lanes preceded mining lanes; every lane prompt carried a siblings line; at
`exhaustive` an adversarial lane ran in round 2 on a stronger model; no toolkit number was
carried into the synthesis without a sampling validation or an explicit unsampled mark; the
synthesis ends with verification spikes; build work left the run as specs; a retro exists.
