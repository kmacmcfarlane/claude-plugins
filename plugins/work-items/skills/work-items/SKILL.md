---
name: work-items
description: Repo-durable work items via the `wi` CLI — one markdown file per item in `.work/` (or `.claude-sandbox/work/`), with ready-ranking, claims, handoff blocks, TODO.md import, and a backlog-yaml bridge. Auto-activates when a repo has a work-item store, or when the user says "what's next", "work item", "next task", "claim it", "hand it off", "mark it done", or asks to migrate a TODO.md. Not for unattended ralph runs (backlog-yaml owns those).
disable-model-invocation: false
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
argument-hint: "[next | show <id> | add | done <id> | import-todo <path>]"
---

# Work items

Work items live in git — one markdown file each, `status:` authoritative, never moved on
completion — so they survive machines, sessions and collaborators, merge cleanly, and cost
tokens only one item at a time. The whole-file `TODO.md` read this replaces cost ~12K tokens
per read; `wi next` costs ~300–500. The file format, resolver rule, deprecation-notice
template and secret rule are canonical in `references/format.md` — read it before editing an
item file by hand; this file does not restate it.

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
| `$WI init --track\|--no-track` | creates the store, or records an existing one's tracking choice in `store.yaml` without re-creating anything; `--no-track` adds the store's directory to the repo's root `.gitignore` (never a duplicate line, never glued onto a last line with no newline). Neither flag: a menu on a terminal (git-ignored is the default); with no terminal, an ignored store and a stderr warning (`references/format.md` § Store tracking) |
| `$WI next [--plain\|--json]` | ready-ranked queue: `todo` with every dep met (done, dropped or in UAT, archived or not), priority then age |
| `$WI show <id> [--brief]` | one item; `--brief` for front matter + handoff only |
| `$WI add "<title>" [--short-display-name "<name>"]` | new item (`<slug>-<4hex>` id); describe, don't dump — path and key, never value; `--short-display-name` is the optional name agents give it to the operator, stripped and 40 characters or fewer (over that exits 1, nothing written: shorten it and re-run), shown as `[<name>] <title>` in text rows (`references/format.md` § Short display name and tag) |
| `$WI claim <id>` / `release <id>` | atomic; claims as `WI_OWNER`, else `<user>@<host>` from `$USER`, git `user.name`, then the login name (`references/format.md` § Claimant); a stale `claimed:` shows up in `next`; refuses (exit 1) a `blocked`, `parked` or `grooming` item, and a `todo` item with any dep `next` counts as unmet, naming each |
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
| `$WI archive` | moves closed items to `archive/` — its own commit, nothing else in it |

Exit codes: 0 ok · 1 usage/validation · 2 not found/empty (e.g. `next` with nothing ready —
report "nothing ready", don't retry) · 3 file/parser error · 4 lock/claim conflict (someone
else holds it — stop, don't force).

`wi` is one provider of a small work-source contract (the other is `backlog.yaml`); the
verbs, capability differences and canonical state mapping are in
`references/provider-interface.md`.

## Rules

- The store is resolved `WI_ROOT` → `.claude-sandbox/work/` → `.work/`; create only via
  `$WI init`, and only when the user asks for the store.
- `$WI init` always gets `--track` or `--no-track` from an agent; never rely on the
  no-terminal default, which picks git-ignored for you. Read
  `echo "${CLAUDE_SANDBOX_CONTAINER-}|${CLAUDE_SANDBOX_TRACK_IN_HOST-}"`. Nothing before the
  `|` means outside claude-sandbox: ask the operator whether the store is tracked or
  git-ignored. Inside, for a store at `.claude-sandbox/work/` (the default whenever
  `.claude-sandbox/` exists), first look for a sidecar from the main checkout, as for the
  layout probe below (a worktree has no `.claude-sandbox/` in a sidecar layout, so the test
  fails there): `test -e .claude-sandbox/.git` succeeds (`.claude-sandbox/` is its own repo,
  as `wi` itself tests) → `--track`, whatever the variable or the host's ignore says, since
  `--no-track` there ignores the store in the sidecar and new items land in no repo. Without
  a sidecar, the part after the `|` is the merged `trackInHost` of the sandbox's config
  cascade: `true` → `--track`; `false` → `--no-track`; any other value → ask the operator.
  Empty means either that no config defines it (the launcher then treats it as false) or
  that the sandbox was launched before the variable was exported, and the two cannot be
  told apart, so read the layout from the main checkout: `git check-ignore -q
  .claude-sandbox/` exits 0 (host git ignores the dir, the false layout) → `--no-track`,
  1 → `--track`, anything else → ask the operator. An env file in the cascade can also set
  the variable when no config defines `trackInHost`, and the launcher still lays out as
  false; if `init --track` then warns that git ignores the store, relay the warning and ask
  the operator. The same flags record the choice for an existing store with none recorded.
- Working an item follows the checkout/worktree rule — process stays in the checkout, the
  item's edits go in a worktree. A worktree is its own checkout: it lacks the main checkout's
  untracked or uncommitted store, and a tracked one there is a stale copy, so from there `WI_ROOT` points at the main checkout's
  store: the main checkout is
  `git rev-parse --path-format=absolute --git-common-dir` minus its trailing `/.git`.
- Item files are hand-editable; run `$WI lint` after hand edits, in the same turn.
- A `wi: WARNING store … is silently untracked` line (second line of `prime`; a problem, exit 3, in `lint`) means new items are git-ignored, or the store holds ≥10 items and none is tracked (below 10, an uncommitted store is treated as new). The line names the ignore rule (file:line) and the remedies for that cause; fix the cause rather than working around it. A store recorded as git-ignored (`tracking: ignored`) gets no warning; one recorded as tracked that git ignores anyway does, since that contradicts the choice; a store with no recorded choice keeps the warning, whose fix ends by recording the choice (`$WI init --track`, or `--no-track` when it is meant to stay local).
- One session claims an item before working it; two sessions on one item is what `claim` is
  for — respect a conflict.
- Migration of a repo's TODO.md is a reviewed, committed change (import → review items →
  write notice → commit), never a drive-by.
