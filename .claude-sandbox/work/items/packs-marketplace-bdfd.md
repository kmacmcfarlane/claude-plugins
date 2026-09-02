---
id: packs-marketplace-bdfd
title: Stand up packs marketplace; move goa, playwright, musubi-tuner, ai-scripts, chat
type: refactor
status: todo
priority: 2
deps:
  - doctrine-9411
parent: plugin-factoring-924b
created: 2026-09-02
updated: 2026-09-02
---

New marketplace repo for expertise packs (make-Claude-good-at-X), one plugin per stack, always standalone, no cross-refs. Move goa, playwright, musubi-tuner from claude-kit, and relocate ai-scripts and chat plugins. Users re-add the new marketplace and re-install; plugin data dirs are per-marketplace-named so expect fresh data dirs (none of these carry state).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
