# claude-plugins

Claude Code plugin marketplace for Kyle McFarlane.

## Plugins

### claude-kit

Claude Code development tooling — reusable across projects.

| Skill | Description |
|-------|-------------|
| `create-skill` | Bootstrap new Claude Code skills from a description |
| `sandbox` | claude-sandbox Docker setup, config, troubleshooting |
| `update-kit` | Sync files upstream to claude-templates/claude-plugins/claude-sandbox |
| `new-project-from-template` | Create a new project from a claude-templates template |
| `backlog-entry` | Create backlog entries (stories, bugs, refactoring) |
| `backlog-grooming` | Conversational backlog grooming and UAT review |
| `backlog-yaml` | backlog.yaml CLI management |
| `goa` | Design-first API development with Goa v3 for Go |
| `musubi-tuner` | LoRA training/inference with kohya's musubi-tuner |
| `playwright` | End-to-end testing with Playwright |
| `chain-of-verification` | CoVe fact-verification pipeline |
| `code-comments` | Rules for writing and reviewing code comments |

### ai-scripts

Context skills for the [ai-scripts](https://github.com/kmacmcfarlane/ai-scripts) repo — Python CLI utilities for AI tasks.

| Skill | Description |
|-------|-------------|
| `ai-scripts` | Project context for caption_util, llm_fetch, token_count, and more |

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

## Updating skills

Skills are authored directly in this repo under `plugins/<plugin>/skills/<skill>/`.

For the claude-kit plugin, skills are authored in-place in this repo.

## Structure

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json         # Plugin index (points to ./plugins/)
├── plugins/
│   ├── ai-scripts/              # AI utility tools
│   │   └── skills/
│   │       └── ai-scripts/
│   └── claude-kit/              # Dev tooling
│       └── skills/
│           ├── backlog-entry/
│           ├── backlog-grooming/
│           ├── backlog-yaml/
│           ├── chain-of-verification/
│           ├── create-skill/
│           ├── goa/
│           ├── musubi-tuner/
│           ├── new-project-from-template/
│           ├── playwright/
│           ├── sandbox/
│           └── update-kit/
└── README.md
```
