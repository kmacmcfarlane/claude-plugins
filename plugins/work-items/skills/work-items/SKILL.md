---
name: work-items
description: Repo-durable work items via the `wi` CLI — one markdown file per item in `.work-items/` at the repo root (git-ignored by default; tracked on request), with ready-ranking, claims, handoff blocks, TODO.md import, and a backlog-yaml bridge. Auto-activates when a repo has a work-item store, or when the user says "what's next", "work item", "next task", "claim it", "hand it off", "mark it done", or asks to migrate a TODO.md. Not for unattended ralph runs (backlog-yaml owns those).
disable-model-invocation: false
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
argument-hint: "[next | show <id> | add | done <id> | import-todo <path>]"
---

# Work items

Work items live beside the repo, in git when the store is tracked — one markdown file each,
`status:` authoritative, never moved on completion — so they survive sessions (and machines
and collaborators when tracked), merge cleanly, and cost tokens only one item at a time. The
whole-file `TODO.md` read this replaces cost ~12K tokens per read; `wi next` costs ~300–500.
The file format, resolver rule, deprecation-notice template and secret rule are canonical in
`references/format.md` — read it before editing an item file by hand; this file does not
restate it.

```bash
WI="python3 ${CLAUDE_PLUGIN_ROOT}/skills/work-items/scripts/wi.py"
```

## Session-start rule

`$WI prime` (≤300 tokens: what's in flight, what's ready; a first `HOLD <n>: …` line lists
open items tagged `hold`, an operator hold that gates what may move — honour it before
picking work) — then `$WI show <id> --brief` for
the **one** item being worked. Never `ls` the whole store into context to pick a task; that is
the TODO.md failure mode with extra steps.

## The verbs

| | |
| --- | --- |
| `$WI init --track\|--no-track` | creates the store (`.work-items/` unless a root is named), or records an existing one's tracking choice in `store.yaml` without re-creating anything; `--no-track` adds the store's directory to the repo's root `.gitignore` (never a duplicate line, never glued onto a last line with no newline). Neither flag: a menu on a terminal (git-ignored is the default); with no terminal, an ignored store and a stderr warning. A git-ignored choice in a sidecar layout (`.claude-sandbox/.git` exists), including the no-terminal default, is refused, exit 1, nothing written; there the menu defaults to tracked and does not take git-ignored (`references/format.md` § Store tracking). In a linked worktree with no store and no root named it refuses, exit 1, nothing written |
| `$WI next [--plain\|--json]` | ready-ranked queue: `todo` with every dep met (done, dropped or in UAT, archived or not), priority then age |
| `$WI show <id> [--brief]` | one item; `--brief` for front matter + handoff only |
| `$WI add "<title>" [--short-display-name "<name>"]` | new item (`<slug>-<4hex>` id); describe, don't dump — path and key, never value; `--short-display-name` is the optional name agents give it to the operator, stripped and 40 characters or fewer (over that exits 1, nothing written: shorten it and re-run), shown as `[<name>] <title>` in text rows (`references/format.md` § Short display name and tag) |
| `$WI claim <id>` / `release <id>` | atomic; claims as `WORK_ITEMS_OWNER`, else `<user>@<host>` from `$USER`, git `user.name`, then the login name (`references/format.md` § Claimant); a stale `claimed:` shows up in `next`; refuses (exit 1) a `blocked`, `parked` or `grooming` item, and a `todo` item with any dep `next` counts as unmet, naming each |
| `$WI handoff <id> --doing … --next … [--blocked …] [--learned …]` | the per-item residue — write it whenever the item is left mid-flight |
| `$WI note <id> [--raw] -- "<text>" ["<text>" …]` | appends each text to `## Notes` under the lock, one write for all of them or none: dated (`- <today> <text>`) by default, verbatim with `--raw` (for a record line such as `decision N:`); always put `--` before the texts. Refuses (exit 1, nothing written, stderr `wi: text <n>: …`, never quoting the text) a line break, an empty text, under `--raw` a `## ` line or a fence opener, and any line `lint` would flag as a secret: reword it as path and key and re-run. `handoff` stays the four-line residue |
| `$WI done <id> [--note <sha>]` / `done --drop` | closes it in place; `implement`'s "Update the work item" step owns this on landed work |
| `$WI block <id> "reason"` / `--on <dep-id>` / `unblock` | runtime vs dependency blocks |
| `$WI park <id> "reason"` / `unpark <id>` | deliberate deferral, not a block: out of `next`, one count line in `prime`, listed by `ls --status parked`; releases any claim; `unpark` → `todo` (or `blocked` if a block reason remains); `release` never unparks, `set status parked` refuses. Drop one with `done --drop` |
| `$WI groom <id> "questions"` / `ungroom <id>` | waiting on the operator's answers: out of `next`, one `GROOMING <n>` line in `prime`, listed by `ls` and `needs-input`; releases any claim; `ungroom` → `todo` (or `blocked`); `set status grooming` refuses |
| `$WI needs-input [--plain\|--json]` | everything awaiting the operator: grooming items and unanswered `decision N:` lines (no matching `answer N:`), each with the item's title (its title cell), N and text; `--json` adds each decision's `raised` and its shown-and-seen fields (`first_shown`, `last_shown`, `last_seen`, `unseen`, from `shown N:` / `seen N:` lines; the format reference's § Shown and seen); exit 2 when none |
| `$WI ls [--status …] [--dep <id>] [--tag …] [--ready]` | list; default open statuses (`todo doing blocked grooming`); `--dep` lists the items depending on an id |
| `$WI estate [--dir DIR …] [--top N] [--stale 24h] [--json]` | read-only sweep of every store one level under DIR (default: the parent of this repo's main checkout, refused when that is `$HOME`, above it or `/`): per repo, counts, top ready, unanswered decisions with their age (and, in `--json`, their shown-and-seen fields), stale claims, a security hint, and unreadable files as problems, each list capped with a count of the rest; never writes, never follows a symlink out of DIR, keeps one entry per git repository (a linked worktree beside its main checkout, or a symlinked alias, is listed under `skipped` with the reason); the `work-review` skill writes the operator's overview from it |
| `$WI migrate-parked [--apply]` | converts `blocked` items whose reason starts `PARKED` (the old convention) to `parked`; a dry run until `--apply` |
| `$WI repair-escapes [--id <id>] [--key <field>] [--apply]` | one-time, **heuristic** repair of quoted front-matter values an older `wi` escape-amplified: lists every front-matter value whose backslashes all pair as `\\` or `\"`, with those layers peeled — a value meant that way is listed too, so review the list; a dry run until `--apply`, and `--id`/`--key` narrow it |
| `$WI set <id> <field> <value> [--force]` | one front-matter field; list fields (`tags deps refs`) take `a,b` and are **replaced whole**; `""` (or `—`) clears any field; `deps`/`parent` targets must resolve — `ext:` deps exempt, `--force` bypasses; `short_display_name` is stripped and must be 40 characters or fewer (exit 1 over), and a blank value clears it |
| `$WI import-todo TODO.md` | idempotent migration; then replace TODO.md with the deprecation notice from `references/format.md` |
| `$WI export/import --format backlog-yaml` | the ralph bridge — backlog.yaml stays authoritative for unattended runs |
| `$WI lint` | format + secret-shape + store-custody check; run before committing hand edits |
| `$WI commit [-m "<message>"]` | the one way to commit the store, never `git` by hand: under the store's lock it commits the store's own files into the repo that holds them (the store's own repo, or the host or sidecar repo that tracks it, whose hooks run), and prints `nothing to commit` for a store that repo ignores. Refuses (exit 1, nothing committed) a message `lint` would flag as a secret, and an own repo `wi` did not set up (unrecorded) or cannot trust (broken); exit 3 when git fails, or is missing for a store with its own repo (`references/format.md` § Committing the store) |
| `$WI archive` | moves closed items to `archive/` — its own commit when the store is tracked, nothing else in it |

Exit codes: 0 ok · 1 usage/validation · 2 not found/empty (e.g. `next` with nothing ready —
report "nothing ready", don't retry) · 3 file/parser error · 4 lock/claim conflict (someone
else holds it — stop, don't force).

`wi` is one provider of a small work-source contract (the other is `backlog.yaml`); the
verbs, capability differences and canonical state mapping are in
`references/provider-interface.md`.

## Rules

- The store is resolved `--root` → `WORK_ITEMS_ROOT` → the first of `.work-items/`,
  `.claude-sandbox/work/`, `.work/` under the cwd that holds `items/`; with none, `init`
  creates `.work-items/`. Create only via `$WI init`, and only when the user asks for the
  store. `.claude-sandbox/work/` and `.work/` are old locations: still found, deprecated, with
  a one-line `wi: deprecated: store … is at an old location` notice from `prime`, `lint` and
  `init` (moving one: `references/format.md` § Moving a store). A
  `wi: WARNING more than one work-item store under …` line means a second store sits beside
  the one in use: `prime` shows it and `lint` counts it as a problem (exit 3) however the
  root was found, and every other command prints it on stderr when the root was
  auto-resolved; move or remove the extra store.
- wi's environment names are `WORK_ITEMS_ROOT` and `WORK_ITEMS_OWNER`. The old `WI_ROOT`
  and `WI_OWNER` still work as deprecated fallbacks; the new name wins when both are set, and
  `prime`, `lint` and `init` print a one-line `wi: deprecated: …` notice when an old name is
  set and its new name is unset or empty, or when both are set and differ (none when both
  are set to the same value, which is how to export for an older wi too). To tell a wi
  with these names from an older one, probe `$WI --help`: it names `WORK_ITEMS_ROOT` only
  in a wi that reads it.
- `$WI init` always gets `--track` or `--no-track` from an agent; never rely on the
  no-terminal default. A new store is `.work-items/` at the repo root and is git-ignored:
  pass `--no-track` unless the operator asked for a tracked store. An existing store with no
  recorded choice keeps what git already does with it. From the main checkout:
  - a sidecar store (`test -e .claude-sandbox/.git`, store at `.claude-sandbox/work/`) →
    `--track` (wi refuses an ignored one);
  - `git ls-files <store> | head -1` prints a path → `--track`;
  - `git check-ignore -q <store>` exits 0 → `--no-track`;
  - otherwise ask the operator.

  The same flags record the choice for an existing store with none recorded.
- Working an item follows the checkout/worktree rule — process stays in the checkout, the
  item's edits go in a worktree. A worktree is its own checkout: it lacks the main checkout's
  untracked or uncommitted store, and a tracked one there is a stale copy, so from there `WORK_ITEMS_ROOT` points at the main checkout's
  store: the main checkout is
  `git rev-parse --path-format=absolute --git-common-dir` minus its trailing `/.git`. In a
  linked worktree with no store and no root named, `wi` fails with the `export
  WORK_ITEMS_ROOT=…` line to run, and `init` refuses rather than make a stray store.
- Item files are hand-editable; run `$WI lint` after hand edits, in the same turn.
- A `wi: WARNING store … is silently untracked` line (second line of `prime`; a problem, exit 3, in `lint`) means new items are git-ignored, or the store holds ≥10 items and none is tracked (below 10, an uncommitted store is treated as new). The line names the ignore rule (file:line) and the remedies for that cause; fix the cause rather than working around it. A store recorded as git-ignored (`tracking: ignored`) gets no warning; one recorded as tracked that git ignores anyway does, since that contradicts the choice; a store with no recorded choice keeps the warning, whose fix ends by recording the choice (`$WI init --track`, or `--no-track` when it is meant to stay local). A sidecar store recorded as git-ignored warns too (`… is recorded git-ignored … so new items land in no repo`), naming `$WI init --track` and any ignore line in the sidecar repo to remove.
- One session claims an item before working it; two sessions on one item is what `claim` is
  for — respect a conflict.
- Migration of a repo's TODO.md is a reviewed change (import → review items → write notice
  → commit; the items are in that commit when the store is tracked), never a drive-by.

## Protecting the store

A `.work-items/` store is git-ignored with no remote, and a tracked store's new items are not
in git until committed: git cannot bring either back, and a lost store takes its decision
numbers with it. Near a store (the harm, the evidence, observed with git 2.39.5, and
the full safe forms are in `references/store-safety.md`):

- `git clean`:
  - Never a doubled `-f` (or `--force` twice) near a store: a doubled force deletes linked
    worktrees and nested repos even when the store is excluded.
  - Never `-x` near a store without excluding it. Preview, then exclude:
    `git clean -n -fdx -e /.work-items/`, then run it without `-n`:
    `git clean -fdx -e /.work-items/` (one `-f` only).
  - `-X` is never safe while the clean reaches a store (from the cwd down, or through its
    pathspec): `-e` and `:!` do not protect it under `-X`. Name only the directories to
    clean instead: preview with `git clean -n -fdX -- build/ dist/`, then run
    `git clean -fdX -- build/ dist/`.
  - A tracked store (`.claude-sandbox/work/`, `.work/`) loses new items to any clean without
    `-X`: add `-e /<store>/` (under `-X`, name the directories as above).
  - A plain store that is not ignored is deleted by `git clean -fd` and moved by
    `git stash -u`.
- `git stash`: never `--all`/`-a`. Commit, or copy files to the scratchpad, instead.
- `rm -r`: never on the store, its repo root or any directory above it, and never "delete
  the checkout and clone again" while it holds a store. Back up first (§ Backing up there).
- Git inside the store: always `git -C <store> …`, never `cd` into it to run git, and never
  run git that writes inside one except a commit under its lock (§ Safe forms there). Never
  `reset`, `checkout`, `switch`, `restore`, `clean`, `stash` or `rm` there.
- Never remove the store's line from `.gitignore`, `git add -f` it, or `git add` it when it
  is its own repo (that commits a gitlink, mode 160000, pointing at the store's current
  commit, which no clone can fetch).
- A worktree or a fresh clone has no store: point `WORK_ITEMS_ROOT` at the main checkout's
  (§ Rules), or restore a backup. Never `$WI init` there to make the error go away.
- Path and key, never value (`references/format.md` § Secret rule): the store's history
  keeps every past text.
