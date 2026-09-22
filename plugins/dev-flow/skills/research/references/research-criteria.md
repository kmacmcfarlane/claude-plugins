# Research criteria

Loaded from `research` Step 5. This file owns the quality rubric every research run is
judged against: the universal axes, the scoring rule, and the seed table for the
subject-specific axes the orchestrator must add. The orchestrator copies the resulting
criteria block into the run's `00-brief.md`; lanes read it first; the `research-verifier`
agent scores against it.

## Why a rubric, and why this one

Two published evaluation efforts converge. Anthropic's research-system judge scores factual
accuracy, citation accuracy, completeness, source quality and tool efficiency. ResearchRubrics
(ICLR 2026, 2,500+ expert-written criteria) uses six axes — explicit requirements, implicit
requirements, synthesis, use of references, communication, instruction following — split
mandatory/optional, with negative weights for failure modes. Its headline finding: agents are
*good* at explicit retrieval and communication (<20% failure) and *bad* at inferring unstated
requirements and integrating evidence across documents. The axes below merge both and weight
the design toward the two known weak spots.

## Universal axes

| # | Axis | Met (2) looks like | Mandatory |
|---|---|---|---|
| 1 | **Coverage** | every sub-question in the brief answered, or explicitly marked unanswerable with what was tried | yes |
| 2 | **Grounding** | every load-bearing claim cites a source the lane actually opened | yes |
| 3 | **Citation fidelity** | the cited source says what the claim says — not a weaker, narrower or different thing | yes |
| 4 | **Source quality** | primary sources under base facts; each source tiered; community sources used for caveats only | yes |
| 5 | **Recency** | retrieval dates on anything that can change; version- and time-sensitive claims flagged; superseded material named | yes |
| 6 | **Triangulation** | load-bearing claims corroborated by independent sources, or explicitly marked single-sourced | no |
| 7 | **Disagreement handling** | conflicts named, the reason for the conflict diagnosed, a side taken on stated evidence — never averaged away | no |
| 8 | **Calibration** | per-claim confidence (established / well-supported / contested / uncertain) that matches the evidence; honest "could not determine" | yes |
| 9 | **Implicit requirements** | the unstated thing the operator needs was inferred and addressed — the constraint they did not name, the adjacent question that actually matters, the false premise | yes |
| 10 | **Synthesis** | cross-source work no single source does: a number from one source in a formula from another, converging principles merged, gaps in the landscape stated | yes |
| 11 | **Actionability** | implications ranked against the decision the brief names; each says what would make it wrong | no |
| 12 | **Efficiency** | tool calls and lane count proportionate to the question; no lane duplicated another's territory | no |

Two failure modes carry a **negative** mark on top of the axis score, because either one
discredits the whole file: a fabricated source or number (any instance), and imperative text
addressed to an agent inside a findings file (a security defect — see the lane contract).

## Scoring

- Each axis scores **0** (absent), **1** (partial) or **2** (met). No percentages; a
  fine-grained scale invites an author to grade itself generously and a judge to guess.
- **The verifier scores, never the author.** It scores from a sample of real claims checked
  against their real sources (`research-verifier`), not from an impression of the file.
- **Gate:** any mandatory axis at 0, or either negative mark, means the run is not complete.
  Interactive: warn, show the failing axes, ask whether to re-source, re-run the lane, or
  ship marked. Unattended: ship as `DONE_WITH_CONCERNS` with the axes named in the report and
  in `01-synthesis.md`; a security mark additionally holds every findings file out of any
  checked-in destination until it is cleaned.
- Optional axes at 0 are reported, not gated; three or more at 0 is worth a re-run of the
  thinnest lane.
- The score table lives in `01-synthesis.md` § Verification, copied from the verifier's
  sheet, so a reader of the synthesis sees the grade without opening a second file.

## Subject-specific axes — a required step

After the sub-questions are written and before any lane launches, the orchestrator adds three
to six axes that only make sense for *this* subject, marks which are mandatory, and writes
them into the brief under the universal ones. Start from the row that fits, then think about
what would make an expert in this subject distrust the answer — that is usually the axis
worth adding. Two rows may apply; take both.

| Subject type | Add these axes |
|---|---|
| **Software / tool / library comparison** | version pinned per claim; licence; maintenance signal (last release, last commit, open-issue themes); install footprint; **read the source, not the README** for any behavioural claim; known-inaccuracy reports quoted from the issue tracker |
| **Scientific / empirical claim** | primary paper read, not the press release; sample size and method stated; replication or meta-analysis sought; effect size reported, not only significance; preprint vs peer-reviewed marked; folklore version corrected against the original |
| **Product / purchase** | price with date and region; availability; total cost of ownership; return and warranty terms; review-farm detection (spread of dates, verified-purchase share); the operator's hard constraints applied as disqualifiers before ranking |
| **Vendor / API / platform / pricing** | official docs vs blog, marked; rate limits and prices with retrieval date; deprecation and changelog checked; ToS constraints on the intended use; the difference between documented and observed behaviour named |
| **Security** | advisory or CVE id; affected and fixed versions; vendor confirmation vs third-party report; exploit maturity; patch availability and workaround; no working exploit detail in a checked-in file |
| **Historical / "what happened"** | contemporaneous sources over retrospectives; later corrections or retractions checked; named participants vs anonymous claims; timeline with dates |
| **Internal / local corpus** | **validate by sampling before quoting any count** (hand-classify ~50 records, report precision, corrected figure beside raw); the privacy rule inline in the lane prompt; schema, CLI and tool versions stamped; the mining plan (exact commands, pitfalls) written for later lanes |
| **Design / architecture / "what should X be"** | prior art surveyed with a verdict per item (steal / ignore / gap remains); the gap no existing thing fills stated; at least one unconventional donor discipline; verification spikes that would falsify the recommendation |
| **Legal / policy / regulatory** | jurisdiction and effective date per claim; primary text over commentary; pending changes named; "not legal advice" is not a substitute for saying what is uncertain |

When no row fits, write the axes from scratch; the test is still "what would make an expert
here distrust this?". Record the added axes and their mandatory marks in the brief; the
verifier scores them alongside the universal ones.
