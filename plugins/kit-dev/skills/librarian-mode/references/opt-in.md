# Opting a repo in

How a repo gets a custody layer: the `## Librarian` section in CLAUDE.md, and the one
dialog that writes it when it is missing. Pointed at from SKILL.md § Critical and
§ Rehydrate step 2.

## When it runs

- **Section present** — skip everything here. Scope, Exclude, Checks, Push and Workflow
  are read as written (Rehydrate step 2). Later edits to the section are ordinary work
  items: filed, dispatched, reviewed, landed.
- **Section absent, `start` or `intake`** — run the dialog below before anything else,
  including creating the work-item store (`first-start.md`).
- **Section absent, `status`** — read-only: print "not opted in; `start` offers
  opt-in" and stop. Never ask, never write.

## The dialog

One AskUserQuestion call, three questions, the first option of each the default, so
Enter three times accepts the defaults.

1. **Scope** — what the librarian owns. Options, in this order:
   - `Whole repo` — every tracked path.
   - `Plugin layer` — only when `plugins/` exists: `plugins/*/skills`, `plugins/*/hooks`,
     the README catalog and doctrine sections, CLAUDE.md.
     On a repo with no code and no `plugins/`, this slot is `Documentation tree`
     instead: README.md, CLAUDE.md, `docs/` and similar. On a code repo with neither,
     the slot is absent.
   - `Listed paths` — the paths or globs, comma-separated, typed in the dialog's Other
     field (Other text alone means the same). Picked with no text: ask once, in prose,
     for the list.
   - `Not now` — creates nothing and stops. The only remaining decline.
2. **Checks every change must pass** — multiSelect, options prefilled from commands
   detected in the repo (below); more through Other. None detected: offer `none —
   generic checklist only` and `add later as a work item`.
3. **Push** — options in this order:
   - `main` — fast-forward `origin/main` after each Report.
   - `none` — land to local `main` only; the push step is skipped.

## Detecting checks

Look, do not run: read the files named below. At most four options; list the rest in
the question text so the operator can paste them into Other.

| Evidence | Offered command |
|---|---|
| `go.mod` at the root | `go test` over every package (Go's `...` wildcard, from the root) |
| a `Makefile` with a `test:` target | `make test` |
| `package.json` with a `scripts.test` entry | `npm test` |
| `scripts/check-*.sh` | each script, by path |
| `plugins/*/hooks/tests/` | `(cd plugins/<p>/hooks && python3 -m unittest discover -s tests -q)` |

## Writing the answer

A named exception to "you do not edit custody files": it transcribes the operator's
answer and changes no behaviour. Write it in the main checkout, on `main`, with Bash —
append the section to CLAUDE.md, creating the file when it does not exist. The checkout
not on `main`, or CLAUDE.md already dirty: stop and ask; never stash around it. In a
worktree session (Rehydrate step 1), write nothing: ask the operator to run `start` from
the main checkout.

```markdown
## Librarian
Scope: whole repo
Exclude: vendor/
Checks:
- make test
Push: main
Workflow: spec-first; update docs/api.md with any endpoint change
```

- `Scope:` — `whole repo`, or one path or glob per `- ` line under it (`Plugin layer` and
  `Documentation tree` are written out as their paths, so the section reads alone).
- `Exclude:` — optional; paths inside Scope the librarian never touches.
- `Checks:` — one command per `- ` line; omit the key for none.
- `Push:` — `main` or `none`; a missing key reads as `main`.
- `Workflow:` — optional free-text repo workflow notes; the dialog does not ask for it,
  so it starts absent and is added later as a work item.

Commit only that file:

```bash
git -C "$MAIN" add CLAUDE.md
git -C "$MAIN" commit -m "librarian: opt in (<scope>)" -- CLAUDE.md
```

`<scope>` is `whole repo`, `plugin layer`, `documentation tree`, or `listed paths`.
Then continue with Rehydrate: the store (`first-start.md`), the queue, the inventory.
The first-start report names the Scope as written.
