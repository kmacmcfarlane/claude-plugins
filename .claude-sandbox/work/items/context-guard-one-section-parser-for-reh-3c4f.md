---
id: context-guard-one-section-parser-for-reh-3c4f
title: "context-guard: one section parser for rehydrate and read_list (tab headings, code fences)"
type: refactor
status: todo
priority: 3
created: 2026-09-23
updated: 2026-09-23
refs:
  - c121 implementer
---

c121 implementer OQ, 2026-09-23: rehydrate._sections splits on '^## ' and ignores fences; read_list has its own parser that now accepts '##<tab>' and fences. A shared parser in lib_context would change rehydrate's Holds/trim behaviour on manifests with tab headings or fenced '## ' lines — needs its own plan. Also: a fence opened inside Read-in-full and never closed silently drops the rest of that section.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- rider from c121 review r2 (2026-09-23): make withhold_next fence-aware — it can remove a closing fence inside ## Next (list lost, note silent) or an opener (note suppressed); fixes both directions at the root.
