---
name: ai-scripts
description: Provides context about the ai-scripts repository - a collection of independent Python CLI utilities for AI-related tasks (caption_util, llm_fetch, token_count, token_embedding_search, generate_rare_token). Use when working in the ai-scripts repo, adding new tools, modifying existing tools, or when the user asks about HuggingFace model fetching, GGUF conversion, token counting, caption file management, or rare token generation. Do NOT use for general Python questions unrelated to this project.
disable-model-invocation: false
allowed-tools: Read, Glob, Grep
---

# ai-scripts Project Reference

This skill provides context for the ai-scripts repository, a collection of independent Python CLI utilities for AI-related tasks. Each tool lives in its own directory with a corresponding bash wrapper in `bin/`.

## Architecture

- **Modular tools**: Each utility is self-contained in its own directory (no cross-imports between tools)
- **Wrapper pattern**: Shell scripts in `bin/` delegate to Python scripts, handling venv setup and path resolution
- **No shared library**: Tools are independent; they don't share code

## When to consult references

### `references/tools.md`
**Read when:** You need details about any specific tool - its purpose, CLI arguments, dependencies, or implementation details.

Contains:
- Full tool inventory with directory paths and purposes
- CLI usage examples for each tool (shell wrapper and direct Python invocation)
- Per-tool dependencies and configuration
- Tool-specific conventions (backup behavior, config files, etc.)

### `references/development.md`
**Read when:** You need to add a new tool, understand project conventions, or modify the wrapper/venv pattern.

Contains:
- Step-by-step guide for adding a new tool
- Shell wrapper pattern with venv management
- Project conventions (argparse, stderr/stdout, exit codes, YAML config)
- Dependency management approach
- Build/test/lint status (none configured)

## Tools Overview

| Directory | Purpose |
|-----------|---------|
| `caption_util/` | Combine/split caption files for batch editing; rename files by extension |
| `llm_fetch/` | Clone HuggingFace models (full repo, subdir, or single file), convert to GGUF, optionally quantize |
| `token_count/` | Count tokens using HuggingFace tokenizers |
| `token_embedding_search/` | Find semantically similar tokens using model embeddings (cosine similarity) |
| `generate_rare_token/` | Find rare single-token candidates by distance from a common-token centroid |

## Key Conventions

- CLI arguments use argparse with long flags (`--model`, `--input-dir`) and short flags where applicable
- Error output goes to stderr; normal output to stdout
- Exit code 0 for success, 1 for errors
- Subprocesses use list-based args (no `shell=True`) to avoid injection
- Config files use YAML (gitignored; see example configs as templates)
- No build step, test framework, or linter is configured
- Do not include "co-authored by claude" messages when committing code
