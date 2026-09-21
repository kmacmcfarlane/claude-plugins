# The work-source provider interface

A *work source* is anything that can answer "what should I work on, and who has it?" —
today a `wi` store (this plugin) or a `backlog.yaml` (the `backlog-yaml` skill, canonical
tooling in the claude-sandbox repo). Tomorrow, plausibly a remote tracker reached over MCP.

**This document is the registry.** There is no JSON/YAML capability descriptor and nothing
mechanically reads a provider list. The reason is deliberate: in this ecosystem, skills
already are the discovery mechanism (an agent learns a provider exists by reading its skill
description), and remote providers self-describe through MCP's tool listing. A second,
machine-readable source of truth with zero mechanical readers would only drift. See
*Reserved: the `provider:` config key* and *Upgrade triggers* below for when that changes.

Rule for editing this file: **describe reality, not aspiration.** Every verb claimed for a
provider must exist in that provider's tool today. Remote providers are a *pattern* section,
explicitly not an implementation.

## The verb contract

Eight verbs. Everything else a provider offers is provider-local — useful, but not something
a consumer may assume.

| Verb | `wi` | `backlog.py` |
|---|---|---|
| `next` | `next` (ready-ranked); `next --pipeline --claim <worker>` for atomic claim-next | `next-work [--format json] [--claim]` |
| `claim` / release | `claim <id>` / `release <id>` | `next-work --claim`; release via `set <id> status todo` + `clear <id> claimed_by` |
| `show` | `show <id> [--brief] [--json]` | `get <id>` |
| `status` | `set <id> status <v>` / `set <id> stage <v>` (open states only — see `close`) | `set <id> status <v>` (open states only — see `close`) |
| `close` | `done <id> [--note <ref>]` / `done <id> --drop` | *policy, not a verb*: agents never set `status: done` — closure belongs to grooming (`/backlog-grooming`); `archive` then moves closed rows |
| `create` | `add "<title>" [-t -p --dep --parent --desc]` | `add` (heredoc), with `next-id <prefix>` |
| `handoff` / comment | `handoff <id> --doing --next [--blocked] [--learned]` | `set-text <id> <field>` (approximate) |
| `query` | `ls [--status --type --tag --owner --ready --json]`; `next --json` | `query --status … --fields …` |

### Per-verb semantics

- **`next` — ready-ranked, never "the whole list".** A provider returns work whose
  dependencies are satisfied, ranked; consumers take the head. Emptiness is a *normal*
  outcome, not an error: `wi next` exits **2** when nothing is ready, and the consumer's
  correct response is to report "nothing ready" and stop, not retry. The claim-fused form
  (`wi next --pipeline --claim`, `backlog.py next-work --claim`) is the only race-free way
  for concurrent workers to take work; both hold their lock across the select-and-write.
- **`claim` / release — atomicity is the whole point.** `wi claim` takes
  `flock(<root>/.lock)`, and re-claiming an item another owner holds exits **4** with the
  holder and age; `--steal` is the deliberate override. A consumer that sees 4 must stop,
  never force. Cross-machine atomicity is git's job, not the provider's. `backlog.py` flocks
  `agent/backlog.lock` and offers claiming only fused into `next-work --claim`.
- **`show` — one item, budgeted.** `--brief` (front matter + handoff) exists so a session can
  rehydrate one item without paying for the body. Consumers should prefer it.
- **`status` — set the canonical state**, per the mapping below. In `wi`, `status` and
  `stage` are two fields (`doing` + `review`); in `backlog.yaml` the pipeline stage is folded
  into the single `status` value. Immutable fields (`id`, `created`) reject with **1**.
  **`status` cannot close an item**: `wi set <id> status done` exits 3 (a closed item needs
  its closed date, which only `done` writes) — use `close`.
- **`close` — the only way to finish work, and providers differ on WHO may.** In `wi`,
  `done <id>` (optionally `--note <ref>` for the landing commit) or `done --drop`; the item
  file never moves. In `backlog.yaml` closure is a *human* act by policy — agents advance
  status through the pipeline but never to `done`; `/backlog-grooming` closes, `archive`
  sweeps. A consumer that finishes work on a backlog provider therefore ends at the last
  agent-legal status and reports, rather than closing.
- **`create` — describe, don't dump.** Ids are provider-shaped (`<slug>-<4hex>` in `wi`,
  `S-052`-style in backlog). Never assume an id format across providers.
- **`handoff` — the per-item residue**, written whenever an item is left mid-flight:
  what was being done, what is next, what blocks, what was learned. `wi` has a first-class
  Handoff block; `backlog.yaml` has no equivalent, and `set-text` into a text field is the
  closest approximation (see the capability table). A consumer must not assume handoff
  round-trips.
- **`query` — filtered projection**, ideally with a field selector so the result is small.
  Both providers offer JSON; consumers parsing prose output are doing it wrong.

### Exit-code conventions

The contract adopts `wi`'s codes (authoritative in `scripts/wi.py`'s module docstring):

| Code | Meaning | Consumer response |
|---|---|---|
| 0 | ok | proceed |
| 1 | usage / validation error | fix the call; do not retry unchanged |
| 2 | not found / empty | a *normal* answer for `next`/`query`; report and stop |
| 3 | file or parser error | the store is malformed or a dependency is missing; surface it |
| 4 | lock or claim conflict | someone else holds it — stop, never force |

A provider that cannot express all five maps onto the nearest; a consumer must at minimum
distinguish 0 / 2 / 4.

Two known deviations in `wi` itself, documented until fixed in code: **argparse-level usage
errors (unknown verb, wrong arity) exit 2**, colliding with not-found/empty — so a consumer
must not read exit 2 as "nothing ready" unless the call shape was known-good (stderr is
empty on a true empty `next`, and `--json` yields no output on usage errors); and
**item-schema validation on `add`/`set` (e.g. an invalid status value) exits 3, not 1** —
only immutable-field, unknown-field, and title-length rejections exit 1.

## Provider registry

### `wi` — this plugin

One markdown file per item under a store resolved `WI_ROOT` → `.claude-sandbox/work/` →
`.work/`. `status:` is the only authority on state; files never move on completion.
Mutations take `flock(<root>/.lock)` and write tmp+rename. Stdlib-only Python; the item file
format, resolver rule and secret rule are canonical in `references/format.md` — that file is
wi-provider detail, not part of this contract. Provider-local verbs beyond the contract:
`init`, `block`/`unblock`, `prime`, `import-todo`, `export`/`import`, `lint`, `archive`.

### `backlog.yaml` — via `backlog.py`

A single YAML file with round-trip-preserving edits, schema validation, atomic writes, and
`flock` on `agent/backlog.lock`. Lives in consuming repos at
`.claude-sandbox/scripts/backlog/backlog.py`; canonical in the claude-sandbox repo. This is
the provider unattended ralph runs use, because `next-work --claim` is atomic and its
validation (`validate --strict`) is enforceable in a loop. Provider-local verbs: `clear`,
`next-id`, `archive`, `validate`, `status` (store overview), `list-ids`.

### The bridge, and what it is not

`wi export/import --format backlog-yaml` syncs the two stores. It is a **sync mechanism, not
a contract verb** — a consumer never calls it as part of doing work. It is also the model for
principle 4 cooperation: it activates only when both stores are present and degrades silently
otherwise.

## Capability table

A consumer must degrade when a verb is absent — never assume.

| Capability | `wi` | `backlog.yaml` | Remote tracker (pattern) |
|---|---|---|---|
| `next` ready-ranked | yes (dependency-aware) | yes | usually (saved view / query) |
| atomic claim | yes (`flock`, exits 4 on conflict) | yes (`next-work --claim`) | **no** — assignee-set is not compare-and-swap; best-effort only |
| `show` brief form | yes (`--brief`) | partial (`get`, no budget mode) | varies |
| `status` with pipeline stage | yes (`status` + `stage`) | yes (folded into one field) | varies; map to the tracker's workflow states |
| `create` | yes | yes | yes |
| `handoff` block | yes (first-class) | approximate (`set-text` into a text field) | approximate (structured comment) |
| `query` with field selection | yes (`ls --json`) | yes (`query --fields`) | yes |
| dependency graph | yes (`deps`, `block --on`) | partial (`blocked_by`) | varies |
| unattended-safe | mechanically yes; ralph *policy* designates backlog.yaml (see the skill description) | yes (the ralph provider) | not without rate/auth handling |

## Canonical state model

`todo` · `doing` (with optional stage `implement` / `review` / `testing` / `uat` /
`uat_feedback`) · `blocked` · `done` · `dropped`.

The mapping between this model and `backlog.yaml` is not restated here — it is **executable
and canonical in `scripts/wi.py`**: `STATE_TO_BACKLOG`, `BACKLOG_TO_STATE`, and
`PRIO_TO_BACKLOG` (wi priority 0–4 → backlog 90/70/50/30/10). Note the asymmetry those tables
encode: `dropped` maps to backlog `closed`, and backlog `closed` maps back to `dropped` —
"closed" is not "done". A new provider adds its own mapping table in the same place, with the
same round-trip test discipline (`tests/test_wi.py` validates the export against
`backlog.py validate --strict` when reachable).

## How a remote provider slots in

Not implemented. This is the mapping pattern a future Linear / GitHub / GitLab / beads
provider would follow.

1. **Transport is MCP.** These trackers already reach agents as MCP servers, and MCP's tool
   listing *is* capability discovery — the server enumerates its tools and schemas at connect
   time. Do not build a bespoke registration mechanism for something the transport already
   provides.
2. **Map verb → tool**, roughly: `next` → a saved-view/query tool; `show` → get-issue;
   `create` → create-issue; `status` → update-issue with the tracker's workflow state;
   `query` → list/search issues; `claim` → set-assignee.
3. **`claim` degrades to best-effort.** Setting an assignee is a plain write, not a
   compare-and-swap: two agents can both "claim" the same issue and the last write wins. A
   remote provider must document claim as advisory and consumers must not rely on exit 4
   arriving. Where the tracker offers optimistic concurrency (a version/ETag), use it.
4. **`handoff` maps to a structured comment** — one comment with the doing/next/blocked/
   learned fields under stable headings, so it can be found and rewritten rather than
   appended forever. There is no remote equivalent of a rewritable handoff block.
5. **State mapping is the real work.** Every tracker has its own workflow states; the
   canonical five-state model above is what they must be projected onto, and that projection
   is design work, per tracker, in prose plus a mapping table — not schema work.

## Reserved: the `provider:` config key

**Sketched, not implemented. Nothing reads this today; do not write it.**

The one consumer that cannot read prose is a future mechanical selector (the ralph shim
picking a provider without an LLM in the loop). It needs exactly one datum — *which provider
is active in this repo* — which is a config key, not a registry:

```yaml
# reserved shape, unimplemented
provider: wi        # or: backlog-yaml
```

Reserved so a future implementation has a stable name and landing spot: one key, one scalar,
in the repo's work config. Capability *descriptors* are deliberately not reserved — if they
are ever needed, they belong in an appendix of this file first.

## Upgrade triggers

Revisit doc-first when **any one** of these happens:

1. **A third provider lands** (beads, Linear, or another) — three providers is where the
   capability differences stop fitting in one table's worth of prose.
2. **A second non-LLM consumer** needs provider selection or capability checks — one shim
   justifies one config key; two mechanical readers justify a schema.
3. **A real bug traces to an agent assuming a capability a provider lacks** — evidence that
   prose is not carrying the contract.

Until then, machine-readability would be a second source of truth with nothing to read it.
