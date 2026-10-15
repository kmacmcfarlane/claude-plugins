# First start on a repo

Everything that only happens the first time the librarian runs in a repo: creating the
work-item store, what the first Rehydrate reports, and the dirt that leaves in the main
checkout. The opt-in that writes `## Librarian` runs before any of it:
`opt-in.md`. Pointed at from `rehydrate.md` § Step 1 and `cycle-bindings.md`
§ Terminal action.

## No store yet (Rehydrate step 1)

**First start:** the store lookup (Rehydrate step 1) exported no `WORK_ITEMS_ROOT`? It
checks the old `.claude-sandbox/work/` and `.work/` locations too, so an existing store
there is used, never shadowed by a fresh one. Truly no store during `start` or `intake` →
resolve the custody layer (step 2) first; no `## Librarian` section means the opt-in dialog
(`opt-in.md`), and its `Not now` means stop, creating nothing. Once a Scope is written, run

```bash
WORK_ITEMS_ROOT="$MAIN/.work-items" WI_ROOT="$MAIN/.work-items" $WI init --no-track
```

(idempotent; both names, so an older installed `wi` creates the same store). The flag is the
`work-items` skill's rule for `$WI init` (never the no-flag default): a new store is
git-ignored by the host repo, so `--no-track`, and `--track` only when the operator asked
for a tracked store. Relay its output (it explains the host `.gitignore` line it wrote, or
why none was needed), and add one line: "initialised .work-items/ — first start on this
repo". When `init` exits 1 because an old-location store (`.claude-sandbox/work/` or
`.work/` holding `items/`) is not yet moved, stop: route the move to the operator as a
numbered decision, or to claude-sandbox's migration where that covers the repo (the
`work-items` skill's format reference, § Moving a store), and never pass
`--allow-old-location` by reflex; it is for a repo whose `.work/` is its own, on the
operator's word. `status` never creates a store: with no `## Librarian` section it prints "not opted
in; `start` offers opt-in" (`opt-in.md`), otherwise "no store", and stops.

## What the first Rehydrate reports

After an init, it also carries "first start: store created, custody layer = <Scope, minus
Exclude, as written>" so the operator can correct scope before the first intake — a
correction is a work item that edits `## Librarian`. `start` commits the opt-in section
(`opt-in.md`) but never the store creation.

## First-start dirt at Land

The main checkout must be on `main` and clean before a merge — except first-start dirt (the
`.gitignore` line `wi init` wrote, and, for a store the host tracks, the store itself; a
store that is its own repo was committed by `init`): commit it with the first landed item or
leave it for the operator; it never blocks a merge. Commit the store with `$WI commit -m
"<message>"` (the `dev-cycle` skill's `references/bindings.md`, the store lookup), which
prints `nothing to commit` for a store the host ignores; then only the `.gitignore` line is
dirt. On another branch with uncommitted work, stop and raise it as a numbered decision
rather than stashing around it.
