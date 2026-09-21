# Work-item file format

One markdown file per item, managed by `scripts/wi.py`. The store is git; the
CLI adds locking, validation and budgeted views on top. Spec of record:
`agents/investigations/context-guardrails/threads/F-wi-spec.md`.

## Root resolver

`wi` finds its root in this order; `init` is the only command that creates it.

1. `$WI_ROOT` (or `--root PATH`) — worktree workers point this at the main
   checkout so claims are visible to each other.
2. `.claude-sandbox/work/` when `.claude-sandbox/` exists in the cwd.
3. `.work/` otherwise.

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
| `status` | `todo doing blocked parked grooming done dropped` | the only authority on state |
| `stage` | `implement review testing uat uat_feedback` | pipeline sub-state; meaningful only when `doing` |
| `priority` | int 0–4, 0 highest | default 2; ↔ backlog.yaml 90/70/50/30/10 |
| `tags` | flow list `[a, b]` | |
| `deps` | block list of ids or `ext: <text>` | structural "cannot start until"; `ext:` never resolves |
| `parent` | id | grouping only, no blocking |
| `owner` | free string, e.g. `user@host` | set by `claim`, cleared by `release`/`done` |
| `claimed` | UTC minute | stale test in `next --stale` |
| `blocked` | string | required iff `status: blocked`; kept while parked or grooming, so `unpark` / `ungroom` returns to `blocked` |
| `parked` | one line | required iff `status: parked`; the deferral reason (set by `park`, cleared by `unpark`, `block` and `groom`); `lint` flags it on a todo/doing/blocked/grooming item, and it stays on a dropped/done item as history |
| `grooming` | one line | required iff `status: grooming`; the open questions for the operator (set by `groom`, cleared by `ungroom`, `park` and `block`); `lint` flags it on a todo/doing/blocked/parked item, and it stays on a dropped/done item as history |
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

**Quoting.** A value is written bare unless wi would read it back
differently or a YAML loader would reject it — empty, leading/trailing
whitespace, `: ` or ` #` inside, a trailing `:`, brackets or braces, a leading
YAML indicator (`- ? : , # & * ! | > ' " % @` and backtick), a bare `—`, a
lone `=` or `<<`, a tab or other control character, or a comma inside a flow
list. YAML's implicit typing is left alone (`priority: 2` and dates stay
bare), so a YAML loader may read a bare `true`, `null` or `0x10` as a
non-string where wi reads a string.
A quoted value is a YAML double-quoted scalar: `\` and `"` are written as
`\\` and `\"`, tab as `\t`, and other control characters, DEL, C1,
U+2028/U+2029, the BOM, U+FFFE/U+FFFF and lone surrogates as `\xNN` /
`\uNNNN`. The reader decodes exactly those plus the other YAML escapes
(`\0 \/ \U…` and the rest), so a value survives any number of rewrites
byte-identical; an unknown escape, or one that would decode to a line break,
is kept as written. So in a hand-written quoted value a backslash is an
escape: write `"C:\\temp"`, not `"C:\temp"` (which holds a tab) — `lint`
reports any front-matter value holding a tab or other control character.
`wi` itself never writes one: a command given one exits 1 and writes nothing,
and `import` folds them to a space as it folds line breaks. A
single-quoted value reads `''` as `'`. A bare `—` or an empty value reads as
no value; a quoted `"—"` is the literal dash (`import` still reads a
backlog field that is `—`, such as `blocked_reason`, as no value).

Older `wi` versions escaped without unescaping, so every rewrite of a quoted
value added a layer of backslashes. `wi repair-escapes` finds them by a
heuristic — every front-matter value (quoted or not: the current writer
may have rewritten one bare) whose backslashes all pair as `\\` or `\"`,
with all such layers peeled — so it also lists a value meant that way: review
the dry run, narrow with `--id` / `--key`, then `--apply` (or fix one value
with `wi set`).

## Editing fields: `wi set <id> <field> <value>`

Sets exactly one front-matter field. `id` and `created` are immutable (exit 1).

- **List fields** (`tags`, `deps`, `refs`) take a comma-separated value —
  `wi set <id> deps a-1111,b-2222` — and are **replaced whole**, never
  appended to (`block --on` / `unblock --dep` add/remove a single dep).
- **Clearing**: the value `""` (or `—`) clears any field — there is no
  `--clear` flag: `wi set <id> deps ""`. (A `--clear` token is eaten by
  argparse regardless of quoting; it only passes as a value after a `--`
  separator.)
- **Validation**: `deps` and `parent` targets must resolve to existing items
  (archive included), exactly as `add --dep`/`--parent` requires — a dangling
  id exits 1, `ext: <text>` deps are exempt, and `--force` writes it anyway.
  An item can never be its own dep or parent — a self-reference exits 1 and
  `--force` does not bypass it. The item is then schema-validated as a whole;
  a value that breaks it (bad `status`, priority out of range, …) exits 3 and
  nothing is written.

## Parked

`parked` is deliberate deferral — "not now, on purpose" — where `blocked` is
"cannot proceed". `wi park <id> "<reason>"` sets `status: parked` and
`parked: <reason>`, releases any claim (`owner`, `claimed`, `stage`) and
appends a dated Notes line; it refuses a done or dropped item. A parked item
is never ready: `next` (every mode) leaves it out and counts it in its footer
and `counts.parked`; `prime` shows one `PARKED <n>` line, never a list and
never under BLOCKED; `ls` omits it by default and `ls --status parked` lists
it. A dep on a parked item does not resolve.

`wi unpark <id>` returns the item to `todo` — or to `blocked` when it still
carries a `blocked:` reason. It never returns to `doing`: the claim was
released on park, and whoever held it is not assumed to still be working it.
To abandon a parked item, `wi done <id> --drop`, then `wi archive` as usual.

`wi park` is the only way in. `wi set <id> status parked` exits 1 and points
at `park`, since set would record no reason and release no claim. `wi set <id>
status <other>` on a parked item counts as an unpark: the `parked:` reason is
cleared and a Notes line is added. `wi release` never unparks. On a parked
item it clears only `owner`/`claimed`/`stage`, so an agent cleaning up a
claim the operator has since parked leaves the park in place.

Before `parked` existed, deferral was spelled `wi block <id> "PARKED: …"`.
`wi migrate-parked` lists the `blocked` items whose reason starts with
`PARKED` (case-sensitive, a whole word) and what their parked reason would
be. `--apply` converts them: the parked reason is the text without the
prefix, `blocked:` is cleared, the claim is released, and a Notes line is
added. Nothing is written without `--apply`. The prefix is `PARKED`, then an
optional parenthesised group, then any `:`/`-`/`—` separator. The group is
provenance, not reason: `PARKED (operator 2026-09-19): Paseo undecided` parks
with reason `Paseo undecided`. The migration's Notes line keeps the whole
original reason, group included (`parked (migrated from blocked: PARKED
(operator 2026-09-19): Paseo undecided)`). A prefix with nothing after it
keeps the whole text as the reason.

The backlog-yaml bridge has no deferred state to map to: a parked item
exports as `status: blocked` with `blocked_reason: "PARKED: <reason>"`, and
importing a blocked story whose reason starts with `PARKED` yields a parked
item — the same prefix rule as `migrate-parked`. The park and its reason
round-trip. A `blocked:` reason kept under a park does not travel: the
export carries only `PARKED: <reason>`. `import --update` keeps the store's
own `blocked:` on a parked story, but a fresh import cannot restore it, so
that item's `unpark` goes to `todo`. A provenance group, if any, is dropped
from the imported reason. A ralph run over the exported backlog sees the
item as blocked, never as work.

## Grooming

`grooming` means the item waits on the operator's answers — it has open
questions, where `parked` is "not now" and `blocked` is "cannot proceed".
`wi groom <id> "<questions>"` sets `status: grooming` and `grooming:
<questions>` (one line), releases any claim (`owner`, `claimed`, `stage`),
clears a `parked:` reason and appends a dated Notes line; it refuses a done
or dropped item. `wi ungroom <id>` returns it to `todo` — or to `blocked`
when it still carries a `blocked:` reason — never to `doing`. The rest
mirrors Parked: `set status grooming` exits 1 and points at `groom`; `set
status <other>` on a grooming item is an ungroom; `release` never ungrooms;
`claim` refuses; `park` and `block` supersede it (and `groom` supersedes a
park).

A grooming item is never ready: `next` (every mode) leaves it out and
counts it in its footer and `counts.grooming`; `prime` shows one
`GROOMING <n>` line; a dep on it does not resolve. Unlike a parked item it
needs attention, so `ls` lists it by default. The backlog-yaml bridge maps
it as it maps a park: `status: blocked`, `blocked_reason: "GROOMING:
<questions>"`, and a blocked story with that prefix imports as grooming.

## Operator questions: `decision N:` / `answer N:`

The canonical marker for a question to the operator is a body line that
starts `decision N: <one line>`; the reply is a body line `answer N:
<reply>`, anywhere in the same item's body (the librarian-mode Report
convention). A decision is unanswered while its item has no `answer N:`
line with the same N. Both must start the line — `- decision 4:` is not a
marker — and a line inside a fenced code block is text, not a marker. N is
never reused across the store; a revised question keeps its number.

`wi needs-input` lists every open item awaiting the operator: each grooming
item (with its questions) and each unanswered `decision N:` (with N and its
text), on todo, doing, blocked, parked and grooming items alike; closed
items never show. `--plain` prints `id<TAB>grooming|decision<TAB>N or
-<TAB>text`; `--json` one record per item with `grooming` and `decisions`.
It exits 2 when nothing awaits the operator.

`wi prime` also shows a `HOLD <n>: <id> (<title>) …` line, first under the
header, for open items tagged `hold` — an operator hold gates what may move.

## Body sections

- untitled text before the first `##` — description; the first paragraph is
  the summary `show --brief` and `prime` print.
- `## Acceptance` — `- [ ]` / `- [x]` bullets; exported to `acceptance:`.
- `## Testing` — bullets, typically `command: …`; exported to `testing:`.
- `## Handoff` — four bullets `- doing: / - next: / - blocked: /
  - learned:` (`—` when empty). `wi handoff` rewrites only those four lines
  (the first of each key) and inserts any that are missing; required by `lint`
  when `status: doing`. Each value is one line (see below).
- `## Notes` — free text; the tool only appends dated lines, after the last
  non-blank line of the section (it adds `## Notes` at the end when absent).
- any other `## …` section round-trips untouched.

A section runs from its `## ` heading to the next `## ` heading, so unheaded
text after a block belongs to that block. A `## ` line inside a fenced code
block (```` ``` ```` or `~~~`) is text, not a heading. A fence opener with no
matching closer is not a fence: it does not hide the headings after it. An
unclosed opener can still pair with a later block's fence and hide the
headings between them. When `## Handoff` or `## Notes` then exists only
inside such a fence, followed there by another `## ` line, `handoff`,
`claim` and `done` exit 3 and write nothing rather than add a second
section: add a real heading outside the fence, or close the unclosed one.
A closed example holding only that heading is text; the section is added.
Every rewriting command edits the body in place: bytes outside the lines it
owns — trailing unheaded text, spacing between sections, section order, CRLF
line endings — are kept exactly. Front matter is re-emitted in canonical form.

Every value a command writes into front matter, a Handoff bullet or a Notes
line is one line. One containing a line break exits 1 and nothing is
written — for a command that writes several items, none of them. The
imports fold instead: `import-todo` folds a title wrapped across lines, and
`import --format backlog-yaml` collapses the whitespace of every story value
except `notes` (a `review_feedback: |` block scalar becomes one line).
Imported `notes` are markdown and land in the body as is: a `## Handoff`
line inside them becomes a real section, and one above the imported
`doing:`/`next:` lines shadows the imported Handoff.

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
item, managed by `wi` (the `work-items` plugin's
`skills/work-items/scripts/wi.py`).

- `wi prime` — what's next, in ≤300 tokens; start every session here
- `wi next` / `wi show <id> --brief` — pick and inspect an item
- `wi add "title"` / `wi claim` / `wi handoff` / `wi done` — the write verbs

Format and rules: the `work-items` plugin's
`skills/work-items/references/format.md`.
```
