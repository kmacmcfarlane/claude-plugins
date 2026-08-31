---
name: work-items
description: Repo-durable work items via the `wi` CLI — one markdown file per item in `.work/` (or `.claude-sandbox/work/`), with ready-ranking, claims, handoff blocks, TODO.md import, and a backlog-yaml bridge. Auto-activates when a repo has a work-item store, or when the user says "what's next", "work item", "next task", "claim it", "hand it off", "mark it done", or asks to migrate a TODO.md. Not for unattended ralph runs (backlog-yaml owns those).
disable-model-invocation: false
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
argument-hint: [next | show <id> | add | done <id> | import-todo <path>]
---

# Work items

Work items live in git — one markdown file each, `status:` authoritative, never moved on
completion — so they survive machines, sessions and collaborators, merge cleanly, and cost
tokens only one item at a time. The whole-file `TODO.md` read this replaces cost ~12K tokens
per read; `wi next` costs ~300–500. The file format, resolver rule, deprecation-notice
template and secret rule are canonical in `references/format.md` — read it before editing an
item file by hand; this file does not restate it.

```bash
WI="python3 ${CLAUDE_PLUGIN_ROOT}/skills/work-items/scripts/wi.py"
```

## Session-start rule

`$WI prime` (≤300 tokens: what's in flight, what's ready) — then `$WI show <id> --brief` for
the **one** item being worked. Never `ls` the whole store into context to pick a task; that is
the TODO.md failure mode with extra steps.

## The verbs

| | |
| --- | --- |
| `$WI next [--plain\|--json]` | ready-ranked queue: `todo` with all deps done, priority then age |
| `$WI show <id> [--brief]` | one item; `--brief` for front matter + handoff only |
| `$WI add "Title here" -p 2 -t task --desc "…" [--ref path]` | new item (`<slug>-<4hex>` id); **title is positional** — describe, don't dump; path and key, never value |
| `$WI claim <id>` / `release <id>` | atomic; a stale `claimed:` shows up in `next` |
| `$WI handoff <id> --doing … --next … [--blocked …] [--learned …]` | the per-item residue — write it whenever the item is left mid-flight |
| `$WI done <id> [--note <sha>]` / `done --drop` | closes it in place; `implement` Step 10a½ owns this on landed work |
| `$WI block <id> "reason"` / `--on <dep-id>` / `unblock` | runtime vs dependency blocks |
| `$WI import-todo TODO.md` | idempotent migration; then replace TODO.md with the deprecation notice from `references/format.md` |
| `$WI export/import --format backlog-yaml` | the ralph bridge — backlog.yaml stays authoritative for unattended runs |
| `$WI lint` | format + secret-shape check; run before committing hand edits |
| `$WI archive` | moves closed items to `archive/` — its own commit, nothing else in it |

Exit codes: 0 ok · 1 error · 2 empty (e.g. `next` with nothing ready — report "nothing
ready", don't retry) · 3 validation · 4 lock/claim conflict (someone else holds it — stop,
don't force).

## Rules

- The store is resolved `WI_ROOT` → `.claude-sandbox/work/` → `./.work/`; create only via
  `$WI init`, and only when the user asks for the store.
- Item files are hand-editable; run `$WI lint` after hand edits, in the same turn.
- One session claims an item before working it; two sessions on one item is what `claim` is
  for — respect a conflict.
- Migration of a repo's TODO.md is a reviewed, committed change (import → review items →
  write notice → commit), never a drive-by.
