# Quality criteria

Loaded from `implement`'s § Quality Criteria: the checklist a finished run is held to, by you
before the Step 11 report and by any reviewer of the run. Each line restates a step's rule as an
outcome; the step owns the rule.

- **The entire series was read in serial order with every `Supersedes` applied** before any
  code was written, and again after any pause.
- Open questions were triaged before code: staleness re-checked first, the verifiable batch in
  **one** background agent launched before Steps 4–6, decisions asked at gate 1 with a defer
  option, and **no blocking question left unresolved** at Step 7.
- Deferred questions were revisited at Step 10c and closed where the build answered them.
- The recorded base branch was re-verified, not trusted blindly; a non-default base was never
  adopted without explicit consent.
- `file:line` citations were re-verified against current `HEAD`, scoped by the provenance SHAs.
- Fan-out happened only with three or more independent tasks **and** a working merge gate;
  otherwise the work was inline, and the choice was stated.
- Every worktree merge was gated on that task's verification, and the **full** verification was
  re-run on the integration branch after each merge.
- **The verification tier reached is stated explicitly**, with its command and its gaps. A lower
  tier is never reported as a higher one.
- Both review gates fired before any commit, push, or write to the investigation record.
- Files were staged specifically; commit messages follow `<verb>: <aspect> - <description>`.
- The terminal action is exactly what the user chose — nothing pushed, tagged, or opened beyond
  it.
- The outcome file was written at the next free serial with a `Supersedes` block, and existing
  serials were neither edited nor deleted.
- `INDEX.md` was rewritten wholesale, with no row left `pending` that was actually implemented.
- Documentation the change made wrong was fixed, not deferred.
- Worktrees were cleaned up, or their retention was reported with a reason.
