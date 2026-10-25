# Work-item file format

One markdown file per item, managed by `scripts/wi.py`. The store lives in the
repo's directory, tracked by git or git-ignored (§ Store tracking); the CLI adds
locking, validation and budgeted views on top. Spec of record:
`agents/investigations/context-guardrails/threads/F-wi-spec.md`.

## Root resolver

`wi` finds its root in this order; `init` is the only command that creates it.

1. `--root PATH`, else `$WORK_ITEMS_ROOT` — worktree workers point this at the
   main checkout so claims are visible to each other. The deprecated `$WI_ROOT`
   is read when `$WORK_ITEMS_ROOT` is unset or empty; when both are set,
   `$WORK_ITEMS_ROOT` wins. An empty value counts as unset.
2. Otherwise the first of these under the cwd that holds `items/`:
   `.work-items/` (the default), `.claude-sandbox/work/`, `.work/`. A
   `.claude-sandbox/` directory alone picks nothing.
3. With none, `.work-items/`: `init` creates it, and every other command exits
   1 with ``no work-item root at .work-items (run `wi init`)``. In a linked git
   worktree (its git dir differs from its common dir) this case differs:
   every command but `init` exits 1 with `wi: no work-item store in this
   linked worktree; the store lives in the main checkout: export
   WORK_ITEMS_ROOT=<main>/<store>`, naming the main checkout's store (the
   first location there holding `items/`, else `.work-items`), and `init`
   refuses, exit 1, nothing written, since a store there would be a stray copy
   no other session sees. When git does not give the main checkout's path
   (the common dir is not named `.git`: a worktree of a bare repo or of a
   `--separate-git-dir` clone), the error names `<main checkout>/.work-items`
   and the refusal says only "run it in the main checkout". A root named by
   flag or env skips this check, and so does a git that is missing or fails.

**Old locations.** `.claude-sandbox/work/` and `.work/` are deprecated: still
found, still used. A store whose real path (symlinks followed) is named `.work`,
or is `work` inside `.claude-sandbox`, gets one line from `prime` (a header
line, reserved from the budget like the custody warning), `lint` (stderr; not a
problem, the exit is unchanged) and `init` (stderr), at most once per run:
`wi: deprecated: store <root> is at an old location; the default is
.work-items/ (the work-items skill's references/format.md § Moving a store)`.
A root from the flag, the env or the lookup is judged alike. No other command
prints it.

**`init` makes or keeps no store at an old location.** `wi init` exits 1, writing
nothing, when the store root is an old location, a new store there included (so `init` never
makes a store the next `init` refuses), or when an old location beside the top of the repo
around the root (or beside the root's own parent directory) holds `items/`: an un-migrated
store next to a new `.work-items/`. A store beside counts only by its `items/` directory,
never by its name alone or by an ignore line naming it, so a store already moved away, with
`/work/` still in a sidecar `.gitignore`, does not trip it. The refusal covers every `init`
there, a re-run on an existing store and the no-flag note included, and comes after the
sidecar refusal of `--no-track` (§ Store tracking), which keeps its message. It names the
old location's path and this file's § Moving a store ("use `.work-items/`, moving the old
store first if there is one"), adds "then change any WORK_ITEMS_ROOT export that names the
old path" when the root was not named with `--root`, and prints no deprecation line
besides.

`--allow-old-location` overrides it, only when the operator keeps the store at the old
location, or the directory is the project's own and not a work-item store. It works with
`--track`, `--no-track`, the menu and an existing store; with it, `--no-track` at an old
location makes a plain ignored store, never an own repo. It is never recorded: every `init`
there needs it again, and `prime` and `lint` keep the deprecation line. Passed where there is nothing to override (a
root not at an old location, with no old location holding `items/` beside it), it is refused,
exit 1.

**More than one store.** When the store in use is one of the three locations
under a directory D (by real path), and another of them under D also holds
`items/`, `prime` shows a header line and `lint` counts a problem (exit 3),
however the root was found: `wi: WARNING more than one work-item store under
<D>: using <store>, also <others> (move or remove the extra one: the
work-items skill's references/format.md § Moving a store)`. With the lookup
(no flag, no env), `.work-items/` wins and every other command prints the same
line on stderr; with a named root the other commands stay silent, since the
caller chose the store. Stores are compared by real path: a symlink to the
same store (`.work` linking to `.work-items`) is one store, not two. The usual
way to get two is checking out a branch from before a move, which brings back
a tracked old store beside the git-ignored `.work-items/`.

```
<root>/
  README.md            what this is, in ten lines
  items/<id>.md        every item, regardless of status
  archive/YYYY/<id>.md closed items moved by `wi archive` (explicit, batched)
  cards/<id>/<N>/      card records, one immutable .json per revision; never archived
  store.yaml           the store's recorded tracking choice and decision counter (§ Store tracking)
  .lock                gitignored; flock target for same-machine mutations
  .git/                the store's own repo, when it has one (§ The store's own repo)
```

## Store tracking

Whether git tracks the store is a choice `wi init` records in `<root>/store.yaml`:

```yaml
# wi store settings; format: the work-items skill's references/format.md
# or: ignored
tracking: tracked
```

`tracking:` is a key on a line of its own; `tracked` and `ignored` its values. `wi`
reads the first `tracking:` line and ignores comment lines. Any other value counts as no
recorded choice, and `wi lint` reports it, as it does more than one `tracking:` line.

A second key, `repo: own`, says the store is its own git repo (`<root>/.git`), set up by
`wi init`, which `wi` commits into; it goes with `tracking: tracked`, since git tracks the
store there, in the store's own repo. `own` is its only value: any other value, or more than
one `repo:` line, is a `wi lint` problem. A `wi` older than this key reads only `tracking:`,
so it sees such a store as tracked. From the `.git` (an `lstat`, no git) and the record,
a store is in one of these states (§ The store's own repo says what is valid):

| State | `.git` | `repo: own` | `wi` commits there? |
|---|---|---|---|
| plain | absent | no | no |
| own | valid | yes | yes |
| own, unrecorded | valid, with a repo around the store | no | no |
| dedicated | valid, no repo around the store (a store at the top of its own repo, `--track`) | no | no: it is tracked by the repo that holds it |
| own, missing | absent | yes | no; a `lint` problem |
| broken | present, not valid | either | no; a `lint` problem |

Commits follow the record, never the `.git` alone: `wi` never starts committing into a repo
no `init` set up. A `.git` in a store at an old location is never own: it is a `lint`
problem, fixed by moving the store (§ Moving a store).

A `counters:` block holds the last decision number the store gave out (§ Allocating a
decision number):

```yaml
# wi store settings; format: the work-items skill's references/format.md
tracking: tracked
counters:
  decision: 309
```

`counters:` sits on a line of its own; the indented lines under it, blank lines between them
included, up to the first line that is neither indented nor blank, are `<key>: <whole
number>` (digits 0-9). Only `decision` is defined; a key written twice is a `wi lint` problem
(the first line counts, and the next write keeps one). A missing
file, block or key reads as 0. `wi raise` and `wi lint` write it, keeping every other line
of the file; `wi init` carries the block over unchanged when it rewrites the file. A store
with no `store.yaml` gets none from a raise (a file without `tracking:` would be a lint
problem); its numbers come from the items alone. A `decision:` value that is not a whole
number, or a `store.yaml` holding merge conflict markers, is a `wi lint` problem (exit 3);
`wi raise` and `wi counter` refuse such a file (exit 1, nothing written), and `lint` never
reseeds over it. A `wi` older than the block reads only `tracking:` and `repo:`; an older
`wi init` re-run rewrites the file without it, and the next raise or lint reseeds it from
the items.

- **Making the choice.** `wi init --track` or `wi init --no-track` (mutually exclusive).
  With neither, a terminal on stdin and stdout gets a two-line menu (1) tracked: items are
  committed with the repo; 2) git-ignored: the repo ignores the store, which keeps its own
  local history; Enter takes git-ignored, or tracked in a sidecar layout). With neither and
  no terminal (an agent's Bash call, a script), `init` creates a git-ignored store with its
  own repo, says so on stderr (tracking it in the repo instead needs the store's `.git`
  gone first, which is the operator's call), and exits 0 (in a sidecar layout, refused: see
  below).
- **The git-ignored choice is the store's own repo.** `--no-track`, the menu's
  git-ignored and the no-terminal default each mean that the repo around the store (the
  host) does not track it: the host ignores it, and the store keeps its history in its own
  local repo, which `init` creates or adopts (§ The store's own repo, Setting it up). The
  record is then `tracking: tracked` plus `repo: own`: the flag names the host, which does
  not track the store, and the record names git, which does, in the store's own repo. At an
  old location (with `--allow-old-location`), or with no git on `PATH`, the choice makes a
  plain ignored store, recorded
  `ignored`, as the bullets below describe, with a stderr line saying it has no history of
  its own.
- **Outside any git repo.** `--no-track` (and the no-terminal default) gives the store its
  own repo, recorded `tracked` + `repo: own`; `--track` records `tracked` with no repo, so
  the store has no history, and `init` says so when git reports no repo around it.
- **Ignoring** (`--no-track`, the menu's git-ignored, the no-terminal default) adds
  `/<store path>/` — `/.work-items/`, or at an old location `/.work/` or
  `/.claude-sandbox/work/` — to the root `.gitignore` of the
  repo that holds the store (glob characters in the path escaped). The file is created when
  it is missing; otherwise the line is appended in one atomic write that keeps the file's
  bytes, its line ending (CRLF stays CRLF) and its mode, with a newline added first when
  its last line has none. No line is added when the store is already ignored by git, as
  `git check-ignore` judges it, from one of the repo's `.gitignore` files: its path in any
  spelling, a glob, a parent directory, or, for the old `.claude-sandbox/work/`, the host
  `.gitignore` ignoring `.claude-sandbox/` as a whole (`init` says that covers the store). A
  literal line followed by a negation does not count. A rule only in `.git/info/exclude` or
  a global excludes file does not count either, since it does not travel with the repo.
  After writing, `init` checks again and warns when the line did not make git ignore the
  store. Outside git, nothing is written and `init` says so.
- **A sidecar store is never ignored.** In a sidecar layout (`.claude-sandbox/.git`
  exists, so `.claude-sandbox/` is its own git repo, which the host does not track) a
  git-ignored store would land in no repo. `init` refuses any git-ignored choice there
  (`--no-track`, the no-terminal default) before anything is written, exits 1, and names
  `wi init --track`; an existing store keeps its recorded choice. The menu there defaults
  to tracked, and answering git-ignored asks again. The refusal covers a named
  `.claude-sandbox/work` root and an existing one the lookup finds; a bare `wi init` with no
  store makes `.work-items/`, which is never a sidecar store.
- **A store that is already its own git repo** inside a host (a `.work-items/.git` that no
  `init` set up) is adopted by the git-ignored choice, its history kept. `--track` refuses a
  store whose own valid repo sits inside a host, exit 1, nothing written: "`<root>` is its
  own git repo; the host cannot track it (that commits a gitlink, mode 160000): use `wi init
  --no-track`". A store at the top of a repo with no repo around it is that repo's root: the
  git-ignored choice is refused there by the rule below, and `--track` records it.
- **What init refuses.** It never writes through a symlink: a symlinked `.gitignore` gets no
  line (`init` names the line to add by hand), and a store directory that is a symlink to a
  place outside the repo holding it is refused outright, with nothing written. A store that
  is the repo root cannot be ignored: a new one is refused before anything is created
  (its own `*.tmp*` line would ignore files across the repo), and an existing one gets no
  line. A symlink on the store's path that sits inside a repo and points out of it (a
  linked `.claude-sandbox/`, a `WORK_ITEMS_ROOT` under a linked dir) is refused the same way; a
  link above every repo, such as a home-directory alias, is left alone. When the store cannot be made
  ignored, `ignored` is not recorded and `init` exits 1: the ignore comes first and the
  record after, so within a git repo, a recorded `ignored` means git ignores the store.
- **Tracking** never edits a `.gitignore`. If git ignores the store anyway, `init` prints
  the custody warning naming the rule to remove.
- **An existing store.** `init` on a store that exists never re-creates or rewrites what is
  there. With a flag, it records (or changes) the choice and, for `--no-track`, adds the
  `.gitignore` line. Without a flag, a recorded choice is kept; a store with no recorded
  choice (every store made before this file existed) is left as it is, with no menu, and a
  stderr note names the two flags. Such a store is treated as unrecorded until one is run.
  An existing store that is its own repo, not set up by `wi` (own, unrecorded), gets a note
  naming `wi init --no-track`, which adopts it.
- **prime and lint.** A store recorded `ignored` gets no custody warning, unless it is a
  sidecar store: that one gets a warning that it is recorded git-ignored and new items land
  in no repo, with the fix `wi init --track`, followed by the ignore line to remove when the
  sidecar repo ignores the store. A store recorded
  `tracked` that git ignores (or that holds ten or more items, none tracked) gets the
  warning, marked as against its recorded choice. A store with no recorded choice gets the
  `silently untracked` warning as before, its fix ending with recording the choice. In a
  sidecar layout neither fix offers `--no-track`. Like every custody warning, it is one
  line in `prime` (exit unchanged) and a problem in `lint` (exit 3). The check asks git
  about a new item's path and a new card record's path under `cards/`, so a rule that
  ignores only card records (a `cards/` or `*.json` line) gets the same warning, naming
  them: "new card records are git-ignored by `<rule>`" in place of "new items". The check
  that a store with its own repo is ignored by the repo around it asks about item paths
  only: there a rule that ignores only card records does not ignore the store.

`status:` is the only authority on state. `done` never moves a file — a
status-only close is a two-line front-matter change that merges cleanly
against any body edit. `wi archive --older-than 90d` moves closed items in a
dedicated commit: in a store that is its own repo `wi archive` makes it (§ The store's
own repo, Each change committed); in a store the repo around it tracks, run `wi commit`
right after it.

A write killed mid-way never blocks the store. An item in both `items/` and
`archive/` as one file (a kill between hard link and unlink) is a move half
done: the next `wi archive` finishes it, whatever the cutoff. If the item
was written in between, the two are separate files and archive refuses: the
`items/` copy is the current one, so `mv` it over the `archive/` copy. An empty item
file is a name reserved by a write that never landed: every command skips it
with a warning naming it, its name stays taken, and `wi lint` gives the fix
(`mv` the `.tmp` file beside it holding the content, or `rm` it).

## Example item

```markdown
---
id: repl3-retention-7f2a
title: Replication task 3 destination retention is a no-op
type: bug
status: doing
stage: implement
priority: 1
tags: [zfs, replication]
deps:
  - snapshot-cleanup-3c1d
owner: kyle@hooper
claimed: 2026-08-30T14:02Z
created: 2026-08-05
updated: 2026-08-30
refs:
  - plans/2026-08-05-snapshot-retention-reduction.md
---

zettarepl's target-side retention is driven only by naming schemas, so task
3's `retention_policy: SOURCE` parses zero destination snapshots.

## Acceptance
- [ ] two hourly runs later, brainboy shows pruning

## Handoff
- doing: applying the midclt call on a test dataset first
- next: verify zettarepl prunes after two runs, then apply to task 3
- blocked: —
- learned: retention_policy SOURCE parses zero snapshots under name_regex

## Notes
- 2026-08-30 claimed by kyle@hooper
```

## Front-matter fields

Emitted in this order, one field per line. Dates are date-only (`YYYY-MM-DD`)
except `claimed` (ISO-8601 UTC to the minute).

| Field | Type | Notes |
|---|---|---|
| `id` | `<slug>-<4hex>` | equals the filename stem; immutable; hash suffix from title+time+random so branches rarely collide; a new id is redrawn until it is in neither the store (items/, archive/) nor the same batch, and a new item is never written over an existing file (the write fails, nothing written) |
| `title` | one line, ≤120 chars | |
| `short_display_name` | one line, 1–40 chars | optional; the name agents give the item to the operator (§ Short display name and tag) |
| `type` | `task bug feature refactor workflow chore epic spike` | default `task`; drives backlog-yaml prefix and bugs-first |
| `status` | `todo doing blocked parked grooming done dropped` | the only authority on state |
| `stage` | `implement review testing uat uat_feedback` | pipeline sub-state; meaningful only when `doing` |
| `priority` | int 0–4, 0 highest | default 2; ↔ backlog.yaml 90/70/50/30/10 |
| `tags` | flow list `[a, b]` | |
| `deps` | block list of ids or `ext: <text>` | structural "cannot start until"; a dep is met when its item is `done`, `dropped`, or `doing` at stage `uat`/`uat_feedback` — looked up in `items/`, then `archive/`, so an archived item is judged by its status like any other and an archived done dep stays met; `ext:` never resolves, nor does an id in neither; one rule for `next`, `ls --ready`, `prime`, `show --json` (`blocked_by_unresolved`) and `claim`, which refuses a `todo` item whose deps are not all met |
| `parent` | id | grouping only, no blocking |
| `owner` | free string, e.g. `user@host` | set by `claim` (`--as`, else the claimant below), cleared by `release`/`done` |
| `claimed` | UTC minute | stale test in `next --stale` |
| `blocked` | string | required iff `status: blocked`; kept while parked or grooming, so `unpark` / `ungroom` returns to `blocked` |
| `parked` | one line | required iff `status: parked`; the deferral reason (set by `park`, cleared by `unpark`, `block` and `groom`); `lint` flags it on a todo/doing/blocked/grooming item (clear it with `wi set <id> parked ""`), and it stays on a dropped/done item as history |
| `grooming` | one line | required iff `status: grooming`; the open questions for the operator (set by `groom`, cleared by `ungroom`, `park` and `block`); `lint` flags it on a todo/doing/blocked/parked item (clear it with `wi set <id> grooming ""`), and it stays on a dropped/done item as history |
| `feedback` | one line | pipeline review feedback |
| `mode` | `autonomous interactive mixed` | backlog's `ticket_mode` |
| `complexity` | `low medium high` | pass-through |
| `alias` | `[SBRWM]-NNN` | allocated on first backlog-yaml export, never reused |
| `created` / `updated` / `closed` | date | `closed` required iff done/dropped |
| `refs` | block list of paths / URLs / `wi:<id>` / `todo:<hash>` | TOC to detail; never read by `wi` |
| `x_backlog` | one-level map of scalars | opaque backlog.yaml passthrough |

The grammar is a strict YAML subset: `key: value` scalars, one-line flow
lists, block lists of scalars, one level of map for `x_backlog`. No multi-line
scalars, anchors or nesting — prose goes in the body. `lint` reports any line
that does not parse, and `wi` never rewrites a file it could not parse.

**Quoting.** A value is written bare unless wi would read it back
differently or a YAML loader would reject it — empty, leading/trailing
whitespace, `: ` or ` #` inside, a trailing `:`, brackets or braces, a leading
YAML indicator (`- ? : , # & * ! | > ' " % @` and backtick), a bare `—`, a
lone `=` or `<<`, a tab or other control character, or a comma inside a flow
list. YAML's implicit typing is left alone (`priority: 2` and dates stay
bare), so a YAML loader may read a bare `true`, `null` or `0x10` as a
non-string where wi reads a string.
A quoted value is a YAML double-quoted scalar: `\` and `"` are written as
`\\` and `\"`, tab as `\t`, and other control characters, DEL, C1,
U+2028/U+2029, the BOM, U+FFFE/U+FFFF and lone surrogates as `\xNN` /
`\uNNNN`. The reader decodes exactly those plus the other YAML escapes
(`\0 \/ \U…` and the rest), so a value survives any number of rewrites
byte-identical; an unknown escape, or one that would decode to a line break,
is kept as written. So in a hand-written quoted value a backslash is an
escape: write `"C:\\temp"`, not `"C:\temp"` (which holds a tab) — `lint`
reports any front-matter value holding a tab or other control character,
or U+2028/U+2029. `wi` itself never writes one: a command given one exits 1 and writes nothing,
and `import` folds them to a space as it folds line breaks. A
single-quoted value reads `''` as `'`. A bare `—` or an empty value reads as
no value; a quoted `"—"` is the literal dash (`import` still reads a
backlog field that is `—`, such as `blocked_reason`, as no value).

Older `wi` versions escaped without unescaping, so every rewrite of a quoted
value added a layer of backslashes. `wi repair-escapes` finds them by a
heuristic — every front-matter value (quoted or not: the current writer
may have rewritten one bare) whose backslashes all pair as `\\` or `\"`,
with all such layers peeled — so it also lists a value meant that way: review
the dry run, narrow with `--id` / `--key`, then `--apply` (or fix one value
with `wi set`).

## Claimant

`claim` (and `prime`'s "you") names the caller as the first of:

1. `WORK_ITEMS_OWNER` — the explicit override, used verbatim (host included).
   Set it to pin one spelling across machines, containers or sessions. The
   deprecated `WI_OWNER` is read when it is unset or empty; when both are set,
   `WORK_ITEMS_OWNER` wins.
2. `$USER`, verbatim, as `<user>@<host>`.
3. `git config user.name`, read from the store's repo (2 s timeout; any
   failure skips it).
4. `getpass.getuser()` (skipped when it raises: no login variable and no
   password-database entry for the uid).
5. `unknown`.

`<host>` is the short hostname. An empty variable counts as unset. Steps 3
and 4 are sanitized to one owner token — each run of characters outside
`A-Z a-z 0-9 . _ -` becomes `-`, edge punctuation is trimmed (`Kyle
McFarlane` → `Kyle-McFarlane`) — so the name never splits `status` columns
or the `@host` suffix; a name with nothing left falls through to the next
step. `owner` is compared as an exact string: a claim recorded under an older
spelling (say `unknown@<host>` from before step 3 existed) reads as someone
else's — `release` still clears it, a re-claim needs `--steal`, or pin
`WORK_ITEMS_OWNER` to the old spelling.

### Deprecated environment names

`WI_ROOT` and `WI_OWNER` are the old names of `WORK_ITEMS_ROOT` and
`WORK_ITEMS_OWNER`, kept as fallbacks. When an old name is set and its new
name is unset or empty, or both are set and differ, `prime`
(a header line on stdout, reserved from the budget like the custody warning),
`lint` (stderr; not a problem, the exit is unchanged) and `init` (stderr) print
one line each, at most once per run: `wi: deprecated: WI_ROOT is set; use
WORK_ITEMS_ROOT`, or `wi: deprecated: WI_ROOT and WORK_ITEMS_ROOT differ;
WORK_ITEMS_ROOT wins` (the same for `_OWNER`). No other command prints them.
Both names set to the same value is silent: that is the transition export, which
works with an older wi too. `wi --help` names `WORK_ITEMS_ROOT` in a wi that
reads it.

## Moving a store

`wi` has no move command: a store moves once per repo, by one of these recipes,
run from the main checkout. Before any of them, back up the store
(`references/store-safety.md` § Backing up), stop the sessions that use the
store (their claims and its `.lock`), and update every `WORK_ITEMS_ROOT` (or
`WI_ROOT`) export that names the old path: briefs, open worktrees. Each recipe
ends with `wi --root .work-items lint`, and leaves no old directory behind (the
two-store warning catches one). `<old>` is the old store path, `.claude-sandbox/work` or `.work`.

A git-ignored store keeps its history in its own local repo (§ The store's own repo), so
most recipes end at one `wi --root .work-items init --no-track`: it adds `/.work-items/` to
the root `.gitignore` when no rule there ignores the store yet, makes or adopts the store's
repo, records `tracking: tracked` plus `repo: own`, and commits the store
(`wi init: adopted <n> item(s)`). An old-location store left in place stops every `init`
until it is moved (§ Root resolver, Old locations).

- **Git-ignored at `.work-items/` → its own repo, in place.** `wi --root .work-items init
  --no-track`. It finds the `/.work-items/` line and adds none, so nothing in the host
  changes. `prime` and `lint` name such a store, recorded `ignored` with no `.git`, with the
  "no history" notice until then.
- **Its own repo made by hand → adopted.** A `.work-items/.git` that no `init` set up (the
  "own, unrecorded" notice): `wi --root .work-items init --no-track`. Its commits, branch and
  any remote are kept, wi's set-up is added, and the outstanding changes are committed;
  history is never rewritten. A repo holding other files, a broken `.git`, an attribute
  file or a promisor config is refused, with nothing written (§ The store's own repo,
  Setting it up).
- **Tracked → its own repo.** `git rm -r -q --cached <old>`, `mv <old> .work-items`,
  `wi --root .work-items init --no-track` (it adds `/.work-items/`, makes the store's repo
  and commits the items), then commit the host's removal and the `.gitignore` line. The
  history before the move stays in the host's `git log` (or a backup bundle); the store's
  repo starts at the move. `init` refuses while the host still tracks paths under
  `.work-items/`, so the `git rm --cached` comes first.

  **Other clones.** The move commit deletes the store's files from git, so every
  other clone that pulls it loses its working copy of the store. Do one of these:
  - run this recipe in each clone **before** pulling the move; or
  - after pulling, recover the store in each clone:
    1. `git archive <move>^ <old> | tar -x`, which restores `<old>` as it was
       just before the move commit (`<move>` is the move commit);
    2. `mv <old> .work-items`;
    3. `wi --root .work-items init --no-track`, which finds the `/.work-items/`
       line already present, makes the store's repo and commits its items;
    4. `wi --root .work-items lint`.

  From then on each clone's store is its own, with its own history: nothing syncs them. A
  clone with uncommitted edits to tracked store files has its pull refused by git until
  they are committed or stashed.
- **Git-ignored at an old location → its own repo.** `mv <old> .work-items`, then
  `wi --root .work-items init --no-track`, then remove the old store's own ignore line from
  `.gitignore` if it has one (`/.work/`) and commit that `.gitignore` change. Nothing else is
  in git.
- **Sidecar → root.** A store at `.claude-sandbox/work/` in a sidecar layout has
  its history in `.claude-sandbox/.git`. Copy it out (`cp -a .claude-sandbox/work
  .work-items`), remove it from the sidecar with a commit in the sidecar repo
  `.claude-sandbox/` (ask the operator before committing there; the sidecar keeps the old
  history), then `wi --root .work-items init --no-track` (or `--track`, for a repo whose
  operator wants the host to track it). `init` refuses while `.claude-sandbox/work/items/`
  is still there.
- **Tracked → tracked**, for a repo whose operator wants the host to track the store.
  `git mv <old> .work-items`, then `wi --root .work-items init --track`, then commit.

## The store's own repo

A store at `.work-items/` can be its own local git repo, with no remote: the repo around it
(the host) ignores it, and the store's history is in `<root>/.git`, where `wi` commits each
change it makes (Each change committed, below).

**Setting it up: `wi init --no-track`.** The git-ignored choice (`--no-track`, the menu's
git-ignored, the no-terminal default) gives a store that is not at an old location its own
repo, new or adopted, in this order:

1. **Refusals**, exit 1, nothing written, after the ones every `init` makes (a linked
   worktree, a symlink out of the repo, a sidecar layout):
   - git does not say whether a repo is around the store;
   - the store's `.git` is broken (below: the reason);
   - an attribute file, a nested repo or gitlink, or a promisor config (below: the
     reasons), in the store's files or, for a store with a `.git`, in its repo;
   - the store's repo tracks a file outside the store's own paths, in its index or in the
     commit `HEAD` names: "`<root>` is a git repo holding other files (`<first>`): refusing
     to adopt it as a store repo";
   - the store's own git config has `include.path` or an `includeIf.<condition>.path`, which
     could set `core.hooksPath` over the `/dev/null` `init` writes, for a hand-run git;
   - the store directory is itself a bare git directory ("a git directory, not a store");
   - a store with no `.git` holds, at its top, anything but `items`, `archive`, `cards`,
     `README.md`, `store.yaml`, `.gitignore`, `.lock` and a write's `*.tmp*` file:
     "`<root>` holds `<name>`, which is not a store file: refusing to give it its own repo",
     since `git init` would make a repo of it all;
   - the host tracks paths under the store: "the host repo at `<host>` tracks `<n>` path(s)
     under `<rel>`: untrack them first" (§ Moving a store).

   A store at the top of a repo with no repo around it and no `repo: own` recorded keeps the
   repo-root refusal (§ Store tracking).
2. **The store files**, as for any store: `items/`, `README.md`, the store's `.gitignore`.
   From here to the first commit, `init` holds the store's lock (a 10 s wait, then exit 4).
   When a `.git` came or went while it waited, the refusals run again first.
3. **The host's ignore line, before any `git init`.** The host is asked from the store's
   parent, and `check-ignore --no-index` runs from the host's top on `<rel>/items` and a new
   item's path, so a store that is already its own repo is judged by the host, not by its
   own repo. A rule from a file inside the store (its own `.gitignore` holding `items/` or
   `*`) never counts: the host must ignore the store itself, or its `add -A` stages it. Outside
   git: "not in a git repo: no .gitignore written", and set-up goes on. A failure here records
   nothing and runs no `git init`, exit 1.
4. **The repo.** A new one is `git init -q --template=`: the empty template installs no
   sample hooks, and wins over `init.templateDir` and `GIT_TEMPLATE_DIR`; then
   `symbolic-ref HEAD refs/heads/main`. An existing valid one is adopted as it is: its
   history, branch and any remote are kept (`lint` names a remote). Both get the local
   config `core.hooksPath=/dev/null` and `core.fsmonitor=false`, so a hand-run git there
   (`references/store-safety.md` § Safe forms) runs no hook either. Then both keys are read
   back as that hand-run git resolves them, with git run without the store runner's `-c`
   pins (its ceiling and scrub kept); an include, an `includeIf` or a worktree config
   (`extensions.worktreeConfig`) that sets either over the written value stops set-up:
   "`<key>` resolves to `<value>` for a hand-run git there". A failure: exit 1,
   `own repo not set up: <why>; tracking not recorded`; a rerun is safe.
5. **The record**, `tracking: tracked` plus `repo: own`, once the repo is valid, so `repo:
   own` always names a repo that was valid at `init`.
6. **The first commit**, as `wi commit` makes one in an own store (its pathspec, deadline,
   retries and identity fallback): `wi init: store created` for a new repo in a store with
   no items, else `wi init: adopted <n> item(s)` (`1 item`, `2 items`). A failure prints `wi: WARNING store not committed: <why> (the
   change is saved; `wi commit` commits it)`, and `init` still exits 0; `lint` then shows
   the uncommitted notice.

Every git call `init` makes, the host's reads included, runs without the caller's git
steering: the runner's scrubbed names, `GIT_LITERAL_PATHSPECS` and `GIT_TEMPLATE_DIR` are
dropped, so a host hook's `GIT_DIR` or `GIT_INDEX_FILE` never sends `init` into the host's
repo. A rerun on an own store commits whatever is outstanding. At an old location (with
`--allow-old-location`) the git-ignored choice makes a plain ignored
store, recorded `ignored`, and says on stderr that an old location gets no repo of its own
(move it: § Moving a store). With no git on `PATH` it
makes the same plain store and warns `wi: WARNING git not found: <root> has no history of
its own; run `wi init --no-track` again where git is available`, exit 0.

**What is valid.** When `<root>/.git` exists, one git call decides it, `git rev-parse
--path-format=absolute --is-bare-repository --git-dir --git-common-dir --show-toplevel`,
run through the store runner (below) with a 2 s bound, before any lock is taken. The `.git`
is valid when that call exits 0, the repo is not bare, its top is the store (real paths),
and its git dir and common dir both lie inside the store but in none of its own paths
(`items`, `archive`, `cards`, `README.md`, `store.yaml`, `.gitignore`: a git dir there would be
committed with them, "`.git` points into the store's own path `<path>`"). So a `.git`
directory, a `.git`
file whose `gitdir:` lies inside the store, and a `.git` symlink to a place inside it are
valid; a `.git` file or symlink pointing outside the store (a linked worktree of another
repo, a submodule's git dir under the host's `.git/modules/`) is "broken: `.git` points
outside the store", and so is a bare repository, and an empty or damaged `.git` (git's
first error line). The runner's ceiling stops git from falling through to the host there.

**Attribute files and nested repos.** An own or own-unrecorded store that holds an attribute
file is broken, with the reason "`<path>` selects git attributes (a filter there can run
commands); remove it". `wi` writes none. It is found by a walk of the whole store (the
store's `.git` skipped) for any `.gitattributes`, by an `lstat` of
`<git-dir>/info/attributes`, and by any `.gitattributes` the store's index lists, which
counts even when it is gone from disk. Names are compared case-blind. Such a store is also
broken when it holds a nested repo, since git recursing into one reads that repo's own,
unpinned config and attributes: a `.git` anywhere below the store's root, or a gitlink (mode
160000) in its index, with the reason "`<path>` is a nested git repo or gitlink; remove it".
Every runner call that compares the work tree (`status`, and `wi commit`'s `diff --cached`)
also passes `--ignore-submodules=all`. Such a store is broken, too, when its git config
(read through the runner with `config --get-regexp`) sets `extensions.partialClone` or any
`remote.<name>.promisor`, with the reason "the store's git config sets `<key>` (a lazy fetch
from a promisor remote can run commands); remove it": a missing object would be fetched
from that remote, running the `uploadpack` or ssh command the config names. The runner also
sets `GIT_NO_LAZY_FETCH=1`; the refusal covers a git that does not read it. A dedicated
store keeps its attributes and its config: its repo's rules are the user's.

Which repo is around the store is asked from the store's parent; when git does not answer,
or fails other than with "not a git repository", the store reads as git missing (every check
silent, `wi commit` exit 3), never as a store with no repo around it.

**The store runner.** Every git call that acts in a store with its own `.git` (validation,
the custody check's `check-ignore` and `ls-files`, `git config user.name` for the claimant,
the checks below, `init`'s set-up and first commit, each write's commit, and `wi commit` in
an own store) goes through one runner. The host's own
reads (is the store ignored, does the host track it) use plain git, since they read the host.
- argv: `git -c core.hooksPath=/dev/null -c core.fsmonitor=false -c commit.gpgSign=false
  -c core.autocrlf=false -c core.safecrlf=false -c gc.auto=0 -c maintenance.auto=false
  -c core.attributesFile=/dev/null -c attr.tree=<the empty tree>`, then the arguments, as a
  list, never through a shell. `/dev/null` can never hold a hook, wherever git looks; the
  empty tree as `attr.tree` makes a git that reads that key take no attributes from any
  tree.
- cwd: the store. env: a copy without `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`,
  `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_COMMON_DIR`,
  `GIT_NAMESPACE`, `GIT_PREFIX` and `GIT_ATTR_SOURCE` (a host hook that calls `wi` has them
  set to the host's), and with `GIT_CEILING_DIRECTORIES` the store's real parent,
  `GIT_ATTR_NOSYSTEM=1`, `GIT_NO_LAZY_FETCH=1`, `GIT_OPTIONAL_LOCKS=0`,
  `GIT_TERMINAL_PROMPT=0`, `LC_ALL=C`, and
  `GIT_LITERAL_PATHSPECS=1` for every call but `check-ignore`, which refuses it.
  `GIT_AUTHOR_*`, `GIT_COMMITTER_*`, `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_NOSYSTEM` pass
  through.
- So no hook, fsmonitor, signing program, background gc, lazy fetch or global or system
  attributes file runs, and a clean filter can be selected only by a store attribute file or
  a nested repo, either of which makes the store broken.
- A store whose parent path holds `:` (the path-list separator) would split the ceiling, so
  the runner does not run there: the store reads as git missing, and every check is silent.

**Pathspecs.** A store path goes into a git pathspec only when git can match it: one
`ls-files -z -c -o --exclude-standard` call over the candidates lists something under it,
in the index (a removal to stage included) or untracked and not ignored. git fails on a
pathspec that matches nothing, which an empty directory does (an `items/` whose items were
all archived). When git cannot list, the paths on disk are used. The store's own paths are
`items`, `archive`, `cards`, `README.md`, `store.yaml` and `.gitignore`.

**What `prime` and `lint` report.** Problems are a `prime` header line and a `lint` problem
(exit 3); notices are a `prime` header line and a `lint` stderr line, exit unchanged.
`prime` shows at most one of these lines, the first in this order. It runs no host or remote
read, takes no lock, and makes at most six short git reads (validation, host lookup, the
promisor config read, attribute and pathspec listings, one `status`).

| Check | When | Tier | Fix named |
|---|---|---|---|
| own, missing | `repo: own`, no `.git` | problem | restore the store's repo from a backup, or `wi init --no-track` to start new history |
| broken | `.git` present and not valid | problem | the reason; never `rm -rf` the `.git` unasked |
| uncommitted | own; `git status --porcelain -z` on the own paths lists any | notice | `wi commit` |
| stale `index.lock` | own; `<git-dir>/index.lock` older than 10 minutes | problem | remove it only when no git process runs in the store (never while a session works it) |
| host does not ignore the store | own; the host's `check-ignore --no-index` from its top on `<rel>/items` and a new item's path names no rule from outside the store (the store's own `.gitignore` does not count) | problem | `wi init --no-track` (it adds the line) |
| host tracks the store | own; `git -C <host> ls-files -s -- <rel>` lists a path (mode 160000 is a gitlink) | problem | `git -C <host> rm -r -q --cached -- <rel>` (the files stay on disk), then commit in the host |
| a remote | own; `git remote` lists names | notice | names only, never URLs: a work-item store repo is meant to be local |
| own, unrecorded | a valid `.git`, no `repo: own`, a repo around the store | notice | `wi init --no-track` adopts it, history kept |
| no history | not at an old location, recorded `ignored`, no `.git`, git found | notice | `wi init --no-track` gives it its own local repo |
| `repo:` not `own`, or more than one `repo:` line | — | problem | `wi init --no-track` rewrites it |
| a `.git` in an old-location store | — | problem | move the store (§ Moving a store) |

`lint`'s uncommitted check takes the store's lock with a 2 s wait, so a write in flight is
never reported; when the lock is busy it skips the check and says so on stderr. The custody
check runs inside the store's own repo, where nothing is ignored unless the store's own
`.gitignore` ignores `items/`, which it then names. Every check is silent when git is
missing or slow.

**Each change committed.** In a store recorded `repo: own`, every command that writes an
item commits what it wrote into the store's repo, under the lock that held the write and
before that lock is released, so no other `wi` write lands between a file's rename and its
commit:
- the commands: `add`, `claim`, `release`, `handoff`, `done`, `note`, `block`, `unblock`,
  `park`, `unpark`, `groom`, `ungroom`, `set`, `next --pipeline --claim`,
  `migrate-parked --apply`, `repair-escapes --apply`, `import-todo` (not `--dry-run`),
  `import`, `export` (it writes aliases into items) and `archive`; `init` makes its own
  first commit (Setting it up, above);
- one commit per command, however many files it wrote; a command that writes nothing (a
  claim already held, a refused write, an archive with nothing old enough) makes none, and
  reads and dry runs run no git at all;
- commits follow the record, never the `.git` alone: a store without `repo: own` (plain,
  tracked by the repo around it, own unrecorded, dedicated) gets no per-change commit and
  runs no git for a write, so its commits stay `wi commit`'s (§ Committing the store).

What it does:
- **Before the lock**, the store's repo is validated as above (What is valid, with the
  attribute, nested-repo and promisor checks), each git call bounded at 2 s. No git runs for
  validation while the lock is held.
- **Only what the command wrote** is committed, and only the shapes `wi` writes: an item
  file one level under `items/` (`items/<name>.md`, no leading dot), an archived one
  (`archive/<year>/<name>.md`), a card record three levels under `cards/`
  (`cards/<id>/<N>/<name>.json`, N digits, no leading dot on any other segment), and
  `README.md`, `store.yaml` and `.gitignore`. For
  `archive` each moved item's source is committed too, so the history shows the move as a
  rename. The pathspec rule applies (Pathspecs, above): a source that was never committed
  and is gone from disk drops out, and only its destination is committed. A file the
  command wrote that git does not list (an ignore rule matches it, such as a global
  excludes file holding `*.md`) is not committed, and gets the warning below with `<path>
  ignored by git (see `wi lint`)`. A hand edit, a file staged by hand, or an earlier change
  whose commit failed is never swept into a command's commit unless it is in a file the
  command itself wrote: a hand edit, a failed commit's change, or a second session's edit
  to the same item file goes into the next commit of that file. Any other stays for
  `wi commit`, and `lint`'s uncommitted notice counts it.
- **Just before `add`**, the store is walked again for an attribute file or a nested repo
  (no git): one that appeared since validation would select a filter `add` runs, so the
  commit is skipped with the warning below, naming it. `export` refuses an output path
  inside the store, exit 1, nothing written.
- **The steps** are `wi commit`'s in an own store (§ Committing the store): the identity
  fallback, `add -A`, `diff --cached --quiet` (no change: no commit), `commit -q -m`, with
  `index.lock` retried three times 0.2 s apart and never deleted, through the store runner,
  all within one 5 s deadline. No `git gc` runs; only `wi commit` runs it.
- **The message** names the command and the item ids, never an item's text: `wi <verb>:
  <id>` for one item; `wi <verb>: <n> items` and a body of one `- <id>` line per item,
  sorted, for several. `archive` always takes the count form with the body (`wi archive:
  1 item`). `<verb>` is the subcommand's name (`next` for `next --pipeline --claim`).
- **A failure keeps the write.** The file is already in place when the commit starts. Any
  failure prints one stderr line, `wi: WARNING store not committed: <why> (the change is
  saved; `wi commit` commits it)`, and leaves the command's exit code and stdout as they
  would be: a caller that saw a failure could retry a write that landed, and a `note`
  would then be appended twice. `<why>` is git's first error line (200 characters at
  most), `another git process holds <git-dir>/index.lock (retried 3 times; never
  deleted)` for an `index.lock` conflict, `timed out` (with the `index.lock` sentence when
  a call was killed), `git not found`, `git did not answer`, or why the store's repo
  cannot take a commit (broken: the reason; own, missing: "`repo: own` is recorded in
  store.yaml but there is no .git"; a `.git` at an old location). Run `wi commit` once the
  cause is gone.
- **Cost.** A write in a store without `repo: own` adds one read of `store.yaml` and no git
  process. In an own store it adds about ten short git processes: four before the lock
  (validation, the host lookup, the promisor config read, the index listing), and under it
  `git var` twice (once per process), one path listing, `add`, `diff --cached` and
  `commit`. Observed 2026-10-15 with git 2.39.5: one `wi note` in a 500-item own store
  took 0.08 s with its commit and 0.06 s without (median of 15 runs, each a fresh `wi`
  process); `prime` and the read commands take no lock and are unchanged.

## Committing the store: `wi commit [-m <message>]`

`wi commit` is the one way to commit a store: a skill that commits the store runs it, never
`git` by hand. In a store that is its own repo, `wi` has already committed each change it
made (§ The store's own repo, Each change committed), so `wi commit` there commits what is
left: hand edits, and a change whose own commit failed. It commits only the store's own
paths that exist (§ The store's own repo, Pathspecs), each git step scoped with `--` to
them, so a file staged by hand outside them stays staged and out of the commit. It always holds the store's lock (a 10 s wait, then
exit 4), so it never races a `wi` write. The message and the store's state are checked
before the lock is taken.

| Store | What `wi commit` does | Exit |
|---|---|---|
| own | Through the store runner: `add -A`, then `diff --cached --quiet` (no change: no commit), then `commit -q -m <message>`, all sharing one 5 s deadline. An `index.lock` conflict (another git process in the store) is retried three times, 0.2 s apart; `index.lock` is never deleted. With no git identity (`git var GIT_AUTHOR_IDENT` or `GIT_COMMITTER_IDENT` fails) it commits as `wi <wi@localhost>`, written to no config; `GIT_AUTHOR_*` and `GIT_COMMITTER_*`, when set, still win. After a commit, once the lock is released, `git gc --auto` runs in the foreground, bounded at 60 s, at git's default threshold (the runner pins `gc.auto=0` for every other call). | 0; 3 when git fails |
| tracked by the repo that holds it: a host or sidecar repo, or a dedicated store's own repo | The same steps on the same paths with plain git: that repo's hooks and signing are its own rules, never bypassed. The caller's `GIT_*` steering (the runner's scrubbed names, and `GIT_LITERAL_PATHSPECS`) is dropped, here and in the ignore check. No prompt, 60 s a call; the lock is held that long, so another `wi` waiting on it may exit 4 after its 10 s. | 0; 3 on a failure, a hook's refusal included |
| ignored by the repo that holds it (`git check-ignore` on the store's directory exits 0), or recorded `tracking: ignored` | Prints `nothing to commit: <root> is git-ignored by <repo>` (or `… is recorded git-ignored …`). | 0 |
| outside git; or git not found, for a store with no `.git` and no `repo: own` | Prints `nothing to commit: <root> is in no git repo` (adding `(git not found)`). | 0 |
| git not found, for a store with a `.git` or `repo: own` | `not committed: git not found`: its changes stay uncommitted. | 3 |
| git did not answer (validation, or which repo is around the store) | `not committed: git did not answer …`. | 3 |
| own, unrecorded | Refuses: "`<root>` is its own git repo, not set up by wi: `wi init --no-track` adopts it". | 1 |
| own, missing; broken; a `.git` at an old location | Refuses with the reason `lint` gives. | 1 |

- **Output.** `committed <short sha>`, or `nothing to commit`. A failure is one stderr line,
  `wi: store <root> not committed: <why>`: git's first error line (200 characters at most);
  for an `index.lock` conflict, `another git process holds <git-dir>/index.lock (retried 3
  times; never deleted)`, which names the lock file whole; or `timed out`, which for a killed git call adds "if `<git-dir>/index.lock` is left,
  remove it only when no git process runs in the store" (for a tracked store, the git dir
  and the repo that holds it).
- **The message** is the caller's (`chore: work-item store - …` stays as it is); without
  `-m` it is `wi commit: outstanding changes`. The secret rule applies to it: a message
  `lint` would flag as a secret is refused, exit 1, never quoted, nothing committed, as
  `wi note` refuses a line. An empty message is refused too.
- **Checks before it.** An own store's commit runs no hook, so a caller with pre-commit
  checks runs them on the store's diff before `wi commit`; a tracked store's commit runs
  its repo's hooks itself.
- **An older `wi`** has no `commit` (argparse: `invalid choice: 'commit'`, exit 2); the
  calling skills name the hand commit under the lock to use there.

## Editing fields: `wi set <id> <field> <value>`

Sets exactly one front-matter field. `id` and `created` are immutable (exit 1).

- **List fields** (`tags`, `deps`, `refs`) take a comma-separated value —
  `wi set <id> deps a-1111,b-2222` — and are **replaced whole**, never
  appended to (`block --on` / `unblock --dep` add/remove a single dep).
- **Clearing**: the value `""` (or `—`) clears any field — there is no
  `--clear` flag: `wi set <id> deps ""`. (A `--clear` token is eaten by
  argparse regardless of quoting; it only passes as a value after a `--`
  separator.)
- **Validation**: `deps` and `parent` targets must resolve to existing items
  (archive included), exactly as `add --dep`/`--parent` requires — a dangling
  id exits 1, `ext: <text>` deps are exempt, and `--force` writes it anyway.
  An item can never be its own dep or parent — a self-reference exits 1 and
  `--force` does not bypass it. The item is then schema-validated as a whole;
  a value that breaks it (bad `status`, …) exits 3 and nothing is written.
  `priority` must be an integer 0-4; anything else exits 1 before anything is
  written.
- **`short_display_name`** is stripped, a blank value clears it, and one
  over 40 characters exits 1 before anything is written (§ Short display
  name and tag).

## Short display name and tag

`short_display_name` is optional: the name agents give the item when they
write to the operator. It is a noun phrase of 3–6 words, with no id or tag
in it and no leading article (`flaky gate test`, not `the flaky gate test`
or `gate test d1e3`). Its words are used verbatim, and an agent adds an
article in prose when the sentence needs one. `wi` checks only its shape,
never its words.

- **Setting it.** At filing, with `wi add "<title>" --short-display-name
  "<name>"`, or later by an explicit `wi set <id> short_display_name
  "<name>"` from the item's owner. A mention never writes it.
- **Its shape.** `add` and `set` strip it. On `add` a blank value (or `—`)
  leaves the field unset; on `set` a blank value (whitespace-only included)
  clears it, as `""` and `—` do. So neither ever writes
  `short_display_name: ""` or a literal dash. Over 40 characters, counted
  after the strip, exits 1 and writes nothing. A hand-written value that is
  blank, padded or over 40 characters is a `lint` problem, and a `set` of
  any other field on that item exits 3 until the name is set right.
- **When it is absent,** an agent writes a name from the title at each
  mention and stores nothing.
- **Output.** Every text row that prints a title prints the title cell
  `[<name>] <title>` in the title's own column: `ls`, `next` (every form),
  `prime` (its HOLD, DOING and READY lines), `needs-input`, and `estate`'s
  SECURITY, DECISION, STALE and READY rows. No `--plain` column is added,
  and an item without the name prints its title alone. Every `--json`
  record carries `short_display_name`, null when unset; it is the
  unambiguous form, since a title that itself starts with `[` reads like a
  name in text. `show --brief` prints it after `title`.
- **Store-only.** The backlog-yaml bridge does not carry it: `export` leaves
  it out, `import --update` keeps it, and a fresh import creates items
  without it.

**The tag** is the id's last four hex, `id[-4:]` (`d1e3` in
`flaky-gate-test-d1e3`): a recognition cue for the operator, not a unique
reference. `wi` resolves an id by exact match or alias, then by unique
prefix, and never by suffix, so a tag handed to `wi` can resolve to a
different item whose slug begins with those four hex, and two items can
share a tag. Given a bare tag, list the files that carry it, and ask when
more than one matches:

```bash
find <store>/items <store>/archive -name '*.md' | grep -E -- "-<tag>\.md$|/<tag>[^/]*\.md$"
```

## Parked

`parked` is deliberate deferral — "not now, on purpose" — where `blocked` is
"cannot proceed". `wi park <id> "<reason>"` sets `status: parked` and
`parked: <reason>`, releases any claim (`owner`, `claimed`, `stage`) and
appends a dated Notes line; it refuses a done or dropped item. A parked item
is never ready: `next` (every mode) leaves it out and counts it in its footer
and `counts.parked`; `prime` shows one `PARKED <n>` line, never a list and
never under BLOCKED; `ls` omits it by default and `ls --status parked` lists
it. A dep on a parked item does not resolve.

`wi unpark <id>` returns the item to `todo` — or to `blocked` when it still
carries a `blocked:` reason. It never returns to `doing`: the claim was
released on park, and whoever held it is not assumed to still be working it.
To abandon a parked item, `wi done <id> --drop`, then `wi archive` as usual.

`wi park` is the only way in. `wi set <id> status parked` exits 1 and points
at `park`, since set would record no reason and release no claim. `wi set <id>
status <other>` on a parked item counts as an unpark: the `parked:` reason is
cleared and a Notes line is added. `wi release` never unparks. On a parked
item it clears only `owner`/`claimed`/`stage`, so an agent cleaning up a
claim the operator has since parked leaves the park in place.

Before `parked` existed, deferral was spelled `wi block <id> "PARKED: …"`.
`wi migrate-parked` lists the `blocked` items whose reason starts with
`PARKED` (case-sensitive, a whole word) and what their parked reason would
be. `--apply` converts them: the parked reason is the text without the
prefix, `blocked:` is cleared, the claim is released, and a Notes line is
added. Nothing is written without `--apply`. The prefix is `PARKED`, then an
optional parenthesised group, then any `:`/`-`/`—` separator. The group is
provenance, not reason: `PARKED (operator 2026-09-19): Paseo undecided` parks
with reason `Paseo undecided`. The migration's Notes line keeps the whole
original reason, group included (`parked (migrated from blocked: PARKED
(operator 2026-09-19): Paseo undecided)`). A prefix with nothing after it
keeps the whole text as the reason.

The backlog-yaml bridge has no deferred state to map to: a parked item
exports as `status: blocked` with `blocked_reason: "PARKED: <reason>"`, and
importing a blocked story whose reason starts with `PARKED` yields a parked
item — the same prefix rule as `migrate-parked`. The park and its reason
round-trip. A `blocked:` reason kept under a park does not travel: the
export carries only `PARKED: <reason>`. `import --update` keeps the store's
own `blocked:` on a parked story, but a fresh import cannot restore it, so
that item's `unpark` goes to `todo`. A provenance group, if any, is dropped
from the imported reason. A ralph run over the exported backlog sees the
item as blocked, never as work. That prefix rule eats any punctuation after
`PARKED`, so a reason that itself starts with punctuation (`-`, `— later`,
`...`) — or one that would read back unwrapped, like `"-"` — exports quoted:
`blocked_reason: "PARKED: \"- later\""`. Import unwraps `PARKED: "…"` (the
prefix, one space, then text in double quotes) only where export would have
written it — when the text inside, written plain, would not read back as
itself; any other quoted reason (`PARKED: "x"`, `PARKED: ""`, `PARKED: "a"
and "b"`) gets the prefix rule, quotes kept. So a reason round-trips
byte-identical from the first cycle — except, on a fresh import, one that
itself ends `; requires ext: …`, whose tail is taken for the `ext:` suffix
(below). `migrate-parked` reads only hand-written text and never unwraps
the quotes.

backlog.yaml `requires` holds story ids only, so an item's `ext:` deps
travel in its `blocked_reason`, after any reason: `vendor; requires ext: a,
ext: b` (on its own for an item with no reason). `import --update` strips
exactly the suffix those deps produce — the store item's own `ext:` deps —
so a reason that itself says `requires ext:` is kept, and export →
`import --update` round-trips byte-identical. A new item has no deps to
check against: import takes the last `; requires ext:` group as the suffix
(and a whole reason `requires ext:…` only on a story that is not
`blocked`), strips it and restores those deps — so on a fresh import a
reason ending `; requires ext: …` of its own becomes a dep. Every exported string
value is double-quoted, a title starting `[` or `{` included; only an extra
story field import stored as JSON (a list or mapping) is written back raw,
as YAML flow. A `notes` value holding a character a YAML loader breaks on or
rejects raw (U+2028, NEL, a control character) is written as a double-quoted
scalar instead of a `|-` block.

## Grooming

`grooming` means the item waits on the operator's answers — it has open
questions, where `parked` is "not now" and `blocked` is "cannot proceed".
`wi groom <id> "<questions>"` sets `status: grooming` and `grooming:
<questions>` (one line), releases any claim (`owner`, `claimed`, `stage`),
clears a `parked:` reason and appends a dated Notes line; it refuses a done
or dropped item. `wi ungroom <id>` returns it to `todo` — or to `blocked`
when it still carries a `blocked:` reason — never to `doing`. The rest
mirrors Parked: `set status grooming` exits 1 and points at `groom`; `set
status <other>` on a grooming item is an ungroom; `release` never ungrooms;
`claim` refuses; `park` and `block` supersede it (and `groom` supersedes a
park).

A grooming item is never ready: `next` (every mode) leaves it out and
counts it in its footer and `counts.grooming`; `prime` shows one
`GROOMING <n>` line; a dep on it does not resolve. Unlike a parked item it
needs attention, so `ls` lists it by default. The backlog-yaml bridge maps
it as it maps a park: `status: blocked`, `blocked_reason: "GROOMING:
<questions>"`, and a blocked story with that prefix imports as grooming —
questions starting with punctuation (`- [ ] x`) export quoted, `GROOMING:
"- [ ] x"`, and import back verbatim, as a park reason does.

## Operator questions: `decision N:` / `answer N:`

The canonical marker for a question to the operator is a body line that
starts `decision N: <one line>`; the reply is a body line
`answer N: <reply>`, anywhere in the same item's body (the librarian-mode
Report convention). A decision is unanswered while its item has no `answer N:`
line with the same N. Both must start the line — `- decision 4:` is not a
marker — and a line inside a fenced code block is text, not a marker. N is
never reused across the store; a revised question keeps its number:
`$WI raise <id> --revise N`, which appends the restated headline under a
`revised:` line (§ Card records) — when N repeats, `needs-input` shows the
last line's text. `answer 40:` answers decision 40
only, never decision 4. `<reply>` is the operator's reply verbatim, on one
physical line (an exact `N: letter` reply is stored as its letter; the
caller's rules give the rest); a caller's form that opens with its own
wording (`answer N: drop …`, say) appends it as ` — "<reply>"`, and a plain
reply that opens with such a form word is written in double quotes. A reply
recorded after the fact goes on an indented `verbatim N …` line under the
answer, which, indented, matches neither marker.

**One counter.** Every question a caller puts to the operator takes its N
from the store's one counter, the `counters:` block in `store.yaml` that
`wi raise` advances under the store's lock (§ Allocating a decision
number), so `needs-input` and the estate sweep see every ask; the caller's
rules may name exceptions (librarian-mode's opt-in dialog and session-name
gate). A source's own label — a series' `OQ3`, a
gate's `G5` — rides in the decision's text (first in the question,
`decision 41: F7 (oversize upload) · …`), never a marker: `decision OQ3:`
and `answer G5:` match neither.

**Another repo's decision: `<repo>#N`.** A line that names a decision in
another repo's store writes it `<repo>#N` (`agents#12`), `<repo>` being
the name of that repo's `origin` remote (its last path part, without
`.git`), else its main checkout's directory name; a bare N, or `decision
N`, always means this store's own. It never starts a line, so neither
marker takes it for one of this store's.

The headline is one physical line: `wi` reads its text to the end of the
line, so a headline wrapped over two lines loses everything after the
break. Its canonical form lists the options in letter order and marks the
recommended one with `[recommended]` right after it:

```
decision N: <question> — options: (a) … [recommended] | (b) … | (z) decide later
```

**Reading the recommendation from a headline.** Older headlines mark it
other ways, and a reader of the store (the `work-review` skill, the
librarian's Groom table) takes each as the same mark:

- `[recommended]`, or a bracket that opens with it — `[recommended: why]`,
  `[recommended by the planner]` — after an option;
- `(rec)`, or `(plan rec)` with or without a reason, after an option;
- `Rec (x)`, `Rec x`, or `rec: (x)`, naming the option's letter;
- the word `recommended` beside an option.

A headline with none of these may carry a label in their place — *your
preference — no recommendation*, or *no recommendation — outside my
authority* — and a reader shows that label. Only a headline that names
neither a recommendation nor a label reads "no recommendation recorded".

`wi needs-input` lists every open item awaiting the operator: each grooming
item (with its questions) and each unanswered `decision N:` (with N and its
text), on todo, doing, blocked, parked and grooming items alike; closed
items never show. A human row reads `<id>  <title cell>  grooming:
<questions>` or `<id>  <title cell>  decision N: <text>`, the title cell
being `[<name>] <title>` or the title alone (§ Short display name and tag).
`--plain` prints `id<TAB>grooming|decision<TAB>N or -<TAB><title
cell><TAB>text`: the title cell is fourth, so the free text stays last;
`--json` one record per item with `title`, `short_display_name`,
`grooming` and `decisions`, each decision a record of `n`, `text`,
`raised` and the four shown-and-seen fields (§ Shown and seen), `null`
where the item has no such line. It exits 2 when nothing awaits the
operator.

**Card lines.** A card stored before v5 (no `card:` line) is read by the
decisions skill's legacy reference; a v5 card is a record (§ Card records).
A caller may store the decision's card as indented lines
under its headline (`raised:`, `what:`, `why now:`, `why ask:`,
`context:`, `impact:`, …; the librarian-mode convention). Indented, they
match neither marker, and `wi` reads none of them except the first
`raised:` per N (the decision's age). `why ask: <class> — <reason>` is one
physical line: why the question came to the operator, opening with its
class. `impact: → <effect> · later: <wait> · reach: <reach> [· ⚠ undo:
<undo>]` is one physical line too: what the decision changes across its
options, written when it is raised, for the views of the decision to read;
its undo is there only when some option is one-way or costly to undo,
marked `⚠ undo:` and naming that option, as the option's own line marks
it (a line stored before that rule may carry a plain `undo:`, read as
written). `wi` reads none of it.

`wi prime` also shows a `HOLD <n>: <id> (<title cell>) …` line, first under
the header, for open items tagged `hold` — an operator hold gates what may
move.

## Allocating a decision number: `wi raise` / `wi counter`

A new decision's N comes from `wi`, never from a grep of the store:

```
$WI raise <id> -- '<question line>'   # prints N
$WI counter                           # prints the last N given out
```

**`wi raise`** takes the store's lock (flock on `<root>/.lock`, 10 s, then exit 4) and, in
that one locked step:

1. refuses a `store.yaml` holding conflict markers or a `decision:` value that is not a
   whole number (exit 1, nothing written);
2. takes the last N: the larger of the counter and the highest N on a column-0
   `decision N:` line outside a fenced code block, in `items/` and `archive/*/` (the
   markers' own rules, § Operator questions);
3. N is that plus one;
4. appends two lines to item `<id>`'s `## Notes`, as `wi note --raw` does:

   ```
   decision N: <question line>
     raised: <UTC time, to the second>
   ```

5. writes `decision: N` in the `counters:` block (§ Store tracking), adding the block when
   the file has none;
6. prints N alone on stdout.

The question goes after `--`. It is one physical line, is not exactly `--`, and does not
start with the word `decision`, in any case (`wi` numbers it); it passes `wi note --raw`'s refusals (a line break, an empty
text, a `## ` line, a fence opener, any line `lint` would flag as a secret), and the
numbered headline passes them too. A refusal exits 1, writes nothing and never quotes the
question. A usage error (more than one text, or a text starting `-` that is not the one text
after `--`) exits 2 and counts and places the texts, never echoing one. `raise` never reads stdin. A store that is its own repo gets one commit holding
the item and `store.yaml`, through the lock's commit path (§ The store's own repo); in a
store the repo around it tracks, `$WI commit` commits both. A crash after the item is
written and before the counter loses nothing: the next reader takes the larger of the two.
A headline with only its `raised:` line is a headline-only decision: no card is stored. The
card-record forms of `raise` (a stored card as its record, a revision of an open decision,
machine lines under a card) extend this step, under the same lock (§ Card records).

**`wi counter`** prints the last N given out, the larger of the counter and the items'
highest N (0 for an empty store), and exits 0. It is read-only and takes no lock. It refuses
a `store.yaml` it cannot read the counter from, as `raise` does (exit 1).

**The reseed.** `wi lint` compares the counter with the items' highest N, `archive/`
included. A counter behind the items (a `decision N:` line written by hand, by an older
`wi`, or by a session that did not run `raise`) is reseeded inside the store's lock, which
commits it in a store that is its own repo: `lint` re-reads the counter and rescans the
items under the lock, and writes only when the larger of the two is above the counter it
re-read. It prints `counter: decision reseeded <old> → <new>` on stderr, a notice, and the
exit code is unchanged. A counter ahead of the items is a gap: numbers are never reused, so
a gap is valid, never lowered, and `lint` says nothing. An existing store seeds itself at
its first `raise` or `lint`; until then it behaves as the old grep did, except fenced lines.

**Accepted limits.** Two branches of a host-tracked store can each give out the same N, as
they could before the counter; the merge shows it as a `store.yaml` conflict, refused until
resolved. A store rolled back to an older copy can give out again a number already shown
whose `decision N:` line the restored copy lacks. `wi counter`, which takes no lock, can
print a lower number while `wi archive` is moving the item that holds the highest N; `raise`
and the reseed read under the lock and are not affected.

## Card records

A decision's card is kept as **one immutable JSON file per revision**, written by `wi` and
read by the decisions skill's card-record reference (operator-interaction), which defines its
fields. `wi` checks only what it needs to write the file safely and build the headline.

```
$WI raise <id> --record <file|-> [--lines <file|->] [--check]
$WI raise <id> --revise N --why '<why>' --record <file|-> [--lines <file|->] [--raised <UTC>] [--check]
$WI raise <id> --revise N --why '<why>' [--raised <UTC>] -- '<question line>'
$WI raise <id> --revise N --why '<why>' --lines <file|->
```

Each prints N (`--check` prints a `check: ok` line instead). stdin is read only when
`--record -` or `--lines -` names it, and at most one of them may. `--record` and a question
line are exclusive (the headline is built from the record); `--why` and `--raised` go only
with `--revise`; `--lines` goes with `--record`, or alone with `--revise N`.

**The file.** `cards/<item id>/<N>/<rev, each : written ->.card<k>.json`, relative to the
store root (the directory holding `items/`), for example
`cards/decision-card-v5-no-card-level-effect-fi-9168/341/2026-10-23T10-00-00Z.card5.json`.
Its bytes are `json.dumps(record, ensure_ascii=False, indent=2)` and a newline, UTF-8, LF,
created exclusively: an existing file is never replaced. A record is never re-serialized
after it is written, so a hash of the file is a hash of the bytes `wi` wrote. `wi archive`
never moves `cards/`: an archived item's `card:` lines still resolve.

**What `wi` checks**, all before anything is written: what reads only the record (its
size, JSON, fields, built headline and both secret scans) before the store lock is taken,
the rest under it:

- the record is at most 256 KB as read and at most 256 KB as written (the indented bytes,
  checked before the secret scans), UTF-8, strict JSON (no `NaN`, `Infinity`, a number that
  overflows to one, or a non-zero number that reads as 0; no duplicate key at any depth),
  nested at most 64 deep (objects and lists, the record itself the first), with no key over
  256 characters, and one object; an error names a position, never content;
- `format` is `decision-card/<k>` (k from 1, at most four digits), `rev` is `YYYY-MM-DDTHH:MM:SSZ` with ASCII
  digits (a minute-form `rev` is refused on write, with the fix: write it to the second,
  `…:00Z`); each by a full match;
- a new raise writes N into `n`, over any value; `--revise N` needs `n` equal to N;
- `q`, each option's `title`, `label.id`, `label.name` and `norec` are non-empty text on one
  line with no control, format (Unicode Cf: zero-width, bidi, soft hyphen, BOM, tag) or
  line-separator character and none of the headline's own tokens: ` — options: `, ` | `,
  `[recommended]` (any case) and `⚠ one-way` anywhere, and an option marker anywhere but
  in `q`: a bracketed lone letter a–z (`(b)`, `[b]`) followed by a space or the end, and not
  touching a letter before it (`file(s)` and `a[i]` are text); a leading tag (`[WIP] …`,
  `(Optional) …`, `(Re)start …`) is text, and a digit (`(1) first`) is never an option letter; `q` does not start with whitespace or the word `decision`, nor, with
  no `label`, read as one (`<id> (<name>) · `); `label.id` and `label.name` hold no `(`, `)`
  or `·`, nor their lookalikes (full-width `（` `）`, U+0387); with `rec` null, no title holds ` — ` (the norec label's boundary);
- the built headline reads back into the record's parts, as built and again in its NFKC
  form with variation selectors dropped (so a no-break or em space around a dash, a
  full-width bracket or bar, or `⚠` with U+FE0F forges nothing): ` — options: ` exactly
  once; `⚠` only as the one-way mark; a question that neither starts with `—`, `|`, `·` or
  `⚠` nor ends in one of those or an open bracket; with `rec` null, ` — ` only as the
  boundary before the norec, which follows it exactly; ` | ` splitting the options into
  exactly one `(k) ` part each, in letter order, with no other option marker and no part
  starting or ending so; `[recommended]` once, closing the rec's option. A refusal names
  the token's class (an option marker (x), the recommended mark, the options separator, a
  dash, the label separator, the one-way mark);
- `options` is a non-empty list, each with a letter `k` (a–z, in order, each once, so (z)
  last) and a `title`; `rec` is any option's letter, (z) included, or `null` with `norec`;
  `label`, when present, is `{id, name}` with `id` one word; `oneway`, when present, is
  `true` or `false`;
- the item's id is one path segment (`[a-z0-9][a-z0-9-]*`, at most 128 characters), so a
  raise that passes every check, and `--check` with it, cannot then fail to name its file;
- every line of the bytes, and every decoded string value of the record (keys too), whole,
  pass the secret scan (§ Secret rule); an item of a list under a key (a string, number or
  boolean) is also scanned as the line scan sees an object's member, `"<key>": "<item>"`
  (so `"api_key": ["…"]` reads as the assignment it is), and a multi-line item also as
  `<key>: <item>`; a hit is named by the record's line, or by the value's JSON path and the
  line within it (`options[1].plan line 2`), never by content (a key is named only when it
  looks harmless, letters, `_` and `-` with at most two trailing digits, at most 32
  characters; any other by its place);
- the bytes and every item line encode as UTF-8 (a lone surrogate is refused);
- `cards`, `cards/<id>` and `cards/<id>/<N>` are each a real directory or missing, never a
  symbolic link, and the record's directory lies under the store's `cards/`; a missing
  level is made one at a time.

A refusal exits 1 (a bad record or form) or 3 (a file in the way, a symbolic link), names
the field or the path, and writes nothing; no directory is made before every check has
passed. `--check` runs every check, the same ones in the same order, and writes nothing: it exits 0 when the raise would go through, else as the raise would.

**The headline**, built, never typed, on one physical line, in § Operator questions' form:

```
decision N: [<label.id> (<label.name>) · ]<q>[ ⚠ one-way] — options: (a) <title> [recommended] | (b) <title> | … | (z) <title>[ — <norec>]
```

`[recommended]` follows the `rec` option's title; with `rec` null, ` — <norec>` follows the
last option; `⚠ one-way` follows the question when `oneway` is true.

**The item's lines**, appended at the end of `## Notes` after the file is written, the
`card:` line last but for the machine lines:

- a new raise: the headline; `  raised: <UTC, to the second>`; the `card:` line; the
  `--lines`;
- `--revise N`: the restated headline (from the record, or the question line); the
  `--raised` line when given; `  revised: <UTC> — <why>`; the `card:` line (with
  `--record`); the `--lines`.

```
  card: cards/<item id>/<N>/<file> rev <rev> · decision-card/<k> — the card is this record; read it with the decisions skill's card-record reference; never backfill this card from lines
```

It is indented, so it matches neither marker and `raised:` is still read past it. `wi`
reads it as `^[ \t]+card: (cards/<id>/<N>/<file>) rev (<rev>) · (decision-card/<k>)(?: — .*)?$`,
a full match, under the block rule of `raised:`: it belongs to the `decision N:` headline it
is indented under, and the last one per N names the current record. The trailing words are
for a session on older plugins, whose backfill rule would otherwise write a legacy card over
this one.

**`--revise N`** (N of 1–9 digits) needs a `decision N:` headline on the item, and is refused (exit 1,
nothing written) when any item in the store, `items/` or `archive/`, holds an `answer N:`
line outside a fence: an answered card is never rewritten. A follow-up (later, tell me, dig
into, expand, hold) is never stored as an answer line; one that was is rewritten as a
`wake N:` line first. A headline-only revision (a question line) is refused when N has a
`card:` line: revise it with `--record`. `--why` is one line, not empty, opens no fence and
holds no secret shape (`wi note --raw`'s refusals). `--raised <UTC>` (the write pattern)
fills the ask time of a decision with no `raised:` line yet, as when a headline-only
decision gets its card; it is refused when N has one.

**Machine lines** (`--lines`): each one indented physical line keyed `delegation:`,
`terms:` (the answer-changes plan), `act:` or `grant:` (the signed-grants plan), secret-clean,
a `grant:` line naming its id; `wi` checks no more of their grammar. Any other key is refused (a card's content goes in the
record), and `raised:`, `revised:` and `card:` are `wi`'s own. `--revise N --why '<why>'
--lines <file>`, with no record and no question line, adds them to an open decision that has
a `card:` line, with no new record (the `rev` and the file stay, so answers to it keep
counting): `  revised: <UTC> — <why> (machine lines added; record unchanged)` and the lines
are inserted directly after the current card's block (its last `card:` line and the indented
lines under it). It is the one place `wi` writes inside a body rather than at the end of
`## Notes`. A card lists a grant by such a `grant: <id>` line; lines can be added only while
N is open.

**A stopped raise.** The file is written before the item's lines. A raise that stopped
between them leaves a file no `card:` line names: the same raise run again finds a file
with its exact bytes, named by no `card:` line in `items/` or `archive/`, and adopts it,
writing only the item's lines. A file named by a `card:` line is immutable (exit 3: give the
revision a new `rev`); an unnamed one with other bytes, or anything at that path that is not
a regular file, is refused (exit 3), with the fix: delete the orphan, then run the raise
again.

**The commit.** A store that is its own repo gets one commit holding the file, the item and
`store.yaml`; in a store the repo around it tracks, `$WI commit` commits them.

## Closed: `closed N:`

Once an answered decision's outcome has taken effect, the caller records it
as a body line in the same item, one physical line, never wrapped, in one
of three forms:

```
closed N: acted <short sha | item id>
closed N: rule <repo path>
closed N: superseded by <M | <repo>#M>
```

`acted` names the commit or the item that carried the answer out; `rule`
the file the answer became a standing rule in; `superseded by` the later
decision that replaced it. An answer carried out by several changes is
closed when the last of them lands; one that changes nothing closes as
`acted <the id of the item it was recorded on>`. A `drop` answer
(`answer N: drop …`, the word `drop` unquoted) needs no `closed N:` line
and counts as closed — a plain reply quoted as `answer N: "drop …"` is not
one; any other answered decision with no `closed N:` line is answered but
not closed. When N repeats, the last line is its state.
`closed N:` is neither `decision N:` nor `answer N:`, so it opens no
question and answers none: `needs-input`, the decision counter and the
estate sweep pass it by. The target is one token, never containing a
space. `wi` does not parse it yet; a reader splits it with
`^closed (\d+): (acted|rule|superseded by) (\S+)$`.

## Shown and seen: `shown N:` / `seen N:`

Each time decision N is put in front of the operator, the session that
displays it appends a body line in the item that holds `decision N:`; at
the operator's next turn in that session (or an answer found at a page or
doc read-back), it appends a second. One physical line each, never wrapped:

```
shown N: <UTC time> <chat | page | doc>
seen N: <UTC time> <turn | page | doc>
```

The time is `YYYY-MM-DDTHH:MM:SSZ`, UTC, on the writer's clock (`date -u
+%Y-%m-%dT%H:%M:%SZ`); `raised:`'s minute form also reads. A line whose
first token after `N:` is not written in one of those two forms is not read
(`wi` checks the form, not the calendar, and keeps the time as written).

- **What is a showing:** a render at card or block level (`chat`); a card
  on an answer page at the publish that put its current `rev` there
  (`page`); a decision's section in the tick-box doc, when shared or
  rewritten unticked (`doc`). A list line, a tag-size mention, a Groom row,
  an echo or a hint is not a showing and writes nothing.
- **What sees it:** the operator's first turn after the showing, in the
  session that showed it (`turn`); a new answer to the card's current
  `rev` found at a page read-back (`page`); changed ticks or words for it
  found at a doc read-back (`doc`). A chat turn never sees a page or doc
  showing.
- **Reading them:** first shown is the first `shown N:` line, last shown
  the last one, last seen the last `seen N:` line. The last showing has
  been seen when a `seen N:` line comes after the last `shown N:` line in
  file order. File order decides, never a comparison of the two times:
  writers' clocks differ. With no `shown N:` line the showing is not
  recorded: the decision's age comes from `raised:`, and the operator
  counts as cold to it. Lines written before this convention do not exist:
  there is no backfill.
- **Writing them:** always append, at column 0; never indent one (an
  indented line is a card line) and never insert one between a
  `decision N:` headline and its card, which ends the card and hides its
  `raised:`. Never write `<repo>#N` here: a session records a showing only
  in the store that holds the decision. `shown 40:` is about decision 40
  only, and a line inside a fenced code block is text.
- **Hold on `seen N:`:** writers append `shown N:` lines only and write no
  `seen N:` line, so no push carries one, until an `answer 180:` line in
  the claude-plugins work store chooses (a) (decision 180 asks whether
  `seen N:` lines may go into a tracked, pushed store; read it with
  `wi --root <that store> show` on the item holding `decision 180:`; a
  store that cannot reach it keeps the hold); any other answer, a
  `wake 180:` or no answer keeps this hold, and every other rule here
  stands either way.

Neither line is `decision N:` nor `answer N:`, so they open no question and
answer none: `needs-input`, the decision counter and the estate sweep pass
them by as questions. `wi` parses them, read-only and into the JSON views
only (`needs-input --json`, `estate --json`): each decision record carries
`first_shown`, `last_shown`, `last_seen` (each the time as written, or
`null`) and `unseen` — `null` with no `shown N:` line, `true` when no
`seen N:` line follows the last `shown N:` line, else `false`. Text and
`--plain` output are unchanged. Append them with `wi note <id> --raw --
'<line>'`, which puts the line at the end of `## Notes` under the store's
lock, or with Bash, as for every other record line.

## Decided alone: `decided:`

What a caller decided without asking is recorded as a body line that starts
`decided:` — one physical line, never wrapped:

```
decided: <UTC time> <class> — <what was decided, and why it was safe to decide alone> · authority: <authority> · reopen: <how to undo it>
```

The time is in `raised:`'s form (`2026-09-30T14:05Z`); the class is a
kebab-case tag from the caller's class list; the authority names what let
the caller decide it (`task`, `answer N`, or a class the caller's rules let
it decide alone); `reopen` says how it is undone. The what field never
contains ` · authority: ` or ` · reopen: `, the separators a reader splits
on. It is neither `decision N:` nor `answer N:`, so it opens no question
and answers none: `needs-input`, the decision counter and the estate sweep
pass it by. `wi` does not parse it yet; a reader splits it
with `^decided: (\S+) ([a-z-]+) — (.*?) · authority: (.*?) · reopen: (.*)$`.

## Body sections

- untitled text before the first `##` — description; the first paragraph is
  the summary `show --brief` and `prime` print.
- `## Acceptance` — `- [ ]` / `- [x]` bullets; exported to `acceptance:`.
- `## Testing` — bullets, typically `command: …`; exported to `testing:`.
- `## Handoff` — four bullets `- doing: / - next: / - blocked: /
  - learned:` (`—` when empty). `wi handoff` rewrites only those four lines
  (the first of each key) and inserts any that are missing; required by `lint`
  when `status: doing`. Each value is one line (see below).
- `## Notes` — free text; the tool only appends lines, after the last
  non-blank line of the section (it adds `## Notes` at the end when absent).
  `wi note <id> -- '<text>' […]` is the free-text append: each text becomes a
  dated line (`- <today> <text>`), or with `--raw` the line as written, all
  in one write under the lock. It refuses (exit 1, nothing written) a line
  break, an empty text, under `--raw` a line starting `## ` or opening a
  fence, any line the secret rule below flags, and a text that is exactly
  `--` after the separator `--` (argparse would drop it); each refusal reads
  `wi: text <n>: …; nothing written` and never quotes the text.
- any other `## …` section round-trips untouched.

A section runs from its `## ` heading to the next `## ` heading, so unheaded
text after a block belongs to that block. A `## ` line inside a fenced code
block (```` ``` ```` or `~~~`) is text, not a heading. A fence opener with no
matching closer is not a fence: it does not hide the headings after it. An
unclosed opener can still pair with a later block's fence and hide the
headings between them. When `## Handoff` or `## Notes` then exists only
inside such a fence, followed there by another `## ` line, `handoff`,
`claim`, `done` and `note` exit 3 and write nothing rather than add a second
section: add a real heading outside the fence, or close the unclosed one.
A closed example holding only that heading is text; the section is added.
Every rewriting command edits the body in place: bytes outside the lines it
owns — trailing unheaded text, spacing between sections, section order, CRLF
line endings — are kept exactly. Front matter is re-emitted in canonical form.

Every value a command writes into front matter, a Handoff bullet or a Notes
line is one line. One containing a line break — any character
`str.splitlines` or a YAML 1.1 loader breaks on, U+2028/U+2029 and NEL
included — exits 1 and nothing is written — for a command that writes
several items, none of them. A batch write (`export`, `archive`,
`import --update`) refused over a hand-written value names the item and its
path. The
imports fold instead: `import-todo` folds a title wrapped across lines, and
`import --format backlog-yaml` folds every story value except `notes` that
holds a line break or a refused character — whitespace collapsed, ends
trimmed (a `review_feedback: |` block scalar becomes one line). A one-line
free-text value (`title`, `blocked_reason`, `review_feedback`, each
`acceptance`/`testing` entry, an extra story field) is kept as the YAML
loader read it, surrounding spaces, runs of spaces and NBSP included, so an
exported title imports back unchanged; every other field (`id`, `requires`,
`claimed_by`, `ticket_mode`, `complexity`) is always folded.
Imported `notes` are markdown and land in the body as is: a `## Handoff`
line inside them becomes a real section, and one above the imported
`doing:`/`next:` lines shadows the imported Handoff.

## Session-start rule

Read `wi prime` (≤300 tokens) and nothing else from the root. Then
`wi show <id> --brief` for the one item you will work. Open a `ref` only when
the Handoff's `next:` needs it. Never `cat` the items directory. Hand off with
`wi handoff <id> --doing … --next …` at every stop, `wi done --note` to close.

## Secret rule

Item files may be tracked in git, now or later (an ignored store can become
tracked), so the rule holds for every store: record **the path and the key, never
the value**. Write `creds: clusterenv.yaml key DISCORD_WEBHOOK_BACKUPS`, not
the webhook URL. In a store that is its own repo, every past text is in its history;
rewriting that history is the operator's. `wi lint` flags PEM blocks, `KEY=value` assignments (bare,
or after a bullet, date, tag, bold or other leading text, unless the key is
glued to a word or follows a URL's `?` or `&`) and
`token/secret/password/webhook`-style pairs that look like live values. It
also flags the looser shapes: a lowercase, mixed-case or dotted `key=value`
(`app.db_pass=…`), `KEY = value`, `key => value`, `key := value`,
`KEY: value` or `KEY :value` (an env-style or snake_case key, or a
mixed-case key of two or more segments that holds a secret word and does
not open with one capital before a capitalised word: `clientSecret: …`,
`JWTSecret: …`, `db2Password: …`, `k8sToken: …`; not `OAuth:`), a
JSON `"key": "value"` pair and `--flag=value`, with the value bare or
quoted, and every pair on a line (`dsn=host=db;db_pass=…`, compact JSON).
It flags an `Authorization: Bearer …` header, any case, after `:`, `=` or
`=>` (never `==`), the credential bare or quoted (an `f"…"` string prefix
included), and its `Basic` and `Token` forms, when the credential is 12+
token characters (`:` and `%` count, so a raw `user:pass` or a
percent-encoded value is read whole) and not a placeholder, one or two
repeated characters (`XXXX…`) or plain words, each lowercase or
capitalised, joined by `:` (`user:password`, `User:Password`; a run such
as `FakeSecretPass` is no plain word).
The `=` forms take a kebab-case key (`db-pass=…`) and `pw` (`pw=…`).

- **Looser key forms.** These count only under a key holding a secret word
  (below), judged as under one, and never a plain value (a word, or words
  joined by `-`, `_` or `'`, each lowercase, capitalised or all capitals:
  `required`, `read-only`, `NOT_SET`, with quotes, brackets and markdown
  around it dropped: `(optional)`, `_(unset)_`) or a whole date: a spaced
  flag (`--password …`, not a value starting `-`); a kebab-case colon key
  (`db-pass: …`); a bare one-word colon key, lowercase, capitalised or all
  capitals, that is itself a secret word or ends with a secret suffix
  (`dbpass:`, `Dbpassword:`, `Passphrase:`, `pw:`, `PWD:`; a key that is
  camelCase too, such as `Q9token:`, is judged as camelCase), never
  `key:`, `auth:`, `cred:`, `creds:`, `webhook:` or `pass:` alone, which
  prose uses; and a Markdown table row
  (`| db_pass | … |`): a cell of one key-shaped token, then a cell of one
  token, a code span or emphasis around either dropped. A colon key here
  needs a space after its colon (`dbpass:/dbpassword:` is prose). A
  closing `**` or `` ` `` and an unbalanced `}` after the value are
  markdown or a brace around the pair (`**pw: ${PW}**` is a placeholder).
- **URL passwords.** `scheme://user:…@host` flags a password of 8+
  characters that is not a whole-value placeholder (`${DB_PASS}`,
  `<password>`, `****`), one or two repeated characters, or a plain word
  (`password`, `changeme`); the user may be empty (`redis://:…@host`).
- **The next line.** Lint reads line by line and keeps one line of state:
  when the previous line was clean and ends in a continuation, its last
  300 characters joined to this line's first 300 are checked too, and a
  hit is reported on this line, the one with the value. A continuation is
  a YAML block scalar (`key: |`, `key: >-`), a trailing `\` (shell,
  Dockerfile; joined with the next line's indent dropped), or an
  `Authorization` header whose credential, or scheme and credential, is
  on the next line.
- **Secret-word keys.** A key is one when a segment of it, split on `_`,
  `-`, `.` and camelCase, is a secret word (`pass`, `password`, `pw`,
  `secret`, `token`, `auth`, `cred`, `key`, `apikey`, `webhook` and the
  like) or ends with `password`, `passwd`, `secret`, `token`, `apikey`,
  `pass`, `passphrase` or `passcode` (`dbpassword`, `clientsecret`,
  `accesstoken`, `dbpass`); `key` counts only as a whole segment, a word
  ending in `pass` such as `bypass`, `compass`, `surpass`, `trespass`,
  `overpass`, `underpass`, `encompass`, `subpass`, `renderpass` or
  `multipass` is no secret word, nor is a plural
  such as `tokens` or `keys` (`passthrough` holds none). A key whose last
  segment names something about a secret (`policy`, `rotation`, `hint`,
  `prompt`, `field`, `label`, `name`, `type`, `mode`, `file`, `path`, `var`,
  `ref`: `password_policy`, `token_file`) is a meta key. When another of
  its segments holds a secret word, only these pass under it: a
  placeholder; a lowercase name of a first run of 15 or fewer letters,
  the later runs letters or digits, joined by
  `-`, `_`, `.` or `:` (`prod-db-creds`, `default-token-x7k2m`,
  `urn:ietf:params:oauth:token-type:jwt`); an env-var name of runs of
  15 or fewer (`GITHUB_TOKEN`); a letters-only word or identifier whose case segments
  are 3 to 15 letters (`bearer`, `ClientCredentials`); a dotted attribute
  (`cfg.token`); or a path starting `~/`, `./`, `/` or `$NAME/` of two or
  more harmless segments (`$HOME/.config/gh/token`). Everything else is
  judged as under a secret-word key (below), so a digit run, any UUID, a
  word with digits mixed in or 16+ lowercase letters in one run flags. A
  meta key with no other secret word is judged as other keys. Under a
  secret-word key any value of 8+ non-space characters counts,
  symbols, hex, letters-only and UUIDs included. A quoted value skips
  nothing; an unquoted one skips only code, a count or a path a note may
  quote: a call `f(…)` or subscript `x[…]` with nothing after the closing
  bracket and no comma-separated argument inside it that would flag on its
  own (an argument holding a space flags when one of its words looks live
  as under other keys, below: `login(user, "Bearer …")`), a spaced or
  nested one included (`auth(user, cfg(x), …)` is read
  to its matching `)`, and split only at commas outside inner brackets); a
  dotted
  attribute of letters and `_` only (`config.api_key`); a number with
  separators (`1,234,567`), or a bare number when another key segment is a
  count word (`count`, `len`, `max`, `min`, `budget`, `total`, `size`,
  `limit`, `num`); or a path starting `~/`, `./` or `/` of two or more
  harmless segments (below).
- **Other keys** (`sha`, `commit`, `*_id`, …) count only a value that looks
  live: 12+ characters holding a letter and a digit, not all hex (a sha),
  not a date, and not two or more segments split on `-`, `_`, `.`, `/` or
  `~` that are each harmless (letters and digits only, so a `+` or `=`
  makes a segment live; all letters, all digits or all hex at any length,
  or 12 characters or fewer that do not mix upper case, lower case and
  digits), so a work-item id, path, version or UUID stays clean.
- **Plain paths.** A value that is plainly a filesystem path passes under
  a key with no secret word, in every form above (`KEY=…` included):
  `XAUTHORITY=/tmp/.docker.xauth`, `XAUTHORITY="$HOME/.Xauthority"`,
  `CXX=/usr/bin/g++-12`. A plain path starts `/`, `~/`, `./`, `../`,
  `$NAME/` or `${NAME}/`, and each segment after that start, split on
  `-`, `_`, `.`, `/` and `~`, is harmless as above, a trailing `+` allowed
  (`g++`), save a segment of 16+ characters that is all hex, all digits
  or mixed-case letters, which is a token; after a bare `/` it needs two
  segments, after any other start one. A `:`-separated list is a plain
  path when every part is one or a whole `$NAME` or `${NAME}` and at
  least one part is a path on its own (`PATH=/usr/local/bin:/usr/bin:/bin`,
  `PATH=$HOME/bin:$PATH`, `KUBECONFIG=~/.kube/config:~/.kube/other`). A
  secret-word key whose last segment names a location (`sock`, `socket`,
  `dir`, `home`, `root`, `store`, `prefix`, `path`) passes a plain path
  too (`SSH_AUTH_SOCK=/run/user/1000/keyring/ssh`,
  `PASSWORD_STORE_DIR=~/.password-store`); any other secret-word key still
  flags one (`PGPASSWORD=/…/…`, `GIT_SSH_KEY=~/.ssh/id_ed25519`).
- **`-D` defines.** A `-D<NAME>=value` define (the `D` glued to one `-`,
  as cmake and compilers take it) is read with `NAME` as its key. When
  `NAME` holds a secret word it is judged as that key (`-DDB_PASSWORD=…`
  flags). Otherwise it flags only a value that is no plain path and that
  looks live or holds a token segment (16+ hex, digits or mixed-case
  letters, or a `+` or `=`), so `-DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-12`
  and `-DCMAKE_BUILD_TYPE=RelWithDebInfo` stay clean. A whole hex value
  passes when `NAME`'s last word, digits dropped, is `sha`, `commit`,
  `hash` or `rev` and no word of it is `hmac`, `salt`, `seed`, `pepper`,
  `signing`, `sign`, `api`, `otp`, `totp`, `nonce`, `key`, `secret` or
  `token`: `-DGIT_SHA=…` and `-DCOMMIT_HASH=…` pass, `-DHMAC_SHA256=…`,
  `-DSALT_HASH=…` and `-DSHARED=…` flag.
- **Placeholders.** A value is a placeholder only as a whole-value `$NAME`,
  `${NAME}`, `${{ name }}`, `$(command)`, `{name}` or `{{ name }}`; all `*`
  (masked) or all `.` (elided, `…` included); or `<…>` holding lowercase
  words, spaces, `_` or `-` with its closing `>` (`<value>`, `<your key>`).
  A value that only starts with `$` or `{` is no placeholder (`$2b$12$…`).
  Under a bare lowercase key (`password: …`) a `$`-led value flags unless
  it starts with `${` or `$(` or is a whole `$NAME`; a `{`-led one does
  not flag there. A `.` may end a placeholder only at the end of a word
  (`$GITHUB_TOKEN.`).
- **Raw and cleaned.** Every rule runs on the line as written and on a
  cleaned copy: NFKC-normalised (a fullwidth equals sign, U+FF1D, is `=`),
  Unicode format characters such as a zero-width space dropped, and
  markdown `` ` ``, `**`, `*` and `__` removed. Either one flagging flags
  the line. Look-alike letters (confusables, such as a Cyrillic a, U+0430,
  in a key) are out of scope for this floor.
- **Known strictness**, kept on purpose: a letters-only value under a
  secret-word key (`auth_level: interactive`), a comma list
  (`KEY_ORDER: priority,status`), a bare name (`self.dedupe_key =
  dedupe_key`), a number with a unit (`pass_rate = 97.5%`), and under other
  keys a single mixed value (`checkpoint_id: ckpt20261009T1104Z`) or a path
  segment over 12 characters that mixes letters and digits. Reword such a
  line, or record the path and key. **Known gaps**, each left open
  because closing it would flag ordinary notes or unbound the scan: a
  separated number under a secret-word key; `key:`, `auth:`, `cred:` or
  `pass:` alone as a colon key; in the looser key forms and URL
  passwords, a plain-word or whole-date value (`passphrase:
  correcthorse`), and
  a colon key with no space after its colon; a call argument holding a
  space whose words do not look live (a short or hex password with a
  space beside it); a table cell holding a space, and a table value not
  in the cell right after its key; a URL password under 8 characters or
  holding an unencoded `/` or `@`, and a token as the URL's user
  (`https://<token>@host`); a value more than one line below its key (a
  YAML block after a blank line, a key two continued lines up), and a
  YAML value on the next indented line with no `|` or `>`; an
  `Authorization` header with a scheme other than `Bearer`, `Basic` or
  `Token`; and, in a plain path, a long one-case letter segment
  (`/opt/FAKESECRETVALUEXYZ`) or a short lowercase-and-digit one
  (`/usr/bin:/hunter22`), which pass as directory names.

`wi note` refuses, writing nothing, a line lint would flag. Lint's shapes
are a floor, not every secret: the path-and-key rule is the guard.

## TODO.md deprecation notice

After `wi import-todo TODO.md`, replace the file's contents with:

```markdown
# TODO — moved

Work items now live in `.work-items/` at the repo root, one file per item,
managed by the work-items `wi` (`$WI`: `python3` and the absolute path of the
`work-items` plugin's `skills/work-items/scripts/wi.py`).
When the store is git-ignored, it is local to this checkout.

- `$WI prime` — what's next, in ≤300 tokens; start every session here
- `$WI next` / `$WI show <id> --brief` — pick and inspect an item
- `$WI add "title"` / `$WI claim` / `$WI handoff` / `$WI done` — the write verbs

Format and rules: the `work-items` plugin's
`skills/work-items/references/format.md`.
```
