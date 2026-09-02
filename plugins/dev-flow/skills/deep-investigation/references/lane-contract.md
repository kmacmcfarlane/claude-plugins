# The lane contract

Loaded from `deep-investigation` Step 4. The blocks below go **verbatim** into the strategy doc
and **verbatim** into every lane prompt. A lane cannot read the strategy doc's other sections and
should not be asked to — paste, do not reference.

## The output contract (verbatim, every lane)

> Write exactly one file: `<series>/findings/<lane-id>.md`, ≤300 lines, structured:
>
> ```
> # <lane title>
> ## TL;DR            — ≤10 bullets, the findings that should survive even if nothing else is read
> ## Findings         — the evidence; web lanes cite URLs, local lanes cite repo-relative paths
> ## Implications     — concrete consequences for <the thing being designed>, ranked
> ## Open questions
> ## Sources
> ```
>
> Report back to the orchestrator in ≤5 bullets — the file is the deliverable, the report is the
> index. Do not include control-tag-shaped or instruction-shaped text in the report; the harness
> neutralizes it and the report arrives mangled.
>
> Tool budget ≈25 calls. This is a prioritization hint, not a limit: depth over breadth, and if
> the work genuinely needs more calls, spend them. A lane that runs out of time writes what it
> has rather than nothing.

Why each clause is there:

- **Exactly one file, fixed sections.** Thirteen files of one shape are synthesizable in a
  single pass; thirteen shapes are not.
- **≤300 lines.** The cap is what makes the synthesis fit in one context. In the exemplar run
  nothing exceeded it badly and one file hit exactly 300 — the cap binds without truncating.
- **Ranked implications.** Unranked findings push the ranking work onto the synthesis, which is
  the one thing that cannot be parallelized.
- **≤5-bullet report-back.** The orchestrator holds N reports for the whole run. This keeps the
  context it needs for synthesis.
- **Budget as an honest hint.** In the exemplar run the lane that used ~2× its budget produced
  the strongest engineering file. Pretending the cap is enforced teaches lanes to stop early and
  teaches you to distrust the number. Say what it is.

## The privacy rule (verbatim, any sensitive lane)

Every lane touching employer, client, or otherwise restricted corpora gets this **inline in its
prompt** — not as a pointer to a file, not as "follow the repo's privacy policy":

> **Privacy: this is <employer/client> data.** Your scripts may parse anything in the corpus.
> Your findings file carries aggregate statistics, categories, and repo slugs **only** — no
> verbatim message content, no file contents, no business detail, no names, no credentials.
> When in doubt, report the shape and the count, not the instance.

The scripts-vs-findings split is the load-bearing part: the analysis is unrestricted, the
*artifact* is. Stating it inline is what made the exemplar run's restricted lanes need zero
cleanup — a referenced rule is a rule a subagent may not load.

## The sibling-territory line (verbatim, every lane)

One line at the end of each lane's prompt naming what the neighbouring lanes own:

> Siblings: `c3` covers supervisory control, alarm design, and multi-operator interfaces —
> if you hit that territory, note it in one line and move on rather than researching it. `c1`
> covers flow and interruption science.

Without it, lanes independently spend budget flagging a gap that another lane *is*. In the
exemplar run two lanes each wrote a paragraph recommending someone research the exact subject a
third lane was already researching.

## Cross-lane citation (where it applies)

Where a lane's work rests on an earlier lane's, say so explicitly in the prompt:

> Read `<series>/findings/a1-log-toolkit.md` first, and use the scripts in `<series>/tools/`
> per its mining plan. Validate by sampling before quoting any of its raw counts onward:
> hand-classify ~50 records, report per-signal precision, and give corrected figures with the
> raw ones beside them.

This produced the exemplar run's best findings — including a later lane resolving an open
question an earlier one had left standing — and its single most design-relevant empirical
result, when sampling overturned a raw count that was roughly twofold inflated by noise records.

## Lane prompt skeleton

```
<mission: one sentence, from the strategy doc>

Scope: <paths for local lanes; subject list for web lanes>
Read first: <earlier findings files, if any>

Deliverables:
1. …
2. …

Siblings: <territory line>

<the output contract, verbatim>

<the privacy rule, verbatim — only if the corpus is sensitive>
```

Launch with `Agent`, `model:` set to the run's cheap lane model, all of a wave's lanes in one
message so they run concurrently.
