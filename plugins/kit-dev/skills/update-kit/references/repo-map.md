# Upstream Repo Structures

Built-in knowledge of the repos this skill syncs into, so a run never has to re-explore them:
two marketplaces (`claude-plugins`, `claude-expertise`), the scaffolding template
(`claude-templates`), the sandbox tool (`claude-sandbox`), and the umbrella repo
(`claude-kit`, README sync only).

**Trees rot.** Each section gives the marker to probe, the shape, and how to derive the
current contents. Where a listing would need refreshing to stay true, this file gives the
command instead of the answer. If a tree here disagrees with disk, disk wins — and fixing this
file is itself a `[M]` for the next sync.

## claude-templates

- **Repo**: `kmacmcfarlane/claude-templates`
- **Expected local path**: Sibling to project root (`../claude-templates`)
- **Marker**: `local-web-app/` directory exists
- **Purpose**: Scaffolding template for new local-web-app projects. Contains canonical agent
  workflow docs, subagent definitions, prompt files, and project skeleton.

### Structure

```
claude-templates/
├── CLAUDE.md                  (repo-level context, NOT synced)
├── README.md
├── LICENSE
└── local-web-app/             ← template root (all synced content lives here)
    ├── CLAUDE.md              (template CLAUDE.md — mixed, always manual review)
    ├── CHANGELOG.md           (NOT synced)
    ├── Makefile               (NOT synced)
    ├── docker-compose.yml     (NOT synced)
    ├── docker-compose.dev.yml (NOT synced)
    ├── .mcp.json
    ├── .gitignore
    ├── .claude-sandbox/       ← the agent workflow lives HERE, not at the template root
    │   ├── agent/             (workflow docs + prompts — the synced universal set)
    │   └── scripts/
    ├── .claude/
    │   ├── settings.json
    │   └── agents/            (subagent definitions — SYNCED)
    ├── backend/               (template Go + Goa skeleton)
    ├── frontend/              (template Vue + Vite skeleton)
    ├── docs/
    └── scripts/
```

### Key facts

- **The agent workflow docs sit under `.claude-sandbox/agent/`**, not `agent/`. A child
  project that still roots them at `agent/` is on the older layout; resolve the real location
  by probing both before diffing, and never construct the upstream path from the project's.
- The `local-web-app/` prefix is required when constructing upstream paths.
- Skills are NOT in the template — they come from marketplace plugins.
- To derive the synced set rather than trusting a list:
  `ls ../claude-templates/local-web-app/.claude-sandbox/agent/*.md` and
  `ls ../claude-templates/local-web-app/.claude/agents/*.md`. Stubs and project-specific files
  (`PRD.md`, `backlog.yaml`, `backlog_done.yaml`, `QUESTIONS.md`) are in the exclude list in
  SKILL.md Step 0.2 and never sync.

## claude-plugins (harness-plugin marketplace)

- **Repo**: `kmacmcfarlane/claude-plugins`
- **Expected local path**: Sibling to project root (`../claude-plugins`)
- **Marker**: `.claude-plugin/marketplace.json` exists
- **Purpose**: Marketplace of aim-named harness plugins — each shapes the development loop.
  Its `README.md` carries the doctrine and the catalog; its `CLAUDE.md` carries the placement
  rules that route a new skill (SKILL.md Step 0.3).

### Structure

```
claude-plugins/
├── README.md                  (doctrine + catalog — the front door)
├── CLAUDE.md                  (placement rules / aim → home table)
├── .claude-plugin/
│   └── marketplace.json       (the plugin index)
└── plugins/
    ├── chat/                  (web-UI chat-session skills)
    │   └── skills/product-research/
    ├── context-guard/         (surviving the context window — a hook-owning plugin)
    │   ├── hooks/             (gate, statusline sensor, ledger, rehydrate + tests)
    │   └── skills/{checkpoint,install-statusline,usage-report}/
    ├── dev-flow/              (plan before you code; the librarian that takes custody of a repo)
    │   └── skills/{investigate,implement,deep-investigation,chain-of-verification,librarian-mode}/
    ├── kit-dev/               (maintaining this kit itself — where THIS skill lives)
    │   └── skills/{create-skill,update-kit,new-project-from-template,factor-analysis}/
    ├── ralph/                 (unattended agent loops over a backlog)
    │   └── skills/{backlog-yaml,backlog-entry,backlog-grooming}/
    ├── sandbox/               (isolated execution: claude-sandbox + checkout/worktree convention — a hook-owning plugin)
    │   ├── hooks/             (checkout guard + tests)
    │   └── skills/sandbox/
    └── work-items/            (repo-durable work items + work-source provider interface)
        └── skills/work-items/ (wi CLI, references/, tests/)
```

Derive the current set with `ls ../claude-plugins/plugins` and
`ls ../claude-plugins/plugins/*/skills`; the README catalog is the human-readable index.

### Key facts

- Every plugin has `.claude-plugin/plugin.json`; the marketplace index is
  `.claude-plugin/marketplace.json`. Adding or removing a plugin updates both it and the
  README catalog, in the same commit.
- Each skill is a directory under `plugins/<plugin>/skills/<name>/` containing at minimum
  `SKILL.md`, and the directory name must match the `name` in its frontmatter.
- **Sync target: there is no single skills root.** An existing skill goes back to the plugin
  it was discovered in; a new one is routed **by aim** through the decision tree in this
  repo's `CLAUDE.md` § Placement rules — harness behavior → the plugin whose aim is that
  behavior; stack knowledge → an expertise pack in `claude-expertise`; kit maintenance →
  `kit-dev`; otherwise the plugin owning that aim. See SKILL.md Step 0.3.
- The marketplace `name` field is `kmacmcfarlane` and is **frozen** — it suffixes every
  plugin-data directory.
- After pushing, subscribers install or update with the `/plugin` command in Claude Code.

## claude-expertise (expertise-pack marketplace)

- **Repo**: `kmacmcfarlane/claude-expertise` (**no remote configured yet** — local checkout
  only, so its plugins are not installable from anywhere until the remote lands and the
  marketplace is registered)
- **Expected local path**: Sibling to project root (`../claude-expertise`) — **optional**;
  probe before use
- **Marker**: `.claude-plugin/marketplace.json` exists, with `"name": "expertise"`
- **Purpose**: The second marketplace: pure stack/tool knowledge, one plugin per stack. **No
  hooks, no status lines, no settings writes, ever** — that quarantine is what makes a
  content marketplace safe to install from.

### Structure

```
claude-expertise/
├── README.md
├── .claude-plugin/
│   └── marketplace.json       ("name": "expertise")
└── plugins/
    ├── ai-scripts/    └── skills/ai-scripts/
    ├── goa/           └── skills/goa/
    ├── musubi-tuner/  └── skills/musubi-tuner/
    └── playwright/    └── skills/playwright/
```

Derive with `ls ../claude-expertise/plugins`.

### Key facts

- Same plugin shape as claude-plugins — one skill per pack today, plugin named for the stack.
- If this repo is not on disk, an expertise-bound `[A?]` skill is **deferred and reported**,
  never redirected into a claude-plugins plugin.
- A skill that wants a hook is by definition not an expertise pack.

## claude-sandbox

- **Repo**: `kmacmcfarlane/claude-sandbox`
- **Expected local path**: Sibling to project root (`../claude-sandbox`)
- **Marker**: `bin/claude-sandbox` file exists
- **Purpose**: Docker-based sandbox for running Claude Code with filesystem isolation and host
  Docker access. Provides the `claude-sandbox` launcher and its `init` / `init-ralph`
  scaffolding (which is what seeds `backlog.py` into a child project).

### Structure

```
claude-sandbox/
├── CLAUDE.md                  (repo guidelines)
├── README.md
├── LICENSE
├── Dockerfile                 (base image)
├── Dockerfile.cli             (Claude Code CLI image)
├── entrypoint.sh              (UID/GID remapping at container start)
├── go.mod, assets.go
├── bin/
│   └── claude-sandbox         (bash shim that builds and runs the Go launcher)
├── cmd/
│   └── claude-sandbox/        (the launcher itself — Go)
└── docs/
```

### Key facts

- **The launcher is a Go program** behind a thin bash shim in `bin/`, built on demand. Older
  descriptions of a pure-bash launcher plus a `lib/stream-filter.js` are obsolete.
- The ralph loop reads the child project's prompt files — it does not carry them itself.
- The sandbox image ships Debian bookworm-slim, Node.js, Docker CLI + compose, git, jq and the
  Claude Code CLI. Language toolchains are NOT included — use project compose services.
- **Nothing syncs here today.** This repo holds infrastructure, not agent workflow docs; it is
  listed so a run can resolve and read it, not write to it.

## claude-kit (umbrella repo)

- **Repo**: `kmacmcfarlane/claude-kit` — **optional**, probe before use
- **Expected local path**: `../claude-kit`, bound to `$KIT`
- **Purpose**: The umbrella README documenting the whole toolkit. **README sync only**
  (SKILL.md Phase 2.5); no skills or workflow files live here.
- **Naming**: the repo keeps this name. The *plugin* once called `claude-kit` dissolved into
  the aim-named plugins above; never write `claude-kit` as if it were an installable plugin.

## Project-Level Config: agent/claude-kit-repo-map.md

Each child project maintains `agent/claude-kit-repo-map.md` (lives in the project, NOT in this
skill; on the newer template layout it sits under `.claude-sandbox/agent/`). It declares:

1. **Which skills sync upstream** — skills that originated in this project and should be
   pushed to a marketplace, with the plugin each belongs to.
2. **Additional template files** — extras beyond the universal set for claude-templates.
3. **Sandbox files** — if a project ever needs to sync files to claude-sandbox (uncommon).

The skill reads this file at runtime for declarations only; the *scan* discovers skills
dynamically (SKILL.md Step 0.3) and never trusts this file for what exists. If missing, offer
to create a starter template.
