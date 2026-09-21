# Run modes

Loaded from `investigate`'s § Running non-interactively and § Running under an orchestrator,
before Step 1 whenever the invocation is unattended or another skill dispatched this one. The
SKILL.md keeps each section's heading and a summary; this file holds the full rules. Steps are
named as well as numbered; a renumber in the SKILL.md updates this file in the same commit.

## Running non-interactively

When the invocation says to run without stopping — an unattended session, or "do it and ask
me afterwards" — the blocking gates (Steps 2, 9, 11, 12) do not disappear, they change form:

- Decide each gate yourself and record the decision under **Confirmed Assumptions**, framed
  as something a reviewer may overturn. A silently-made decision is the thing this skill
  exists to prevent.
- A **relayed** decision — one arriving through a peer session, a message, or secondhand
  notes rather than from the operator in this loop — is evidence of intent, not
  confirmation. When it would change behaviour or a default for people not present
  (interactive users, say), record it as an **Open Question that blocks implementation**,
  never as a Confirmed Assumption: the people it affects cannot confirm it in-session.
  The failure this prevents: "agents should use worktrees" relayed into "worktrees on by
  default for everyone", which broke resume history for interactive sessions.
- Anything you would have *asked* becomes an **Open Question** with an owner and a
  blocks-or-not marking. If one genuinely blocks, stop and say so rather than guessing.
- Treat Step 12 as Save, and report every recorded decision together at the end so the user
  reviews them in one pass.

## Running under an orchestrator

When another skill dispatches this one as a sub-agent (`dev-cycle`'s plan agent or
implementer, a `deep-investigation` POC spec), the orchestrator owns git, the work item and
every dialog. It gives a **Series home** (an absolute directory for the series), the
**base** branch and, when it has one, the **worktree**. Run as **Running
non-interactively** above, with these changes, named as well as numbered so a renumber
updates this list in the same commit:

- **Step 1 / 1a (Resolve the issue, the series)** — the orchestrator's brief is the
  description; a work item is read, never claimed. The series lives at the Series home,
  never inside the repo or a worktree; one already there is extended by its next serial.
- **Step 2 (Scoping gate), Step 9 (Requirements gate), Step 11 (Open-question sweep)** — nothing
  asked. The verification agent still runs; each question you would ask becomes an Open
  Question marked blocking or not.
- **Step 3a (Survey open branches)** — skipped, no fetch: the given base holds. Record it in
  Confirmed Assumptions and Deployment & Rollout Notes.
- **Step 6 (Explore)** — create no branch or worktree; a probe that needs repo edits runs in
  a worktree the orchestrator gave, reverted before the plan is written, or is left to
  `implement` to settle.
- **Step 12 (Review gate)** — Save; the orchestrator's review replaces it. **Step 13/14
  (Write, Rewrite the index)** — at the Series home.
- **Step 15 (Report), Step 16 (Retrospective)** — replaced by the return below; no retro.
- Never ask the user — no dialog, no numbered list. Each gate decision you made yourself is a
  Confirmed Assumption, as above, and is listed again under DEVIATIONS in the return.

Return: `STATUS` (DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT or BLOCKED), `SERIES` (the absolute
path), `OPEN QUESTIONS` (each marked blocking or not), `DEVIATIONS` (with why).
