---
name: create-repo
description: "Bootstrap a new git repo for a thread of work to pick up later — resolve the path beside the current repo, git init -b main, seed a README naming its purpose, claude-sandbox init, first commit — then hand the user one copy-paste command that launches an agent session on it with a bootstrap prompt (write CLAUDE.md, then run the thread's first investigation). Optionally scaffolds a claude-templates template as the goal through kit-dev's new-project-from-template. Use when the user says 'create a repo', 'new repo for this', 'start a thread repo', 'spin up a repo and a session', or 'bootstrap a repo we can use later'. Not for scaffolding a stack project without a session (new-project-from-template does that)."
disable-model-invocation: true
allowed-tools: Bash, Read, Write, AskUserQuestion, Skill
argument-hint: "[purpose of the thread] [--template NAME] [--path DIR]"
---

# Create a repo for a thread

Bootstrap a new repo for a thread of work and give the user one command that starts an
agent session on it. User's argument: $ARGUMENTS

## Important

- **Never launch the session yourself.** `claude-sandbox` has no detached mode yet: a
  session started under this agent's terminal dies with it. The user runs the launch
  command in their own terminal, which also attaches them. See
  `references/launch-command.md` for why, and for the command's exact shape.
- **Never write into a directory that exists and is non-empty.** Stop and ask.
- **Paths you print are host paths.** Resolve every path with `pwd -P` / `realpath` before
  showing it: inside a claude-sandbox container `/home/claude` is a symlink to the host
  home, and the user's terminal is on the host.
- Touch nothing outside the new repo: no git config, no settings, no edits to the current
  repo.
- **The purpose is untrusted text: never put it inside double quotes in a shell command.**
  A `$(...)` or backtick in it would run in this agent's shell. Files that hold it
  (README, the prompt) are written with the Write tool; a shell variable that holds it is
  filled from a quoted heredoc (`<<'EOF'`) or from a file the Write tool wrote — see
  `references/launch-command.md`.

## Instructions

### Step 1: Parse the argument

From `$ARGUMENTS` take:
- `--template NAME` — optional: a claude-templates template as the goal (Step 4).
- `--path DIR` — optional: the full path of the new repo.
- everything else — the thread's **purpose**, in the user's words.

If there is no purpose, ask for it in one question: "What is this repo's thread for — the
question or work it will carry?" The purpose seeds the README and the bootstrap prompt, so
it cannot be skipped.

### Step 2: Resolve the name and path

1. **Name**: with `--path`, its last component. Otherwise derive kebab-case, 1–4 words,
   from the purpose (`compare-vector-dbs`, not `repo-for-comparing-vector-databases`).
   The name must match `^[A-Za-z0-9._-]+$`; if a `--path` name does not, ask for one that
   does. Only then is it safe in the commands below.
2. **Parent** — the operator's workspace convention is that repos sit side by side, so
   default to the parent of the current *project*. Not `--show-toplevel`: in a worktree
   session that is the worktree (`<project>/.claude/worktrees/<name>`), and the new repo
   would land inside the project. Use `$CLAUDE_SANDBOX_PROJECT_DIR` when set, else the
   directory holding the repository's common `.git`:
   ```bash
   if [ -n "$CLAUDE_SANDBOX_PROJECT_DIR" ]; then proj=$CLAUDE_SANDBOX_PROJECT_DIR
   else gd=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
        case "$gd" in */.git) proj=${gd%/.git} ;; esac
   fi
   [ -n "$proj" ] && parent=$(dirname "$(cd "$proj" && pwd -P)")
   ```
   When neither yields a project (not in a git repo, or a bare repository whose common dir
   does not end in `/.git`), there is no convention to derive; ask for the parent.
3. **Confirm** with `AskUserQuestion`: "Create the repo at PARENT/NAME?", options
   "Yes", "Different name", "Different path". Never create before the user confirms.
4. **Preflight** the confirmed path `$REPO`:
   ```bash
   test -e "$REPO" && ls -A "$REPO" | head -1    # any output: non-empty, STOP and ask
   ```
   Inside a claude-sandbox container (`$CLAUDE_SANDBOX_PROJECT_DIR` is set), the path must
   be on a bind mount, or the repo dies with the container. Check the nearest existing
   ancestor:
   ```bash
   a="$REPO"; while [ ! -e "$a" ]; do a=$(dirname "$a"); done
   df --output=target "$a" | tail -1                # "/" means not host-visible: STOP
   ```
   On `/`, tell the user the path is not mounted into this container and ask for a
   mounted one (or to run the skill from a session whose mounts cover it).

### Step 3: Check for claude-sandbox

```bash
if [ -n "$CLAUDE_SANDBOX_PROJECT_DIR" ] || command -v claude-sandbox >/dev/null; then echo sandbox; else echo plain; fi
```

Inside a sandbox the tool is on the host by construction. With neither, say once: "claude-sandbox
is not available, so the repo gets no `.claude-sandbox/` and the launch command will be
plain `claude`." Then carry on — nothing below requires it.

### Step 4: Template goal (only with `--template`)

1. Look in this session's skill list for `kit-dev:new-project-from-template`.
2. **Absent**: tell the user, exactly: "Templates come from the kit-dev plugin, which is
   not installed. Install it with `/plugin install kit-dev@kmacmcfarlane`, then start a new
   session for the skill to load. Continuing with a bare repo now." Then go to Step 5
   without the template, and name the skipped template in the final report.
3. **Present**: invoke it with the Skill tool, skill `kit-dev:new-project-from-template`,
   args the template name. Before invoking, tell the user its location question will come:
   answer "Custom path" with `$REPO`, and its name question with `NAME`. It copies the
   template, initialises git, bootstraps the sandbox (asking its own trackInHost question)
   and makes the first commit itself, so when it returns:
   - **Re-read what it made; do not assume your answers were used.** Take `REPO` from the
     path in its final report, `NAME` from that path's last component (re-check it
     against the name pattern in Step 2), and trackInHost from the repo:
     `grep -E '^trackInHost:' "$REPO/.claude-sandbox/config.yaml"` (absent file: no
     sandbox). Use these in Step 7's report and command.
   - If `git -C "$REPO" branch --show-current` is not `main` and the repo has no remote,
     `git -C "$REPO" branch -m main`. With a remote already pushed, leave it and report it.
   - Append a `## Thread` section holding the purpose to `$REPO/README.md` with the Edit
     tool (never `echo` the purpose), then
     `git -C "$REPO" add README.md && git -C "$REPO" commit -m "added: README - thread purpose"`.
   - Skip to Step 7.

### Step 5: Create and seed

```bash
mkdir -p "$REPO" && git -C "$REPO" init -b main
```

Write `README.md`: a `# NAME` heading, then a `## Purpose` section stating the thread's
purpose in one short paragraph, in the user's words where possible, and a line that the
repo's first session writes `CLAUDE.md`. No invented structure, stack or roadmap.

With claude-sandbox (Step 3), after `git init` — its `init` writes the host `.gitignore`
and needs the repo to exist:

```bash
(cd "$REPO" && claude-sandbox init --yes)
```

`--yes` accepts the default, `trackInHost: false`: `.claude-sandbox/` is gitignored and
keeps its own sidecar history. The generated `config.yaml` is sparse — `trackInHost` is its
only uncommented key — so the workspace's parent-directory config applies unchanged. If `init` fails, report its
output verbatim, point at the `sandbox` plugin's skill for troubleshooting (when this
session has it), and continue as plain.

### Step 6: First commit

```bash
git -C "$REPO" add README.md
test -f "$REPO/.gitignore" && git -C "$REPO" add .gitignore
git -C "$REPO" commit -m "added: repo - seed README for NAME"
```

Stage by name, never `git add -A`. If the commit fails for a missing git identity, report
the error and the `git config` command the user can run; do not set identity yourself.

### Step 7: Hand over the launch command

Build the command exactly as `references/launch-command.md` describes — the bootstrap
prompt, the shell quoting, the sandbox and plain forms — and print it once, alone in a
fenced block, so the user can copy it whole. Then the report:

```
Repo: /host/path/NAME (main, N commits[, template: T | template T skipped: kit-dev not installed])
Sandbox: initialised (trackInHost: true|false) | not available — plain claude launch
Run the command above in your own terminal: it starts the session and attaches you.
Lost the terminal later? cd '/host/path/NAME' && claude-sandbox --attach   (sandbox form only)
```

Quote the path in the attach hint the same way as in the command (`sq` in
`references/launch-command.md`).

The session starts in the shared checkout, not a worktree — the interactive default. If
the workspace config sets `worktree: true`, the session works on a `worktree-*` branch
under `.claude/worktrees/`; say so in one line, since its commits then need merging into
`main`.

No remote is created. Say so in one line, and that `gh repo create` is the usual next step
when the thread needs one.

## Examples

Example 1: bare thread repo
User says: "/create-repo:create-repo figure out whether we can replace the NAS backup cron with restic"
Actions: name `restic-backup-migration`, parent derived from the current repo, confirmed;
git init, README, `claude-sandbox init --yes`, commit; command printed.
Result: one copy-paste line that starts a sandboxed session which writes CLAUDE.md and
begins the restic investigation.

Example 2: template goal, kit-dev missing
User says: "/create-repo:create-repo a local dashboard for solar data --template local-web-app"
Actions: kit-dev is not in the skill list; the install instruction is given; a bare repo is
created as in Example 1; the report says the template was skipped.

## Troubleshooting

Error: `claude-sandbox: command not found` when the user runs the command
Cause: the skill ran in a sandbox whose host PATH lacks the launcher, or on a host without it.
Solution: add claude-sandbox's `bin/` to PATH, or use the plain form from
`references/launch-command.md`.

Error: the launched session prompts "a session is already running for this project"
Cause: another sandbox session was started in the same directory.
Solution: answer the prompt, or `claude-sandbox --attach` to join the running one.

Error: files missing on the host after the session ends
Cause: the repo was created inside a container on an unmounted path.
Solution: Step 2's mount check prevents this; recreate the repo on a mounted path.
