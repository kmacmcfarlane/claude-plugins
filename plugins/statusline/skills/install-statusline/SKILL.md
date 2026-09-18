---
name: install-statusline
description: Install, move or remove the always-on status line — a one-line footer showing context left (tokens and percent), plan usage limits with reset countdowns, model, effort and session name. The plugin installs it by itself on the first session; use this to put it in another scope, remove it, or replace a status line another tool set. Use when the user says "install the statusline", "set up the status line", "set up the context gauge", "remove the statusline", "move the statusline to this project", or "replace my status line with this one".
disable-model-invocation: false
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: [--user | --local | --project] [--remove]
---

# Install the status line

The footer looks like this:

```
[Opus 5·high] my-repo  (session name)  ████░░░░░░ 42%  580k left  5h ██░░░░░░░░ 23% resets 2h10m  7d █████████░ 91% resets 3d
```

## You may not need this skill

The plugin sets itself up. On the first session after it is installed, its SessionStart hook
adds the entry to the settings file where the plugin is enabled and shows one line, e.g.
`statusline: status line installed in ~/.claude/settings.json; it shows from your next
session.` It never replaces a status line another tool set: it says so once and leaves it.
It also takes over an older copy of this same status line, and puts the entry back if an
older session's settings write drops it. It never re-adds an entry you removed. If the
settings file cannot be used (not valid JSON, read-only, or a project's
`settings.local.json` that git does not ignore), it says so once, naming the file and the
fix, and retries quietly in later sessions.

Run this skill to install into another scope, to remove the status line, or to replace a
status line another tool set.

## Instructions

### Step 1: Check the arguments

`$ARGUMENTS` may contain only these words, each at most once:

- one scope: `--user`, `--local` or `--project`
- `--remove`

If it contains anything else, do not run the installer. Tell the user which words it accepts
and stop. The consent flags `--replace` and `--write-read-only` are never taken from
`$ARGUMENTS`: add one only after the user answers yes to its own question in Step 3.

### Step 2: Pick the scope

- `--user` (default): your user settings file, `~/.claude/settings.json` (or
  `$CLAUDE_CONFIG_DIR/settings.json`). The right choice on a personal machine.
- `--local`: `.claude/settings.local.json` in the current repo — only you, only this repo.
- `--project`: `.claude/settings.json` in the current repo. It is shared with everyone who
  uses the repo, it **overrides each teammate's own status line**, and the command it writes
  is an absolute path on this machine. Confirm with the user before using it. For a team,
  prefer enabling the plugin for the repo: each person's first session installs it into
  their own `settings.local.json`.

### Step 3: Run the installer

Pass the checked arguments (none means `--user`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/install-statusline/scripts/install_statusline.py" $ARGUMENTS
```

Expected output: `installed statusLine in PATH` (or `updated` when it was already there),
the script path it points at, and `It shows from the next session.` Tell the user to start a
new session (or restart Claude Code) to see it.

The command it writes is an absolute path under the plugin's data dir
(`plugins/data/statusline-*/current-hooks/statusline.py`), which survives plugin updates:
the plugin's SessionStart hook keeps the `current-hooks` link pointing at the installed
version, and the installer creates that link itself if no session has run it yet. Running
the installer again is harmless.

Each exit code other than 0 means nothing was written:

| Exit | Meaning | What to do |
|---|---|---|
| 1 | An error: the settings file is not valid JSON, the plugin's data dir was not found, or the entry changed while writing | Show the message; see Troubleshooting |
| 2 | Usage error: an unknown flag, or two scopes | Show the usage line it printed; fix the arguments |
| 3 | The settings file has a *different* status line (from another tool or your own script) | Ask: "Replace the existing status line in PATH?" Only on a yes, run the same command with `--replace` added |
| 4 | The settings file is read-only | Ask: "PATH is read-only. Write it anyway? Its mode is kept." Only on a yes, run the same command with `--write-read-only` added |

Ask the two questions separately: a yes to one is not a yes to the other. A command with
`--replace` can still exit 4, and then the second question is asked.

An earlier copy of this same status line (installed from another plugin of this
marketplace) is recognised and replaced without asking.

Settings are changed in place. The file is read again at the moment of writing, and only
its `statusLine` entry is changed, so edits made meanwhile by another session are kept. Only
that entry's text changes: the rest of the file keeps its formatting byte for byte,
including CRLF line endings. When that splice cannot be proved right (an empty `{}`, a
repeated `statusLine` key, or removing the file's only key), the whole file is written again
in its own indent style and line endings. An empty (0-byte) settings file counts as `{}`.

### Step 4: Verify

In the next session the footer shows the gauge. Before the first reply of a session it may
read `ctx --` (the numbers arrive with the first response). That is not a fault.

## Coworker install (from scratch)

Requirements: `python3` on `PATH`; Linux or macOS (Windows is untested).

```bash
claude plugin marketplace add kmacmcfarlane/claude-plugins
claude plugin install statusline@kmacmcfarlane
```

Or inside a session: `/plugin marketplace add kmacmcfarlane/claude-plugins`, then
`/plugin install statusline@kmacmcfarlane`. Nothing else from the marketplace is needed.

Then start a new session. It shows `statusline: status line installed in PATH; it shows from
your next session.` The footer appears from the session after that. If you already had a
status line, the message says so instead and nothing is changed; run `/install-statusline`
and answer yes to replace it.

## What it shows

- **Context gauge**: a 10-cell bar, percent used, and tokens left in the window. Colour
  tracks tokens left: green while plenty remains, yellow when it is getting low, red when
  it is nearly gone. The thresholds scale with the window size (on a 1M window: yellow at
  150K left, red at 60K; on 200K: 70K and 40K). If another installed plugin publishes its
  own thresholds for the session, the gauge uses those and may add a short word for the band
  and a counter after `left`.
- **Plan usage bars** (Pro/Max, Claude Code 2.1.251 or later): `5h` (session window), `7d`
  (weekly) and `$` where a spend limit is set, each with the used percentage and a reset
  countdown. They appear after the session's first response. API-key sessions never receive
  these numbers, so they never show bars; there is nothing to configure.
- **Session name** in parentheses: the name set with `/rename` or `--name` (or one an agent
  gave itself), else the automatic title. It is shown on one line whatever it contains:
  control characters collapse to spaces, invisible format characters are dropped, and it is
  cut to 60 terminal columns with an ellipsis. The footer re-renders on the next event, not
  instantly, unless `statusLine.refreshInterval` is set. On macOS (no `/proc`) a shell
  between Claude Code and the script hides the `/rename` name until the payload carries it.

Each render also writes this session's numbers (context used, window, plan usage) to
`~/.claude/statusline/sensor/SESSION.json` (under `$CLAUDE_CONFIG_DIR` when that is set), so hooks and tools that never see the status
line payload can read exact depth and reset times. The format is documented in
`references/sensor-contract.md`.

## Remove or move

- Move to another scope: install in the new one, then remove from the old one.
- Remove: `/install-statusline --remove` (add the scope flag it was installed with, e.g.
  `/install-statusline --local --remove`). It deletes only an entry this plugin installed; a
  different status line exits 3 and needs a yes to `--replace`. After a removal the plugin
  never adds the entry back by itself; installing again with this skill turns it back on.
- Uninstall the plugin **after** removing the entry, in this order:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/install-statusline/scripts/install_statusline.py" --remove
claude plugin uninstall statusline@kmacmcfarlane
rm -rf "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/statusline"
```

Uninstalling first deletes the plugin's data dir, which leaves the settings entry pointing
at a script that no longer exists (a blank footer). The last line removes the per-session
sensor files. They are also pruned automatically after 30 days.

## Troubleshooting

Error: `the plugin's data dir was not found`
Cause: the plugin is not installed, or the script was run from a plain checkout.
Solution: install the plugin (above), start one session, run the skill again.

Error: `... is missing - the current-hooks link could not be created`
Cause: the link could not be made (a read-only config dir, say).
Solution: start one session with the plugin enabled (its SessionStart hook makes the link),
then run the skill again.

Error: `... is not readable JSON; left unchanged`
Cause: the settings file has a syntax error. The installer never overwrites a file it cannot
parse.
Solution: fix the file, then run the skill again.

The footer vanished after a `/plugin` toggle or a model change in an older session: that
session wrote its stale copy of the settings. The next new session puts it back and says so.
To fix it at once, run the installer again.

The first session said `your settings already define a statusLine`, or later said
`was changed by something else; left alone`: another tool owns the entry, and the plugin will
not fight it. Run `/install-statusline` and answer yes to replace it.

The first session said `... is read-only`, `... is not valid JSON` or `... could not be
written; status line not installed`: fix what it names, then start a new session (it retries
quietly each session), or run `/install-statusline`.

The first session said `... settings.local.json is not git-ignored`: the entry is an absolute
path on your machine and must not be committed. Add `.claude/settings.local.json` to the
repo's `.gitignore` and start a new session, or run `/install-statusline` to put it in your
user settings.

A repo enables the plugin but no footer appears there: the automatic install happens once
per machine, into the first settings file where the plugin is enabled. In other repos, run
`/install-statusline --local`.
