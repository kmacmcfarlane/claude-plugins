# Work-item file format

One markdown file per item, managed by `scripts/wi.py`. The store is git; the
CLI adds locking, validation and budgeted views on top. Spec of record:
`agents/investigations/context-guardrails/threads/F-wi-spec.md`.

## Root resolver

`wi` finds its root in this order; `init` is the only command that creates it.

1. `$WI_ROOT` (or `--root PATH`) — worktree workers point this at the main
   checkout so claims are visible to each other.
2. `.claude-sandbox/work/` when `.claude-sandbox/` exists in the cwd.
3. `./.work/` otherwise.

```
<root>/
  README.md            what this is, in ten lines
  items/<id>.md        every item, regardless of status
  archive/YYYY/<id>.md closed items moved by `wi archive` (explicit, batched)
  .lock                gitignored; flock target for same-machine mutations
```

`status:` is the only authority on state. `done` never moves a file — a
status-only close is a two-line front-matter change that merges cleanly
against any body edit. `wi archive --older-than 90d` moves closed items in a
dedicated commit.

## Example item

```markdown
---
id: repl3-retention-7f2a
title: Replication task 3 destination retention is a no-op
type: bug
status: doing
stage: implement
priority: 1
tags: [zfs, replication]
deps:
  - snapshot-cleanup-3c1d
owner: kyle@hooper
claimed: 2026-08-30T14:02Z
created: 2026-08-05
updated: 2026-08-30
refs:
  - plans/2026-08-05-snapshot-retention-reduction.md
---

zettarepl's target-side retention is driven only by naming schemas, so task
3's `retention_policy: SOURCE` parses zero destination snapshots.

## Acceptance
- [ ] two hourly runs later, brainboy shows pruning

## Handoff
- doing: applying the midclt call on a test dataset first
- next: verify zettarepl prunes after two runs, then apply to task 3
- blocked: —
- learned: retention_policy SOURCE parses zero snapshots under name_regex

## Notes
- 2026-08-30 claimed by kyle@hooper
```

## Front-matter fields

Emitted in this order, one field per line. Dates are date-only (`YYYY-MM-DD`)
except `claimed` (ISO-8601 UTC to the minute).

| Field | Type | Notes |
|---|---|---|
| `id` | `<slug>-<4hex>` | equals the filename stem; immutable; hash suffix from title+time+random so branches never collide |
| `title` | one line, ≤120 chars | |
| `type` | `task bug feature refactor workflow chore epic spike` | default `task`; drives backlog-yaml prefix and bugs-first |
| `status` | `todo doing blocked done dropped` | the only authority on state |
| `stage` | `implement review testing uat uat_feedback` | pipeline sub-state; meaningful only when `doing` |
| `priority` | int 0–4, 0 highest | default 2; ↔ backlog.yaml 90/70/50/30/10 |
| `tags` | flow list `[a, b]` | |
| `deps` | block list of ids or `ext: <text>` | structural "cannot start until"; `ext:` never resolves |
| `parent` | id | grouping only, no blocking |
| `owner` | free string, e.g. `user@host` | set by `claim`, cleared by `release`/`done` |
| `claimed` | UTC minute | stale test in `next --stale` |
| `blocked` | string | required iff `status: blocked` |
| `feedback` | one line | pipeline review feedback |
| `mode` | `autonomous interactive mixed` | backlog's `ticket_mode` |
| `complexity` | `low medium high` | pass-through |
| `alias` | `[SBRWM]-NNN` | allocated on first backlog-yaml export, never reused |
| `created` / `updated` / `closed` | date | `closed` required iff done/dropped |
| `refs` | block list of paths / URLs / `wi:<id>` / `todo:<hash>` | TOC to detail; never read by `wi` |
| `x_backlog` | one-level map of scalars | opaque backlog.yaml passthrough |

The grammar is a strict YAML subset: `key: value` scalars, one-line flow
lists, block lists of scalars, one level of map for `x_backlog`. No multi-line
scalars, anchors or nesting — prose goes in the body. `lint` reports any line
that does not parse, and `wi` never rewrites a file it could not parse.

## Body sections

- untitled text before the first `##` — description; the first paragraph is
  the summary `show --brief` and `prime` print.
- `## Acceptance` — `- [ ]` / `- [x]` bullets; exported to `acceptance:`.
- `## Testing` — bullets, typically `command: …`; exported to `testing:`.
- `## Handoff` — exactly four bullets `- doing: / - next: / - blocked: /
  - learned:` (`—` when empty). Rewritten whole by `wi handoff`; required by
  `lint` when `status: doing`.
- `## Notes` — free text; the tool only appends dated lines.
- any other `## …` section round-trips untouched.

## Session-start rule

Read `wi prime` (≤300 tokens) and nothing else from the root. Then
`wi show <id> --brief` for the one item you will work. Open a `ref` only when
the Handoff's `next:` needs it. Never `cat` the items directory. Hand off with
`wi handoff <id> --doing … --next …` at every stop, `wi done --note` to close.

## Secret rule

Item files are tracked forever in git: record **the path and the key, never
the value**. Write `creds: clusterenv.yaml key DISCORD_WEBHOOK_BACKUPS`, not
the webhook URL. `wi lint` flags PEM blocks, `KEY=value` assignments and
`token/secret/password/webhook`-style pairs that look like live values.

## TODO.md deprecation notice

After `wi import-todo TODO.md`, replace the file's contents with:

```markdown
# TODO — moved

Work items now live in `.work/` (or `.claude-sandbox/work/`), one file per
item, managed by `wi` (claude-kit `skills/work-items/scripts/wi.py`).

- `wi prime` — what's next, in ≤300 tokens; start every session here
- `wi next` / `wi show <id> --brief` — pick and inspect an item
- `wi add "title"` / `wi claim` / `wi handoff` / `wi done` — the write verbs

Format and rules: claude-kit `skills/work-items/references/format.md`.
```
