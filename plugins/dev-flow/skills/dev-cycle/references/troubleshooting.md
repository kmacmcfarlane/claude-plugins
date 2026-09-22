# Troubleshooting

Failure modes a cycle meets while running SKILL.md's steps, and what to do about each.
Pointed at from SKILL.md § Troubleshooting and from `fix-loop.md` for the permission case.
"Raise it" always means the decision channel (`bindings.md` § Decisions).

## Resolving the run

- **A caller's handoff lacks a binding.** A setup error, not something to guess: stop
  before any dispatch and name the missing binding. Standalone resolution never fills in
  for a caller.
- **No work-item store.** Normal. The record sink is the scratchpad run record,
  `<scratchpad>/dev-cycle/<slug>/record.md` — never a file in an investigation series;
  nothing is filed and nothing is claimed.
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
- **`review <branch>` finds no such branch, or no such worktree can be added.** A setup
  error like a missing binding: stop and name it; never fall back to a full cycle.
- **`review <branch>` comes back `NEEDS_CHANGES` or `SHOW_STOPPER` and the operator
  declines to dispatch an implementer.** Report the findings and stop; nothing lands and
  nothing is fixed here — they go back to the branch's author.

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
  setup: recreate the worktree (SKILL.md § Step 3) and re-dispatch; not a round. When
  `worktree-<name>` still exists, add the worktree on it (`git -C "$MAIN" worktree add
  .claude/worktrees/<name> worktree-<name>`, no `-b`): a fresh branch off the base would
  drop the commits already on it.

## Resuming

Every case here is a row of `resume.md`'s state table; the table decides, this list only
names the symptom.

- **The run was interrupted.** Re-invoke `/dev-cycle` on the same target: SKILL.md
  § Step 0.4 reduces the record and takes the one action its state names.
- **A store-less run, re-invoked in a new session, finds what the old one left.** S0b: not
  resumable from this session — report it and stop; `resume.md` § The reduction, REMNANT names what
  counts, and the orphan-worktree rule below decides it. Nothing is re-dispatched over it.
- **A recorded dispatch's agent does not answer.** S3b: it counts as gone only after a
  SendMessage to its recorded id fails; then salvage what it left and re-dispatch on top of
  it, never over it.
- **Two recorded agents are both alive.** S13: stop, and let a human say which to keep;
  never stop one on the cycle's own say-so.
- **The worktree of a resumed run is gone.** Its verdict reads `STALE`, the fresh review
  blocks on `setup`, and the case above ("the implementer's worktree … missing")
  recreates it.
- **A decision is recorded with no answer.** The GATE (`resume.md` § The GATE): re-asked at
  the start of the next turn on an ephemeral channel, handed back on a durable one — never
  waited on.

## Landing

- **The main checkout is dirty.** Read `git -C "$MAIN" status --short` against what the
  cycle wrote itself: paths under the record sink or the store (`$WI add`, `claim` and
  appended lines), the Series home, and `.claude/worktrees/`. That dirt never blocks a
  merge; leave it as it is. Any other dirt — a path the merge would touch, or anything
  the user owns — stops the merge: say which paths and ask. Never stash, switch branches
  or commit someone else's work around it; the `git stash` stack is shared by every
  worktree and session of the repository.
- **The main checkout is not on the base.** Stop and ask; never check the base out over
  someone's work.
- **`.claude/worktrees/` is not ignored.** Step 3 appends it to
  `"$MAIN"/.git/info/exclude` and says so; never `.gitignore`, which is a tracked file.
- **This session runs inside a worktree.** `git -C "$MAIN" …` still merges in the main
  checkout; the harness blocks Edit/Write there, not git. When the main checkout is
  another live session's working tree, prefer `Leave the branch` and say why.
- **Merge conflict on the base.** Never resolve it yourself: `git -C "$MAIN" merge
  --abort`, record it as a finding, and re-dispatch into the fix loop, counting toward
  the cap — `fix-loop.md` § A merge conflict. The re-review judges the implementer's
  resolution with `git show --remerge-diff <merge sha>` (git 2.36+; older git: the
  fallback in `review-brief.md`, which checks both sides), never plain `git show`: its
  combined diff can hide a one-sided resolution, so a dropped side would pass unseen.
- **A red check in the worktree at Land.** `$WI handoff <id> --blocked "<what>"` (no
  item: a `blocked:` line in the record sink); back into the fix loop as a finding,
  counting toward the cap.
- **A dirty worktree at cleanup.** Never removed: report its `git status --short` and ask.
- **A check is red on the base after the merge.** Two green branches can be red together.
  Do not revert or patch by hand: file it (a new item when a store exists) or raise it,
  and report it on the `verified:` line.
- **Orphan worktree from a crashed run.** Dirty: surface it, do not remove. Clean and
  merged: remove it; clean and unmerged: ask.
- **Push rejected (non-fast-forward)** — only when the terminal action included a push.
  Do not pull, fetch, rebase or merge around it, and never `--force`: stop and report it.
