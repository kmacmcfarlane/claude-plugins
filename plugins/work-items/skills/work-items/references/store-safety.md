# Store safety

The rules are in `SKILL.md` § Protecting the store; this file holds the harm, the evidence,
the safe forms in full, backup and recovery. It does not restate the rules. Other homes stay
where they are: the worktree export (`SKILL.md` § Rules), the secret rule
(`references/format.md` § Secret rule), and moves (`references/format.md` § Moving a store).

Every git behaviour below was observed on 2026-10-15 with git 2.39.5, in scratch repos built
for each case, and is pinned by `tests/test_store_safety.py`, which re-runs it against the
installed git (a git upgrade that changes one fails that suite).

## Why the store needs care

A store comes in two shapes:

- **plain**: an ignored `.work-items/` folder;
- **own repo**: an ignored `.work-items/` folder that is its own local git repo, with no
  remote.

Either way the host repo ignores it, so the host's git holds no copy and cannot restore it,
and nothing else on the machine does either. A lost store loses its items, its decision log
and its next decision number. The old locations (`.claude-sandbox/work/`, `.work/`) are
often tracked by the host instead; the tracked-store rows below cover them.

## What destroys it (never run these near a store)

Run in the host repo, with the store ignored unless the row says otherwise:

| Command | Plain store | Own-repo store |
|---|---|---|
| `git clean -fdx`, `git clean -fdX` | **deleted** | kept |
| `git clean -fx` (no `-d`) | kept | kept |
| `git clean -ffdx`, `git clean -ffdX` | **deleted** | **deleted** |
| `git clean -fd` (store ignored) | kept | kept |
| `git clean -fd` (store not ignored) | **deleted** | kept |
| `git clean -fdx -e /.work-items/`, `git clean -fdx -- . ':!.work-items'` | kept | kept |
| `git clean -fdX -e /.work-items/`, `git clean -fdX -- . ':!.work-items'` | **deleted** | — |
| `git clean -ffdX -e /.work-items/` | — | **deleted** |
| `git clean -fdX -- build/` (a positive pathspec that leaves the store out) | kept | kept |
| `git stash --all` (`-a`) | **moved into the stash** | kept |
| `git stash -u` (store ignored) | kept | kept |
| `git stash -u` (store not ignored) | **moved into the stash** | kept |
| `git checkout -f <branch>`, `git reset --hard` | kept | kept |
| `git add -f .work-items` | items staged into the host repo | a gitlink (mode 160000), as below |
| `git add .work-items` (store not ignored) | items staged | a gitlink (mode 160000) at the store's current commit, which no clone can fetch |

Also observed:

- **Under `-X`, exclusions do not keep a store.** `-e /.work-items/` and `':!.work-items'`
  keep it under `-x` and are ignored under `-X`; only a positive pathspec that leaves the
  store out keeps it.
- **`git clean` with no pathspec works from the current directory down**, so the same
  command is harmless in one directory and destroys the store from another.
- **A tracked store** (an old location the host tracks) loses an untracked new item to
  `git clean -f`, and its `.lock` and `*.tmp*` files to `git clean -fx`, `-d` or not.
  `-e /<store>/` keeps both, except under `-X`, where it deletes the new items. A deleted
  `.lock` under a running session splits wi's lock: the next writer locks a new file.
- **Git run inside a plain store acts on the host repo** (`git rev-parse --show-toplevel`
  prints the host's root), and `git clean -fdx .` from inside it empties the store.
- **Inside an own-repo store**, `git reset --hard` reverts an uncommitted item edit and
  `git clean -fd` deletes an uncommitted new item. Until wi commits into the store, every
  item changed since the store's last commit is uncommitted.
- **`rm -r`** of the store, its repo root or a directory above it has no undo.

Harm: a deletion by `git clean` or `rm` is total (no undo; restore a backup). A stash move
is recoverable while the stash entry lives (§ Recovering), but the store is gone from every
session at once, and a `stash drop`, `stash clear`, or a `wi init` in the gap that `pop`
then collides with, loses it. A host-repo commit of a plain store publishes the items with
the next push.

## Safe forms

- **Clean, `-x`:** preview with `git clean -n -fdx -e /.work-items/`, then run it without
  `-n`: `git clean -fdx -e /.work-items/` (one `-f` only: a doubled force, `-ff` or
  `--force` twice, deletes linked worktrees and nested repos that the one-`-f` preview
  skipped, even when the store is excluded). A pathspec does the same:
  `git clean -fdx -- . ':!.work-items'`. Add one `-e` per other store location the repo holds
  (`-e /.claude-sandbox/work/`).
- **Clean, `-X`:** exclusions do not protect a store under `-X`, so name only the
  directories to clean: preview with `git clean -n -fdX -- build/ dist/`, then run
  `git clean -fdX -- build/ dist/` (one `-f` only). Never `.`, `./`, `..`, `:/`, a glob, or a
  directory holding a store as the pathspec.
- **Clean, tracked store:** even `git clean -f` takes its new items; add `-e /<store>/`:
  `git clean -f -e /.claude-sandbox/work/`. Not under `-X`, where `-e` deletes them: there,
  name the directories to clean, as above.
- **Stash:** don't. Commit to a branch, or copy the files to the scratchpad.
- **rm:** name exact paths; never `.`, `..`, a repo root or a parent of one.
- **Git in an own-repo store:** set `S=<absolute store path>`, then
  `git -C "$S" status|log|diff|show`. To commit, take the store's lock, and pass the
  fallback identity only when git has none:

  ```bash
  if git -C "$S" var GIT_AUTHOR_IDENT >/dev/null 2>&1; then id=(); else id=(-c user.name=wi -c user.email=wi@localhost); fi
  flock -w 10 "$S/.lock" git -C "$S" add -A
  flock -w 10 "$S/.lock" git -C "$S" "${id[@]}" commit -q -m "<what>"
  ```

  The store's own `.gitignore` keeps `.lock` and `*.tmp*` out of the `add`. `flock(1)` on
  `<store>/.lock` takes the same lock wi takes. With no `flock` (macOS), commit only when no
  session is working the store.

## Worktrees and clones

A worktree has no store: export `WORK_ITEMS_ROOT` as `SKILL.md` § Rules says. A fresh clone
has none either: restore it from a backup (§ Backing up), or ask the operator. A new store
made there restarts decision numbering.

## Concurrency and `index.lock`

- wi's writes are serialised by its lock on `<store>/.lock`. Git that writes in the store
  takes the same lock (§ Safe forms).
- An `index.lock` error: wait and retry. Remove the file only when no git process runs in
  that repo, and say so in the report.

## Commit failures

- **No identity** (`Author identity unknown`): the § Safe forms commit passes the fallback
  identity exactly when `git var GIT_AUTHOR_IDENT` fails, which is exactly when a plain
  commit would fail.
- **No git:** the item write still lands (wi needs no git to write). Report "store not
  committed", and leave the commit to a session that has git.

## Secrets in the store's history

The rule is `references/format.md` § Secret rule. A store's history keeps every past text, so
a secret that lands is reported to the operator, by path and key, before any bundle or backup
leaves the machine. Rewriting the store's history is the operator's job.

## Backing up

Back up into the host repo's git dir, which `git clean`, `stash` and `reset` never touch, and
which persists inside a sandbox (the project tree is mounted). From the host checkout, with
`S` the store's absolute path:

```bash
B="$(git rev-parse --path-format=absolute --git-common-dir)/work-items-backup"; mkdir -p "$B"
```

- **Own-repo store:** commit first under the lock (§ Safe forms), since a bundle holds only
  commits, then `git -C "$S" bundle create "$B/$(date +%F).bundle" --all`.
- **Plain store:** `tar -C "$(dirname "$S")" -czf "$B/$(date +%F).tgz" "$(basename "$S")"`.
- **Restore, own repo:** `git clone -q "$B/<date>.bundle" .work-items`, then
  `git -C .work-items remote remove origin` (the store keeps no remote). The committed items and
  their history come back. A bundle in `"$B"` survives a doubled-force clean, `-ffdx`, in the
  host (observed).
- **Restore, plain:** `tar -C "$(dirname "$S")" -xzf "$B/<date>.tgz"`.
- **When:** before a move, before any wholesale checkout operation (a re-clone, a large
  clean), and at the end of a long session.
- **Limits:** this copy dies with the checkout or the disk. If this machine's own backup
  already copies the checkout off the machine, this local copy covers the gap since its last
  run.

## Recovering

- **A stash took it:** find the entry with `git stash list`, then
  `git stash apply stash@{n}` (apply, not pop, until the items are checked).
- **A dropped stash:** `git fsck --unreachable | grep commit` lists candidates; the stash
  commit is the one with three parents, and `git show --stat <sha>^3` lists the untracked
  and ignored files it holds. Restore with `git stash apply <sha>`. Recoverable until gc.
- **`git clean` or `rm`:** no undo. Restore the latest backup (§ Backing up).
