# Worktree orchestration

How `implement` isolates parallel work. Read this before fanning out.

## Why worktrees, and when they are not worth it

The evidence for multi-agent implementation is conditional, not general.

Anthropic's own position is that coding is a poor fit for multi-agent systems: domains "that
require all agents to share the same context or involve many dependencies between agents are
not a good fit… most coding tasks involve fewer truly parallelizable tasks than research", at
roughly 15× the tokens of a single chat.

The counterweight is Geng & Neubig, *Effective Strategies for Asynchronous Software
Engineering Agents* (arXiv:2603.21489), which measures +25.6% absolute on PaperBench and
+14.7% on Commit0 over single-agent baselines — but only for a specific arrangement (CAID)
resting on three primitives:

1. **Centralized dependency-aware planning** — one planner decides what can run concurrently.
2. **Isolated workspaces** — concurrent edits do not interfere, because each agent has its own
   checkout.
3. **Consolidation by executable test verification** — merging is gated on tests, not on an
   agent's opinion.

**All three or none.** Fan-out without isolation produces interfering edits. Fan-out without
test-gated merge produces a plausible-looking integration nobody verified.

Note what is *not* in that list: an LLM reviewer agent. The evidence there is split — one
ablation that added a review agent **lowered** resolved-issue rate (21.33% → 18.33%), while
another found removing self-review collapsed precision (0.62 → 0.13). Review is a secondary
lens. **Tests are the gate.**

### The decision

Work inline, in the main checkout, when any of these hold:

- The plan has fewer than three tasks.
- The tasks touch overlapping files.
- The whole change is small enough to hold in one head — a few files, one concern.
- The project has no automated verification at all (see Verification tiers in the `investigate`
  skill's `references/investigation-format.md`). With nothing to gate the merge, the third
  primitive is missing and fan-out is unjustified.

Fan out only when the plan has **three or more genuinely independent tasks** *and* there is a
test or build command that can gate the merge.

Say which you chose and why. Silent fan-out on a two-file change is a cost with no return.

## The existing convention — use it

This is established tooling, not something to reinvent.

- Worktrees live at **`.worktrees/<id>/`** in the repo root.
- `.worktrees/` is gitignored and documented as ephemeral local state. The commits live in the
  main `.git`, so the directory is disposable.
- Ralph-scaffolded projects ship a lifecycle manager at
  **`.claude-sandbox/scripts/worktree/worktree.py`**:

  ```bash
  python3 .claude-sandbox/scripts/worktree/worktree.py --format json create <id>
  python3 .claude-sandbox/scripts/worktree/worktree.py list
  python3 .claude-sandbox/scripts/worktree/worktree.py detect-stale
  python3 .claude-sandbox/scripts/worktree/worktree.py recover
  python3 .claude-sandbox/scripts/worktree/worktree.py remove <id> [--force] [--delete-branch]
  ```

  Plus `merge_helper.py` for conflict resolution:

  ```bash
  python3 .claude-sandbox/scripts/worktree/merge_helper.py --repo-dir . --format json
  ```

- **Check whether the script exists before using it.** It ships only with ralph-scaffolded
  projects and is coupled to `backlog.yaml` — its `create` and `detect-stale` read story
  status. When the id is an investigation slug rather than a story id, or the script is
  absent, fall back to plain git:

  ```bash
  git -C <repo> worktree add .worktrees/<id> -b <id> <base>
  git -C <repo> worktree remove .worktrees/<id>
  ```

  If `.worktrees/` is not in `.gitignore`, add it before creating the first worktree.

## Naming

- Integration branch for the whole run: **`<slug>`** — the investigation slug, bare.
- Per-task branches when fanning out: **`<slug>-<n>`**, matching worktree `.worktrees/<slug>-<n>/`.
- Single-task runs use `<slug>` for both, with no worktree at all.

## Gotchas

**Tooling that must read the main checkout.** Anything keyed to repo-root state breaks when
run from a worktree. `backlog.py` is the known case — it must read `backlog.yaml` from the main
checkout, via `BACKLOG_REPO_ROOT` or `--repo-root`. Check for equivalents before dispatching.

**Docker compose port collisions.** Two worktrees running compose at once will fight over
project names and host ports. Projects that support this set a scoping variable — checkpoint-
sampler uses `STORY_ID` with `docker-compose.worktree.yml` and `scripts/compose-project-name.sh`.
If the project has no such mechanism, **do not run compose from more than one worktree
concurrently**; serialize those tasks instead.

**Dependencies and generated code are per-worktree.** A fresh worktree has no `node_modules`,
no vendored deps, no generated output. Run install and codegen inside each worktree before
building. Immediately after creating a worktree, regenerate anything checked in that a base
branch may carry stale — a base branch can ship generated files that were never regenerated,
so the branch does not compile until you do. A no-op diff afterwards means the artifacts were
correct; a diff means the base shipped stale ones.

**Stale worktrees survive crashes.** Before creating any, check for orphans from a previous
run (`worktree.py detect-stale` / `recover`, or `git worktree list` plus `git -C <path> status
--short`). A worktree with uncommitted changes is never removed automatically — surface it to
the user and ask.

## Dispatch

For each independent task, spawn a **vanilla `general-purpose` subagent**. There are no custom
agent definitions for this; the brief carries everything.

Each brief is self-contained and states:

- The absolute worktree path, and that all work happens **there** and nowhere else
- The one task, scoped to specific files — not the whole plan
- The relevant slice of the investigation: approach, patterns to follow, files to modify
- The build and test commands, and that it must run them before reporting
- What to report back: files changed, commands run with their outcomes, deviations from the
  plan, anything it could not do

Tell it explicitly **not** to commit outside its worktree, not to touch files outside its task,
and not to merge anything.

Dispatch in dependency order. Tasks in the same dependency group run concurrently — send them
in a single message so they run in parallel. A later group starts only when everything it
depends on has merged and verified.

## Consolidation

Per task, in dependency order:

1. Run the task's own verification inside its worktree. A task whose tests fail does not merge.
2. Merge its branch into the integration branch in the main checkout.
3. On conflict, use `merge_helper.py` where available; otherwise resolve by hand with the
   investigation's approach as the tiebreaker. Never resolve by taking one side wholesale
   without reading both.
4. **Re-run the full verification on the integration branch after every merge**, not only at
   the end. Two independently-green tasks can be red together, and finding that out after six
   merges means bisecting your own work.
5. Remove the worktree once merged and clean.

If a merge cannot be made green, stop. Report which task broke it, what the failure is, and
what you tried — do not keep merging on top of a red integration branch.

## Cleanup

Before reporting completion:

- Every worktree removed, or explicitly reported as retained with the reason.
- Per-task branches deleted once merged; the integration branch retained.
- `git worktree list` shows only the main checkout, or exactly what you said you kept.
- `git status` in the main checkout is clean apart from intended changes.
