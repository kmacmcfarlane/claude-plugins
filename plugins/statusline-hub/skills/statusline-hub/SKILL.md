---
name: statusline-hub
description: Wire the statusline-hub tee into whatever draws your status line — a ccstatusline Custom Command widget, a Starship custom module, or a shell wrapper around an existing statusLine command — so the context depth and plan usage Claude Code hands the status line reach the sensor record that context-guard and other tools read. Use when the user says "set up statusline-hub", "tee the status line", "I use ccstatusline and context-guard can't see my depth", "make context-guard work with my status line", "add the hub to ccstatusline", "keep my status line but feed the sensor", or asks how to use the hub with Starship or their own statusLine script. Not for installing the statusline plugin's own footer (install-statusline does that).
disable-model-invocation: false
allowed-tools: Read, Glob
argument-hint: "[ccstatusline | starship | wrap]"
---

# statusline-hub: feed the sensor record from any status line

## What the hub is

Claude Code has one status-line slot, and the JSON it hands that slot on every render is the
only live source of exact context depth and plan usage. `statusline-hub` is the plugin for
sharing that slot. Today it ships one piece, the **tee**: a command that reads the status-line
JSON on stdin, writes the sensor record
(`${CLAUDE_CONFIG_DIR:-~/.claude}/statusline/sensor/<session>.json`, the same file and
format the `statusline` plugin writes), and prints nothing. Planned next: the hub owns the
slot itself, tees on every render, then runs registered display hooks (the `statusline`
footer first) in parallel under timeouts; an embed mode for renderers like ccstatusline;
and a consent-only wrap mode for closed renderers. None of that exists yet.

## Important

- This skill never edits `settings.json`, never registers a hook, and never edits another
  tool's config file (ccstatusline's, Starship's). It shows the user what to add; the user
  applies it, or asks for the edit explicitly.
- The `statusline` plugin's own footer already writes the sensor record. If it is the
  user's status line, they need none of this — say so and stop.
- The tee prints nothing and exits 0 whatever it is fed, so a broken wiring shows nothing
  either. Always finish with the check in Step 4.

## Instructions

`$ARGUMENTS` may name one recipe: `ccstatusline`, `starship` or `wrap`. Without one, ask
the user what renders their status line now (their `statusLine` command tells them; do not
read settings files yourself), then pick the recipe.

### Step 1: Find the tee

The plugin root is the directory two levels above this skill's base directory; the tee is
`hooks/tee.py` under it. Confirm the file exists with Read or Glob. That absolute path works
until the plugin updates, when the version directory in it changes.

Expected output: an absolute path ending in `statusline-hub/<version>/hooks/tee.py`.

### Step 2: Offer an update-proof launcher

Foreign configs should not embed a versioned path. Offer to write this launcher to
`~/.local/bin/statusline-hub-tee` (the user may pick another directory on their `PATH`), with
Write, then `chmod +x` it. It runs the most recently installed copy of the tee, and when
none is installed it drains stdin and prints nothing:

```sh
#!/bin/sh
# statusline-hub tee launcher: runs the most recently installed copy of the tee.
t=$(ls -td "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/kmacmcfarlane/statusline-hub/*/hooks/tee.py 2>/dev/null | head -n 1)
[ -n "$t" ] && exec python3 "$t"
cat >/dev/null
```

If the user declines, use `python3 "<the path from Step 1>"` wherever the recipes below say
`statusline-hub-tee`, and tell them to redo the recipe after a plugin update.

### Step 3: Give the recipe

**ccstatusline** (a Custom Command widget gets the full status-line JSON on stdin):

1. Run `npx ccstatusline@latest` (or their usual way in), open the line editor, and add a
   **Custom Command** widget.
2. Command: `statusline-hub-tee` (or the launcher's absolute path, if that directory is not
   on the `PATH` ccstatusline sees). Timeout: the default 1000 ms is plenty; the tee takes
   tens of milliseconds.
3. The widget shows nothing; it only writes the record. Put it anywhere on the line.

ccstatusline runs widgets one after another, so this adds one short process to each render.

**Starship** (a `custom` module does not get Claude Code's stdin, so the script that runs
Starship must pass the JSON on). In that script:

```sh
#!/bin/sh
export CLAUDE_STATUSLINE_JSON="$(cat)"
exec starship prompt
```

and in `starship.toml`:

```toml
[custom.statusline_hub]
command = 'printf "%s" "$CLAUDE_STATUSLINE_JSON" | statusline-hub-tee'
when = true
shell = ["sh"]
format = "$output"
```

Starship's `command_timeout` (500 ms by default) bounds it. If the user runs Starship through
someone else's wrapper (starship-claude, for one), that wrapper must export the JSON the same
way; if it does not, use the shell wrapper below instead, with their Starship script as the
inner command.

**Shell wrapper** (any other status line): keep the existing command and put a wrapper in
front of it:

```sh
#!/bin/sh
# ~/.local/bin/claude-statusline: feed the sensor record, then draw the usual line.
input=$(cat)
printf '%s' "$input" | statusline-hub-tee
printf '%s' "$input" | THE-EXISTING-COMMAND
```

Replace `THE-EXISTING-COMMAND` with the user's current `statusLine` command, `chmod +x` the
wrapper, and have the user point their `statusLine` `command` at it. Show them the entry:

```json
"statusLine": {"type": "command", "command": "/home/USER/.local/bin/claude-statusline"}
```

### Step 4: Check it

After the next render (send any message), the session's record must exist:

```sh
ls -l "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/statusline/sensor/"
```

A file named for the current session id, touched seconds ago, means it works. To test the
tee alone, feed it a sample and read the result back, then delete it:

```sh
printf '%s' '{"session_id":"hub-check","context_window":{"used_percentage":1,"context_window_size":200000,"total_input_tokens":2000}}' | statusline-hub-tee
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/statusline/sensor/hub-check.json"
rm "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/statusline/sensor/hub-check.json"
```

## Examples

Example 1: ccstatusline user
User says: "I use ccstatusline; context-guard keeps saying the depth is inferred."
Actions: Step 1, write the launcher (Step 2), give the ccstatusline recipe, then Step 4.
Result: the next render writes the record, and context-guard reads exact depth from it.

Example 2: a hand-written statusLine script
User says: "Keep my status line script but feed the sensor."
Actions: Steps 1–2, the shell wrapper with their script as the inner command, the
`statusLine` entry for them to apply, Step 4.

## Troubleshooting

No record after a render.
Cause: the tee never ran, or ran with a different config dir.
Solution: run the Step 4 sample by hand. If that works, the renderer is not calling the
command (check it is on the `PATH` the renderer sees, or use an absolute path), or the
renderer runs with another `CLAUDE_CONFIG_DIR` than the session.

ccstatusline shows `[Exit: N]` or `[Timeout]` in the widget.
Cause: the command was not found or failed to start.
Solution: use the launcher's absolute path; check `python3` is on that `PATH`.

The record exists but is old.
Cause: the payload carried no usable context-window numbers (early in a session), or a newer
record was already on disk. Both are expected; the next render updates it.

Records pile up in the sensor directory.
Cause: pruning (records untouched for 30 days) runs from the `statusline` plugin's
SessionStart hook; the hub has none yet. The files are small; delete old ones by hand if
wanted.
