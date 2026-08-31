---
name: backlog-yaml
description: Backlog YAML management via the backlog.py CLI tool. Auto-activates when working with backlog.yaml, story status changes, ticket creation, or querying stories. Trigger phrases include "backlog", "story status", "set status", "add ticket", "query stories", "next id", "validate backlog".
disable-model-invocation: false
allowed-tools: "Read, Bash, Glob, Grep"
---

# Backlog YAML Management

All backlog reads and writes MUST use `python3 .claude-sandbox/scripts/backlog/backlog.py` instead of direct YAML editing. This ensures round-trip YAML preservation (comments, ordering, formatting), schema validation, atomic writes, and `flock`-based locking with an atomic `--claim` (the tool locks `agent/backlog.lock`; earlier versions of this doc understated that).

**Interactive sessions should prefer the `work-items` skill (`wi`)** — one markdown file per
item in git. `backlog.yaml` remains authoritative for unattended ralph runs; the bridge is
`wi export --format backlog-yaml` before a run and `wi import --format backlog-yaml --update`
after it. Which store is authoritative long-term is an open decision recorded in the
context-guardrails series.

The tool is canonical in the claude-sandbox repo (`scaffold-ralph/scripts/backlog/`) and is seeded into a project by `claude-sandbox init-ralph`. If `.claude-sandbox/scripts/backlog/backlog.py` is missing, run `claude-sandbox init-ralph` (idempotent — it only fills gaps).

**Never edit `.claude-sandbox/agent/backlog.yaml` or `.claude-sandbox/agent/backlog_done.yaml` directly.** Always use the CLI tool.

**Sidecar commit SOP:** when the project's `.claude-sandbox/config.yaml` has `trackInHost: false`, the `.claude-sandbox/` dir is gitignored in the host repo and kept in an internal sidecar git repo. After grooming the backlog, PROMPT the user to commit the change in the sidecar (do not auto-commit): `git -C .claude-sandbox add -A && git -C .claude-sandbox commit -m "..."`.

See `references/cli-reference.md` for the full command reference with examples.

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
