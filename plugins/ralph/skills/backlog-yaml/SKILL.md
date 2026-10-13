---
name: backlog-yaml
description: Backlog YAML management via the backlog.py CLI tool. Auto-activates when working with backlog.yaml, story status changes, ticket creation, or querying stories. Trigger phrases include "backlog", "story status", "set status", "add ticket", "query stories", "next id", "validate backlog".
disable-model-invocation: false
allowed-tools: "Read, Bash, Glob, Grep"
argument-hint: "[optional backlog.py subcommand or question]"
---

# Backlog YAML Management

All backlog reads and writes MUST use `python3 .claude-sandbox/scripts/backlog/backlog.py` instead of direct YAML editing. This ensures round-trip YAML preservation (comments, ordering, formatting), schema validation, atomic writes, and `flock`-based locking with an atomic `--claim` (the tool locks `agent/backlog.lock`; earlier versions of this doc understated that).

**Interactive sessions should prefer the `work-items` skill (`wi`)** — one markdown file per
item in git. `backlog.yaml` is the **default work-source provider for unattended ralph
runs**, because `next-work --claim` is atomic and `validate --strict` is enforceable in a
loop. The verb contract it implements — and the exit-code and canonical-state conventions a
consumer must honour — is the work-source provider interface documented in the `work-items`
plugin; read that document, through the `work-items` skill when it is listed, before writing
anything that drives a backlog from a loop. Without `work-items` that document is not on this
machine: the contract here is then `references/cli-reference.md` and the rules below. Two
things that document settles and this one does not: closure is a *policy*
difference, not a verb (agents advance status but never set `status: done` — see
`/backlog-grooming`), and the contract reserves a `provider:` config key for future
mechanical provider selection, which is **sketched and unimplemented — nothing reads it, do
not write it**. The bridge to `wi` is `wi export --format backlog-yaml` before a run and
`wi import --format backlog-yaml --update` after it.

**Reaching `wi`.** `wi` is not on `PATH`: it is a script in the `work-items` plugin, found
from the repo's own tree when it carries that plugin, else from the installed copy. This is
ralph's one copy of the lookup; run it before either bridge command:

```bash
MAIN=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) && MAIN=${MAIN%/.git} || MAIN=$PWD
for d in "$MAIN/.claude-sandbox/work" "$MAIN/.work"; do test -d "$d/items" && { export WI_ROOT="$d"; break; }; done
WI_PY=$(ls "$MAIN"/plugins/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)
P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"
IP="$(python3 -I - "$P/installed_plugins.json" work-items@kmacmcfarlane "$MAIN" 2>/dev/null <<'PY'
import json, os, sys
es = json.load(open(sys.argv[1]))["plugins"][sys.argv[2]]
here = os.path.realpath(sys.argv[3])
def rank(e):  # the install that applies here: deepest local/project path, then user
    pp = e.get("projectPath")
    if e.get("scope") in ("local", "project") and pp:
        pp = os.path.realpath(pp)
        if here == pp or here.startswith(pp.rstrip("/") + "/"):
            return (2, len(pp), e["scope"] == "local")
    return (1, 0, False) if e.get("scope") == "user" else (0, 0, False)
best = max(es, key=rank)
print(best["installPath"] if rank(best)[0] else "")
PY
)"
test -n "$WI_PY" || WI_PY="$IP/skills/work-items/scripts/wi.py"
test -f "$WI_PY" || WI_PY=$(ls -t "$P"/cache/kmacmcfarlane/work-items/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)
if test -f "$WI_PY"; then WI="python3 $WI_PY"; echo "$WI"; else WI=no-wi-found; echo "no wi found"; fi
```

Then `$WI export --format backlog-yaml` and `$WI import --format backlog-yaml --update`, in
the same Bash call (shell variables do not outlive one), or with the printed command. `WI` is
bound to `python3` only when the file exists, so a miss never runs a bare `python3`; a `$WI`
call run anyway fails with exit 127. The install-record read runs `python3 -I`, so a
`json.py` in the working directory is never imported. The install record holds one entry
per install scope, so the read takes the entry that applies to this repo, never the first
listed: a `local` or `project` entry whose `projectPath` is the main checkout or a
directory above it (the deepest, `local` before `project`), else the `user` entry; another
project's install never answers. On `no wi found`, run neither command and say that the
work items and `backlog.yaml` were not synced because `work-items` is not installed. No
store (no `WI_ROOT` exported) means there is nothing to bridge.

The tool is canonical in the claude-sandbox repo (`scaffold-ralph/scripts/backlog/`) and is seeded into a project by `claude-sandbox init-ralph`. If `.claude-sandbox/scripts/backlog/backlog.py` is missing, run `claude-sandbox init-ralph` (idempotent — it only fills gaps).

**Never edit `.claude-sandbox/agent/backlog.yaml` or `.claude-sandbox/agent/backlog_done.yaml` directly.** Always use the CLI tool.

**Sidecar commit SOP:** when the project's `.claude-sandbox/config.yaml` has `trackInHost: false`, the `.claude-sandbox/` dir is gitignored in the host repo and kept in an internal sidecar git repo. After grooming the backlog, PROMPT the user to commit the change in the sidecar (do not auto-commit): `git -C .claude-sandbox add -A && git -C .claude-sandbox commit -m "..."`.

See `references/cli-reference.md` for the full command reference with examples.

## Worktree-Run Contract (ralph)

Unattended ralph runs execute in a single Claude Code worktree per run (`.claude/worktrees/<name>` on branch `worktree-<name>`), reopened every iteration. The contract:

- **No per-story branches.** Every story is committed on the run branch. The legacy conventions — `story/<id>` branches, `.worktrees/<id>` per-story worktrees, the `scripts/worktree/` helper — are retired (migration recipe: claude-sandbox `docs/MIGRATION.md`).
- **Ralph never merges.** The run branch `worktree-<name>` is the deliverable; a human reviews it and fast-forwards `main` from it (`git merge --ff-only worktree-<name>`) or opens a PR. `uat` means "on the run branch".
- **`base_sha`** (optional story field): the commit the story's work started from — HEAD when the story entered `in_progress`. `next-work --claim` records it atomically with the claim, and the orchestrator records a fresh one on every entry to `in_progress` (from `todo` or `uat_feedback`) via `set <id> base_sha "$(git rev-parse HEAD)"`.
- **Review/QA context is `git diff <base_sha>`** (working tree against the story's base) — never `git diff main`, which after the first story would include every earlier, already-reviewed story on the run branch. A story with no `base_sha` (claimed before the field existed): record one now — the last commit on the branch that is not this story's — and proceed.
- **Developer briefs carry the base line** `**Base**: <base_sha> (work on the current branch; do not create branches or merge)`.
- **`.claude-sandbox/` lives in the main checkout** and is gitignored, so it does not exist inside the worktree. Claude Code blocks the Edit/Write/NotebookEdit tools against the main checkout from inside a worktree, so all writes to `.claude-sandbox/` (backlog mutations via `backlog.py`, stop files, ideas/, QUESTIONS.md) go through Bash. UNVERIFIED (pending a live ralph run): whether such Bash writes from the worktree into the gitignored sidecar pass the harness guard.

## Quick Reference

```bash
# Query stories by status
python3 .claude-sandbox/scripts/backlog/backlog.py query --status todo --fields id,title,priority

# Dependency-aware status overview
python3 .claude-sandbox/scripts/backlog/backlog.py status

# Query with blocked_by virtual field
python3 .claude-sandbox/scripts/backlog/backlog.py query --status todo --fields id,title,blocked_by

# Select next eligible work (deterministic algorithm)
python3 .claude-sandbox/scripts/backlog/backlog.py next-work --format json

# Atomically claim it: sets status=in_progress, claimed_by, base_sha=HEAD
python3 .claude-sandbox/scripts/backlog/backlog.py next-work --claim worker-1 --format json

# Record a story's base commit on (re-)entry to in_progress
python3 .claude-sandbox/scripts/backlog/backlog.py set S-052 base_sha "$(git rev-parse HEAD)"

# Get a single story
python3 .claude-sandbox/scripts/backlog/backlog.py get S-052

# Set a scalar field
python3 .claude-sandbox/scripts/backlog/backlog.py set S-052 status in_progress
python3 .claude-sandbox/scripts/backlog/backlog.py set S-052 ticket_mode mixed

# Set a text field from stdin
echo "Changes requested: missing null guard" | python3 .claude-sandbox/scripts/backlog/backlog.py set-text S-052 review_feedback

# Clear an optional field
python3 .claude-sandbox/scripts/backlog/backlog.py clear S-052 review_feedback

# Get next available ID
python3 .claude-sandbox/scripts/backlog/backlog.py next-id B

# Add a new story from stdin
cat <<'EOF' | python3 .claude-sandbox/scripts/backlog/backlog.py add
- id: B-038
  title: "Grid flicker on resize"
  priority: 70
  status: todo
  complexity: medium
  requires: []
  acceptance:
    - "FE: Grid does not flicker during window resize"
  testing:
    - "command: cd frontend && npx vitest run"
EOF

# Archive a story to backlog_done.yaml
python3 .claude-sandbox/scripts/backlog/backlog.py archive S-001

# Validate the backlog
python3 .claude-sandbox/scripts/backlog/backlog.py validate --strict
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation error (invalid field value, schema violation) |
| 2 | Story not found |
| 3 | File error (cannot read/write) |

## Important Rules

- New stories always get `status: todo`
- IDs are globally unique across both `backlog.yaml` and `backlog_done.yaml`
- The `complexity` field (`low`, `medium`, `high`) is required for new entries
- Agents never set `status: done` — only users via `/backlog-grooming`
- All mutations validate before writing — invalid data is never persisted
- `ticket_mode` controls dispatch: `autonomous` (default/omitted), `interactive`, `mixed`
- Interactive AC in mixed-mode stories are prefixed with `[INTERACTIVE]`
