# claude-plugins

**Tools for humans and agents to address common problems with using an LLM harness to
develop code.**

This repository is a Claude Code plugin marketplace. The marketplace itself is the kit —
there is no single kitchen-sink plugin. Each plugin is named for an *aim*: the answer to a
problem a user would state out loud ("I keep losing context", "I want unattended runs", "I
want a plan before I code"). Install the ones that match your problems; leave the rest.

The marketplace was refactored out of one history-indexed plugin (`claude-kit`) into
aim-named, standalone-installable plugins; that plugin no longer exists. **The catalog below
is the current state** — every row in it exists on disk today. If you are upgrading from
`claude-kit`, see [Migrating from `claude-kit`](#migrating-from-claude-kit).

## Families

Three product families, named provisionally pending review:

| Family | What it is | Where it lives |
|---|---|---|
| **Harness capabilities** | Plugins that shape the development loop itself; may register hooks, a status line, or settings | This marketplace (`kmacmcfarlane/claude-plugins`) |
| **Expertise packs** | Pure knowledge — make Claude good at stack X. No hooks, ever | A second marketplace, `expertise` (repo `claude-expertise`) — **local scaffold, remote pending** |
| **Webui chat skills** | Skills for LLM chat sessions in web UIs, not for a coding harness | The `chat` plugin — **family home under review** |

The cleanest way to say the split: **harness plugins** shape the loop and may alter harness
behavior; **content plugins** are knowledge only. The harness-behavior quarantine
(principle 3) then holds structurally, because a content marketplace simply never ships
hooks.

## The doctrine

These seven principles are the ruler every plugin in this marketplace is measured against.
**This section is the canonical statement** — do not restate the principles elsewhere in the
repo; link here.

1. **One plugin, one aim.** The description completes "install this if you want ___" in one
   clause. If it needs an "and", it is two plugins.
2. **Standalone test.** Every plugin is independently installable and useful with nothing
   else from the marketplace present — except the hard dependencies it declares in
   `plugin.json` (principle 4), which count as part of the install because the framework
   brings them. The test is applied to the plugin plus its declared hard dependencies.
   Whatever fails that test lives *inside* the plugin whose aim it serves.
3. **Harness-behavior quarantine.** Hooks, status lines, and settings writes belong only in a
   plugin whose stated aim *is* that behavior. Knowledge skills never carry hooks as
   passengers.
4. **Dependencies: soft by default, declared, directional — hard only when it cannot be
   otherwise.** A dependency degrades gracefully when the other side is absent (the
   work-items ↔ backlog bridge is the model), is declared in the plugin description and the
   catalog, and points at a named support plugin or an external repo. The one exception is
   a **hard** dependency, which the framework installs with the dependent and without which
   it disables the dependent. A plugin may declare one only when it has no function at all
   without the other, the edge stays within this marketplace, the declaration is in its
   `plugin.json` `dependencies` (never its `marketplace.json` entry, which the framework
   also reads), and the catalog marks it (hard). A plugin that merely reads another's data
   is never hard: it keeps a fallback, because a hard edge would switch it off whenever the
   support plugin is off. Never undocumented peer prose-coupling.
5. **Names are API.** Names end up in plugin data dirs, absolute paths inside `settings.json`,
   hook state dirs, and muscle memory. Choose for decades. See *Naming practices* below.
6. **New aim → new plugin.** Never stretch an existing description to cover something new.
   Small is fine; incoherent is not.
7. **The catalog is the front door.** This README carries the problem-indexed catalog
   (aim → plugin → depends-on) and the contributor decision tree, and every change to the
   shape of the marketplace updates it in the same commit.

## Catalog

Problem-indexed. **Status is load-bearing:** *current* rows exist on disk today and are
installable from this marketplace; *moved* rows live in the expertise marketplace, not here.
Names are **provisional** pending operator review.

**Depends on** uses one notation (principle 4). **(hard)** — declared in the dependent's
`plugin.json` `dependencies` (never its `marketplace.json` entry): installing the dependent
installs it, and the dependent is disabled without it. **(soft; …)** — not declared; the
dependent degrades when it is absent, and the note says what it gains when present.
**(external)** — a tool or repo outside this marketplace, named in the plugin description,
never declared. Every (hard) in this column is declared in `plugin.json`, and every declared
dependency is marked (hard) here.

| Aim — "install this if you want…" | Plugin | Status | Depends on |
|---|---|---|---|
| …project context for the `ai-scripts` Python CLI utilities | `ai-scripts` | **moved** to the expertise marketplace (local scaffold, remote pending) | — |
| …structured product research in a web chat session | `chat` | current; *family home under review* | — |
| …to survive the finite context window (gate, checkpoint, rehydration, token-spend report) | `context-guard` | **current** | `statusline-hub` (soft; exact depth from the sensor record it writes, when it owns the status-line slot or tees from another renderer; installing `statusline` brings it) |
| …an always-on status line (context left — the session's and each sub-agent's, in the agent panel — plan usage, model, session name) | `statusline` | **current** | `statusline-hub` (hard; the hub owns the status-line slot, and the footer draws as one of its display hooks), `context-guard` (soft; epoch and checkpoint thresholds in the gauge when installed) |
| …to share the status-line slot, so the data Claude Code hands the status line reaches the tools that read it whatever renders the line (the hub owns the slot and runs the hooks other plugins register, or its `tee` feeds the record from another renderer) | `statusline-hub` | **current** | `statusline` (soft; its footer is the hub's first display hook, and the hub takes over a slot an earlier `statusline` version installed once that footer has registered) |
| …a plan before you code: investigate → reviewed plan → verified implementation, research that lands as sourced findings or a curated knowledge base, and a standing librarian that takes custody of a repo's work (files, dispatches, reviews, lands) | `dev-flow` | **current** | `work-items` (soft; `librarian-mode` and `dev-cycle` find `wi` via the repo tree, or the installed plugin's copy; `dev-cycle` runs without it on a scratchpad record), `statusline-hub` (soft; the fable fallback in `librarian-mode` and `dev-cycle` reads rate-limit reset times from the sensor record it writes, and the `research` skills read its usage windows to size a run; installing `statusline` brings it), `context-guard` (soft; `investigate` offers a checkpoint-then-implement path when its checkpoint skill is present; `librarian-mode` answers its gate advisories with a checkpoint and weighs its manifest and ledger when it rehydrates; the fable fallback reads reset times from its older state record), `kit-dev` (soft; the `investigate` and `implement` retrospectives hand findings to its user-invoked `update-kit`; without it the findings stand as the record) |
| …repo-durable work items and a pluggable work source | `work-items` | **current** | — |
| …isolated execution for agent sessions (containers, and the checkout/worktree convention) | `sandbox` | **current** | claude-sandbox repo (external) |
| …unattended agent loops over a backlog ("ralph") | `ralph` | **current** | claude-sandbox repo (external; its `init-ralph` seeds `backlog.py`, and the loops run in its containers), `sandbox` (soft; its skill bootstraps and troubleshoots those containers), `work-items` (soft; the `wi` ↔ `backlog.yaml` bridge, when both stores are present) |
| …to start a new repo for a thread of work, with an agent session launched on it | `create-repo` | **current** | claude-sandbox repo (external; `init` bootstraps the repo's `.claude-sandbox/` and the launch command runs the session in its container; without it the repo is created all the same and the command is plain `claude`), `kit-dev` (soft; `new-project-from-template` scaffolds a claude-templates template as the goal), `sandbox` (soft; its skill troubleshoots an `init` or launch that fails), `dev-flow` (soft; the launched session runs the first investigation with its `investigate` skill when installed, and investigates directly without it) |
| …to maintain this kit itself (skill authoring, upstream sync, templates) | `kit-dev` | **current** | claude-templates repo (external; `new-project-from-template` scaffolds from it, `update-kit` syncs to it), claude-sandbox repo (external; `new-project-from-template` bootstraps with its `init-ralph`, `update-kit` syncs to it), claude-expertise repo (external; `update-kit` syncs to it), `create-repo` (soft; `new-project-from-template` points at it for a bare repo with a session launched on it) |
| …to make Claude good at a specific stack (Goa, Playwright, musubi-tuner, …) | one plugin per stack | **moved** to the expertise marketplace (local scaffold, remote pending) | — |

Retired: the deprecated plan-execution skill and the three sub-agent definitions used only by
it (Phase 3); the `claude-kit` plugin itself (Phase 6) — its skills are in `kit-dev` and the
other rows above.

Moved out of this marketplace at Phase 2: `goa`, `playwright`, `musubi-tuner` and the
`ai-scripts` plugin, into the `expertise` marketplace (repo `claude-expertise`). That repo
exists as a **local scaffold only** — no remote is configured yet, so the four are not
installable from anywhere until the remote lands.

## Where does a new thing go?

The contributor decision tree. Answer in order; the first match wins.

1. **Does it alter harness behavior?** Hooks, a status line, `settings.json` writes,
   background state. → It belongs *only* in a plugin whose stated aim is that behavior
   (today `context-guard` for the context system, `statusline` for the status line's
   footer and the agent panel's sub-agent rows (`subagentStatusLine`), `statusline-hub`
   for the status-line slot and its setting, `sandbox` for the checkout/worktree guard).
   Never bolt it onto a knowledge skill (principle 3).
2. **Is it pure stack/tool knowledge** — "make Claude good at X"? → Expertise family, which
   now lives in its own marketplace (`expertise`, repo `claude-expertise`) — not this repo.
   No hooks, no settings.
3. **Is it for LLM chat sessions in a web UI, not a coding harness?** → the `chat` family
   (home under review).
4. **Otherwise, it is a harness capability.** Find the aim it serves in the placement table
   in [CLAUDE.md](CLAUDE.md) and add it to that plugin's current home.
5. **No existing aim fits?** New aim → new plugin (principle 6). Do not stretch a
   description. Write the catalog row first — if you cannot write the one-clause aim, the
   thing is not yet one plugin.

Every plugin in the aim→home table now exists on disk, so the home the table names is the
home you write to. If a future phase ever plans a move again, write to the **current** home
until that phase lands — a planned destination is never a place to put files today.

Cross-plugin cooperation follows principle 4. The work-items ↔ backlog bridge (activates
only when both stores are present, degrades silently otherwise) is the pattern to copy.

## Naming practices

Folded in from the naming research lane (2026-09-02).

### Rules

1. **Aim-named.** The name completes "install this if you want ___" — the aim, not the
   implementation (`context-guard`, not `hooks-bundle`). Marketplaces are named for their
   family, not their host.
2. **kebab-case, short, sayable.** Two words where possible. It must survive being said
   aloud in "install X" and typed into a `/plugin` search.
3. **No redundant `claude-` prefix** on plugin names — everything here is for Claude, so the
   prefix carries zero bits inside a marketplace. Repo names may carry it for GitHub
   discoverability (`claude-plugins`).
4. **Never reuse a retired name for a different aim.** Data dirs and muscle memory outlive
   the retirement.
5. **Prefer the operator's established term over an abstract synonym** when the audience is
   this ecosystem's users (`ralph` over `autonomy`; `work-items` over `work`).

### Why names are API here

Rename cost, worst first:

| Identifier | Embeds into | Rename cost |
|---|---|---|
| marketplace `name` in `.claude-plugin/marketplace.json` (`kmacmcfarlane`) | every plugin-data dir, as the suffix in `<plugin>-<marketplace>` | **FROZEN — never rename.** Every plugin's data dir, and every absolute path written from one, breaks at once |
| plugin name | `plugins/data/<plugin>-<marketplace>/`, absolute paths written into `settings.json`, hook state dirs | High — e.g. a status line entry points at a plugin-data path that a rename orphans |
| repo name / marketplace add-URL | each machine's marketplace registration | Medium — GitHub redirects renamed repos; re-adding is one command |
| skill name | prose references and `/name` muscle memory | Low |
| files inside a plugin | nothing external, when a stable-path symlink mediates | Cheapest |

**The marketplace `name` field `kmacmcfarlane` is frozen.** It suffixes every plugin-data
directory. Nothing in this repo may propose changing it.

### Renaming a plugin, when it must happen

1. Add the new-name plugin to `marketplace.json`; the old entry stays for one release.
2. Ship a legacy migration on `SessionStart`: detect the old data dir or marker, rewrite any
   settings entries the plugin owns, create fresh symlinks.
3. Dual-read old state dirs for a transition window; write only to the new ones.
4. Per machine: install the new plugin, start one session so the migration fires, verify,
   then uninstall the old one.
5. Delete the old marketplace entry the following release.

### Current name status

The plugin names above (`context-guard` — shipped at Phase 1, its data dir and settings path
now live state; `dev-flow` — shipped at Phase 3, no state of its own; `work-items` — shipped
at Phase 4, no state of its own, though `wi` stores in consuming repos are not affected by a
rename; `statusline` — shipped with item 3c48, its data dir and settings path live state from
first install; `sandbox`, `ralph`, `kit-dev`, `create-repo`), the second marketplace's working name (`expertise` / repo
`claude-expertise`), and the `chat` family's home are **provisional**, adopted so work can
proceed, and confirmable or changeable at operator review. Names that have shipped state
(a data dir, a settings path) are changed only via the rename procedure above.

`statusline-hub` is **confirmed** by the operator, not provisional: the dispatcher puts it
into a data dir and the `statusLine` command path, so it was chosen once, before it shipped.
Since owner mode (F2) those are live state, as is its registry path
(`~/.claude/statusline-hub/hooks.d/`), which other plugins write to.

## Plugins today

What is installable from this marketplace right now.

### kit-dev

Maintainer tooling for this ecosystem itself — authoring skills, scaffolding projects from the
templates, syncing work back upstream. Install it if you *develop* the kit; you do not need
it to use the kit.

| Skill | Description |
|---|---|
| `create-skill` | Bootstrap a new Claude Code skill from a description, routed to its plugin by aim |
| `factor-analysis` | Analyze how a repo, plugin, or toolset should be factored into coherent standalone pieces |
| `new-project-from-template` | Create a new project from a claude-templates template |
| `update-kit` | Sync skills and workflow files upstream to claude-templates / claude-plugins / claude-expertise / claude-sandbox |

The four skills need nothing else here. (`librarian-mode` lived here until it moved to
`dev-flow`, whose aim it serves.) `new-project-from-template` points at the `create-repo`
plugin for a bare repo with a session launched on it; `create-repo` uses it, when present,
to scaffold a template.

`plugins/kit-dev/` is what remains of the old kitchen-sink plugin after the factoring: its
`hooks/`, `checkpoint` and `install-statusline` went to `context-guard` (except the checkout
guard, which went to `sandbox` with the convention it enforces; the status line and
`install-statusline` have since moved on to `statusline`); the plan-first
lifecycle skills to `dev-flow`; the `work-items` skill to `work-items`; the `sandbox` skill to
`sandbox` and the backlog trio to `ralph`; `goa`, `playwright` and `musubi-tuner` to the
`expertise` marketplace; its `agents/` directory and the deprecated plan-execution skill they
served were retired with the `dev-flow` move. The `claude-kit` *plugin* name is retired — the
separate umbrella **repo** `kmacmcfarlane/claude-kit` keeps its name and is unaffected.

### dev-flow

A plan before you code. Investigate a problem into a reviewed plan series under
`.claude-sandbox/investigations/<slug>/`, then carry that series to verified code — by hand,
or through `dev-cycle`, which takes one change from plan to merge through sub-agents (a
routed implementer in its own worktree, a review gate with a capped fix loop, the repo's
checks, a local merge on the user's say-so). Plus the research and verification techniques
that feed it — including a `research` family that turns any question into sourced, verified
findings and, where a repo keeps one, a curated knowledge base — and a standing librarian that takes custody of a repo's work: it files every
request, factors it, and dispatches each piece through `dev-cycle` with its own bindings
(its Scope, checks and decision channel), then reports what landed.

| Skill | Description |
|---|---|
| `investigate` | Research a problem and write a reviewed plan to an investigation series |
| `implement` | Carry out an investigation series — plan, build, verify, record the outcome |
| `dev-cycle` | Carry one change — a work item, a plan, or the conversation — from plan to merge through sub-agents: route by model tier, build in a worktree, review with a capped fix loop, run the checks, land |
| `deep-investigation` | Multi-agent research fan-out — strategy doc, lanes on a cheap model, one-pass synthesis |
| `research` | Research a question into sourced, verified findings — intensity with its cost stated, lanes on a cheap model, a verifier that is not the author, one synthesis, landed as a reply, report, run record or knowledge-base note |
| `research-deep` | The research skill at deep or exhaustive intensity — rounds, a gap gate, an adversarial lane, a forked synthesis |
| `research-refine` | Extend or correct an existing research run — pull a thread, re-check a claim, change scope; a new run that supersedes the old |
| `research-prune` | Curate a research knowledge base — fit check against its charter, propose and execute a rebalance, archive superseded notes, regenerate indexes |
| `chain-of-verification` | CoVe fact-verification pipeline — baseline, verify, revise |
| `librarian-mode` | Standing single-writer custodian of a repo's custody layer — a marketplace's shared agent layer, or whatever scope an operator opts a repo in with: file, factor, route by model tier, delegate to worktree agents, review, land, report |

Which dev-flow skill:

| Skill | Use it when… | Not when… |
|---|---|---|
| `investigate` | a scoped bug or feature needs a plan: one session reads the code, settles requirements with you, writes the series | the question is a broad landscape (`deep-investigation`) |
| `deep-investigation` | a broad, open-ended question needs many sources: recon, a strategy doc, cheap-model lanes against a fixed contract, one synthesis | the problem is a scoped bug or feature (`investigate`) |
| `research` | a question needs a sourced answer, kept or not: quick on its own, or lanes at a stated cost, verified and landed where the repo says | it is a bug or feature in this repo (`investigate`), or a fan-out writing a series' plan (`deep-investigation`) |
| `research-deep` | the question is too broad for one round and the operator has said so | the question is narrow (`research`), or the fan-out feeds an investigation series (`deep-investigation`) |
| `research-refine` | a prior run exists and a thread, claim or scope needs another pass | there is no prior run (`research`) |
| `research-prune` | a knowledge base is strained: rebalance, archive, re-index | new research is wanted (`research`) |
| `implement` | a finished investigation series is ready to build, hands-on in this session, fanning out to worktrees when the plan does | there is no plan yet (`investigate`), or you want the build delegated and reviewed (`dev-cycle`) |
| `dev-cycle` | one change — item, series, plan or this conversation — should go to merge through a sub-agent build and a review gate | one session should own every change to the repo (`librarian-mode`) |
| `librarian-mode` | one standing session should take custody of a repo's whole stream of work | the work is a one-off change (`dev-cycle`, or a worktree and a PR) |
| `chain-of-verification` | a factual answer must be right: baseline, independent verification, revision | the prompt has no falsifiable factual content, or speed matters more than accuracy |

The plugin ships two agents for the research family: `research-lane` (sonnet, effort medium —
gathers evidence for one lane and writes one findings file to a fixed shape) and
`research-verifier` (haiku, effort low — checks sampled claims against their sources and scores
the run). Their contract lives in the agent body, so every dispatch loads it. Soft dependency
on `statusline-hub` for the research skills: they read the usage windows from its sensor record
to pick an intensity that fits; without it they ask.

Soft dependency on `work-items`: the flow threads work items through `wi` when a store is
present, and degrades to plain investigation series when it is not; `dev-cycle` then keeps
its record in the session scratchpad. `librarian-mode` drives `wi` throughout, found through
the repo's own `plugins/*/skills/work-items` tree or the installed plugin's copy; without
either it stops at start and says to install `work-items`. Soft dependency on
`statusline-hub`: when `librarian-mode` or `dev-cycle` cannot dispatch to fable, it reads
the exhausted usage window's reset time from the sensor record the hub writes on every
status-line render (installing `statusline` brings the hub); without it the reset time is
unknown and the fallback runs on opus at once. Soft dependency on `context-guard`:
`investigate` offers a checkpoint, `/clear`, then implement path when the checkpoint skill
is in the session; `librarian-mode` answers the context gate's advisories with a
checkpoint and weighs its manifest and ledger when it rehydrates; the fable fallback also
reads reset times from its older state record. Without it none of these fire. Soft
dependency on `kit-dev`: the `investigate` and `implement` retrospectives hand their findings
to its user-invoked `update-kit`; without it the findings stand as the record.

### work-items

Repo-durable work items — one markdown file per item in `.work/` (or `.claude-sandbox/work/`),
`status:` authoritative, files never moved on completion, so they survive machines, sessions
and collaborators and merge cleanly.

| Skill | Description |
|---|---|
| `work-items` | `wi` — ready-ranked queue, atomic claims, handoff blocks, TODO.md importer, backlog-yaml bridge |

It also carries the **work-source provider interface**
(`plugins/work-items/skills/work-items/references/provider-interface.md`): the eight-verb
contract over pluggable work sources, its exit-code and canonical-state conventions, and the
per-provider capability table. The two providers described today are the `wi` store and
`backlog.yaml`; remote trackers are a documented mapping pattern, not an implementation. The
document itself is the registry — there is no machine-readable descriptor, by decision.

The `backlog.yaml` provider's own skills (`backlog-yaml`, `backlog-entry`,
`backlog-grooming`) live in the `ralph` plugin; the bridge
(`wi export/import --format backlog-yaml`) works regardless, and degrades silently when only
one store is present.

Tests: `cd plugins/work-items/skills/work-items && python3 -m unittest discover -s tests -q`.

### context-guard

Survive the finite context window. Registers the context-gate hooks, the reasoning ledger and
session rehydration — one of the plugins here whose aim *is* harness behavior (the others
are `statusline`, for the status line, `sandbox`, for the checkout guard, and
`statusline-hub`, for the shared status-line slot).

| Skill | Description |
|---|---|
| `checkpoint` | Land a long session's state before compaction; rehydration manifest + ledger |
| `usage-report` | Token spend per session, model and sub-agent dispatch from the local transcripts (stub: parser, price table and tests; report tables follow) |

It also carries `hooks/` — the depth gate, the ledger, the SessionStart rehydration, and
`gauge.json`, the thresholds and labels it publishes for the status line — with its unit tests
(`cd plugins/context-guard/hooks && python3 -m unittest discover -s tests -q`). The
`usage-report` skill has its own suite:
`cd plugins/context-guard/skills/usage-report && python3 -m unittest discover -s tests -q`.

Soft dependency on `statusline-hub`: the sensor record it writes on every status-line render
(as the `statusLine` command, or through its tee from another renderer; installing
`statusline` brings the hub) gives the gate exact depth. Without it the gate derives the window itself, mirroring Claude Code's own selection logic from the
transcript's model line and the `CLAUDE_CODE_*` window variables (`hooks/window_rules.py`).
A hard block needs an exact depth, or a derived one whose every input was observed; a derived
window that depends on something a hook cannot see (SDK betas, a 3P provider or gateway, an
unknown model, a pending model switch, a credits latch it cannot rule out for this process, an
auto-compact window a hidden settings layer could change) only warns, and so does a depth
inferred from the transcript. With the status line present its reading wins and cross-checks
the derived window. `CONTEXT_GUARD_DERIVE=off` turns derivation off. `context-guard`
never writes `settings.json`. For one more release it still ships its older copy of the status
line (`hooks/statusline.py`, deprecated), so an existing `statusLine` entry that points at it
keeps rendering. While such an entry is active and `statusline` is not installed, SessionStart
shows a "moved to the `statusline` plugin" notice at most once a week.

Upgrading from `claude-kit`: install `context-guard` for the context system. For the status
line, install `statusline`: the `statusline-hub` it brings takes over the old entry once the
footer has registered.
Hook state stays in `~/.claude/claude-kit/` (a historical directory name,
kept deliberately — renaming it would be a migration for cosmetics). See
[Migrating from `claude-kit`](#migrating-from-claude-kit) for the whole-machine checklist.

### statusline

An always-on status line: a one-line footer with context left (bar, percent, tokens), plan
usage limits with reset countdowns (Pro/Max), model, effort and session name — the plugin to
hand a coworker who wants the footer. It draws through `statusline-hub`, which installs with
it.

| Skill | Description |
|---|---|
| `install-statusline` | The coworker install; hands moving, removing or replacing the status line to `/install-statusline-hub` |

It writes no settings. On every session start its SessionStart hook registers the footer as
the hub's first display hook (`~/.claude/statusline-hub/hooks.d/statusline.json`, per the
hub's hook contract), and the hub, which owns the `statusLine` slot, runs it on every render.
A slot that an earlier version of this plugin installed keeps running the footer directly
until the hub takes it over, once, after the footer has registered: the footer draws on both
sides of the change, and nothing moves the slot back. The hook also prunes sensor files older
than 30 days.

It also draws the agent panel's sub-agent rows (`name · 43% 86k/200k · description`): each
agent's context fill, exact from its sidechain transcript (`<session>/subagents/agent-<id>.jsonl`,
read incrementally), else Claude Code's own token count marked `~`. That ships as the
`subagentStatusLine` default in the plugin's own `settings.json`, the lowest settings layer,
so no settings are written and a user-set `subagentStatusLine` always wins. Known limitation:
the footer always shows the main session's context and does not follow a sub-agent opened
from the panel, because Claude Code does not tell a status-line command which agent is in view
([anthropics/claude-code#76863](https://github.com/anthropics/claude-code/issues/76863),
closed not planned); the agent's fill is in its panel row.

It also carries `hooks/` — `statusline.py` (the renderer; with `--segment`, as the hub runs
it, it writes no sensor record, since the hub already did; run directly, as the older entry
does, it writes the record itself), `subagent_statusline.py` (the sub-agent rows),
`sensor.py` (the sensor record's writer, its pruning, and the gauge policy) and
`session_start.py` (the hook registration and prune above), after the `current-hooks` link
command that keeps an older entry's path current, and the path the `settings.json` default
names (plugin settings cannot use the plugin's path variables) — with its unit tests
(`cd plugins/statusline/hooks && python3 -m unittest discover -s tests -q`). The data
contract both ways is `skills/install-statusline/references/sensor-contract.md`; its
`test_contract.py` checks parity with `context-guard` whenever both sit in this repo.

Hard dependency on `statusline-hub` (principle 4): the footer has no function without it.
This plugin no longer installs a status line of its own, so without the hub nothing runs the
footer. `/plugin update` of a version from before the dependency does not install the hub
(a Claude Code bug), so the hook checks Claude Code's install records: with no
`statusline-hub` there, it says once to run `/plugin install statusline@kmacmcfarlane`
again. Soft dependency on `context-guard`: when it is installed and active in the session,
the gauge colours by its published thresholds and shows its epoch and `checkpoint DUE` /
`HARD gate` labels; without it, default thresholds, no epoch, no labels, and nothing is
written outside `~/.claude/statusline/` and the hub's registry.

### statusline-hub

The status-line slot, shared. Claude Code has one status-line slot, and the JSON it hands that
slot on each render is the only live source of exact context depth and plan usage. The hub
makes that slot shareable, two ways:

- **Owner mode.** The hub is the `statusLine` command. Each render it writes the sensor
  record first (`~/.claude/statusline/sensor/<session>.json`, the same file, format and rules
  as the `statusline` plugin's writer), then runs the hooks other plugins register in
  `~/.claude/statusline-hub/hooks.d/`:
  - **display** hooks run in parallel under hard timeouts, with a last-good cache, and
    their sanitised text is joined into the line;
  - **record** hooks get the raw payload byte for byte, detached, and never block the
    render;
  - an optional health file per hook adds one warning glyph when that hook is failing.
- **Embed mode.** Another renderer keeps the slot and runs `hooks/tee.py`, which writes the
  same record and prints nothing. The tools that read the record (`context-guard`'s exact
  depth, `dev-flow`'s rate-limit reset times) work there too.
- **Wrap mode**, only on the user's consent (`/install-statusline-hub --wrap`), and only
  for a status line in the user settings, never a project's. The hub owns the slot and
  runs the user's previous `statusLine` command on every render. Its
  output shows first, then the display hooks, and the record is written as in owner mode.
  A slow command is shown from the render after (a last-good cache) and killed at 5 s, and
  a failing or hung one costs only its own output. The previous entry is kept in the hub's
  private `wrap.json`, never printed, and `--unwrap` puts it back byte for byte. Unwrap
  before uninstalling; after an uninstall, reinstall and unwrap.

| Skill | Description |
|---|---|
| `statusline-hub` | Wire the tee into a ccstatusline Custom Command widget, a Starship `custom` module, or a shell wrapper around an existing status line; the hook contract for plugin authors (`references/hook-contract.md`) |
| `install-statusline-hub` | Optional: put the hub in another scope, remove it, replace a status line another tool set, or wrap one and unwrap it; list registered hooks, why any is skipped, and their health |

It sets itself up. On the first session its SessionStart hook takes a free `statusLine` slot
where the plugin is enabled (the same scope rules as `statusline`: user settings, or a
project's git-ignored `.claude/settings.local.json`) and says so in one line. It never writes
over a status line another tool set: it says so once, in a line that asks whether to wrap
it and points at embed mode and the installer; it never wraps on its own. It restores its
entry when a stale session's settings write drops it (or, while wrapping, writes back the
pre-wrap entry), and never
re-adds one the user removed, including a `statusline` footer removed before the hub
arrived. It leaves the `statusline` plugin's footer in place until that plugin registers as
a hub display hook (its first session start), then takes the slot over once, with the footer
drawing through it. When it refuses every registered hook for a reason that lies with its
directories (a config dir inside a git repository, say), it says so once. The same hook
prunes sensor records older than 30 days (the tee's included), dead hook manifests (not
refreshed for 14 days), stale caches and logs.

Soft dependency on `statusline`: its footer is the hub's first display hook. The hub also
reads the `owner.json` marker an earlier `statusline` version left, its `enabledPlugins`
entry and its `statusLine` command, but only to leave the footer alone until it registers
as a hub display hook, and then to take over its slot (or an older copy's, from
`context-guard`'s or `claude-kit`'s data dir). Without `statusline` there is nothing to wait
for, and the hub takes a free slot straight away, drawing only the hooks others register.

It carries `hooks/`, with its unit tests
(`cd plugins/statusline-hub/hooks && python3 -m unittest discover -s tests -q`):
- `hub.py`, the owner-mode render;
- `registry.py`, the manifests, their trust checks, config, health and output hygiene;
- `tee.py`;
- `owner.py` and `session_start.py`, the settings entry and the first-run, heal and takeover
  logic;
- `housekeeping.py`, the prune.

`tee.py`'s writer and `housekeeping.py`'s sensor prune are vendored copies of
`statusline`'s (a plugin may not import another's code). `tests/test_parity.py` and
`tests/test_vendored.py` fail when a copy drifts, whenever both plugins sit in this repo.
`owner.py`'s settings write began as a copy of `statusline`'s too; since that plugin stopped
writing settings it lives here only. `tests/test_handover.py` runs both plugins' session
starts together through the slot's handover. `tests/test_wrap.py` covers wrap mode.

### sandbox

Isolated execution for Claude Code sessions. Configure, bootstrap and troubleshoot
`claude-sandbox` containers — the config cascade, the child Dockerfile, host-access flags,
volume mounts and launch failures — and follow the checkout/worktree convention the launcher
implements (process stays in the checkout, work goes in a worktree). Standalone: no dependency
on any other plugin here.

| Skill | Description |
|---|---|
| `sandbox` | claude-sandbox Docker setup, config, troubleshooting, and the checkout/worktree convention |

It also carries `hooks/` — `checkout_guard.py`, a PreToolUse guard that denies `Edit`/`Write`/
`MultiEdit`/`NotebookEdit` on git-tracked files when the session's cwd is a main checkout, the
direction the harness's own worktree guard does not cover. Enforcement is on wherever the plugin
is installed; the per-repo opt-out is a `.claude/allow-checkout-edits` marker file or
`SANDBOX_ALLOW_CHECKOUT_EDITS=1` in the environment (`CLAUDE_KIT_ALLOW_CHECKOUT_EDITS=1` is still
honoured as a deprecated alias, so existing env files keep working). Every git failure fails open. Unit tests:
`cd plugins/sandbox/hooks && python3 -m unittest discover -s tests -q`.

### ralph

Unattended agent loops over a backlog. The `backlog.yaml` workflow a ralph run consumes:
CLI-mediated reads and writes, entry authoring, and the human grooming pass that closes work.

| Skill | Description |
|---|---|
| `backlog-yaml` | `backlog.yaml` management via the `backlog.py` CLI |
| `backlog-entry` | Create backlog entries (stories, bugs, refactoring) in `backlog.yaml` |
| `backlog-grooming` | Conversational backlog grooming and UAT review |

Requires the `claude-sandbox` tool (external): the loops run inside its containers, and
`backlog.py` itself is seeded per project by `claude-sandbox init-ralph` (canonical in the
claude-sandbox repo, not shipped here). Soft dependency on `sandbox`: its skill bootstraps
and troubleshoots those containers, but ralph's skills never call it, so it is not declared
in `plugin.json`. Soft dependency on a work source through the **work-source interface**
documented in `work-items` — `backlog.yaml` is the default provider for unattended runs, and
the `wi` bridge activates only when both stores are present.

### create-repo

Start a new repo for a thread of work you will pick up later, and hand it to an agent
session. The skill resolves the path (beside the current repo by default, confirmed with
you), creates the directory, runs `git init -b main`, seeds a README naming the thread's
purpose, runs `claude-sandbox init --yes` (so the repo inherits the workspace's sandbox
config) and makes the first commit. It then gives you one copy-paste command that launches
the session in your own terminal with a bootstrap prompt: write the repo's `CLAUDE.md`, then
run the thread's first investigation.

| Skill | Description |
|---|---|
| `create-repo` | Bootstrap a thread repo — path, `git init`, purpose README, `claude-sandbox init`, first commit — then one command that launches a session on it |

The skill never launches the session itself. `claude-sandbox` has no detached mode yet, so a
session started under the agent's terminal would die with it; the command runs in yours and
you are attached from the start.

External dependency on the `claude-sandbox` tool, soft in practice: without it the repo is
still created and committed, and the command is a plain `claude` launch, as the skill says.
Soft dependency on `kit-dev`: name a claude-templates template as the goal and, when its
`new-project-from-template` skill is in the session, the skill scaffolds from it; without it
the skill gives the install command and carries on with a bare repo.
`new-project-from-template` points back here for a bare repo. Soft dependency on `sandbox`:
its skill troubleshoots an `init` or a launch that fails. Soft dependency on `dev-flow`: the
launched session uses its `investigate` skill for the first investigation when installed,
and investigates directly without it.

### chat

Skills for LLM chat sessions in web UIs. Family home under review.

| Skill | Description |
|---|---|
| `product-research` | Structured, goal-driven product research — requirements, web search, candidate analysis, comparison writeup |

## Setup

### Add the marketplace

```bash
/plugin marketplace add https://github.com/kmacmcfarlane/claude-plugins.git
```

Or in `.claude/settings.json` (`~/.claude/settings.json` for user scope):

```json
{
  "extraKnownMarketplaces": {
    "kmacmcfarlane": {
      "source": {
        "source": "git",
        "url": "https://github.com/kmacmcfarlane/claude-plugins.git"
      },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "statusline@kmacmcfarlane": true,
    "statusline-hub@kmacmcfarlane": true
  }
}
```

List `statusline-hub` beside `statusline`: the footer draws only through it, and enabling
`statusline` from a settings file is not known to enable its dependency too. Auto-install from
`enabledPlugins` is unverified; the reliable path is still the explicit
`/plugin install statusline@kmacmcfarlane` below.

### Install plugins

```bash
/plugin install context-guard@kmacmcfarlane
/plugin install statusline@kmacmcfarlane
```

Installing `statusline` installs `statusline-hub` with it. Start a new session: the hub puts
itself in the status-line slot and says so (in the first session, or the second when the
footer had not registered yet), and the footer shows from the session after that.
`/install-statusline-hub` (or `/install-statusline`, which hands off to it) is only for
another scope, removal, or replacing a status line another tool set.

Upgrading from a `statusline` that predates the hub: `/plugin update` does not install a
new dependency, so run `/plugin install statusline@kmacmcfarlane` again (the footer says so
at session start when the hub is missing).

To keep this marketplace itself up to date automatically, see "Keep it updated" in the
`install-statusline` skill.

Or browse: `/plugin` → Discover tab. Install the plugins whose aims match your problems — the
catalog above is the index; nothing here requires anything else here, except a declared
(hard) dependency, which installs with it.

## Migrating from `claude-kit`

The `claude-kit` plugin is gone from the marketplace. Per machine, once:

1. **Refresh the marketplace** so the new plugin list is visible:
   `/plugin marketplace update kmacmcfarlane`.
2. **Install what that machine actually needs** (`/plugin install <name>@kmacmcfarlane`) —
   the primary dev machine typically takes all of them; a work machine may want only
   `context-guard`, plus `dev-flow` / `work-items` if you use the plan-first flow; an
   inference box like `lucy` wants expertise packs rather than these.
3. **Uninstall `claude-kit` in the same `/plugin` sitting, before the first session**:
   `/plugin uninstall claude-kit@kmacmcfarlane`. Its hooks and `context-guard`'s (and
   `sandbox`'s) would otherwise all fire in that session — two gates, two relays, two
   guards. It no longer exists in the marketplace, so removing it also stops the duplicate
   skills showing up.
4. **Take over the status line:** install `statusline` (it brings `statusline-hub`) and
   start a session or two. Once the footer has registered with the hub, the hub's
   SessionStart recognises an entry that points into `plugins/data/claude-kit-*/` or
   `plugins/data/context-guard-*/` by its path (no marker needed), repoints it at the hub,
   and says `took over the status line slot in PATH`. Verify the gauge renders in the next
   session. (`/install-statusline-hub --replace` does it by hand.)
5. **Expertise packs** (`goa`, `playwright`, `musubi-tuner`, `ai-scripts`) arrive when the
   `claude-expertise` repo gains a remote and that marketplace is registered. Until then they
   are not installable anywhere — this is the one gap the refactor leaves open.

Nothing else needs doing: hook state stays where it was (`~/.claude/claude-kit/`), and `wi`
stores inside your repos are path-stable.

## Structure

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json         # Plugin index (points to ./plugins/)
├── plugins/
│   ├── chat/
│   ├── context-guard/
│   ├── create-repo/
│   ├── dev-flow/
│   ├── kit-dev/
│   ├── ralph/
│   ├── sandbox/
│   ├── statusline/
│   ├── statusline-hub/
│   └── work-items/
├── CLAUDE.md                    # Placement rules for contributors and agents
└── README.md                    # This file — doctrine and catalog
```

Plugin internals are deliberately not listed here; the catalog above is the front door, and
per-directory trees go stale. Skills are authored in place under
`plugins/<plugin>/skills/<skill>/`.
