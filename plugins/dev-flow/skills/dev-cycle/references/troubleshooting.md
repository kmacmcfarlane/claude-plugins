# Troubleshooting

Failure modes a cycle meets while running SKILL.md's steps, and what to do about each.
Pointed at from SKILL.md § Troubleshooting and from `fix-loop.md` for the permission case.
"Raise it" always means the decision channel (`bindings.md` § Decisions).

## Resolving the run

- **A caller's handoff lacks a binding.** A setup error, not something to guess: stop
  before any dispatch and name the missing binding. Standalone resolution never fills in
  for a caller.
- **No work-item store.** Normal. The record sink is the plan's outcome file or
  `<scratchpad>/dev-cycle/<slug>/record.md`; nothing is filed and nothing is claimed.
  Never `wi init` from a cycle.
- **A store, but no `wi`.** Resolve it with the lines in `bindings.md` § Store; an empty
  result after all three sources means `work-items` is not installed. Say so once and run
  on the scratchpad record.
- **`wi claim` exits 4.** Another session holds the item. Do not force; stop and report
  who holds it.
- **The target is ambiguous.** An argument that is both an item id and a series slug: take
  the item (its body names the series when there is one) and say so in the Step 0
  summary.
- **The user rejects the cycle brief.** Nothing was written or filed; stop.
- **`review <branch>` asked for.** Not available yet: say it is coming and stop; do not
  run a full cycle in its place.

## Dispatch and review

- **Agent (implementer or reviewer) returns `BLOCKED` on permissions.** A decision for a
  human, not a reason to do the work yourself: block the item when there is one, and
  raise it.
- **A fable dispatch returns HTTP 429 or a usage-credits error.** Not a `BLOCKED`: the
  reset time decides between opus and asking — a `model: fable` pin always asks —
  `model-routing.md` § Fallback.
- **Implementer disputes a medium-or-above finding.** It cannot decline it: it fixes, or
  states the counter-case for the re-review. The reviewer withdraws on the merits (the
  failure cannot occur) or holds; if it holds, fix it — that round is spent.
- **Reviewer returns `SHOW_STOPPER` for something a fix would close.** Ask it to state
  the fix path in one line; if a fix exists inside the change's scope, route the verdict as
  `NEEDS_CHANGES` and note the re-routing in the record sink — routing only; the finding
  keeps its severity.
- **The implementer's worktree is on the wrong branch or missing.** Its `BLOCKED` is your
  setup: recreate the worktree (SKILL.md § Step 3) and re-dispatch; not a round.

## Landing

- **The main checkout is not on the base, or is dirty.** Stop and raise it; never stash,
  switch branches or commit someone else's work around it. The `git stash` stack is
  shared by every worktree and session of the repository.
- **This session runs inside a worktree.** `git -C "$MAIN" …` still merges in the main
  checkout; the harness blocks Edit/Write there, not git. When the main checkout is
  another live session's working tree, prefer `Leave the branch` and say why.
- **Merge conflict on the base.** Resolve by reading both sides with the change's approach
  as tiebreaker; never take one side wholesale. If the resolution needs judgement,
  re-dispatch with the moved base as the new base; the review gate runs again.
- **A check is red on the base after the merge.** Two green branches can be red together.
  Do not revert or patch by hand: file it (a new item when a store exists) or raise it,
  and report it on the `verified:` line.
- **Orphan worktree from a crashed run.** Dirty: surface it, do not remove. Clean and
  merged: remove it; clean and unmerged: ask.
- **Push rejected (non-fast-forward)** — only when the terminal action included a push.
  Do not pull, fetch, rebase or merge around it, and never `--force`: stop and report it.
