# claude-plugins

Claude Code plugin marketplace. **The doctrine — the seven principles every plugin is
measured against, plus naming practices and the catalog — lives in [README.md](README.md).**
Read it before adding or moving anything. This file carries only the mechanics: where files
go today, and where they are planned to go.

Do not restate the principles here; restated rules drift.

## Repository Layout

```
plugins/
  claude-kit/          # Dissolving kitchen-sink plugin (see README catalog)
    skills/
      <skill-name>/
        SKILL.md
        references/
        scripts/
        assets/
  context-guard/       # Surviving the context window (the only hook-owning plugin)
    hooks/             # Gate, statusline sensor, ledger, rehydrate + unit tests
    skills/
      {checkpoint,install-statusline}/
  dev-flow/            # Plan before you code
    skills/
      {investigate,implement,deep-investigation,chain-of-verification}/
  work-items/          # Repo-durable work items + the work-source provider interface
    skills/
      work-items/      # wi CLI, references/{format,provider-interface}.md, tests/
  sandbox/             # Isolated container execution (claude-sandbox)
    skills/
      sandbox/
  ralph/               # Unattended agent loops over a backlog
    skills/
      {backlog-yaml,backlog-entry,backlog-grooming}/
  chat/                # Skills for LLM chat sessions in web UIs
    skills/
      <skill-name>/SKILL.md
```

## Conventions

- **Skill location**: `plugins/<plugin>/skills/<name>/SKILL.md` (never `.claude/skills/`).
- **Agent location**: `plugins/<plugin>/agents/<name>.md` — auto-loaded by the plugin system.
  Agent `.md` files define role, tools, and model. Task-specific context is injected via the
  Agent prompt, not baked into the definition. *No plugin here ships agents today* — the last
  three were retired with the deprecated plan-execution skill they served (Phase 3).
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
   whose stated aim *is* that behavior (`plugins/context-guard/`). Never attach it to a
   knowledge skill.
2. Pure stack/tool knowledge? → the expertise family, in its own marketplace (`expertise`,
   repo `claude-expertise`) — not this repo.
3. For web-UI chat sessions rather than a coding harness? → the `chat` family (home under
   review).
4. Otherwise, a harness capability: find its aim in the table below and use the **current
   home** column.
5. No aim fits? → new aim, new plugin. Write its catalog row first.

### Aim → home

Planned homes are **provisional** pending operator review, and none of them exist yet except
where a row says **landed**. Write files to the *current* home; each factoring phase moves its
own rows and updates this table.

| Aim | Current home | Target home (planned) |
|---|---|---|
| Survive the finite context window (gate, gauge, checkpoint, rehydration) | `plugins/context-guard/` | `plugins/context-guard/` — **landed** (Phase 1) |
| Plan-before-code development flow | `plugins/dev-flow/` | `plugins/dev-flow/` — **landed** (Phase 3) |
| Repo-durable work items / work-source interface | `plugins/work-items/` | `plugins/work-items/` — **landed** (Phase 4) |
| Isolated container execution | `plugins/sandbox/` | `plugins/sandbox/` — **landed** (Phase 5) |
| Unattended agent loops over a backlog ("ralph") | `plugins/ralph/` | `plugins/ralph/` — **landed** (Phase 5) |
| Maintaining this kit itself | `plugins/claude-kit/skills/{create-skill,update-kit,new-project-from-template,factor-analysis}/` | `plugins/kit-dev/` |
| Stack expertise ("make Claude good at X") | the `expertise` marketplace (repo `claude-expertise`) — not this repo | moved to the expertise marketplace (local scaffold, remote pending) — **landed** (Phase 2) |
| Web-UI chat-session skills | `plugins/chat/` | family home under review |

Retired at Phase 3: the deprecated plan-execution skill under `plugins/claude-kit/skills/`
and `plugins/claude-kit/agents/`, which existed only to serve it. Both are recoverable from
git history on this branch.

### Known temporary inconsistency

`create-skill`'s own SKILL.md still says to place new skills in `claude-kit`. That is now only
the fallback, not the rule — the aim table above wins — and it will be aligned with this
decision tree when the `kit-dev` phase lands.
