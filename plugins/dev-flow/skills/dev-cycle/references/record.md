# Record line shapes

Fixed shapes for the lines the steps append to the record sink; every step that writes
one uses this exact shape, and each shape below names the step, or steps, that write it —
**one writer per role**, so that no two steps can write the same line about the same
thing. Two shapes have two writers, each for a different role: `return:` (SKILL.md
§ Step 3.5 for an implementer, § Step 1 for a planner) and `answer:` (§ Decisions for a
raised decision, SKILL.md § Step 3.5 for a `NEEDS_CONTEXT`). The
record is a log, read in the order it was written:

- `dispatch: <role> <model> — <signal>` — SKILL.md § Step 2 rule 7, written before every
  dispatch (implementer, planner or reviewer)
- `agent: <role> <id> round <n>` — SKILL.md § Step 2 rule 7, written as soon as the Agent
  call returns an id, directly under the `dispatch:` line it belongs to. `<n>` is the
  round that dispatch serves (the first build or the first review is round 1). It is what
  SKILL.md § Step 4.3 resumes an agent by and what a caller copies into a handoff: an id
  that lives only in `ListAgents` is gone with the process, so the record carries it. A
  `dispatch:` with no `agent:` under it means the Agent call never returned an id.
- `return: <role> <STATUS> <token>` — SKILL.md § Step 3.5 for an **implementer** and
  SKILL.md § Step 1 for a **planner** (`plan` mode never reaches Step 3, so Step 1 is its
  only producer-return writer), written as soon as the producer's report comes back.
  `<STATUS>` is its `DONE` | `DONE_WITH_CONCERNS` | `NEEDS_CONTEXT` | `BLOCKED`;
  `<token>` is the implementer's COMMIT sha, or the series path a planner wrote. A
  reviewer's return is its `verdict:` line below — it never gets a separate `return:` of
  its own. A `BLOCKED` carries a reason, below.
- `verdict: <V> round <n> at <sha>` — SKILL.md § Step 4.5, written as soon as a
  **reviewer's** report comes back. `<n>` is the review round, counted only for
  `CLEAR`, `NEEDS_CHANGES` and `SHOW_STOPPER` — a `BLOCKED` never reached a verdict on
  the change, so it is never a round (`review-brief.md` § Verdict meanings) and carries a
  reason in place of its round number, below. `<sha>` is
  the HEAD reviewed for a change; for a **plan-mode** review, in its place:
  `at <series path>` (the review covers the whole series, not one sha) — a finding's own
  file:line still names the serial, and `baseline:` below, not this field, is what says
  whether the series has moved.
- The **`BLOCKED` reason**, on a `return:` and a `verdict:` and on no other line:

  ```
  return: <role> BLOCKED <token> — permission | setup
  verdict: BLOCKED at <token> — permission | setup
  ```

  `<token>` is what the dispatch was pointed at — the HEAD it was given, or the series
  path — and on a `BLOCKED` it is a **locator only**, saying what the setup failed on. It
  is never a freshness token: a `BLOCKED` reached no verdict on the change, so nothing
  compares it against anything. Where the writer has no such value (a reviewer blocked
  before it could read the workspace), it writes the workspace instead, and never
  fabricates a sha.

  The reason is a closed set of two values, taken from the agent's own report by the step
  that writes the line, never widened and never invented by a reader. `permission` is the
  permission-denial case (`troubleshooting.md` § Dispatch and review): never
  re-dispatched, always a decision for a human. `setup` is everything else — the brief,
  the worktree, the environment — fixable and re-dispatchable within `fix-loop.md`'s
  limit, and not a round. **A `BLOCKED` line with no reason reads as `permission`**, the
  conservative value, so a line written before this shape existed still has one.
- `baseline: <sha256 list>` — SKILL.md § Step 4.1, written before **every** plan review,
  the first and each re-review alike, with no condition: the output of
  `sha256sum <series>/[0-9][0-9]_*.md` over the serials that review covers. Step 4.1 also
  **reads** the previous one where there is one — from the second plan review on — and
  diffs the fresh output against it: the serials that changed are the ones the planner
  added or rewrote since the review being re-run, and they go into the re-review brief's
  "Files changed, with reasons" slot, which a plan re-review otherwise fills with `none`.
  The `verdict:` line's `at <series path>` cannot say this, naming the series and not its
  state. A list that has not moved means the planner wrote nothing; that is a finding for
  the re-review, not a new baseline.
- `findings: …` — SKILL.md § Step 4.5, written together with a `NEEDS_CHANGES` or
  `SHOW_STOPPER` verdict: the reviewer's FINDINGS section, pasted verbatim, one line per
  finding in the reviewer's own numbering — the source `fix-loop.md`'s NEEDS_CHANGES
  round hands to the fix dispatch unchanged.
- `target: <mode> <ref> <workspace>` — SKILL.md § Step 0.3, **every mode**, written before
  any dispatch.
  - `<mode>` is one bare word, `full` | `plan` | `review` — **one token wide in every
    mode**, since `review <branch>`'s branch is already `<ref>` and the line would
    otherwise carry it twice and shift the fields a reader counts. It is recorded, never
    inferred later, and it names **the path the run takes, not the word the user typed**.
    Decide it in this order: `review` when the invocation was `review <branch>`;
    otherwise `plan` when the run takes SKILL.md § Step 1's plan-agent bullet, which
    produces a series, reviews it with the plan-review variant and ends at Step 6 without
    a worktree; otherwise `full`. Keying on the bullet rather than on the word "spike" is
    what keeps a spike whose target already has a series — which skips Step 1 and goes on
    to Step 3 and Land (SKILL.md § Step 1's preamble) — recorded as the `full` run it is.
  - `<ref>` is the target as the run was given it: the branch (`review`), or the
    item id, series slug or plan path (`full`, `plan`). It says what was asked for; the
    workspace says where the work is.
  - `<workspace>` is the **absolute** path the run's work lives at, and it is written
    absolute even when the command that made it took a relative one: the path § Review
    target resolved (`review`), `"$MAIN"/.claude/worktrees/<name>` for the
    worktree SKILL.md § Step 3.1 adds (`full`), or — a plan run having no worktree — the
    series path under the Series home. A later step, or a later session, runs
    `git -C <workspace>` from a working directory this one cannot predict, so a
    repo-relative path here resolves against the wrong tree.

  Every later step reads the workspace from this line instead of reconstructing it.
- `intent: <one line>` — § Intent, `review <branch>` mode with no item or plan
- `decision: <question> — options: <a> | <b> | <c>` — § Decisions, written before a
  decision is raised. **Self-contained**: the question in full and its options,
  recommendation first, so that a reader who was not in the session that raised it can put
  it to a human verbatim. Under a caller it composes as
  `decision N: <question> — options: …`, so the caller's numbered channel is unchanged.
  **Exactly one decision carries a tag**: SKILL.md § Usage's `review <branch>` ask,
  whether to dispatch an implementer for the findings, is written
  `decision: dispatch-permission — <question> — options: <a> | <b>`, and under a caller
  the same tag follows the number of `decision N:`. The tag is a fixed identifier, not a
  kind: every other decision is untagged. It lets a later reader find that one decision
  by name; what its answer's scope is, § Decisions says.
- `answer: <decision> — <reply>` — § Decisions and SKILL.md § Step 3.5 (a
  `NEEDS_CONTEXT` answer), written as soon as the reply arrives; `<decision>` repeats the
  `decision:` line's question (or, for a `NEEDS_CONTEXT`, the question) — for the one
  tagged decision, its tag instead: `answer: dispatch-permission — <reply>`. A caller's
  numbered pair — librarian-mode's `decision N: …` and `answer N: <reply>`, matched by
  `N` — is the same pair and is read the same way; its `answer N:` carries no tag, the
  number already pairing it. A `decision:` with no matching `answer:` is **pending**
  (§ Decisions says what a run does with one), and an answered one is never raised again
  while its answer is in force (§ Decisions).
- `spent:` — § Resume's line, which writes and reads it. § Resume is not specified yet,
  so nothing writes one until it is.
- `landed: <merge sha>` — SKILL.md § Step 5.5, written once Land's merge succeeds and
  before `$WI done` / `$WI handoff`. It is the record's only evidence that a target
  reached a merge, and SKILL.md § Step 6 reports it on the `verified:` line. `Leave the
  branch` lands nothing and writes no `landed:` line.
- `checks:`, the `changed:` block — §§ Checks, Undeclared files
