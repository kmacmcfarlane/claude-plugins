# The launch command

The one command the user copies to start the new repo's first session. It launches the
session **and** attaches them, because it runs in their own terminal, in the foreground.

## Why the skill never launches it

- **No detached mode.** `claude-sandbox` has no `--detach` yet (tracked in the
  claude-sandbox repo's own store). A launch runs in the foreground of whatever terminal
  started it, so a session started under this agent's pty dies when this session ends,
  and the user could never see it in the meantime.
- **In-sandbox launches are fragile.** Launching from inside a container needs a
  host-visible `TMPDIR`, and the launch lock is per container. A launch from the user's
  own terminal on the host has neither problem.

When `claude-sandbox` gains a detached mode, the skill can launch and hand over a bare
`claude-sandbox --attach` instead. Until then: one command that does both.

## The bootstrap prompt

Pass it as claude's initial prompt. Fill NAME and PURPOSE (the user's words from Step 1,
one line — collapse newlines to spaces):

```
This is NAME, a new repo for this thread: PURPOSE. README.md states the purpose; nothing else exists yet. First, write this repo's CLAUDE.md the way /init does: the purpose, the layout, how to build and test once there is something to build, and the conventions to follow. Keep it short and grounded in what is actually here, and commit it. Then run the thread's first investigation into the purpose above: use the investigate skill (dev-flow plugin) if this session has it, otherwise investigate directly and write your findings and the proposed next steps into the repo. Ask me before choosing a stack or anything else that is hard to reverse.
```

With a template goal (Step 4 ran), replace "nothing else exists yet" with "it was
scaffolded from the TEMPLATE template, whose CLAUDE.md is already here", and "write this
repo's CLAUDE.md" with "update CLAUDE.md for this thread's purpose".

With an existing investigation series (Step 1 noted one; SLUG its slug, OLD its current
`repo:path`), replace "nothing else exists yet" with "an investigation series for this
thread is at .claude-sandbox/investigations/SLUG/, moved here from OLD" (with a template,
append that clause after the template one), and replace the sentence beginning "Then run
the thread's first investigation" with:

```
Then read that series and extend it rather than starting a new one: use the investigate skill (dev-flow plugin) if this session has it, writing the next serial after the highest one there, never a new 00; otherwise add your findings and the proposed next steps as a new file at that next serial. If that directory is not here yet, the series has not been moved: move it from OLD as the investigate skill describes if you can reach it, otherwise ask me where it is.
```

SLUG and OLD passed Step 1's check (SKILL.md), so each is one line with no newline to
collapse, and the prompt stays one line; they are then handled as PURPOSE is below.

## Getting the prompt into the shell

The prompt carries the user's purpose, which is untrusted text: a `$(...)` or backtick in
it runs in this agent's shell the moment it sits inside double quotes. So never build
`PROMPT` as `PROMPT="...PURPOSE..."`. Either:

- **Quoted heredoc** — the quoted delimiter turns off every expansion, so the text is
  taken byte for byte:
  ```bash
  PROMPT=$(cat <<'EOF'
  This is NAME, a new repo for this thread: PURPOSE. ...
  EOF
  )
  ```
  The prompt is one line (PURPOSE's newlines collapsed above, SLUG and OLD checked to one
  line), so no line of it can equal `EOF`.
- **A file** — write the filled prompt with the Write tool to a scratch file (the session
  scratchpad when there is one), then `PROMPT=$(cat "$file")`.

`REPO` and `NAME` passed the character check (SKILL.md, Important and Step 2), so they are
assigned in single quotes at the top of the same Bash call:
`REPO='/home/me/work/restic-backup-migration'; NAME='restic-backup-migration'`.

## The command

Shell-quote every value with single quotes (a `'` inside becomes `'\''`) so a purpose
containing quotes, `$` or backticks reaches claude verbatim. A helper that does it:

```bash
sq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
```

**Sandbox form** (Step 3 found claude-sandbox):

```bash
echo "cd $(sq "$REPO") && claude-sandbox -- --name $(sq "$NAME") $(sq "$PROMPT")"
```

**Plain form** (no claude-sandbox — say so above the command):

```bash
echo "cd $(sq "$REPO") && claude --name $(sq "$NAME") $(sq "$PROMPT")"
```

Print the resulting line, not the `echo` — that line is what the user copies.

The `'\''` escape is POSIX-shell quoting (bash, zsh, sh). In fish, a quote inside single
quotes is `\'` instead, so a fish user runs the line from a POSIX shell: type `bash`,
then paste it.

## Why these flags

Verified against `claude-sandbox --help` and the launcher's argument grammar:

- **`--`** ends the launcher's own flags. Everything after it goes to `claude` verbatim.
  Without it, a positional prompt would also pass through, but a prompt that happens to
  start with `--` would be read as an unknown launcher flag and rejected.
- **`--name NAME`** is claude's session display name (`-n, --name`). It shows in the
  prompt box and in `/resume`, so the thread is easy to find again.
- **The prompt** is claude's positional `[prompt]`: an interactive session that starts
  with that message already sent.
- **Nothing else.** The session inherits the repo's sparse `.claude-sandbox/config.yaml`,
  which defers to the workspace's parent-directory config (model, host access, memory
  limit). Worktree mode stays at the interactive default, the shared checkout, which suits
  a repo with one thread and one session. A workspace config with `worktree: true`
  overrides that: the session then works on a `worktree-*` branch whose commits need
  merging into `main` (the skill's report says so).

## Recovering a lost terminal

`cd REPO && claude-sandbox --attach` reattaches to the running session (sandbox form only).
With the plain form, `cd REPO && claude --resume` and pick the session by its name.
