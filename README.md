# claude-plugins

**Tools for humans and agents to address common problems with using an LLM harness to
develop code.**

This repository is a Claude Code plugin marketplace. The marketplace itself is the kit —
there is no single kitchen-sink plugin. Each plugin is named for an *aim*: the answer to a
problem a user would state out loud ("I keep losing context", "I want unattended runs", "I
want a plan before I code"). Install the ones that match your problems; leave the rest.

The marketplace is currently being refactored from one history-indexed plugin (`claude-kit`)
into aim-named, standalone-installable plugins. **The catalog below marks what exists today
and what is planned.** Nothing marked *planned* exists yet.

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
   else from the marketplace present. Whatever fails that test lives *inside* the plugin
   whose aim it serves.
3. **Harness-behavior quarantine.** Hooks, status lines, and settings writes belong only in a
   plugin whose stated aim *is* that behavior. Knowledge skills never carry hooks as
   passengers.
4. **Dependencies: soft, declared, directional.** A dependency degrades gracefully when the
   other side is absent (the work-items ↔ backlog bridge is the model), is declared in the
   plugin description and the catalog, and points at a named support plugin or an external
   repo. Never undocumented peer prose-coupling.
5. **Names are API.** Names end up in plugin data dirs, absolute paths inside `settings.json`,
   hook state dirs, and muscle memory. Choose for decades. See *Naming practices* below.
6. **New aim → new plugin.** Never stretch an existing description to cover something new.
   Small is fine; incoherent is not.
7. **The catalog is the front door.** This README carries the problem-indexed catalog
   (aim → plugin → depends-on) and the contributor decision tree, and every change to the
   shape of the marketplace updates it in the same commit.

## Catalog

Problem-indexed. **Status is load-bearing:** *current* rows exist on disk today; *planned*
rows do not exist yet and must not be installed, referenced, or linked as if they did;
*moved* rows live in the expertise marketplace, not here.
Planned names are **provisional** pending operator review.

| Aim — "install this if you want…" | Plugin | Status | Depends on |
|---|---|---|---|
| …everything below, in one plugin (the historical kitchen sink) | `claude-kit` | **current — dissolving** into the planned plugins below | — |
| …project context for the `ai-scripts` Python CLI utilities | `ai-scripts` | **moved** to the expertise marketplace (local scaffold, remote pending) | — |
| …structured product research in a web chat session | `chat` | current; *family home under review* | — |
| …to survive the finite context window (gate, gauge, checkpoint, rehydration) | `context-guard` | **current** | — |
| …a plan before you code: investigate → reviewed plan → verified implementation | `dev-flow` | **current** | `work-items` (soft) |
| …repo-durable work items and a pluggable work source | `work-items` | **current** | — |
| …isolated container execution for agent sessions | `sandbox` | **current** | claude-sandbox repo (external) |
| …unattended agent loops over a backlog ("ralph") | `ralph` | **current** | `sandbox` (hard), `work-items` (soft) |
| …to maintain this kit itself (skill authoring, upstream sync, templates) | `kit-dev` | **planned** (Phase 6) | — |
| …to make Claude good at a specific stack (Goa, Playwright, musubi-tuner, …) | one plugin per stack | **moved** to the expertise marketplace (local scaffold, remote pending) | — |

Retired: the deprecated plan-execution skill and the three sub-agent definitions used only by
it (Phase 3). Still to retire when its phase lands: the `claude-kit` plugin name.

Moved out of this marketplace at Phase 2: `goa`, `playwright`, `musubi-tuner` and the
`ai-scripts` plugin, into the `expertise` marketplace (repo `claude-expertise`). That repo
exists as a **local scaffold only** — no remote is configured yet, so the four are not
installable from anywhere until the remote lands.

## Where does a new thing go?

The contributor decision tree. Answer in order; the first match wins.

1. **Does it alter harness behavior?** Hooks, a status line, `settings.json` writes,
   background state. → It belongs *only* in a plugin whose stated aim is that behavior
   (that plugin is `context-guard`: `plugins/context-guard/`). Never bolt it
   onto a knowledge skill (principle 3).
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

Until a planned plugin's phase lands, write to the **current home** in CLAUDE.md's aim→home
table — a planned destination is never a place to put files today.

Cross-plugin cooperation follows principle 4: soft, declared, directional. The work-items ↔
backlog bridge (activates only when both stores are present, degrades silently otherwise) is
the pattern to copy.

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
rename; `sandbox`, `ralph`, `kit-dev`), the second marketplace's working name (`expertise` / repo
`claude-expertise`), and the `chat` family's home are **provisional**, adopted so work can
proceed, and confirmable or changeable at operator review. Names that have shipped state
(a data dir, a settings path) are changed only via the rename procedure above.

## Plugins today

What is installable from this marketplace right now.

### claude-kit

Claude Code development tooling — reusable across projects. Dissolving into the planned
plugins in the catalog; until those phases land, this is where these skills live.

| Skill | Description | Planned home |
|---|---|---|
| `create-skill` | Bootstrap a new Claude Code skill from a description | `kit-dev` |
| `factor-analysis` | Analyze how a repo, plugin, or toolset should be factored into coherent standalone pieces | `kit-dev` (under review) |
| `new-project-from-template` | Create a new project from a claude-templates template | `kit-dev` |
| `update-kit` | Sync skills and workflow files upstream to claude-templates / claude-plugins / claude-sandbox | `kit-dev` |

`plugins/claude-kit/` is now skills only. Its `hooks/`, `checkpoint` and `install-statusline`
moved out into `context-guard`; the plan-first lifecycle skills moved into `dev-flow`; the
`work-items` skill moved into `work-items`; the `sandbox` skill moved into `sandbox` and the
backlog trio into `ralph`; the `goa`, `playwright` and `musubi-tuner` skills moved out to the
`expertise` marketplace; its `agents/` directory and the deprecated plan-execution skill they
served were retired with the `dev-flow` move.

### dev-flow

A plan before you code. Investigate a problem into a reviewed plan series under
`.claude-sandbox/investigations/<slug>/`, then carry that series to verified code — plus the
research and verification techniques that feed it.

| Skill | Description |
|---|---|
| `investigate` | Research a problem and write a reviewed plan to an investigation series |
| `implement` | Carry out an investigation series — plan, build, verify, record the outcome |
| `deep-investigation` | Multi-agent research fan-out — strategy doc, lanes on a cheap model, one-pass synthesis |
| `chain-of-verification` | CoVe fact-verification pipeline — baseline, verify, revise |

Soft dependency on `work-items`: the flow threads work items through `wi` when a store is
present, and degrades to plain investigation series when it is not.

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

Survive the finite context window. Registers the context-gate hooks, the status-line sensor,
the reasoning ledger and session rehydration — the one plugin here whose aim *is* harness
behavior.

| Skill | Description |
|---|---|
| `checkpoint` | Land a long session's state before compaction; rehydration manifest + ledger |
| `install-statusline` | Install the context gauge (tokens left, epoch, checkpoint state), which also feeds the gate hooks their exact depth |

It also carries `hooks/` — the depth gate, the status line sensor, the ledger, and the
SessionStart rehydration/self-heal — with its unit tests
(`cd plugins/context-guard/hooks && python3 -m unittest discover -s tests -q`).

Upgrading from `claude-kit`: install `context-guard` and start one session; the SessionStart
hook migrates an existing status-line entry to this plugin's data path. `/install-statusline`
is the fallback. Hook state stays in `~/.claude/claude-kit/` (a historical directory name).

### sandbox

Isolated Docker execution environments for Claude Code. Configure, bootstrap and troubleshoot
`claude-sandbox` containers — the config cascade, the child Dockerfile, host-access flags,
volume mounts and launch failures. Standalone: no dependency on any other plugin here.

| Skill | Description |
|---|---|
| `sandbox` | claude-sandbox Docker setup, config, and troubleshooting |

### ralph

Unattended agent loops over a backlog. The `backlog.yaml` workflow a ralph run consumes:
CLI-mediated reads and writes, entry authoring, and the human grooming pass that closes work.

| Skill | Description |
|---|---|
| `backlog-yaml` | `backlog.yaml` management via the `backlog.py` CLI |
| `backlog-entry` | Create backlog entries (stories, bugs, refactoring) in `backlog.yaml` |
| `backlog-grooming` | Conversational backlog grooming and UAT review |

Hard dependency on `sandbox`: the loops run inside `claude-sandbox`, and `backlog.py` itself
is seeded per project by `claude-sandbox init-ralph` (canonical in the claude-sandbox repo,
not shipped here). Soft dependency on a work source through the **work-source interface**
documented in `work-items` — `backlog.yaml` is the default provider for unattended runs, and
the `wi` bridge activates only when both stores are present.

### chat

Skills for LLM chat sessions in web UIs. Family home under review.

| Skill | Description |
|---|---|
| `product-research` | Structured, goal-driven product research — requirements, web search, candidate analysis, comparison writeup |

## Setup

### Add the marketplace

```bash
/plugin marketplace add kmacmcfarlane/claude-plugins
```

Or in `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "kmacmcfarlane": {
      "source": {
        "source": "github",
        "repo": "kmacmcfarlane/claude-plugins"
      }
    }
  }
}
```

### Install plugins

```bash
/plugin install claude-kit@kmacmcfarlane
```

Or browse: `/plugin` → Discover tab.

## Structure

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json         # Plugin index (points to ./plugins/)
├── plugins/
│   ├── chat/
│   ├── claude-kit/
│   ├── context-guard/
│   ├── dev-flow/
│   ├── ralph/
│   ├── sandbox/
│   └── work-items/
├── CLAUDE.md                    # Placement rules for contributors and agents
└── README.md                    # This file — doctrine and catalog
```

Plugin internals are deliberately not listed here; the catalog above is the front door, and
per-directory trees go stale. Skills are authored in place under
`plugins/<plugin>/skills/<skill>/`.
