---
name: install-statusline
description: Install, move or remove the always-on status line — a one-line footer showing context left (tokens and percent; each sub-agent's in the agent panel), plan usage limits with reset countdowns, model, effort and session name. The footer draws through statusline-hub, which owns the status-line slot and installs itself on the first session; this skill covers the coworker install, and hands moving, removing or replacing the slot to the install-statusline-hub skill. Use when the user says "install the statusline", "set up the status line", "set up the context gauge", "remove the statusline", "move the statusline to this project", or "replace my status line with this one".
disable-model-invocation: false
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: "[--user | --local | --project] [--remove]"
---

# Install the status line

The footer looks like this:

```
[Opus 5·high] my-repo  (session name)  ████░░░░░░ 42%  580k left  5h ██░░░░░░░░ 23% resets 2h10m  7d █████████░ 91% resets 3d
```

## How it is set up

Claude Code has one status-line slot. The `statusline-hub` plugin owns it: this plugin
depends on it, and installing this plugin installs the hub too. Each render, the hub
writes the sensor record other tools read, then runs the footer as one of its display
hooks. This plugin writes no settings. At each session start it only registers the footer
with the hub.

On the first session after install (or the second, when the footer had not registered yet
as the hub looked), the hub puts itself in the slot where the plugins are enabled, and says
so in one line, e.g. `statusline-hub: status line slot taken in
~/.claude/settings.json: …`. The footer shows from the session after that. If the footer is
already in the slot from an earlier version of this plugin, the hub takes that entry over
once, with the footer drawing on both sides of the change, and says
`took over the status line slot in PATH`. It never replaces a status line another tool
set. It says so once and leaves it.

## Instructions

### Step 1: Check the arguments

`$ARGUMENTS` may contain only these words, each at most once:

- one scope: `--user`, `--local` or `--project`
- `--remove`

If it contains anything else, stop and tell the user which words it accepts.

### Step 2: Hand it to the hub's installer

Moving the status line to another scope, removing it, or replacing a status line another
tool set are all changes to the slot. The slot belongs to `statusline-hub`, so run its
skill, `/install-statusline-hub`, with the same arguments. Follow that skill's steps: its
consent questions (replace, write a read-only file) are asked there, one at a time.

- `--project` writes the team-shared `.claude/settings.json` with an absolute path from this
  machine. Confirm with the user first, or suggest `--local`. For a team, prefer enabling
  the plugin for the repo: each person's first session installs it into their own
  `settings.local.json`.
- `--remove` takes the hub out of the slot, and the footer with it. The hub never adds it
  back by itself; installing again turns it back on.

If `/install-statusline-hub` is not available, `statusline-hub` is not installed or not
enabled. Run the coworker install below; it brings the hub along.

### Step 3: Verify

In the next session the footer shows the gauge. Before the first reply of a session it may
read `ctx --` (the numbers arrive with the first response). That is not a fault.

## Coworker install (from scratch)

Requirements: `python3` on `PATH`; Linux or macOS (Windows is untested).

```bash
claude plugin marketplace add https://github.com/kmacmcfarlane/claude-plugins.git
claude plugin install statusline@kmacmcfarlane
```

Or inside a session: `/plugin marketplace add https://github.com/kmacmcfarlane/claude-plugins.git`,
then `/plugin install statusline@kmacmcfarlane`. That also installs `statusline-hub`, its
one dependency. Nothing else from the marketplace is needed.

Then start a new session. The hub says in one line when it takes the slot: in the first
session, or in the second when it had to wait for the footer to register. The footer shows
from the session after that. If you already had a status line, the hub says so and changes
nothing; run `/install-statusline` and answer yes to replace it.

Upgrading from a version of this plugin that predates the hub: `/plugin update` (and
auto-update) does not install a new dependency, so run
`/plugin install statusline@kmacmcfarlane` once more to bring `statusline-hub`. The session
start says so when the hub is missing.

### Keep it updated

The `claude plugin marketplace add` command has no auto-update flag. To have this
marketplace refresh itself instead of running `/plugin marketplace update kmacmcfarlane` by
hand, turn on auto-update one of two ways:

- In a session: `/plugin` → Marketplaces → `kmacmcfarlane` → turn on auto-update.
- In settings, add `autoUpdate: true` to the marketplace's `extraKnownMarketplaces` entry:

```json
{
  "extraKnownMarketplaces": {
    "kmacmcfarlane": {
      "source": {
        "source": "git",
        "url": "https://github.com/kmacmcfarlane/claude-plugins.git"
      },
      "autoUpdate": true
    }
  }
}
```

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
  instantly, unless `statusLine.refreshInterval` is set. On macOS (no `/proc`) the hub
  between Claude Code and the footer hides the `/rename` name until the payload carries it.

### Sub-agent rows

While sub-agents run, the agent panel below the prompt shows one row per sub-agent. This
plugin draws each row as `name · 43% 86k/200k · description`: the agent's own context fill,
coloured like the footer's gauge. The fill is exact, read from the agent's transcript
(`SESSION/subagents/agent-ID.jsonl` beside the session's transcript); after the first read,
each refresh reads only the lines added since the last one. A `~` marks an approximate figure (`~43% ~86k/200k`):
Claude Code's own token count for the agent, shown until the transcript has a reading, for
example in the first seconds of a new agent or right after it compacts. That count
overstates the depth, more the longer the agent runs. The rows refresh every 5 seconds.
Agent-team teammates get no row from this plugin; Claude Code does not pass them to it.

It is on by default, with nothing written to your settings: the plugin's own
`settings.json` ships a default `subagentStatusLine` (Claude Code 2.1.205 or later for the
percentages). Plugin defaults are the lowest settings layer, so a `subagentStatusLine` you
set in any settings file wins over it and is never touched. To keep Claude Code's default
rows, set one that prints nothing:

```json
{ "subagentStatusLine": { "type": "command", "command": "true" } }
```

If another enabled plugin also ships a `subagentStatusLine`, Claude Code uses the one it
loads last. The default reaches the script through this plugin's data directory
(`~/.claude/plugins/data/statusline-kmacmcfarlane/`), because a plugin's `settings.json`
cannot name the plugin's own install path; installed from a marketplace under another name,
set `subagentStatusLine` yourself to `python3 ".../plugins/data/statusline-NAME/current-hooks/subagent_statusline.py"`.

Each render also records this session's numbers (context used, window, plan usage) in
`~/.claude/statusline/sensor/SESSION.json` (under `$CLAUDE_CONFIG_DIR` when that is set),
so hooks and tools that never see the status line payload can read exact depth and reset
times. The hub writes it. The format is documented in `references/sensor-contract.md`. A
reader may treat a fresh reading as exact depth and act on it more firmly than on its own
estimate; how the one reader in this marketplace does so - including when it stops a prompt
without this status line - is described there.

## Uninstall

Remove the entry first, then the plugins, in this order:

```bash
# in a session: /install-statusline --remove   (add the scope flag it was installed with)
claude plugin uninstall statusline@kmacmcfarlane
claude plugin uninstall statusline-hub@kmacmcfarlane
rm -rf "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/statusline" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/statusline-hub"
```

Uninstalling first deletes the hub's data dir, which leaves the settings entry pointing at
a script that no longer exists (a blank footer). The last line removes the per-session
sensor files, the sub-agent rows' read cache and the hub's registry. The sub-agent rows go
with the plugin: their default lives in the plugin, not in your settings. Sensor files are also pruned automatically after 30
days. Uninstalling only this plugin leaves the hub in the slot: its footer disappears within
14 days, or at once if you delete `~/.claude/statusline-hub/hooks.d/statusline.json`.

## Known limitations

The status line does not render while Claude Code shows a modal prompt — a permission
request (documented) and, in practice, an `AskUserQuestion` dialog or plan approval. This
is harness behavior, not a plugin bug: the [docs](https://code.claude.com/docs/en/statusline)
state it "temporarily hides during certain UI interactions, including autocomplete
suggestions, the help menu, and permission prompts." There is no setting to keep it
visible. Upstream requests, all closed with the docs unchanged:
[#21349](https://github.com/anthropics/claude-code/issues/21349) (closed as completed by
its reporter once plan approval gained a context-remaining option; the status line itself
still hides), [#26847](https://github.com/anthropics/claude-code/issues/26847) (duplicate
of #21349), [#30232](https://github.com/anthropics/claude-code/issues/30232) (closed as
stale).

The footer always shows the main session's context. While you view a sub-agent (opened from
the agent panel or `/tasks`), it does not switch to that agent: Claude Code does not tell a
status-line command which agent is in view
([#76863](https://github.com/anthropics/claude-code/issues/76863), closed as not planned).
The agent's fill is in its row of the agent panel instead (see Sub-agent rows).

## Troubleshooting

Error: `Cannot add marketplace "kmacmcfarlane": its network source differs from the one
declared for it in settings …`
Cause: `kmacmcfarlane` is already declared in settings with a different source spelling than
the one just given to `add`.
Solution, in order:
- Run `claude plugin marketplace list`. If `kmacmcfarlane` is already listed, run
  `claude plugin marketplace update kmacmcfarlane` instead of `add`.
- If it is not listed yet, the settings declaration has not been reconciled into the
  known-marketplaces list — that happens in the background when a Claude Code session
  starts. Start one session, then run `claude plugin marketplace update kmacmcfarlane`.
  (Running `update` before that reconcile fails with `Marketplace 'kmacmcfarlane' not
  found`.)
- Or skip both: change the source declared in settings to match exactly what you're adding.

No footer after two sessions.
Cause: the hub is not in the slot (another status line is there, or it was removed), or it
does not run the footer.
Solution: run `/install-statusline-hub --status`. It lists the footer's hook as
`statusline`, or says why it is skipped. A config dir inside a git repository refuses every
hook, and the hub says so at session start.

The first session said `your settings already define a statusLine`: another tool owns the
slot, and the hub will not fight it. Run `/install-statusline` and answer yes to replace it.

The footer vanished after a `/plugin` toggle or a model change in an older session: that
session wrote its stale copy of the settings. When `statusline-hub` is installed, the next
new session puts the hub's entry back and says so (`restored the status line in PATH`),
including when the stale copy held this plugin's earlier entry. Without the hub nothing
puts it back: see the next entry.

The session start said `statusline: the footer draws through the statusline-hub plugin,
which is not installed`.
Cause: `/plugin update` brought a version of this plugin that depends on `statusline-hub`,
but Claude Code does not install a dependency that is new in an update. Without the hub
nothing runs the footer once an older entry is gone.
Solution: run `/plugin install statusline@kmacmcfarlane` again (it brings the hub), or
`/plugin install statusline-hub@kmacmcfarlane`, then start a new session. The notice is said
once; it comes back only if the hub goes missing again.

A repo enables the plugin but no footer appears there: the automatic install happens once
per machine, into the first settings file where the plugin is enabled. In other repos, run
`/install-statusline --local`.
