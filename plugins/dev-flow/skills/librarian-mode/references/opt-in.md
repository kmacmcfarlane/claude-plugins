# Opting a repo in

How a repo gets a custody layer: the `## Librarian` section in CLAUDE.md, and the one
dialog that writes it when it is missing. Pointed at from SKILL.md § Critical and
§ Rehydrate step 2.

## When it runs

- **Section present, with a `Scope:` line** — skip everything here. Scope, Exclude,
  Checks, Push and Workflow are read as written (Rehydrate step 2). Later edits to the
  section are ordinary work items: filed, dispatched, reviewed, landed.
- **Section present, no `Scope:` line** (a free-form declaration from before the opt-in)
  — the Scope question alone, then the answer is inserted as a `Scope:` line directly
  under the heading; the free-form text stays as it is and is read like `Workflow:`
  notes. Missing Checks and Push read as none and `main`. `status` reports "scope not
  set; `start` asks for it" and stops.
- **Section absent, `start` or `intake`** — run the dialog below before anything else,
  including creating the work-item store (`first-start.md`).
- **Section absent, `status`** — read-only: print "not opted in; `start` offers
  opt-in" and stop, whether or not a store exists. Never ask, never write.

## Before asking

The answer is written in the main checkout, so check first and ask only when it can be
written:

- **Worktree session** (Rehydrate step 1: `MAIN` is not the cwd) — no dialog, nothing
  written: tell the operator to run `start` from the main checkout, and stop.
- **Main checkout not on `main`, or CLAUDE.md dirty** — no dialog: say which, and stop
  until the operator clears it; never stash around it.

## The dialog

One AskUserQuestion call, three questions, the first option of each the default, so
Enter three times accepts the defaults.

1. **Scope** — what the librarian owns. Options, in this order:
   - `Whole repo` — every tracked path except `.claude-sandbox/` and `.claude/`, which
     are always outside Scope (the store, sandbox config and worktrees belong to the
     tooling; a change to them goes to the operator).
   - `Plugin layer` — only when `plugins/` exists: `plugins/*/skills`, `plugins/*/hooks`,
     the README catalog and doctrine sections, CLAUDE.md.
     On a repo with no code and no `plugins/`, and only there, this slot is
     `Documentation tree` instead: README.md, CLAUDE.md, `docs/` and similar — the
     codeless default from before the opt-in, kept as an option (an addition to the
     approved design's list). On a code repo with neither, the slot is absent.
   - `Listed paths` — the paths or globs, comma-separated, typed in the dialog's Other
     field (Other text alone means the same). Picked with no text: ask once, in prose,
     for the list.
   - `Not now` — creates nothing and stops. The only remaining decline.
2. **Checks every change must pass** — multiSelect: up to three commands detected in
   the repo (below), then always `None beyond the generic checklist` last, so the
   question has two to four options; more through Other. Ticked commands and Other text
   become `Checks:`. An empty submit, or only `None…` ticked, means no `Checks:` key;
   `None…` ticked alongside commands is ignored.
3. **Push** — options in this order:
   - `main` — fast-forward `origin/main` after each Report.
   - `none` — land to local `main` only; the push step is skipped.

## Detecting checks

Look, do not run: read the files named below. At most three command options; list the
rest in the question text so the operator can paste them into Other.

| Evidence | Offered command |
|---|---|
| `go.mod` at the root | `go test` with the all-packages pattern: `.` then `/...`, written joined (split here only to pass the dot-slash lint) |
| a `Makefile` with a `test:` target | `make test` |
| `package.json` with a `scripts.test` entry | `npm test` |
| `scripts/check-*.sh` | each script, by path |
| `plugins/*/hooks/tests/` | `(cd plugins/<p>/hooks && python3 -m unittest discover -s tests -q)` |

## Writing the answer

A named exception to "you do not edit custody files": it transcribes the operator's
answer and changes no behaviour. Write it in the main checkout, on `main`, with Bash —
append the section to CLAUDE.md, creating the file when it does not exist; for a
section with no `Scope:` line, insert that line under the heading and touch nothing
else.

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
