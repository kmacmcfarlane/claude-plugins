# Operator playbook — staying in the context power band

Measured from a real 1M-token session that filled its window twice (`design-rationale.md`
has the full numbers). The short version: **the window was not filled by tool output. It was
filled by the assistant's own output, most of it hidden reasoning, plus harness overhead the
operator never sees.** Fixing that is mostly about session *shape*, not about reading fewer files.

## The numbers that matter

| Fact | Value | Consequence |
| --- | --- | --- |
| Cost of a turn, averaged | ~7K tokens | 1M ≈ 130 turns; 200K ≈ 25 turns |
| What a compaction keeps | 14–18K of ~1M (1.4–1.8%) | everything not on disk is gone |
| Compaction wall time | 140–150 s | plus a full prompt-cache rebuild after |
| Base cost after compaction | 75–107K | summary + CLAUDE.md + hooks + tool/skill listings |
| One SessionStart hook (context-mode) | ~15K tokens per start/resume/compact | 7.5% of a 200K window before you type |
| Subagent results, 24 calls | 2.7% of tool bytes | cheapest way to read a lot |
| A model switch mid-session | full cache rebuild, ±65K counted | avoid mid-thread |
| Hidden thinking persisted to disk | 1.8K chars of 559 blocks (≈0) | only the live session can write it down |
| Harness attachments per fill (hooks, diffs, listings) | ~105K tokens | as much as all tool output; audit with `context_forensics.py` |

**The gate thinks in remaining tokens, not percent.** Advisories at 60/75% used; **DUE** when
~150K tokens remain (1M window; 70K on 200K) — finish things, run `/checkpoint`; **HARD** at
60K/40K left — on an *exact* depth (a fresh status-line reading) or a *derived* one (the
window mirrored from Claude Code's own selection logic, every input observed — including,
above 200K, that this Claude Code process has not hit the long-context credits limit) the gate blocks
every prompt until a checkpoint records; on an *inferred* depth, or a derived one it could not
fully resolve, it only warns, because the real window may be larger than the guess — and
that warning keeps the DUE cadence (first time, then every 3 prompts or 25K tokens), so a
quiet stretch is not an all-clear. The whitelist that passes a blocked prompt through is
`/checkpoint`, `/compact` and `/clear`, bare or plugin-prefixed (`/context-guard:checkpoint`).
Under ~20K left (`CHECKPOINT_MIN_TOKENS`) the HARD advice, blocking or not, drops `/checkpoint`
for `/clear` (the work is on disk) or `/compact <guidance>`, since a checkpoint no longer fits;
when the gate blocks does not change. All of it resets per epoch (each compaction or `/clear`). The gate also warns against the
auto-compact window when one is set below the model window (`/autocompact`,
`CLAUDE_CODE_AUTO_COMPACT_WINDOW`, a valid `autoCompactWindow` of 100000–1000000), because that
is where Claude Code compacts. **The auto-compact window is advisory: the gate warns there but never hard-stops there on
Claude Code 2.1.277.** A hard stop at it would need every settings layer that can set or
cancel it to be read, and one of them never can be: server-managed (remote) policy. Whether an
account gets it depends on account data the gate never reads, and it may be kept in Claude
Code's storage backend rather than in `remote-settings.json`. The other conditions, all of
which would also keep it advisory on their own: `"autoCompactEnabled": true` must be set in a
settings file (without it Claude Code may take the value from its legacy global config); no
policy tier may be present — a `managed-settings.json`, a `managed-settings.d/` drop-in, a
`remote-settings.json`, an MDM profile (macOS, Windows), or `CLAUDE_CODE_MANAGED_SETTINGS_PATH`
set; no `--settings`, `--setting-sources`, `--managed-settings`, `--autocompact` or similar
flag on the `claude` command line and not an SDK session; and the `claude` process the hook
runs under must be verified (its binary, and its own session-registry entry).
The gate recognises its own `claude` by the `CLAUDE_PID` Claude Code gives every hook. A
`claude` started from another session's Bash tool is never verified: it does not register,
and it is never matched to the outer session. So in it any derived window above 200K and any
auto-compact window only warn. The hard stop
near the model window is unaffected. The compaction gate never uses the derived or
auto-compact window: it defers only on the depth it used before the window mirror.

**Inside a turn** the prompt gate cannot speak, so a check runs after every tool call
(main thread only; a subagent's calls are skipped). It never blocks, and it is **silent
unless the depth could hard-block** — exact or resolved-derived; an inferred depth waits
for the next prompt's advisory. Under the DUE line it says, once and then every 25K,
finish the step in hand and checkpoint at the turn's natural end. Under the HARD line it
opens `HARD, mid-turn` and says start nothing new and checkpoint now: the checkpoint
skill then runs unattended (no questions, mode `handoff` unless a custody skill such as
librarian-mode names its own), and its opener is the turn's last message. Under ~20K left
it says a checkpoint no longer fits: the turn ends with a three-line brief, and `/clear`
or `/compact <guidance>` is yours to run. A checkpoint this epoch stands it down too.

## Tools, and when

| Tool | Use it when | What it costs / keeps |
| --- | --- | --- |
| `/clear` | the task is done and its state is on disk | everything; cheapest reset there is — except after a `continue` or `handoff` checkpoint: when the `/clear` runs in the same Claude Code process within two minutes of that session's end and the manifest is still the version it wrote, the successor gets it in full plus the old session's ledger digest (otherwise nothing: paste the checkpoint's opener, whose Read of the printed path brings it) |
| `/rename <name>` | at the start of any thread you may resume | nothing; makes `--resume` findable |
| `/compact <guidance>` | the thread is open-ended and must continue *here* | keeps ~2%; guidance is a documented input, use it |
| `/rewind` → *Summarize up to here* | old turns are noise, recent ones are load-bearing | condenses only the old part; recent turns verbatim |
| `/btw <question>` | a side question that needn't enter history | answers from context; never stored |
| `/subtask` (fork) | a side task that needs everything this session knows | inherits history + cache; tool calls stay out |
| `/fork` | a competing plan from this exact point | whole session copied to a background session |
| "use a subagent to …" | read-heavy research, log digging, doc reading | returns 1–2K tokens; the reads never enter your window |
| `Explore` / `Plan` agents | codebase survey before implementation | skip CLAUDE.md, cheap, read-only |
| `/context` | any time you want the truth | free |
| Read `HANDOFF.md` in full vs `cat` | taking over a `mode: handoff` manifest (at the absolute path its checkpoint printed) vs only looking at another session's | a whole-file Read adopts that version (re-injected after your next compaction); `cat` or a Read with offset/limit adopts nothing |
| status line | always | shows `used_percentage`; when the `statusline-hub` plugin records it (installing `statusline` brings it) its reading wins over the gate's derived window and cross-checks it |

Environment & knobs: `/autocompact 900k` lowers the auto-compact trigger so the gate's deferral
is provably safe (`CLAUDE_CODE_AUTO_COMPACT_WINDOW=900000` per project — plain integer, `900k`
reads as 900, which Claude Code raises to its 100K floor, and the gate then scores against
100K too); `CONTEXT_GUARD_LEDGER_EVERY` tunes the ledger nudge (default 60000; the deprecated alias
`CLAUDE_KIT_LEDGER_EVERY` still works, and the new name wins when both are valid integers);
`CLAUDE_CODE_TASK_LIST_ID=<name>` shares a task list across sessions.

## Session shapes that stay in the band

1. **One workstream per session — one stage, in a skill chain.** Investigate in one session,
   write the result to disk, implement in a fresh one; whenever the next skill reads its
   inputs from files this session already published, `/checkpoint handoff` at that boundary
   regardless of window health. A session that spans two repos will accumulate two repos'
   worth of context.
2. **Rename at the start, clear at the end.** Named sessions are branches; `--resume` is
   checkout.
3. **Delegate reads, keep writes.** Anything that would return more than a screen goes to a
   subagent; the main session stays single-threaded on writes (this is also what the
   multi-agent literature converged on).
4. **Write as you go.** Investigation serials, `INDEX.md`, commit messages with the reasoning.
   The compaction survivors in the measured session were exactly the things already on disk.
5. **Don't switch models mid-thread.** Do it at a boundary.
6. **Trim fixed overhead.** Every start pays for CLAUDE.md, rules, skill descriptions, MCP tool
   lists, and SessionStart hook output. Look at `/context` once and cut what you don't read.
7. **Large files: index, don't read.** A 49KB `TODO.md` costs ~12K tokens per read; a skill
   that reads it every time pays that on every invocation. Keep an index at the top and grep
   the rest.

## The three questions at the gate

When the depth warning fires, answer these before touching anything:

1. **What is the goal from here** — continue here, or hand off? Only you know. (A finished
   thread is a handoff whose goal says so.)
2. **What did we decide, reject, or correct that isn't written down yet?** That is the only
   content that cannot be recovered later.
3. **Which repo owns each of those?** Working in one repo on another repo's problem is fine;
   leaving the knowledge there is not.

Then `/checkpoint <mode>`. The ledger (`~/.claude/claude-kit/ledger/<session>.md` — a
historical directory name, kept across the move into `context-guard`) has been collecting decisions as you worked — the checkpoint is a delta, and after compaction the
ledger, and the manifest when this session owns it (the format spec's "Whose memory it is"
in `references/handoff-format.md`), are re-injected and outrank the machine summary (current repo state — git
log, the work-item store — outranks the manifest).

## Where the manifest lives

One file per session, in the Claude config dir:
`${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/handoff/<sid>/HANDOFF.md`. Nothing goes into the
repo, so concurrent sessions in one checkout never overwrite each other's, and the manifest
is never committed. Its path cannot be guessed, so **every checkpoint's last message prints
it**; a handoff also prints `/clear`, `/compact <guidance>` and a one-line opener to paste,
whose "Read (the Read tool) <path> in full" is what hands the file to a new session.

A handoff's close, for example (a session in librarian mode, handing on to an implement
run):

````text
Manifest: /home/me/.claude/claude-kit/handoff/1f0c…/HANDOFF.md
/clear — the successor in this process gets the manifest in full plus this session's ledger digest
/compact keep the F3b-4 thread; manifest /home/me/.claude/claude-kit/handoff/1f0c…/HANDOFF.md; no push until decision 52
```text
/dev-flow:librarian-mode start — Read (the Read tool) /home/me/.claude/claude-kit/handoff/1f0c…/HANDOFF.md in full first; then run /dev-flow:implement 8cc2-turn-gate-port; HOLD no push until decision 52
```
````

**Unattended checkpoints need three commands allowed.** The checkpoint writes the manifest
only through its draft in the session scratchpad (which needs no prompt) and a plugin
command that installs it, so an unattended checkpoint runs without a prompt once these
Bash commands are allowed (`permissions.allow` in a settings file, or "don't ask again"
at the first prompt). `<root>` is the plugin's install path — the `installPath` the
snippet under "If the gate blocks wrongly" finds; it carries the plugin version, so the
rules need re-adding after an update. They are literal prefix matches on the command as the
skill runs it, the script path in double quotes: run each command exactly as the skill
prints it — the same argument order and quoting — or it falls outside the rule and
prompts.

```text
Bash(python3 "<root>/hooks/turn_gate.py":*)
Bash(python3 "<root>/hooks/mark_checkpoint.py":*)
Bash(python3 "<root>/hooks/handoff_path.py":*)
```

- **A bystander sees nothing.** A session that starts in a repo where another session
  checkpointed gets no manifest line at all (it used to get a one-line foreign header).
  To pass work on, paste the opener; to look without taking it over, `cat` the path.
- **An old-layout `HANDOFF.md`** (`.claude-sandbox/HANDOFF.md` or the repo root) is never
  written again. A session with no manifest of its own still reads it, read-only, and is
  told once where its own now lives. If its `session:` is that session and it is untouched since that session's mark step
  stamped it, it is copied once
  into the session's store and read from there after — so a session that checkpointed
  before the store layout keeps its memory when a peer later overwrites the shared file.
  Delete the repo file when no session without a manifest of its own still needs it:
  once each session that wrote it has started again (and so has its copy), nothing reads
  it for them.
- **`… has changed since the copy`** at the mark step: the repo file was rewritten after
  its copy was taken. If it names another session, that session wrote it and there is
  nothing to do. If this session wrote it — a long-running session still following the
  pre-store Step 4b writes the repo file with `session: <stamped>` — its new content is
  not in the session's memory: draft the manifest again and install it with
  `mark_checkpoint.py --from <draft>`. The warning repeats on every mark until the repo
  file matches the copy again or is deleted. The copy keeps the source's mtime, so a copy
  taken of a manifest written over 30 minutes earlier is also `not stamped` (the window
  rule) and keeps its old stamp; its label does not flag that — it reads FRESH until the
  stamp is 24 hours old (or the code moves) — so this warning is the one signal that the
  body is older than the latest write.
- **Across config dirs the path does not resolve.** Sibling sandboxes on one host share
  the config dir (`~/.claude`, mounted at the same path), so a printed path works in all of
  them. It does not work for a tree that exports its own `CLAUDE_CONFIG_DIR`, another
  host, or a reader that is not a Claude Code session. There the work item is the only
  channel, and it is lossy: its handoff block carries `doing`, `next`, `blocked` and
  `learned`, so before handing off across that boundary, copy into the item's body the
  manifest's Holds, In flight, Copy forward, Read in full and every CORRECTION/REFUSED
  line. Goal, Doing, Scrolls and the other Aware-of lines do not cross.

## Reading the gate state (checkpoint Step 1)

The gate state gives the epoch and a depth, but **stores no source label** — the source is
derived when the gate reads the file. The status line writes an `exact` block (`pct`,
`tokens`, `window`, `at`) to its sensor file, `statusline/sensor/<session>.json` (written
by the `statusline-hub` plugin, which installing `statusline` brings; absent when it is not
installed). An older install whose status line
still runs context-guard's deprecated copy writes the block into the gate state instead; the
gate reads both and takes the one with the larger `at`. That block counts as *exact* only
while `now - at` is under 600s, and once it goes stale the depth is re-derived from the
transcript and is *inferred* (or
`inferred, window from status line`, the literal the gate messages print when a stale block
still supplied the window — the window is trustworthy there, the token count is not). Without a fresh
`exact` block the gate first tries to *derive* the window (the gate state's `derived` block:
`window`, `rule`, `resolved`), and a plain `tokens`/`pct` with neither is a guess. An exact
depth, or a derived one with `resolved: true`, can hard-block; an inferred depth, or a derived
one that is not resolved, only warns. `CONTEXT_GUARD_DERIVE=off` (or a
`CONTEXT_GUARD_CONTEXT_WINDOW` pin; deprecated alias `CLAUDE_KIT_CONTEXT_WINDOW`) in Claude
Code's launch environment turns derivation off.

## If the gate blocks wrongly

(Moved here from the installer skill when the status line became its own plugin,
`statusline`: this is gate content.)

A hard block needs a fresh exact reading or a resolved derived window (the mirror of Claude
Code's own window selection); an inferred depth or an unresolved derived one only warns. So a
wrong block means a fresh-but-wrong record, e.g. one written just before a compaction, or a
derived window that drifted from a newer Claude Code (the block message names the source:
`derived`; with a sensor record from `statusline-hub` a drift is caught, logged to
`claude-kit/context-gate/window-mismatch.jsonl`, and that version drops to warn-only). Three
escape hatches:
1. Pin the window: `CONTEXT_GUARD_CONTEXT_WINDOW=1000000` (tokens) in the environment Claude
   Code is launched from; the hooks then never guess the denominator, and the pin also turns
   the derived window off (as hatch 3 does). The deprecated alias `CLAUDE_KIT_CONTEXT_WINDOW`
   still works. The new name wins when both are valid (digits only, no `1m`, spaces or
   underscores); a malformed new name never switches off a valid old-name pin — the old one
   then applies, since a pin can only remove derived blocks.
2. Emergency stand-down: record a checkpoint for the current epoch — exactly what
   `/checkpoint` records — with the plugin's own `mark_checkpoint.py`. It writes through the
   same locked read-modify-write as every hook, so a hook firing at the same moment cannot
   drop the change (a hand-edit of the state file can). The session id names the state file
   under `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-kit/context-gate/` (the newest `.json`
   there is the live session; `gauge.json`, `window-mismatch.jsonl` and the `_`-prefixed
   files are not sessions). It refuses, exiting non-zero and
   writing nothing, when no state file exists for that id — a mistyped id, since a live
   session always has one. It also stamps the machine fields of that session's own
   manifest — found by the session id, in the config dir (above), wherever you run it —
   but only a manifest written in the last 30 minutes (the format spec's "Machine fields"
   rule); an older one is left as it is. The working directory supplies only the `head:`,
   `branch:` and `top:` it records, so run it from the repo the manifest is about; the
   installed-path lookup below wants the project directory too. The gate stays down until the next compaction or
   `/clear`. The
   HARD STOP message itself prints this command with the script's absolute path filled in;
   to run it by hand, resolve the path as below, which works the same from a Bash tool call
   inside the session and from a plain terminal. `${CLAUDE_PLUGIN_ROOT}` does not work here:
   Claude Code substitutes it into a plugin's `SKILL.md` text and exports it to hook
   processes, but it is not in the Bash tool's environment, and this reference file is read,
   not substituted. The path comes from the harness's own install record,
   `installed_plugins.json`, whose `plugins['context-guard@kmacmcfarlane']` holds one entry
   per install scope. The snippet takes the `installPath` of the entry that applies where it
   runs, not the first one listed: a `local` or `project` entry whose `projectPath` is the
   current directory or one above it (the deepest such path, `local` before `project`),
   else the `user` entry — so run it from the project directory. The fallback, when that
   record is missing, unreadable or has no entry that applies, is the update-stable
   `current-hooks` link in the newest `context-guard-*` data dir (one per marketplace the
   plugin was installed from — list them with plain `ls -d` and pick yours if unsure):

```bash
P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"
MC="$(python3 - "$P/installed_plugins.json" 2>/dev/null <<'PY'
import json, os, sys
es = json.load(open(sys.argv[1]))["plugins"]["context-guard@kmacmcfarlane"]
cwd = os.path.realpath(os.getcwd())
def rank(e):  # the scope that applies here: deepest project/local path, then user
    pp = e.get("projectPath")
    if e.get("scope") in ("local", "project") and pp:
        pp = os.path.realpath(pp)
        if cwd == pp or cwd.startswith(pp.rstrip("/") + "/"):
            return (2, len(pp), e["scope"] == "local")
    return (1, 0, False) if e.get("scope") == "user" else (0, 0, False)
best = max(es, key=rank)
print(best["installPath"] if rank(best)[0] else "")
PY
)/hooks/mark_checkpoint.py"
test -f "$MC" || MC="$(ls -td "$P"/data/context-guard-*/ 2>/dev/null | head -1)current-hooks/mark_checkpoint.py"
python3 "$MC" <session_id>
```
3. Turn the window mirror off: `CONTEXT_GUARD_DERIVE=off` in the environment Claude Code is
   launched from. The gate is then exactly what it was before the mirror: exact from the
   status line, else inferred (warn-only). Worth a note to the plugin maintainers: a derived
   block that was wrong means the mirrored table needs a new Claude Code version.
