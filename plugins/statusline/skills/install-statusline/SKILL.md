---
name: install-statusline
description: Install, move or remove the always-on status line — a one-line footer showing context left (tokens and percent), plan usage limits with reset countdowns, model, effort and session name. Use when the user says "install the statusline", "set up the status line", "set up the context gauge", "remove the statusline", "move the statusline to this project", or right after installing the statusline plugin on a machine.
disable-model-invocation: false
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: [--user | --project | --local | --remove]
---

# Install the status line

The footer looks like this:

```
[Opus 5·high] my-repo  (session name)  ████░░░░░░ 42%  580k left  5h ██░░░░░░░░ 23% resets 2h10m  7d █████████░ 91% resets 3d
```

## Instructions

### Step 1: Pick the scope

- `--user` (default): your user settings file, `~/.claude/settings.json` (or
  `$CLAUDE_CONFIG_DIR/settings.json`). The right choice on a personal machine.
- `--local`: `.claude/settings.local.json` in the current repo — only you, only this repo.
- `--project`: `.claude/settings.json` in the current repo. It is shared with everyone who
  uses the repo, it **overrides each teammate's own status line**, and the command it writes
  is an absolute path on this machine. Confirm with the user before using it; for a team,
  prefer each person installing the plugin and running this skill with `--user`.

### Step 2: Run the installer

Pass the user's arguments through unchanged (a scope flag and/or `--remove`; none means
`--user`):

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

**Exit code 1** with `is read-only; left unchanged` means the settings file is not writable
by you. Nothing was written. Ask the user whether it is read-only on purpose; only on a
go-ahead, run the same command with `--force` added.

**Exit code 3** means the settings file already has a *different* status line (from another
tool or your own script). Nothing was written. Ask the user whether to replace it; only on a
yes, run the same command with `--force` added.

An earlier copy of this same status line (installed from another plugin of this
marketplace) is recognised and replaced without asking.

### Step 3: Verify

In the next session the footer shows the gauge. Before the first reply of a session it may
read `ctx --` (the numbers arrive with the first response); that is not a fault.

## Coworker install (from scratch)

Requirements: `python3` on `PATH`; Linux or macOS (Windows is untested).

```bash
claude plugin marketplace add kmacmcfarlane/claude-plugins
claude plugin install statusline@kmacmcfarlane
```

Or inside a session: `/plugin marketplace add kmacmcfarlane/claude-plugins`, then
`/plugin install statusline@kmacmcfarlane`. Nothing else from the marketplace is needed.

Then, in a Claude Code session, run `/install-statusline` (this skill). Installing the
plugin alone does not change your settings; the footer appears from the session after the
installer runs.

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
  `/install-statusline --local --remove`). It
  deletes only an entry this plugin installed; a different status line needs `--force`.
- Uninstall the plugin **after** removing the entry, in this order:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/install-statusline/scripts/install_statusline.py" --remove
claude plugin uninstall statusline@kmacmcfarlane
rm -rf "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/statusline"
```

Uninstalling first deletes the plugin's data dir, which leaves the settings entry pointing
at a script that no longer exists (a blank footer). The last line removes the per-session
sensor files.

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
session wrote its stale copy of the settings. Run the installer again.
