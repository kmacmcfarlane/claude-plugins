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
| **Expertise packs** | Pure knowledge — make Claude good at stack X. No hooks, ever | A second marketplace, **planned** (working name `expertise`, repo `claude-expertise`) |
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
rows do not exist yet and must not be installed, referenced, or linked as if they did.
Planned names are **provisional** pending operator review.

| Aim — "install this if you want…" | Plugin | Status | Depends on |
|---|---|---|---|
| …everything below, in one plugin (the historical kitchen sink) | `claude-kit` | **current — dissolving** into the planned plugins below | — |
| …project context for the `ai-scripts` Python CLI utilities | `ai-scripts` | current; *planned* move to the expertise marketplace | — |
| …structured product research in a web chat session | `chat` | current; *family home under review* | — |
| …to survive the finite context window (gate, gauge, checkpoint, rehydration) | `context-guard` | **planned** (Phase 1) | — |
| …a plan before you code: investigate → reviewed plan → verified implementation | `dev-flow` | **planned** (Phase 3) | `work-items` (soft) |
| …repo-durable work items and a pluggable work source | `work-items` | **planned** (Phase 4) | — |
| …isolated container execution for agent sessions | `sandbox` | **planned** (Phase 5) | claude-sandbox repo (external) |
| …unattended agent loops over a backlog ("ralph") | `ralph` | **planned** (Phase 5) | `sandbox` (hard), `work-items` (soft) |
| …to maintain this kit itself (skill authoring, upstream sync, templates) | `kit-dev` | **planned** (Phase 6) | — |
| …to make Claude good at a specific stack (Goa, Playwright, musubi-tuner, …) | one plugin per stack | **planned** — second marketplace | — |

Retired when their phases land: the `claude-kit` plugin name, the `implement-plan` skill, and
the three agents used only by it.

## Where does a new thing go?

The contributor decision tree. Answer in order; the first match wins.

1. **Does it alter harness behavior?** Hooks, a status line, `settings.json` writes,
   background state. → It belongs *only* in a plugin whose stated aim is that behavior
   (current home: `plugins/claude-kit/hooks/`; planned: `context-guard`). Never bolt it
   onto a knowledge skill (principle 3).
2. **Is it pure stack/tool knowledge** — "make Claude good at X"? → Expertise family
   (second marketplace, planned; current home: this repo, see the aim→home table in
   [CLAUDE.md](CLAUDE.md)). No hooks, no settings.
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

The planned plugin names above (`context-guard`, `dev-flow`, `work-items`, `sandbox`,
`ralph`, `kit-dev`), the second marketplace's working name (`expertise` / repo
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
| `backlog-entry` | Create backlog entries (stories, bugs, refactoring) in `backlog.yaml` | `ralph` |
| `backlog-grooming` | Conversational backlog grooming and UAT review | `ralph` |
| `backlog-yaml` | `backlog.yaml` management via the `backlog.py` CLI | `ralph` |
| `chain-of-verification` | CoVe fact-verification pipeline — baseline, verify, revise | `dev-flow` |
| `checkpoint` | Land a long session's state before compaction; rehydration manifest + ledger | `context-guard` |
| `create-skill` | Bootstrap a new Claude Code skill from a description | `kit-dev` |
| `deep-investigation` | Multi-agent research fan-out — strategy doc, lanes on a cheap model, one-pass synthesis | `dev-flow` |
| `factor-analysis` | Analyze how a repo, plugin, or toolset should be factored into coherent standalone pieces | `kit-dev` (under review) |
| `goa` | Design-first API development with Goa v3 for Go | expertise marketplace |
| `implement` | Carry out an investigation series — plan, build, verify, record the outcome | `dev-flow` |
| `implement-plan` | **Deprecated** — superseded by `investigate` + `implement`; retired at Phase 3 | *retired* |
| `install-statusline` | Context gauge (tokens left, epoch, checkpoint state) that also feeds the gate hooks | `context-guard` |
| `investigate` | Research a problem and write a reviewed plan to an investigation series | `dev-flow` |
| `musubi-tuner` | LoRA training and inference with kohya's musubi-tuner | expertise marketplace |
| `new-project-from-template` | Create a new project from a claude-templates template | `kit-dev` |
| `playwright` | End-to-end testing with Playwright | expertise marketplace |
| `sandbox` | claude-sandbox Docker setup, config, and troubleshooting | `sandbox` |
| `update-kit` | Sync skills and workflow files upstream to claude-templates / claude-plugins / claude-sandbox | `kit-dev` |
| `work-items` | `wi` — repo-durable work items in `.work/`, TODO.md importer, backlog-yaml bridge | `work-items` |

`plugins/claude-kit/` also carries `hooks/` (the context gate, status line sensor, ledger, and
session rehydration — planned home `context-guard`) and `agents/` (three agent definitions
used only by the deprecated `implement-plan`, retired with it).

### ai-scripts

Context skills for the [ai-scripts](https://github.com/kmacmcfarlane/ai-scripts) repo —
Python CLI utilities for AI tasks. Planned to move to the expertise marketplace; it stays
here and fully functional until that phase lands.

| Skill | Description |
|---|---|
| `ai-scripts` | Project context for `caption_util`, `llm_fetch`, `token_count`, `token_embedding_search`, `generate_rare_token` |

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
│   ├── ai-scripts/
│   ├── chat/
│   └── claude-kit/
├── CLAUDE.md                    # Placement rules for contributors and agents
└── README.md                    # This file — doctrine and catalog
```

Plugin internals are deliberately not listed here; the catalog above is the front door, and
per-directory trees go stale. Skills are authored in place under
`plugins/<plugin>/skills/<skill>/`.
