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
- **A fable dispatch returns HTTP 429 or a usage-credits error.** Not a `BLOCKED`. Under
  a `model: fable` pin, ask through the decision channel — wait for the reset, or opus
  now — never falling back unasked; a second-opinion reviewer is dropped, and the opus
  `CLEAR` before it stands. `model-routing.md` §§ Fallback, Second opinion.
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
  resumable from this session — report it and stop; `resume.md` § The reduction, REMNANT
  names what counts. A leftover worktree, branch or series goes to the orphan-worktree rule
  below; a pending merge goes to "A merge left uncommitted in the main checkout" below,
  since it may not be this run's. Nothing is re-dispatched over it.
- **A run died after Land's merge, before its `landed:` line.** Its worktree may already be
  gone, so the last `CLEAR` would read `STALE`. S2b: `resume.md` § The reduction, MERGED
  finds the merge on the base whose merged parent is the `CLEAR`'s sha; the run writes
  `landed:` with it and runs `resume.md` § The landing tail — never a second review or
  merge.
- **A run died after its `landed:` line, before the item was closed.** S2: `resume.md`
  § The landing tail finishes the base checks, push, cleanup and `$WI done` that are still
  undone, and names any push it did not make.
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
  and report it on the `verified:` line. The merge has landed — its `landed:` line is
  written — so it never re-enters the fix loop, and nothing is pushed past it.
- **Orphan worktree from a crashed run.** Dirty: surface it, do not remove. Clean and
  merged: remove it; clean and unmerged: ask.
- **Push rejected (non-fast-forward or fetch first)** — only when the terminal action
  included a push. Someone pushed to `origin/<base>` since the last sync. Get past it only
  by a checked merge, the procedure the `librarian-mode` skill's
  `references/troubleshooting.md` § Push rejected sets out (read `main` there as
  `<base>`): never `git pull`, rebase, reset or `--force`, never a conflict resolved by
  hand, never a push past a red check.
  - **Under a librarian** the cycle never pushes — the push is the librarian's, after its
    Report (`bindings.md` § What a librarian binds), and a rejection is handled by that
    section as written.
  - **Standalone**, the user asked for one push of the cycle's own landing, not for a
    merge of other people's commits. So look, then ask once: `git -C "$MAIN" fetch
    origin`, and list the incoming commits
    (`git -C "$MAIN" log --format='%h %s — %an' <base>..origin/<base>`) and what they
    touch (`git -C "$MAIN" diff --stat <base>...origin/<base>`). AskUserQuestion, with
    that list as its evidence: `Leave it unpushed` first — the local merge stands, and the
    Report's `verified:` line says the push was rejected and names the incoming commits —
    then `Merge origin/<base> and push`: `git -C "$MAIN" merge --no-ff --no-commit
    origin/<base>` on `<base>` in the main checkout, every Check run from `$MAIN`
    against the merged tree, all green → `git -C "$MAIN" commit --no-edit` (a merge
    commit) and `git -C "$MAIN" push origin <base>`, now a fast-forward; the Report names
    each incoming commit as not the cycle's. If git refuses to start the merge (dirt in
    its way), stop and say which paths; clear nothing. **A conflict or a red check
    stops:** `git -C "$MAIN" merge --abort`, so `<base>` is as it was, nothing is pushed,
    and the Report raises a decision naming the conflicting paths or the failing check and
    the incoming commits, with two options: a new cycle whose implementer merges
    `origin/<base>` into a worktree branch cut from the local `<base>` and resolves or
    fixes it there — a conflict round, reviewed like any other, the shape of `fix-loop.md`
    § A merge conflict — then lands and pushes it; or the user resolving it on origin. A
    second rejection is reported, not retried.
- **A merge left uncommitted in the main checkout.** `git -C "$MAIN" rev-parse -q
  --verify MERGE_HEAD` succeeds when a cycle is re-invoked or reaches Land: a merge was
  interrupted before its commit or abort, and its Checks result is gone. Never commit it
  as found. `MERGE_HEAD` equal to `origin/<base>`'s commit
  (`git -C "$MAIN" rev-parse origin/<base>`) is a push-rejection merge from the entry
  above: `git -C "$MAIN" merge --abort`, then either redo that entry from the fetch and
  the ask, or report the push as not done — the local landing merge stands either way.
  Any other `MERGE_HEAD` is not the cycle's to decide: stop and ask.
