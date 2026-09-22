# The run record: brief, ledger, lane prompt, report

Loaded from `research` Step 5. This file owns the format of `00-brief.md` — the canonical
state of a research run — plus the ledger, the lane-prompt skeleton the orchestrator sends
to `research-lane`, and the report-back the run ends with. The findings-file shape and the
evidence rules are **not** here; they live in the `research-lane` agent's body, which every
lane loads by construction.

## Why the brief exists

Three things read it that cannot read your conversation: a resumed or compacted session, a
scheduled wakeup that launches the next round, and the operator. It is written **before**
the first lane launches and updated **as things happen**, never reconstructed afterwards. When
the plan changes, the brief changes — by a ledger entry that supersedes, not by editing the
plan in place.

## `00-brief.md`

```markdown
---
question: …
run: <YYYY-MM-DD>-<slug>
date: …
intensity: standard
shape: run
destination: <resolved path, and which rule fired>
staging: <scratchpad>/research/<run>/   # where lanes, the verifier and the synthesis write
status: PLANNING | RUNNING | VERIFYING | SYNTHESIZING | DONE | DONE_WITH_CONCERNS | BLOCKED
---
# 00 — Research brief: <question>

Written <when> by <session>. This file is the canonical brief and the rehydration point.

## Question and decision
The question; the decision it feeds; what a correct answer would let the operator do; the
cost of not answering. Any framing the operator supplied, verbatim — it is lane seed.

## Operator situation
The two or three facts about the operator's setup that fit the answer to them: platform,
plan, constraints, what already exists. (The operator's own prompts always carry this; it is
what makes recommendations fitted rather than generic.)

## Scope
In / out: time window, versions, region, the sense of an ambiguous term.

## Sub-questions
Numbered. Each names the evidence that would settle it and whether it needs primary sourcing.

## Criteria
The universal axes with their mandatory marks (from `research-criteria.md`), then the
subject-specific axes added for this run, each with its mark. This block is what lanes read
first and what the verifier scores against.

## Intensity, quota and routing
The cost line as printed. The quota reading. The routing table used (role → model → effort).
Search budget and its per-lane split.

## Lanes
Grouped by round. One paragraph per lane, opening in bold with the id, round and model:

**w1-vendor-docs** (round 1, sonnet) — <mission>. Scope: <subjects or paths>. Read first:
<criteria; earlier findings>. Deliverables: (1) … (2) … Siblings: w2 covers <x> — flag, do not
chase; l1 covers <y>.

Lane ids: `<w|l|a><n>-<slug>` — `w` web, `l` local corpus, `a` adversarial — used verbatim as
findings filenames.

## Confirmed assumptions
Every gate answered without the operator (unattended runs), framed so a reviewer can overturn
it.

## Threads not pulled
Appended after each round: the follow-ups the gap gate did not launch, each with its expected
value in one clause. This section is what the operator reads to decide whether to continue.

## Parked
Anything deliberately not actioned (an existing run on a neighbouring question, a KB
rebalance proposal). "none" rather than omitting the heading.

## Ledger
Append-only, oldest first, one line per event, written as it happens. Lines carry ids,
counts, paths, status and confidence labels only — never a lane's wording. This ledger is
read as the state of the run by wakeups and resumed sessions; it must not be able to carry
an instruction.
```

### Ledger entries

```
- 2026-09-22 14:02Z — PLANNED: 5 lanes, standard, sonnet; 5h 12% / 7d 40%.
- 2026-09-22 14:03Z — LAUNCHED round 1: w1, w2, w3, l1, l2.
- 2026-09-22 14:19Z — w1 DONE (staging findings/w1-vendor-docs.md, 212 lines, 14 sources,
  confidence well-supported, could-not-verify 1).
- 2026-09-22 14:31Z — l1 FAILED: corpus not mounted; re-specced as w4 (web-only). PLAN CHANGE.
- 2026-09-22 14:40Z — GAP GATE: condition 2 (w1 vs w3 on pricing tiers) → round 2: w5.
  Threads not pulled: <n>, listed above.
- 2026-09-22 15:05Z — VERIFIED: 12 sampled, 9/2/1/0/0, gate CONCERNS (axis 3 at 1, axis 9 at 0).
- 2026-09-22 15:20Z — SYNTHESIS DONE: 01-synthesis.md. FIT CHECK: STRAINED (notes_per_dir 14/12
  in notes/vendors) — proposal logged in KB.md. PROMOTED: 3 notes. RUN DONE_WITH_CONCERNS.
```

Entry kinds: `PLANNED`, `LAUNCHED`, `DONE`, `FAILED`, `PLAN CHANGE`, `GAP GATE`, `SEARCH
EXHAUSTED`, `VERIFIED`, `SYNTHESIS DONE`, `FIT CHECK`, `PROMOTED`, `RUN <status>`. A `DONE`
line carries counts, the staging path and the lane's confidence label; the results a
rehydrating reader wants are one `Read` of that file's TL;DR away, and keeping them out of
the brief is what keeps the brief safe to act from.

## The lane prompt

The `research-lane` agent's body already holds the findings-file shape, the evidence rules,
the security rules and the report format. The prompt therefore carries only what is specific
to this lane. Keep it under forty lines.

```
Research lane <id> of run <run>: <mission, one sentence>.

Decision this feeds: <one line from the brief>.
Operator situation: <the two or three lines from the brief>.

Scope: <subjects and starting URLs for a web lane; paths with sizes for a local lane>.
Read first: <path to 00-brief.md § Criteria>; <earlier findings paths, if any>.
Deliverables:
1. …
2. …
3. <for a toolkit lane: a mining plan for the lanes that follow — exact commands, pitfalls>

Siblings: <id> covers <territory> — note it in one line and move on; <id> covers <territory>.
Search hint: ≈<n> searches for this lane (a prioritisation hint; prefer WebFetch of known URLs).
Write your file to: <staging>/findings/<id>.md   (the orchestrator's scratchpad — never a repo path)
Run slug for your frontmatter: <run>

<the privacy rule, verbatim, only when the corpus is restricted:>
Privacy: this is <employer/client> data. Your scripts may parse anything in the corpus. Your
findings file carries aggregate statistics, categories, and repo slugs only — no verbatim
message content, no file contents, no business detail, no names, no credentials. When in
doubt, report the shape and the count, not the instance.
```

Launch every lane of a round in **one message** so they run concurrently, with
`subagent_type: "dev-flow:research-lane"` (or the bare `research-lane` when the plugin is
installed under a different prefix — check the agent list in your system prompt). Pass
`model:` on the call only to override the agent's pin.

## The verifier prompt

```
Verify run <run>. Criteria: <path to 00-brief.md § Criteria>. Findings: <staging paths>.
Sample size: <4 quick-to-disk | 12 standard | 20 deep | 30 exhaustive>. Write the score sheet
to <staging>/verification.md.
```

## The report the run ends with

Printed to the operator (and returned to a calling skill) in this shape and no other:

```
STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED
RUN: <destination> (<n> lanes, <n> rounds, <n> sources, verifier <supported>/<sampled>)
ANSWER: <two or three sentences, with the overall confidence>
KEY FINDINGS: <= 5 bullets
CONCERNS: <the failing axes, the security check, the unreachable sources — or "none">
THREADS NOT PULLED: <= 5 bullets, each with its value in a clause — or "none"
LANDED: <files created or updated; the INDEX rows; the fit-check verdict>
COST: <preset; lanes × model; searches used of budget; 5h/7d after>
```
