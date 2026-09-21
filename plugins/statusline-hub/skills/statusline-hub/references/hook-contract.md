# The hub's hook contract (v1)

How another plugin, or a user, runs code on every status-line render through
`statusline-hub`. When the hub owns the `statusLine` slot (owner mode), each render it
writes the sensor record first, then runs the registered hooks. This file is the whole
interface. The hub's `hooks/registry.py` and `hooks/hub.py` implement it, and their tests
hold them to it. The sensor record itself (what a *reader* gets without registering
anything) has its own contract, the `statusline` plugin's `sensor-contract.md`, which is
unchanged.

## The agreed consumer contract

Agreed with the claude-analytics session (2026-09-19/20), carried verbatim:

> Registry at `${CLAUDE_CONFIG_DIR}/statusline-hub/hooks.d/<name>.json` with `{name,
> command, timeout_ms, kind: "display"|"record", health_path?}`. A `record` hook gets the
> raw status-line payload BYTE-FOR-BYTE on every render, runs detached and never blocks
> the render; a crashing or slow record hook leaves the gauge and the sensor record intact.
> Optional health_path: the hub reads that small file at render (capped) and shows a
> one-glyph warning when the last run errored or there is no last_ok within N minutes; a
> missing/stale/oversized/malformed health file shows nothing; no glyph until the hook has
> run once; never delays the render. A `display` hook gets a hard timeout and a last-good
> cache; a failing hook never blanks the line. Dead entries pruned in the prune pass.

The sections below spell out each clause. Where they add a rule (the trust checks, the
exec form, the caps), the rule is additive: a manifest written to the agreed shape still
works.

## 1. Where

`CFG` is `${CLAUDE_CONFIG_DIR:-~/.claude}` (an empty value counts as unset).

```
CFG/statusline-hub/
  hooks.d/<name>.json        one manifest per hook (you write it)
  config.json                the user's order / disabled / separator (the user writes it)
  cache/<name>/<session>.json   a display hook's last good text (the hub writes it)
  log/<name>.log             your hook's stderr (the hub writes it)
```

`<name>` is `[a-z0-9][a-z0-9-]{0,39}`: lowercase letters, digits and hyphens, starting with
a letter or digit, at most 40 characters. It is the file name, and it must equal the
manifest's `name` field.

## 2. The manifest

```json
{"v": 1, "name": "analytics", "kind": "record",
 "command": ["python3", "/abs/path/to/plugin/hooks/sample.py"],
 "timeout_ms": 2000,
 "health_path": "/home/me/.claude/analytics/health.json"}
```

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Equals the file name without `.json`. |
| `kind` | yes | `"display"` (its first stdout line is shown) or `"record"` (gets the payload, shows nothing). |
| `command` | yes | Preferred: a JSON array of strings, exec'd as is. A string is split into words by POSIX shell rules and exec'd, **with no shell**. See § 4. |
| `shell` | no | `true` runs a string `command` as `/bin/sh -c <command>`. Default `false`. |
| `timeout_ms` | no | Display: default 150, clamped to 10–250. Record: default 1000, clamped to 10–10000. |
| `health_path` | no | An absolute path inside `CFG` to your health file (§ 7). Anything else is ignored, and the hook still runs. |
| `order` | no | An integer hint for display position (lower first). The user's `config.json` wins. |
| `pinned` | no | `true` exempts the manifest from the 14-day staleness rule (§ 8). For a manifest a person writes by hand; a plugin refreshes its own instead. |
| `v` | no | `1`. Any other value makes the hub skip the manifest. |

Other keys are ignored, so a newer manifest stays readable. The program (`command[0]`)
must be a bare name found on `PATH` or an absolute path. A relative path with a slash in
it is refused.

## 3. Writing it

- Write it from your plugin's **SessionStart** hook, every session. A plugin cannot run
  anything at install time, and `${CLAUDE_PLUGIN_ROOT}` changes on every plugin update, so
  write the absolute path it has *now*. Rewriting also refreshes the file's mtime, which is
  how the hub knows the hook is alive (§ 8).
- Create missing directories with mode `0700`, e.g. `os.makedirs(d, mode=0o700,
  exist_ok=True)`. The hub's own SessionStart creates `hooks.d` too.
- Write atomically: a temp file in `hooks.d` (made by `tempfile.mkstemp`, which creates it
  `0600`), then `os.replace` onto `<name>.json`. Never truncate the file in place, since a
  render may read it at any moment.
- To unregister, delete your file. If you forget, it is pruned 14 days after your last
  refresh.
- **Writing one by hand?** Nothing refreshes it, so it would be ignored, then pruned,
  after 14 days. Add `"pinned": true` to keep it; delete it yourself when you are done.

## 4. Trust: which manifests run

A manifest runs code as the user, so the hub counts one only when **all** of these hold.
Otherwise it skips the manifest silently: nothing runs, and the line is unaffected.
`/install-statusline-hub --status` says which rule a skipped manifest broke. When a rule
about the directories refuses every manifest, the hub's SessionStart also says so, once
(§ 10).

- `CFG/statusline-hub` and `hooks.d` are real directories, not symlinks, owned by the user
  running the hub, and **not writable by group or others**.
- The manifest is a regular file, opened without following a symlink, owned by the user,
  **not writable by group or others**, at most 16 KiB, and modified within the last 14
  days.
- `CFG` does not lie inside the session's project tree. A home directory, or a directory
  above it, does not count as a project tree.
- `CFG` does not lie inside a git work tree: no `.git` in `CFG` or in any directory above
  it, up to but not including the home directory. The default `~/.claude` is exempt,
  since a repository cannot relocate it, and a dotfiles repo there is the user's own.
  Together with the rule above, this means a config dir relocated into a cloned repo never
  supplies hooks. That holds even when Claude Code started in a subdirectory, or the
  payload names no directory.
- At most 32 manifests are read, in name order.

**Why no shell by default.** The exec form never expands, globs, redirects or chains, so a
path with spaces or `$` in it is just a path, and nothing in a string `command` can smuggle
in a second command. It also costs no extra `sh` start-up on every render. A manifest can
still ask for a shell with `"shell": true`. That departs from a strict "never a shell" rule
on purpose, and grants nothing new: an argv array can already name `/bin/sh -c`, and
whoever can write the manifest can already name any program. What the flag adds is that
the shell has to be asked for explicitly, in the file, where a reader sees it.

## 5. How every hook runs

- **stdin**: the status-line payload, exactly the bytes Claude Code sent. Each hook gets
  its own copy, file-backed rather than a pipe, so a hook that never reads cannot stall
  anyone. The hub reads at most 1 MiB. A larger payload is not one Claude Code sends: the
  hub runs no hooks for it and prints an empty line.
- **Working directory**: `CFG/statusline-hub`, never the project.
- **Environment**: the hub's own, plus `STATUSLINE_HUB=1`, `STATUSLINE_HUB_KIND`
  (`display` or `record`) and `STATUSLINE_HUB_HOOK` (your name).
- **stderr**: appended to `CFG/statusline-hub/log/<name>.log`, private. The log is emptied
  once it passes 64 KiB, and pruned after 14 days untouched. It never reaches the
  terminal.
- **Process**: each hook leads its own session. At its timeout the hub kills its whole
  process group. A display hook still running when Claude Code cancels a render is
  killed only at the hub's own timeout: if the hub process itself is killed first, nothing
  kills the hook and it runs until it exits, so keep hooks fast and safe to run twice.

## 6. Kinds

### display

- The hub starts every display hook **at once** and waits for each until its `timeout_ms`,
  all within a 250 ms budget per render. Display hooks share that budget rather than
  adding to it.
- **On time, exit 0**: the first line of stdout (at most 4 KiB read) is sanitised and
  shown, and cached as this session's last-good text. The hub stops reading at the end of
  the first line, so a background child that keeps stdout open does not make the hook
  count as timed out, as long as the hook itself exits 0 in time. Empty output means "show nothing
  this time".
- **Timeout, non-zero exit, or a failed start**: the last-good text is shown if it is
  under 60 s old, otherwise nothing. A failing hook costs only its own slot, never the
  line, and never the sensor record, which was written before any hook started.
- **Sanitising** (the same treatment as the session name, with one addition): only the
  first line is kept. SGR colour sequences (`ESC [ … m`) are kept, and a reset is appended
  so a colour cannot bleed into the next hook's text. Every other escape sequence is
  dropped: cursor moves, clears, window titles, hyperlinks. Other control characters are
  dropped too, with a tab becoming a space. Unicode format characters (bidi overrides,
  zero-width padding) are dropped, except a joiner, and so are the Unicode line and
  paragraph separators (U+2028, U+2029). At most 300 printable characters are
  kept.
- **Order**: the user's `config.json` `order` first, then `order` hints, then name.
  Segments are joined with the configured separator (two spaces by default).

### record

- It gets the **raw payload, byte for byte, on every render**. There is no parsing,
  re-encoding or filtering.
- It runs **detached**. The render hands the payload to one background runner in its own
  session and returns without waiting. Nothing the runner or your hook does can hold the
  render, its stdout, the line or the sensor record.
- **At most one live instance per hook.** A record hook still running from an earlier
  render is skipped for this one: it gets no payload for that render. So "every render"
  means every render the hook is free for. A hook that finishes within the gap between
  renders sees them all, and a hung hook costs one process, not one per render. The runner
  holds a per-hook lock (`run/<name>.lock`) while the hook runs, releases it when the hook
  exits, and kills the hook at its `timeout_ms`.
- Keep a record hook short. Write its outputs by atomic replace or append: even with one
  instance, a render the hook skipped is not replayed.
- stdout is discarded.

## 7. Health (optional, any kind)

Your hook owns its errors. If you set `health_path`, keep a small JSON file there, written
by atomic replace after every run:

```json
{"last_ok": 1790000000.5, "last_error": null, "error": "short text", "runs": 42, "errors": 1}
```

- `last_ok` and `last_error` are epoch seconds (numbers), or ISO-8601 strings; missing or
  `null` means never.
- `error`, `runs` and `errors` are yours to use. The hub reads only `runs`: `0` means the
  hook has not run yet.

At each render the hub makes one read of at most 4 KiB, and shows **one glyph, `⚠`,
once** at the end of the line when any hook's file says:

- the last run errored: a `last_error` at or after `last_ok`; or
- there has been no `last_ok` within N minutes of the file's own latest write. N comes
  from `config.json` `health_stale_min`, default 15.

It shows nothing when:

- the file is missing, not a regular file, over 4 KiB, not a JSON object, or untouched for
  24 h;
- the hook has not run yet (`runs` is 0, or neither time is set).

Measuring against the file's own mtime means an idle session does not raise a false alarm
on its first render back. A hook that dies without writing its file at all shows nothing
here, so catch that end to end (`ca doctor`, say).

`health_path` must resolve inside `CFG`. The hub never shows the file's text, only the
glyph. `/install-statusline-hub --status` shows each hook's health.

## 8. Liveness and pruning

- A manifest not modified for **14 days** is ignored at render, unless it says
  `"pinned": true`. The hub's SessionStart prune pass deletes it, again unless pinned.
  That is how a hook of an uninstalled or disabled plugin dies away, since its
  SessionStart no longer refreshes the file.
- The same pass deletes last-good cache entries older than a day, logs untouched for 14
  days, and orphaned temp files. It also deletes sensor records untouched for 30 days,
  including records only the hub's tee ever wrote.

## 9. The user's config.json

```json
{"order": ["statusline", "analytics"], "disabled": ["noisy"], "separator": "  ", "health_stale_min": 15}
```

All keys are optional. A malformed file means defaults. A disabled hook does not run and
shows no health glyph.

## 10. Owner mode and the statusline plugin

- The hub only runs hooks when it is the `statusLine` command: owner mode. With a foreign
  status line the hub stays deferred, and that renderer can still feed the sensor record
  through `hub tee` (the `statusline-hub` skill's recipes).
- The `statusline` plugin's footer is a display hook, the first to follow this contract:
  its SessionStart writes `hooks.d/statusline.json` (kind `display`, command
  `["python3", "<its hooks dir>/statusline.py", "--segment"]`, `timeout_ms` 250) every
  session, and it writes no settings. With `--segment` the footer writes no sensor record,
  since the hub wrote it before the hook started.
- Until that manifest exists and is trusted, the hub **never** takes the slot from the
  footer and never races it for an empty slot. Doing either would drop the footer. Once it
  exists, the hub's SessionStart repoints a slot the statusline plugin (or an older copy of
  its footer) installed at the hub, and the footer keeps drawing through it. The slot
  changes hands once: nothing moves it back.
- A registry refused as a whole (§ 4: the config dir inside a git work tree, or the hub
  dirs not private) runs no hooks, so it would draw no footer either; the hub's
  SessionStart says so once, naming the directory and the reason.
- A plugin disabled or uninstalled stops refreshing its manifest, so its hook keeps
  running until the manifest is 14 days old (§ 8). To stop one at once, list it under
  `disabled` in `config.json` (§ 9), or delete its manifest.
