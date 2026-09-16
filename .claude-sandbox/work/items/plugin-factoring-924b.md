---
id: plugin-factoring-924b
title: Refactor marketplace into aim-indexed plugins (dissolve claude-kit)
type: epic
status: done
priority: 1
created: 2026-09-02
updated: 2026-09-02
closed: 2026-09-02
---

Reshape this repo from one history-indexed kitchen-sink plugin into aim-named, standalone-installable plugins per the factoring doctrine settled 2026-09-02: one plugin one aim; standalone test; harness-behavior quarantine; soft declared directional deps; names are API; new aim = new plugin; README as problem-indexed catalog. Decisions: claude-kit dissolves (marketplace IS the kit); work-items becomes a support plugin; sandbox stands alone; expertise packs move to a second marketplace. Full plan: .claude-sandbox/investigations/plugin-factoring/ (local-only in this repo).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-02 done: all 7 children done; branch plugin-factoring 0b4983b..2e7ea0b, 11 commits, unpushed; claude-expertise scaffold local
