---
id: packs-marketplace-bdfd
title: Stand up expertise-pack marketplace; move goa, playwright, musubi-tuner, ai-scripts
type: refactor
status: done
priority: 2
deps:
  - doctrine-9411
parent: plugin-factoring-924b
created: 2026-09-02
updated: 2026-09-02
closed: 2026-09-02
---

New marketplace repo for expertise packs (make-Claude-good-at-X), one plugin per stack, always standalone, no cross-refs. Move goa, playwright, musubi-tuner from claude-kit, and relocate ai-scripts. Users re-add the new marketplace and re-install; plugin data dirs are per-marketplace-named so expect fresh data dirs (none of these carry state). Scope changes 2026-09-02 (serial 01): chat is EXCLUDED - it is a third family (webui chat-session skills), home decided at morning review; the name "packs" is rejected by the operator - final repo name pends the naming research; overnight runs scaffold locally only, no remote repo creation.

## Handoff
- doing: implemented, pending review
- next: fable review, then wi done; remote repo creation is a morning decision
- blocked: —
- learned: —

## Notes
- 2026-09-02 claimed by unknown@e7c6135255e0
- 2026-09-02 done: claude-expertise@9419911+a7696a9, this repo 436dcc8+89d5539; fable review APPROVED; remote+registration is a morning step
