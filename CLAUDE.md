# claude-plugins

Claude Code plugin marketplace. **The doctrine — the seven principles every plugin is
measured against, plus naming practices and the catalog — lives in [README.md](README.md).**
Read it before adding or moving anything. This file carries only the mechanics: where files
go.

Do not restate the principles here; restated rules drift.

## Repository Layout

```
plugins/
  chat/                # Skills for LLM chat sessions in web UIs
    skills/
      product-research/
  context-guard/       # Surviving the context window (hook-owning)
    hooks/             # Gate, statusline sensor, ledger, rehydrate + unit tests
    skills/
      {checkpoint,install-statusline,usage-report}/
  dev-flow/            # Plan before you code; the librarian that takes custody of a repo
    skills/
      {investigate,implement,deep-investigation,chain-of-verification,librarian-mode}/
  kit-dev/             # Maintaining this kit itself
    skills/
      {create-skill,update-kit,new-project-from-template,factor-analysis}/
  ralph/               # Unattended agent loops over a backlog
    skills/
      {backlog-yaml,backlog-entry,backlog-grooming}/
  sandbox/             # Isolated execution: claude-sandbox + the checkout/worktree convention (hook-owning)
    hooks/             # Checkout guard + hooks.json + unit tests
    skills/
      sandbox/
  work-items/          # Repo-durable work items + the work-source provider interface
    skills/
      work-items/      # wi CLI, references/{format,provider-interface}.md, tests/
```

Every plugin carries `.claude-plugin/plugin.json`; a skill directory holds `SKILL.md` plus
optional `references/`, `scripts/`, `assets/`.

## Conventions

- **Skill location**: `plugins/<plugin>/skills/<name>/SKILL.md` (never `.claude/skills/`).
- **Agent location**: `plugins/<plugin>/agents/<name>.md` — auto-loaded by the plugin system.
  Agent `.md` files define role, tools, and model. Task-specific context is injected via the
  Agent prompt, not baked into the definition. *No plugin here ships agents today* — the last
  three were retired with the deprecated plan-execution skill they served (Phase 3).
- **Hook location**: `plugins/<plugin>/hooks/<name>.py` — registered in that plugin's
  `plugins/<plugin>/hooks/hooks.json`, which lists each hook under its event (`PreToolUse`,
  `UserPromptSubmit`, `SessionStart`, `Stop`, …) with a `matcher` and a `command` that names
  the script through the plugin root, `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<name>.py"` —
  never a relative path, since the command runs with no guaranteed working directory. Tests
  live in `plugins/<plugin>/hooks/tests/` and run with `python3 -m unittest discover -s tests -q`
  from the hooks dir. Hooks, status lines and `settings.json` writes belong only in the
  plugin whose stated aim is that behavior; each such plugin carries its own `hooks.json`
  with only its hooks.
- **Plugin registry**: `.claude-plugin/marketplace.json` — update when adding or removing a
  plugin (not when adding skills to an existing plugin). Its `name` field, `kmacmcfarlane`,
  is **frozen**: it suffixes every plugin-data directory.
- **Skill reference paths**: bare relative paths (no `./`, no `${CLAUDE_SKILL_DIR}`).
- **Catalog upkeep**: any change to the shape of the marketplace updates the README catalog
  in the same commit.

## Placement rules

Where a new or moved thing goes. The full decision tree is in
[README.md § Where does a new thing go?](README.md); the short form:

1. Alters harness behavior (hooks, status line, `settings.json` writes)? → only a plugin
   whose stated aim *is* that behavior (`plugins/context-guard/` for the context system,
   `plugins/sandbox/` for the checkout/worktree guard). Never attach it to a knowledge skill.
2. Pure stack/tool knowledge? → the expertise family, in its own marketplace (`expertise`,
   repo `claude-expertise`) — not this repo.
3. For web-UI chat sessions rather than a coding harness? → the `chat` family (home under
   review).
4. Otherwise, a harness capability: find its aim in the table below and use the **current
   home** column.
5. No aim fits? → new aim, new plugin. Write its catalog row first.

### Aim → home

Plugin names are **provisional** pending operator review. Every row below has landed: the
current home is the real home, and is where files go.

| Aim | Current home | Target home (planned) |
|---|---|---|
| Survive the finite context window (gate, gauge, checkpoint, rehydration, token-spend report) | `plugins/context-guard/` | `plugins/context-guard/` — **landed** (Phase 1) |
| Plan-before-code development flow, and a standing librarian that takes custody of a repo's work | `plugins/dev-flow/` | `plugins/dev-flow/` — **landed** (Phase 3) |
| Repo-durable work items / work-source interface | `plugins/work-items/` | `plugins/work-items/` — **landed** (Phase 4) |
| Isolated execution (containers; the checkout/worktree convention and its guard) | `plugins/sandbox/` | `plugins/sandbox/` — **landed** (Phase 5) |
| Unattended agent loops over a backlog ("ralph") | `plugins/ralph/` | `plugins/ralph/` — **landed** (Phase 5) |
| Maintaining this kit itself | `plugins/kit-dev/` | `plugins/kit-dev/` — **landed** (Phase 6) |
| Stack expertise ("make Claude good at X") | the `expertise` marketplace (repo `claude-expertise`) — not this repo | moved to the expertise marketplace (local scaffold, remote pending) — **landed** (Phase 2) |
| Web-UI chat-session skills | `plugins/chat/` | family home under review |

Retired at Phase 3: the deprecated plan-execution skill under the then-`claude-kit` plugin's
`skills/`, and its `agents/`, which existed only to serve it. Retired at Phase 6: the
`claude-kit` plugin itself. All are recoverable from git history on this branch. (The separate
umbrella **repo** `kmacmcfarlane/claude-kit` is unaffected and keeps its name.)
