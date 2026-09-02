---
id: context-guard-67ff
title: Extract context-guard plugin (hooks + checkpoint + install-statusline)
type: refactor
status: todo
priority: 1
deps:
  - doctrine-9411
parent: plugin-factoring-924b
created: 2026-09-02
updated: 2026-09-02
---

Move hooks/ (all of it - gate, statusline sensor, ledger, rehydrate, tests), checkpoint skill, install-statusline skill into new plugin context-guard. Migration: settings.json statusLine embeds plugins/data/claude-kit-<marketplace> absolute path - extend rehydrate self-heal to migrate the old entry, or re-run install-statusline per machine (blast radius: 2 machines). Keep dual-read fallback on old state dirs ~/.claude/claude-kit/{context-gate,ledger}/ for a transition. Analysis: session 2026-09-01/02 + investigation series.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
