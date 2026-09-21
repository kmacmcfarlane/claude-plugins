# Quality criteria

Loaded from `investigate`'s § Quality Criteria: the checklist a finished run is held to, by
you before the report and by any reviewer of the series. Each line restates a step's rule as
an outcome; the step owns the rule.

- The scoping gate ran before exploration, or its omission was stated and justified.
- Project context is loaded before searching, trimmed to what applies, with a reason per
  omission.
- Context-heavy exploration was delegated to subagents; `file:line` findings came back, not
  file dumps.
- Claims about what the code does are backed by having run the build or tests, not by reading
  alone, wherever running was possible.
- Where the plan rests on a low-level nuance of a tool's behaviour, the tool's **source** was
  read and cited — or the claim is marked as documentation-only for `implement` to re-verify.
- Where it rests on a fact outside the codebase, the **primary** source was opened and cited,
  or the claim is marked secondhand; and any such fact contradicted by the live system was
  reconciled rather than left standing.
- Where the plan offered genuinely-open alternatives, a discriminating measurement was taken
  before one was recommended — or its absence is stated and the dependent choice flagged.
- Any new convention the work introduces was checked against existing ones first; adopting an
  existing convention is the default, and diverging is stated and justified in the plan.
- The requirements gate **blocked** the plan and looped until the user confirmed there was
  nothing left — including looping back to exploration when an answer opened a question the
  code could settle.
- The sweep ran against the drafted plan before anything was written: candidates classified,
  the verifiable batch in **one** background agent launched *before* the user was asked,
  a defer option on every user question, looping until a round produced nothing new. Its
  outcome is reported at the gate.
- Open Questions contain **only** genuinely external or blocked items, each naming an owner
  and whether it blocks implementation.
- Findings cite `file:line`, and are flagged as point-in-time.
- Blast radius is assessed and stated — including an explicit "self-contained" when it is.
- The file follows the standard outline and the writing rule, and carries a concrete
  **Proposed Fix** or **Implementation Approach**.
- Serials are append-only: a re-investigation writes the next serial with a `Supersedes` block
  and edits nothing.
- `INDEX.md` was rewritten wholesale with a provenance line carrying per-repo SHAs.
- The review gate fired before anything was written to disk.
