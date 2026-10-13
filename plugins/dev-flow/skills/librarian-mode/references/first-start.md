# First start on a repo

Everything that only happens the first time the librarian runs in a repo: creating the
work-item store, what the first Rehydrate reports, and the dirt that leaves in the main
checkout. The opt-in that writes `## Librarian` runs before any of it:
`opt-in.md`. Pointed at from SKILL.md § Rehydrate and § The cycle.

## No store yet (Rehydrate step 1)

**First start:** the store lookup (Rehydrate step 1) exported no `WI_ROOT`? It checks
`.work/` too, so an existing `.work/` store is used, never shadowed by a fresh one. Truly
no store during `start` or `intake` → resolve the custody layer (step 2) first; no
`## Librarian` section means the opt-in dialog (`opt-in.md`), and its `Not now` means
stop, creating nothing. Once a Scope is written, run `$WI init --track` or
`$WI init --no-track` (idempotent), the flag chosen by the `work-items` skill's rule for
`$WI init` (never the no-flag default), with
`WI_ROOT="$MAIN/.claude-sandbox/work"`, relay its output (it explains any host
`.gitignore` decision), and add one line: "initialised .claude-sandbox/work/ — first start
on this repo". `status` never creates a store:
with no `## Librarian` section it prints "not opted in; `start` offers opt-in"
(`opt-in.md`), otherwise "no store", and stops.

## What the first Rehydrate reports

After an init, it also carries "first start: store created, custody layer = <Scope, minus
Exclude, as written>" so the operator can correct scope before the first intake — a
correction is a work item that edits `## Librarian`. `start` commits the opt-in section
(`opt-in.md`) but never the store creation.

## First-start dirt at Land

The main checkout must be on `main` and clean before a merge — except first-start dirt
(the store and any `.gitignore` line `wi init` wrote): commit it with the first landed
item or leave it for the operator; it never blocks a merge. On another branch with
uncommitted work, stop and raise it as a numbered decision rather than stashing around
it.
