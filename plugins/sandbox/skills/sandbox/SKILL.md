---
name: sandbox
description: "Guides setup, configuration, and troubleshooting of claude-sandbox Docker containers. Use when user asks about claude-sandbox, sandbox configuration, .claude-sandbox/config.yaml, .claude-sandbox/Dockerfile, config cascade, bootstrapping a project (claude-sandbox init / init-ralph), ralph loops, container isolation, host access flags (--docker-socket, --aws, --git, --ssh), worktree mode (--worktree, --no-worktree, the worktree config key), model selection (--model), image rebuilding (--rebuild), or Claude Code version updates. Also triggers on sandbox launch errors, entrypoint issues, volume mount problems, a session that died or vanished mid-command, OOM, or a container/build exiting with code 137."
disable-model-invocation: false
allowed-tools: "Read, Glob, Grep, Bash, Edit, Write, Agent"
argument-hint: [init | config | worktree | troubleshoot | question]
---

# claude-sandbox Skill

Expert guidance for the claude-sandbox project — a Docker-based sandbox for running Claude Code with filesystem isolation and opt-in host access.

## Important

- claude-sandbox lives at `https://github.com/kmacmcfarlane/claude-sandbox`, part of the [claude-kit](https://github.com/kmacmcfarlane/claude-kit) ecosystem
- The project CLAUDE.md is the authoritative source for architecture details — read it first
- Always check the current state of launcher script and config files before giving advice

## Core Concepts

### Two-Layer Image System
1. **Base image** (`claude-sandbox`): OS, build-essential, Node 22, Claude CLI, Docker CLI, Python venv, sandbox scripts
2. **Child image** (`claude-sandbox-{project-slug}`): Project-specific tools via `.claude-sandbox/Dockerfile` extending `FROM claude-sandbox`

The launcher auto-builds both layers. Base rebuilds trigger child rebuilds.

### Home Directory Convention
The base image provides `/home/claude` as the build-time home directory. Child Dockerfiles should always use `/home/claude` for any paths under the home dir — never hardcode a host-specific path like `/home/yourname`.

At runtime, the entrypoint:
1. Renames the `claude` user to match the host caller (e.g. `rt`)
2. Moves all build-time files from `/home/claude` to the host home path (e.g. `/home/rt`), skipping anything already present (bind mounts from the host are never overwritten)
3. Symlinks `/home/claude → /home/rt` so any hardcoded paths still resolve
4. Chowns all non-bind-mounted files to the host UID/GID

Use `USER claude` for `RUN` steps that write to the home dir, and end with `USER root` so the entrypoint has privileges:

```dockerfile
USER claude
RUN mkdir -p /home/claude/.cache/mytool && echo "config" > /home/claude/.cache/mytool/settings
USER root
```

### Same-Path Mounting
The container sees the project at its real host path. This is critical for `docker compose` volume resolution against the host daemon.

### The Worktree Convention — process stays in the checkout, work goes in a worktree
Interactive launches run Claude in the shared repo checkout; worktree mode is **off by default for interactive sessions, on for ralph**. The rationale: Claude Code files transcripts by working directory, so a process living in a worktree has an empty resume history — the process stays in the checkout, the work goes in a worktree.

The working convention:

1. A session starts in the repo checkout. Before substantive edits to the repo, enter a worktree (`EnterWorktree`) or delegate to an Agent with worktree isolation; return with `ExitWorktree` once the work is merged or handed off.
2. Reading, planning, answering questions, and editing files under `.claude-sandbox/` need no worktree.
3. Parallel tasks each get their own worktree; never share one.
4. A worktree is a fresh checkout: untracked inputs (`.env`, `node_modules`) are absent unless listed in `.worktreeinclude` or covered by Claude Code's `worktree.symlinkDirectories` setting.
5. Ralph is the exception: its whole run is work, the launcher starts it in a worktree, and the run branch is the deliverable.

**Enforcement:** this plugin ships a PreToolUse hook (`hooks/checkout_guard.py`, registered in `hooks/hooks.json`) that blocks `Edit`/`Write`/`MultiEdit`/`NotebookEdit` on git-tracked files when the session's cwd is a main checkout — the direction the harness's own worktree guard does not cover. Untracked files, paths under `.claude-sandbox/` or `.claude/`, worktree cwds, and non-git cwds pass untouched, and any git error fails open (ralph runs in a worktree, so it is exempt by construction). Escape hatches: set `SANDBOX_ALLOW_CHECKOUT_EDITS=1` in the environment (`CLAUDE_KIT_ALLOW_CHECKOUT_EDITS=1` still works as a deprecated alias with the same semantics), or create a `.claude/allow-checkout-edits` marker file in the repo root for a standing per-repo opt-out. Not guarded: Bash writes (sed, heredocs), and files inside submodules edited from the superproject's checkout (the superproject tracks only the gitlink).

When the mode resolves on, the launcher runs Claude in a git worktree, not the main checkout: `.claude/worktrees/<name>` on branch `worktree-<name>`. The name defaults to the container's instance noun, so container, worktree, and branch share one word. `--worktree=NAME` reopens the existing worktree NAME; a join runs bare `--worktree` and `--branch` composes with the fork flags as `--worktree <new-noun>` — both only when the mode resolves on. The launcher prints a `Worktree: …` banner only when a worktree is in use or a requested one stood down; a shared-checkout launch prints nothing.

Every container gets `CLAUDE_SANDBOX_PROJECT_DIR` set to the project root (useful for reaching `.claude-sandbox/` from inside a worktree). Shell commands in this skill spell sandbox paths as `"${CLAUDE_SANDBOX_PROJECT_DIR:-.}"/.claude-sandbox/...` so they work from a worktree cwd inside a container and fall back to the project-root cwd on the host. The container carries a `claude-sandbox.worktree` label, `claude-sandbox sessions` lists a WORKTREE column, and attach reports the worktree. The choice is per-session and excluded from the config drift fingerprint.

When the mode resolves on but the project is not a git work tree, the launcher stands down with the banner `Worktree: off (not a git repository)` and runs in the project directory — see Troubleshooting.

**Unverified:** whether Bash writes from inside the worktree into the gitignored `.claude-sandbox/` sidecar pass the harness guard (a live ralph run will settle it).

### Configuration Precedence
CLI flag > env var > merged `.claude-sandbox/config.yaml` cascade > defaults

For worktree mode specifically: `--worktree[=NAME]` / `--no-worktree` > `CLAUDE_SANDBOX_WORKTREE` > `worktree: true|false` in the cascade > the per-kind default (off for interactive launches, on for ralph). One flag/env/key governs both kinds of launch; only the fall-through default differs. The `worktree` key cascades like any other scalar — a more-local `config.yaml` overrides an upstream one.

Three kinds of files are resolved by walking parent directories (direnv-style), each with its own semantics:
- `.claude-sandbox/config.yaml` — **cascades**: every config from the filesystem root down to the project is deep-merged; more-local values override, `mounts` append (a same `host`+`container` entry overrides the upstream one, e.g. to flip `writable`). The launcher prints the cascade at startup.
- `.claude-sandbox/env` — **layers**: every env file is passed as a stacked `--env-file` flag; a variable set in a more-local file overrides the upstream value.
- `.claude-sandbox/Dockerfile` — **nearest wins**: the closest one up the tree is used wholesale (no merging).

This supports a catch-all `.claude-sandbox/` at a workspace root that provides defaults for every project beneath it; per-project configs stay sparse and only override what differs.

**Layout:** all sandbox files live under `.claude-sandbox/` — `config.yaml`, `env`, `Dockerfile`, `ralph/`, `agent/`, and `scripts/`. The legacy scattered-root layout is no longer supported. See claude-sandbox `docs/MIGRATION.md`.

### `trackInHost` — how `.claude-sandbox/` is version-controlled
Set in `.claude-sandbox/config.yaml`:
- **`false` (default, foreign-safe):** the launcher adds `/.claude-sandbox/` to the host `.gitignore` and creates an internal **sidecar git repo** inside `.claude-sandbox/` for history. Use when working in someone else's repo — nothing leaks into their history.
- **`true` (your own projects):** the dir is tracked by the host repo; no sidecar. Only `.claude-sandbox/env`, `.claude-sandbox/temp/`, and `.claude-sandbox/ralph/` are gitignored.

In **both** modes the launcher also adds `.claude/worktrees/` to the host `.gitignore`, so worktree-mode checkouts never appear as untracked files in the host repo.

**Sidecar commit SOP (when `trackInHost: false`):** after grooming the backlog or changing the agent flow, PROMPT the user to commit in the sidecar — do not auto-commit:
```bash
git -C "${CLAUDE_SANDBOX_PROJECT_DIR:-.}"/.claude-sandbox add -A && git -C "${CLAUDE_SANDBOX_PROJECT_DIR:-.}"/.claude-sandbox commit -m "..."
```

## Common Tasks

### Setting Up a New Project
Run the bootstrap subcommand from the project directory:
```bash
claude-sandbox init          # base: sparse config.yaml + env + Dockerfile.example, gitignore, sidecar
claude-sandbox init-ralph    # init + ralph agent/ + scripts/ scaffolding (backlog tools)
```
- Only `--track-in-host` / `--no-track-in-host` apply to these subcommands (they set `trackInHost` non-interactively; otherwise `init` prompts — unless an upstream config already defines it, then it's inherited).
- Both are **idempotent**: existing files are never overwritten, so template-provided docs win and re-running fills only gaps.
- The seeded `config.yaml`/`env` are **sparse (fully commented)** — they override nothing in the cascade; uncomment a key to set it for this project.
- Rename `.claude-sandbox/Dockerfile.example` → `Dockerfile` to activate project-specific tooling.
- Then run `claude-sandbox` to launch.

### Choosing a Model
- **CLI flag**: `claude-sandbox --model claude-opus-4-8` (or alias like `opus`)
- **YAML** (`.claude-sandbox/config.yaml`): `model: claude-opus-4-8`
- Forwarded to both `claude` and `ralph` as `--model`

### Updating Claude Code
On launch, the sandbox checks whether a newer Claude Code version is available on npm and prompts to rebuild. Use `--no-update-check` or `CLAUDE_SANDBOX_NO_UPDATE_CHECK=1` to skip.

Force a full rebuild with `claude-sandbox --rebuild`.

### Enabling Host Access
Options (pick any):
- **CLI flags**: `--docker-socket`, `--aws`, `--git`, `--ssh`
- **Env vars**: `CLAUDE_SANDBOX_HOST_ACCESS_DOCKER_SOCKET_ENABLED=1`, etc.
- **YAML** (`.claude-sandbox/config.yaml`):
  ```yaml
  hostAccess:
    dockerSocket:
      enabled: true
    ssh:
      enabled: true
  ```

### Controlling Worktree Mode
Off by default for interactive launches, on for ralph; precedence CLI > env > cascade YAML > per-kind default:
- **CLI flags**: `--worktree[=NAME]` opts an interactive session in (`--worktree=NAME` reopens the existing worktree NAME; bare `--worktree` uses the default name — the instance noun); `--no-worktree` turns it off — already the interactive default, so rarely needed, but it also turns ralph's worktree off
- **Env var**: `CLAUDE_SANDBOX_WORKTREE` (`1` enables, `0` disables — sets the default for both interactive and ralph)
- **YAML** (`.claude-sandbox/config.yaml`): `worktree: true` or `worktree: false` (cascades; one key sets the default for both interactive and ralph)

`claude-sandbox sessions` shows which worktree each session is in (WORKTREE column).

### Running Ralph (Loop Runner)
```bash
claude-sandbox --ralph --docker-socket --dangerous --limit 5
```
- Runs Claude in fresh-context iterations (new process each time)
- Runs in one worktree named `ralph` per run — the worktree convention's exception: the whole run is work and the run branch is the deliverable (details are ralph's own contract, not covered here)
- Stop gracefully: `touch "${CLAUDE_SANDBOX_PROJECT_DIR:-.}"/.claude-sandbox/ralph/stop`
- Debug: read `"${CLAUDE_SANDBOX_PROJECT_DIR:-.}"/.claude-sandbox/ralph/runlogs/rawlog_*` for full NDJSON streams
- Metrics: `"${CLAUDE_SANDBOX_PROJECT_DIR:-.}"/.claude-sandbox/ralph/runlog.json`

### Adding Extra Volume Mounts
In `.claude-sandbox/config.yaml`:
```yaml
mounts:
  - host: /home/user/shared-libs
    container: /home/user/shared-libs
  - host: /data/datasets
    container: /mnt/data
    writable: true
```
Mounts append down the config cascade. To change an upstream mount (e.g. make it writable), re-declare the same `host` + `container` pair locally with the new settings — it overrides the upstream entry instead of duplicating it.

## Troubleshooting

### A path the user named doesn't exist inside the container

**Check the mounts before concluding it isn't there.** Only the project directory and the
configured mounts are visible from inside; a host path the user refers to by its host-side
name — especially one reached through a symlink — is commonly present at a *different* path,
or reachable but not where you looked. `find` returning nothing looks identical to "the
directory does not exist", so the wrong conclusion is the easy one.

```bash
grep -A15 '^mounts:' "${CLAUDE_SANDBOX_PROJECT_DIR:-.}"/.claude-sandbox/config.yaml     # this project's mounts
```

Mounts cascade and **append**, so also check every ancestor — a parent directory's
`.claude-sandbox/config.yaml` may supply the mount:

```bash
d="${CLAUDE_SANDBOX_PROJECT_DIR:-$PWD}"; while [ "$d" != / ]; do
  [ -f "$d/.claude-sandbox/config.yaml" ] && grep -l -A15 '^mounts:' "$d/.claude-sandbox/config.yaml"
  d=$(dirname "$d")
done
```

The launcher prints the resolved cascade at startup (root → project), so the same information
is in the scrollback of the run that started this session.

Symlinks are resolved on the host, so `~/foo` pointing at `/srv/bar` appears inside the
container at `/srv/bar` (or wherever `container:` maps it) — never at `~/foo`. Search for the
directory's *basename* rather than the path the user gave you.

Only after the mounts show no route to it should you report it as unreachable — and then say
what would fix it: add a mount to `.claude-sandbox/config.yaml` and relaunch.

### Banner says "Worktree: off (not a git repository)"
Not an error. A requested worktree needs the project to be a git work tree; when it isn't, the launcher stands down and runs Claude in the project directory directly. To use worktree mode, `git init` the project first. This stand-down line is the launcher's only off-state banner: a session in the shared checkout (the interactive default, or `--no-worktree`) prints no worktree banner at all — though a `--no-worktree` ralph run still shows `worktree: off (shared checkout)` in the ralph loop's own startup block.

### `--resume` picker is empty or missing conversations
Claude Code files transcripts by working directory, and a worktree is a different directory with its own history — an empty picker usually means the session is inside a worktree. `Ctrl+W` in the picker lists sessions across all worktrees (including transcripts from sessions launched while worktree mode was still the interactive default); `Ctrl+A` lists all projects.

### Container won't start
1. Check Docker daemon is running: `docker info`
2. Check base image exists: `docker images claude-sandbox`
3. Look for build errors in launcher output
4. Verify `.claude-sandbox/Dockerfile` syntax if using child image

### File permission issues
The entrypoint remaps UID/GID and chowns all non-bind-mounted files under the home directory. If files have wrong ownership:
1. Check that the child Dockerfile uses `/home/claude` (not a hardcoded host path)
2. Check that `USER claude` / `USER root` bracketing is correct for home-dir writes
3. Verify the host user's UID matches expectations: `id`
4. If a tool can't write to `~/.cache` or similar, the entrypoint's chown may have missed it — check `entrypoint.sh` for the mountinfo-based prune logic

### Docker commands fail inside container
Ensure `--docker-socket` flag or `hostAccess.dockerSocket.enabled: true` is set. The container talks to the host Docker daemon — there is no daemon inside.

### Ralph loop won't stop
1. `touch "${CLAUDE_SANDBOX_PROJECT_DIR:-.}"/.claude-sandbox/ralph/stop`
2. If stuck, check `"${CLAUDE_SANDBOX_PROJECT_DIR:-.}"/.claude-sandbox/ralph/lock` for the PID
3. The activity watchdog (`logstream/activity-watchdog.js`) exits after N minutes of silence

### Session dies mid-command and relaunching resumes it (container OOM-killed)

**Symptom:** the Claude session is simply gone mid-command — no error dialog, the terminal
line just ends — and relaunching `claude-sandbox` resumes the same conversation as if nothing
happened. This looks like the Claude process crashing, but it is usually the container being
OOM-killed by the host kernel: the session was mid-`Bash` on a heavy build or test run, memory
usage crossed the container's limit, and the kernel killed the container's main process (or
init/PID 1, which takes the whole container with it).

The cgroup OOM killer picks whatever has the highest `oom_score`, often the build process
itself rather than `claude`/`node` — in that case only the `Bash` call exits `137` and the
session survives to report it. A build step failing with a lone `exit 137` inside an
otherwise-alive session is the same memory-ceiling problem, just caught before it took the
session down too.

**Check:** run these on the host, or in a relaunched sandbox with the docker socket enabled
(`--docker-socket` / `hostAccess.dockerSocket.enabled` — see "Docker commands fail inside
container" above). The launcher runs containers with `--rm`, so a dead container is deleted
immediately — `docker ps -a` won't list it and `docker inspect` returns "No such object";
there is nothing left to inspect after the fact. Query the daemon's event log instead:
```bash
docker events --since 1h --until 0s --filter event=oom --filter event=die \
  --format '{{.Time}} {{.Action}} {{.Actor.Attributes.name}} exit={{.Actor.Attributes.exitCode}}'
```
An `oom` event followed by `die exit=137` for the same container name confirms it. The
launcher's own exit status of `137` is a second signal.

**Remedies:**
- Raise `memoryLimit` in `.claude-sandbox/config.yaml` for this project — it defaults to
  `8g`, swap is off (the launcher sets `--memory-swap` equal to `memoryLimit`, so there's no
  overflow room), and being cascade config it takes effect only on the next relaunch, not the
  running container.
- Cap build and test parallelism inside the container — flags like `-p`/`-j` and env vars
  like `GOMAXPROCS` multiply memory use per worker. (Project-specific example: Go's
  `go test`/`ginkgo -r --race` builds are especially heavy, since the race detector
  instruments every memory access.)
- Avoid running heavy builds in parallel across subagents in the same container — each one
  adds to the same memory ceiling.

Note: the launcher does not yet report an OOM kill on exit — it just looks like the session
dying, which is why the check above is manual. Tracked in the claude-sandbox repo as item
`d95a`.

### Child Dockerfile not found
The launcher walks parent directories. To skip child image detection entirely:
- Set `baseOnly: true` in `.claude-sandbox/config.yaml`
- Or `CLAUDE_SANDBOX_BASE_ONLY=1`

## Key Files Reference

| File | Purpose |
|---|---|
| `bin/claude-sandbox` | Main launcher script |
| `bin/ralph` | Loop runner |
| `entrypoint.sh` | Container entrypoint (UID/GID remapping) |
| `Dockerfile` | Base image definition |
| `notification-hooks.json` | Hook fragment merged into settings.json |
| `container-context.md` | Injected into container's CLAUDE.md |
| `scaffold/` (in claude-sandbox repo) | Base bootstrap seed for `init` (sparse config.yaml, env, Dockerfile.example) |
| `scaffold-ralph/` (in claude-sandbox repo) | Ralph scaffolding seed for `init-ralph` (agent/ docs, scripts/ backlog tools) |
