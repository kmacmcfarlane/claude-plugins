---
name: install-statusline
description: Install (or move or remove) the claude-kit context status line — the always-on gauge showing tokens left, epoch, and checkpoint state, which also feeds the context-gate hooks their exact depth. Use when the user says "install the statusline", "set up the context gauge", "remove the statusline", or after installing claude-kit on a new machine.
disable-model-invocation: false
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: [--user | --project | --local | --remove]
---

# Install the claude-kit status line

The status line is the sensor of the context gate: Claude Code exposes exact
`context_window.used_percentage` only to it, and it writes that depth to the state file the
hooks read. Without it the hooks fall back to transcript inference.

Run, with the scope the user asked for (`--user` is the default and the right choice on a
personal machine; `--project` writes the shared `.claude/settings.json` and **overrides every
teammate's personal status line** — confirm before using it):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/install-statusline/scripts/install_statusline.py" --user
```

The script writes an absolute path under the plugin-data dir
(`plugins/data/claude-kit-*/current-hooks/`), which survives plugin updates; the
`current-hooks` symlink there is refreshed by this plugin's SessionStart hook. If the script
reports the data dir missing, one session must start with the plugin enabled first.

The install leaves a marker (`statusline-installed.json` in plugin data) and the
plugin's SessionStart hook **self-heals**: a harness settings write from a session
launched before the install serializes a stale snapshot and drops the entry
(live-fired 2026-08-31 via a `/plugin` toggle); the next session start detects
the loss and restores it, announcing the repair. `--remove` also deletes the
marker, so removal is not "healed" back.

`--remove` deletes the entry from the chosen scope. Changing scope = install in one, remove
from the other. Verify after install: the gauge shows `NN%  NNNk left  eN` in the footer of
the next session.
