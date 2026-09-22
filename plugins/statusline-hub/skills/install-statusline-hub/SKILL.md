---
name: install-statusline-hub
description: Put statusline-hub in the status-line slot (owner mode), move it to another settings scope, take it out, have it replace a status line another tool set, or wrap one (the hub owns the slot and runs your old status line inside it; unwrap puts it back exactly) — and list the hooks registered with the hub, why any is skipped, and their health. The hub takes a free slot by itself on the first session; use this for everything else. Use when the user says "install the statusline hub", "make the hub my status line", "remove the statusline hub", "replace my status line with the hub", "wrap my status line", "unwrap my status line", "which status line hooks are registered", "why is my hub hook not showing", or "what does the warning sign on my status line mean". Not for feeding the sensor from a status line the user keeps (the statusline-hub skill does that).
disable-model-invocation: false
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: "[--user | --local | --project] [--remove | --wrap | --unwrap] [--status]"
---

# Install or inspect the statusline hub

## Important

- Settings are written only by the bundled script, which changes only the `statusLine` key,
  atomically, and never prints a setting's value. Never edit a settings file yourself, and
  never read or quote one: the script reports what it found.
- Never pass `--replace` or `--write-read-only` without asking the user first, in that
  turn, and getting a yes. They are separate questions: `--replace` overwrites or removes
  a status line some other tool set, and `--write-read-only` writes a file the user made
  read-only.
- `--wrap` is consent too: pass it only when the user asked for their status line to be
  wrapped (the hub's first-session message offers exactly that), or said yes when you
  asked. Say what it does before running it: the hub takes the slot, and on every render
  runs their existing status line command unchanged and shows its output, followed by any
  hub display hooks, after writing the sensor record. The old entry is kept in the hub's
  private wrap record and never printed. `--unwrap` puts it back exactly.
- Wrap mode is user scope only: `--wrap` works on the user settings file and refuses a
  project's, whose command would run in every other project's sessions (and could come
  from a repository). Never offer `--local --wrap` or `--project --wrap`.
- Tell a user who wraps to run `--unwrap` **before** uninstalling the plugin. Until then
  their settings run the hub, and their own entry is kept only in the wrap record.
- Before the `statusline` plugin draws as a hub display hook (it registers itself at each
  session start, so this is only before its first session), replacing its footer with the
  hub drops the footer until it does. The script refuses without `--replace` and says so;
  relay that before asking.

## You may not need this skill

On the first session after install, the hub's SessionStart puts it in a free slot where the
plugin is enabled and says so in one line. It never replaces or wraps a status line another
tool set: it says so once, asking whether the user wants it wrapped, and leaves it. While
it wraps one, it re-applies the wrap when an older session's settings write drops it or
puts the old entry back, yields to anything else, and after `--unwrap` undoes an older
session's write that puts the hub's entry back. It leaves the `statusline` plugin's footer in place
until that plugin registers as a hub display hook (from its first session), then takes the
slot over with the footer drawing through the hub. It puts the entry back if an older
session's settings write drops it, and never re-adds one the user removed (that includes a
`statusline` footer the user removed before the hub arrived). If the hub's hooks are
refused as a whole (a config dir inside a git repository, say), it says so once at session
start; `--status` gives the detail.

## Instructions

### Step 1: Check the arguments

`$ARGUMENTS` may hold only these words, each at most once:

- one scope: `--user` (the default), `--local` or `--project`;
- one of `--remove`, `--wrap` or `--unwrap`;
- `--status`, alone.

`--wrap` takes no scope other than `--user`. `--unwrap` without a scope acts on the file
the hub wrapped; `--remove` on that file also unwraps it.

Anything else: say which words are allowed and stop. `--project` writes the team-shared
`.claude/settings.json` with an absolute path from this machine; confirm the user wants
that, or suggest `--local`.

### Step 2: Find the script

The plugin root is the directory two levels above this skill's base directory. The script
is `skills/install-statusline-hub/scripts/install_hub.py` under it. Confirm it exists with
Read.

### Step 3: Run it

```bash
python3 "<plugin root>/skills/install-statusline-hub/scripts/install_hub.py" $ARGUMENTS
```

Exit codes:

| Code | Meaning | Next |
|---|---|---|
| 0 | Done, or nothing to do | Relay the output. Changes show from the next session. |
| 1 | Error, nothing written | Relay the message. It names the file and the fix. |
| 2 | Usage error | Recheck Step 1. |
| 3 | A different status line is there | Relay the output. Ask the user whether to replace it; on a yes, rerun with `--replace` added. With `--unwrap`, the question is whether to put the wrapped one back over the one there now. |
| 4 | The settings file is read-only | Ask whether to write it anyway; on a yes, rerun with `--write-read-only` added. |

### Step 4: Explain `--status` output

`--status` lists each hook registered in `${CLAUDE_CONFIG_DIR:-~/.claude}/statusline-hub/hooks.d/`:

- its kind (display or record);
- whether it is active or disabled in `config.json`;
- its timeout;
- its health: `warn` means its health file says it is failing, which is the `⚠` at the end
  of the status line.

A skipped hook has its reason in brackets, for example: `group- or other-writable`,
`not refreshed for 14 days` (its plugin no longer runs), `command is not valid`,
`inside the project tree`. Every rule is in the `statusline-hub` skill's
`references/hook-contract.md`. A hook's error output is in
`${CLAUDE_CONFIG_DIR:-~/.claude}/statusline-hub/log/<name>.log`. Read it when a hook shows
nothing.

## Examples

Example 1: take over from a hand-written status line
User says: "Make the hub my status line."
Actions: run the script. It exits 3 naming the file. Ask "Replace the status line set in
that file with the hub?" On a yes, rerun with `--replace`.
Result: the hub owns the slot from the next session. It shows only the display hooks
registered with it (the `statusline` footer when that plugin is installed; none means a
blank line), so tell the user that.

Example 2: keep a closed renderer, and the hub
User says: "Wrap my status line" (after the first-session message offered it).
Actions: say what wrapping does (Important), then run the script with `--wrap`.
Result: from the next session the hub owns the slot and runs their old command inside it;
their line looks as before, and the sensor record is written on every render. If they
would rather not have a hub display hook (the `statusline` footer, say) beside it, it goes
under `disabled` in `${CLAUDE_CONFIG_DIR:-~/.claude}/statusline-hub/config.json`.
`--unwrap` puts the old entry back exactly.

Example 3: a warning sign on the line
User says: "What is the ⚠ at the end of my status line?"
Actions: run `--status`. Name the hook whose health is `warn`, and point at its own tooling
or its log.

## Troubleshooting

The status line went blank after statusline-hub was uninstalled while it wrapped one.
Cause: the settings still run the hub's removed script; the user's own entry is still in
`${CLAUDE_CONFIG_DIR:-~/.claude}/statusline-hub/wrap.json`, which an uninstall leaves.
Solution: reinstall statusline-hub, then run the script with `--unwrap`: it puts the
entry back exactly, then the plugin can be uninstalled. Without reinstalling, the user can
copy the `entry` object from that file into their `statusLine` by hand (you do not read
or print it).

The wrapped status line shows nothing, or old text.
Cause: the old command failed, or took longer than the render's 250 ms budget (its output
then shows from the render after, and the last output stays up to 10 minutes); it is killed
after 5 s.
Solution: `--status` shows the wrap state; the command's error output is in
`${CLAUDE_CONFIG_DIR:-~/.claude}/statusline-hub/log/_wrapped.log`.

The line is blank after install.
Cause: no display hook is registered (the `statusline` plugin, which registers the
footer at each session start, is not installed or enabled), or every hook failed.
Solution: run `--status`. The sensor record is still written on every render either way.

A hook is listed as skipped.
Cause: it breaks a trust or format rule; the reason is printed.
Solution: the plugin that owns the hook must write its manifest as the contract says. For
a hand-written hook, fix the file's mode (`chmod 600`) or its fields. A hand-written
manifest skipped as `not refreshed for 14 days` needs `"pinned": true` in it: nothing
refreshes it, and without the pin the prune pass also deletes it.
