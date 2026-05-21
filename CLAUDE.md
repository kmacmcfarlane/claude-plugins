# claude-plugins

Plugin marketplace repo for Claude Code skills.

## Repository Layout

```
plugins/
  claude-kit/          # Primary dev tooling plugin
    agents/            # Agent definitions (.md files, auto-loaded)
      <agent-name>.md
    skills/            # All skills live here
      <skill-name>/
        SKILL.md
        references/
        scripts/
        assets/
  ai-scripts/          # AI utility tools plugin
    skills/
      <skill-name>/
        SKILL.md
```

## Conventions

- **Skill location**: `plugins/claude-kit/skills/<name>/SKILL.md` (not `.claude/skills/`)
- **Agent location**: `plugins/claude-kit/agents/<name>.md` — auto-loaded by the plugin system. Agent `.md` files define role, tools, and model. Task-specific context is injected via the Agent prompt, not baked into the definition.
- **Plugin registry**: `.claude-plugin/marketplace.json` — update when adding new plugins (not when adding skills to existing plugins).

## When Creating Skills (`/create-skill`)

Place new skills at `plugins/claude-kit/skills/<name>/` unless the user specifies a different plugin.
