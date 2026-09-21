---
id: doctrine-codify-hard-plugin-dependencies-5343
title: "doctrine: codify hard plugin dependencies (principles 2/4) + declare ralph→sandbox"
type: chore
status: doing
priority: 1
parent: spike-status-line-multiplexer-dependency-d193
owner: unknown@360f41058e92
claimed: 2026-09-21T18:01Z
created: 2026-09-19
updated: 2026-09-21
refs:
  - operator decision 42
---

Operator decision 42(a) 2026-09-19: amend README principles 2 and 4 to allow a framework-declared hard dependency (plugin.json dependencies) only when the dependent has no function without the support plugin, same marketplace; data readers stay soft. Present the current and proposed hard-dependency graph first (done in the 2026-09-19 report); codify the approach explicitly in README doctrine + catalog 'Depends on' notation + create-skill/checklist where they check dependencies. Also declare the one existing hard edge ralph→sandbox in plugins/ralph/.claude-plugin/plugin.json. Precedes d193 F3 (statusline→statusline-hub).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-21 claimed by unknown@360f41058e92

## Dispatch
- dispatch: implementer opus — doctrine (README principles, catalog), marketplace shape (plugin.json dependencies)
