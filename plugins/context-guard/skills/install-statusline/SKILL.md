---
name: install-statusline
description: Install (or move or remove) the context-guard status line — the always-on gauge showing tokens left, epoch, and checkpoint state, which also feeds the context-gate hooks their exact depth. Use when the user says "install the statusline", "set up the context gauge", "remove the statusline", or after installing context-guard on a new machine.
disable-model-invocation: false
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: [--user | --project | --local | --remove]
---

# Install the context-guard status line

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
(`plugins/data/context-guard-*/current-hooks/`), which survives plugin updates; the
`current-hooks` symlink there is refreshed by this plugin's SessionStart hook. If the symlink
(or the data dir itself) does not exist yet — e.g. the session started before the plugin
loaded, so the hook never fired — the script creates it itself, the same way the hook does.

The install leaves a marker (`statusline-installed.json` in plugin data) and the
plugin's SessionStart hook **self-heals**: a harness settings write from a session
launched before the install serializes a stale snapshot and drops the entry
(live-fired 2026-08-31 via a `/plugin` toggle); the next session start detects
the loss and restores it, announcing the repair. `--remove` also deletes the
marker, so removal is not "healed" back.

If the status line was installed while the context system still shipped inside the
`claude-kit` plugin, the settings entry points at `plugins/data/claude-kit-*/current-hooks/`.
The SessionStart hook migrates it automatically on the next session start (it repoints the
command at this plugin's data dir and moves the marker across, announcing the migration). If
that does not happen — the legacy marker was already deleted, say — just re-run the install
command above; it is idempotent.

`--remove` deletes the entry from the chosen scope. Changing scope = install in one, remove
from the other. Verify after install: the gauge shows `NN%  NNNk left  eN` in the footer of
the next session.
