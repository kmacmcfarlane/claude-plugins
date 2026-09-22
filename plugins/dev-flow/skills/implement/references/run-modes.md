# Run modes

Loaded from `implement`'s § Running non-interactively and § Running under an orchestrator,
before Step 2 whenever the invocation is unattended or another skill dispatched this one. The
SKILL.md keeps each section's heading and a summary; this file holds the full rules. Steps are
named as well as numbered; a renumber in the SKILL.md updates this file in the same commit.

## Running non-interactively

When the invocation says to run without stopping, the gates change form rather than vanishing:

- **Gate 1 (Step 6, the plan)** — decide yourself, and record each decision under
  **Confirmed Assumptions** in the outcome file, framed as something a reviewer may overturn.
- **Gate 2 (the diff)** — approve only on a passing verification at the planned tier. A failing
  or incomplete verification is still a stop: report it and leave the work uncommitted.
- **Step 10a (terminal action)** — do the least irreversible thing the invocation authorises.
  Absent an explicit instruction, commit locally and leave the push to the user.
- **Step 4 (base drift)** — the recorded base holds. Leaving it, or adopting a non-default
  base nobody recorded, is a blocking **Open Question**: stop. An unresolved repo is the same:
  stop, never clone silently.
- **Step 7 (a plan revision or a missed in-scope issue)** — a plan revision: take the least
  irreversible choice (carry it into the outcome file) and record it under Confirmed
  Assumptions. A missed in-scope issue is a finding, not license to expand scope: record it as
  a non-blocking **Open Question**, never silently fixed and never silently dropped.
- **Step 8 (a step needing human action)** — record it as manual, deferred; verification is
  then incomplete, so Gate 2's stop applies. (Running under an orchestrator differs on
  purpose: it commits and lists the step under COULD NOT DO.)
- A **blocking** open question still blocks. Say so and stop rather than guessing past it.

Report every recorded decision together at the end so the user reviews them in one pass.

## Running under an orchestrator

When another skill dispatches this one as a sub-agent (`dev-cycle`'s implementer, a
`deep-investigation` POC break-out), the orchestrator owns git, landing, the work item and
every dialog. It gives the **series** (a directory, anywhere, or a single plan file), the
**worktree** to edit in and the **base** branch, and its brief sets the commit. Run as
**Running non-interactively** above, with these changes. Steps are named as well as
numbered; a renumber updates this list in the same commit.

- **Step 1 (Resolve the series)** — skipped. Take the given series and start at Step 2
  (Read the whole series); a single plan file is the whole plan.
- **Step 4 (Resolve repos and re-verify the base branch)** — skipped: no fetch, no branch,
  no worktree. The given base holds. Every edit goes in the given worktree; nothing is run
  or written in the main checkout.
- **Step 6 (gate 1) and Step 9 (gate 2)** — non-interactive. Gate 1's decisions go under
  DEVIATIONS in the return, since there is no outcome file to hold them. Gate 2 passes on
  verification at the planned tier; the orchestrator's review replaces its approval. A
  failing verification is still a stop, reported, never committed around; a verification
  incomplete only by a human-gated step is Step 8's case — committed, not a stop.
- **Step 7 (Implement)** — inline only, in the given worktree: no fan-out, no
  `EnterWorktree`, no integration branch, no merge. Before the first edit, regenerate
  anything checked in that the base may carry stale (codegen, mocks, generated clients) in
  the given worktree; a diff means the base shipped stale ones — reconcile it and say so
  under DEVIATIONS. A plan revision or a missed in-scope issue is reported (DEVIATIONS,
  OPEN QUESTIONS), never recorded on the series or silently built.
- **Step 8 (Verify)** — a step that needs a human action is not a wait: commit once the
  rest passes at the planned tier, and list the human-gated step under COULD NOT DO.
- **Step 10 (Finalize)** — only **10d (Documentation follow-ups)** runs, inside the worktree
  and inside the same change, without the propose step: a doc the change made wrong is part
  of the change. It edits existing docs only, and a fix outside the orchestrator's declared
  scope goes under OPEN QUESTIONS. No terminal action (10a), work-item update (10a½),
  outcome (10b) or index write (10c). Commit once, as the brief says, with 10a's hygiene.
- **Step 11 (Report), Step 12 (Retrospective)** — replaced by the return below; no retro.
- **Questions** — never `AskUserQuestion`. Take the least irreversible choice and record it
  under DEVIATIONS; one that blocks goes under OPEN QUESTIONS, with `NEEDS_CONTEXT` when you
  cannot go on.

Stop after verify and commit, and return this shape (a brief that adds fields, such as
COMMIT, wins):

```
STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
CHANGED: files, absolute paths, a phrase each
VERIFIED: each command, its outcome and the tier reached
DEVIATIONS: from the plan or brief, with why
COULD NOT DO: anything asked for that is not in the commit
OPEN QUESTIONS: each marked blocking or not
```
