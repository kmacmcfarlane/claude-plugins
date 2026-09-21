---
id: librarian-series-home-durable-path-not-t-1dab
title: "librarian Series home: durable path, not the session scratchpad"
type: chore
status: todo
priority: 2
created: 2026-09-21
updated: 2026-09-21
---

Noticed by the librarian at the F2 landing (2026-09-21). librarian-mode binds Series home to 'your scratchpad (.claude-sandbox/ is outside every Scope)', preserved from before F2. But the scratchpad is session-scoped: a later session cannot find a spike's series, and F2 now closes a spike with 'wi done --note <series path>' pointing there. In practice this session wrote spike series to $MAIN/.claude-sandbox/investigations/<slug>/ (d193, 7e3b), which is dev-cycle's default and where /implement looks. Acceptance: librarian Series home = $MAIN/.claude-sandbox/investigations/<slug>/ (tooling-owned like the store: written by the cycle, never a custody edit), in librarian-mode's bindings and dev-cycle bindings.md's librarian row; say why it is not a Scope violation (same class as the store).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
