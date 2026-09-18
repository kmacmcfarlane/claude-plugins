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

On a Pro/Max subscription (Claude Code >= 2.1.251) the gauge also shows plan usage bars after
the context gauge — `5h` (session window), `7d` (weekly), and `$` where a spend limit is set —
each with the used percentage and a reset countdown, read from the official `rate_limits`
field of the status-line payload. They appear only after the session's first API response,
so an empty footer before the first reply is not a fault. API-key sessions never receive
`rate_limits`, so they see none; the bars need no configuration and cannot be enabled for them. The same windows (used percentage and `resets_at`, numbers only) are recorded under `rate_limits` in the context-gate state file, where librarian-mode's fable-unavailable fallback reads the reset time.

The name in parentheses is the explicitly set name from Claude Code's session registry (`/rename`, `--name`, or an agent naming itself through the peer channel) and otherwise the payload's `session_name` (the AI title); the line re-renders only on the next event, not instantly, unless `statusLine.refreshInterval` is set. The name is shown on one line whatever it contains (control characters and newlines collapse to spaces, invisible format characters such as bidi overrides and zero-width spaces are dropped, and it is cut to 60 terminal columns with an ellipsis, a CJK character or emoji counting as two). The registry is found by walking the hook's ancestor processes through `/proc`; without `/proc` (macOS) only the direct parent is checked, so a shell between the session and the script leaves just the payload title.

## If the gate blocks wrongly

A hard block needs a fresh exact reading; an inferred depth (stale or missing record) only
warns. So a wrong block means a fresh-but-wrong record, e.g. one written just before a
compaction. Two escape hatches:
1. Pin the window: `CLAUDE_KIT_CONTEXT_WINDOW=1000000` (tokens) in the environment Claude
   Code is launched from; the hooks then never guess the denominator.
2. Emergency stand-down: record a checkpoint for the current epoch — exactly what
   `/checkpoint` records — with the plugin's own `mark_checkpoint.py`. It writes through the
   same locked read-modify-write as every hook, so a status-line render or hook firing at the
   same moment cannot drop the change (a hand-edit of the state file can). The session id
   names the state file under `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-kit/context-gate/`
   (the newest `.json` there is the live session). It refuses, exiting non-zero and writing
   nothing, when no state file exists for that id — a mistyped id, since a live session always
   has one. The gate stays down until the next compaction or `/clear`. From a Bash tool call
   inside the session (where Claude Code sets `CLAUDE_PLUGIN_ROOT`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/mark_checkpoint.py" <session_id>
```

   That form fails in a plain terminal, where `CLAUDE_PLUGIN_ROOT` is unset. There, use the
   stable plugin-data path; `ls -td … | head -1` picks the most recently refreshed
   `context-guard-*` data dir if more than one exists (one per marketplace the plugin was
   installed from — list them with plain `ls -d` and pick yours if unsure):

```bash
d=$(ls -td "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/data/context-guard-*/ | head -1)
python3 "${d}current-hooks/mark_checkpoint.py" <session_id>
```
