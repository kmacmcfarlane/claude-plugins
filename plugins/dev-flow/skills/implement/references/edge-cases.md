# Edge cases

Loaded from `implement`'s § Edge Cases when a run goes off the main path. Most entries restate a
step's rule at the point you are likely to need it; a few live only here — a `Supersedes` block
naming a missing file, a fan-out merge going red, a worktree with uncommitted changes at
cleanup, two worktrees needing docker compose.

- **No slug given** — use the series the conversation just produced, else list what exists and
  ask. Never guess.
- **Slug not found / no investigations at all** — stop with the error in Step 1.
- **No Proposed Fix in the composed plan** — stop; point at `/investigate <slug>`.
- **Only `INDEX.md` was read** — a bug in the run, not a shortcut. Read the serials.
- **A `Supersedes` block names a file that does not exist** — the series is inconsistent.
  Report it and ask before proceeding; do not silently pick an interpretation.
- **An open question is marked blocking** — resolve or explicitly waive before Step 7. If the
  user defers a blocker, implementation waits.
- **A question carries no blocks-or-not marking** — decide yourself and state which way you
  called it.
- **A deferred question is answerable by the end of the build** — close it at Step 10c with its
  evidence. A resolved question must not survive into the record.
- **A question deferred twice with no movement** — offer to spin it onto its own investigation.
- **The recorded base branch has merged** — say so and get agreement before switching to the
  default.
- **Code drifted since the investigation** — record the drift, present it at gate 1, let the
  user decide whether the plan still holds.
- **An in-scope issue the investigation missed** — surface via `AskUserQuestion`. Never
  silently expand or silently ignore.
- **The project has no tests** — verification is build-only or run-only. State the tier, and do
  not fan out (the merge gate is missing).
- **Fan-out merge goes red** — stop merging. Report which task broke it and what you tried.
- **A worktree has uncommitted changes at cleanup** — never remove it automatically. Surface it
  and ask.
- **Two worktrees need docker compose and the project has no scoping variable** — serialize
  those tasks; do not run compose concurrently.
- **Verification blocked on a human action** — ask the user to do it and finish the check in
  this run. Do not mark it deferred for convenience.
- **User rejects at gate 1** — nothing changed, clean stop.
- **User rejects at gate 2** — discard changes, remove worktrees, delete branches, clean stop.
