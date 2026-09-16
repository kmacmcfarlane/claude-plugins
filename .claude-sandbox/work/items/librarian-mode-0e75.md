---
id: librarian-mode-0e75
title: Create kit-dev librarian-mode skill
type: feature
status: done
priority: 1
tags: [kit-dev]
created: 2026-09-04
updated: 2026-09-04
closed: 2026-09-04
---

Operator request (2026-09-04): a kit-dev skill that puts a session into librarian mode — standing single-writer custodian of this plugin repo. Intake requests from operator and peer agents, file work items per request, factor into features, delegate each to a background agent in a worktree, review what lands, report briefly (changed / verified / open questions / decisions needed). Background: agents/retro/2026-09-04-session-organization-and-librarian-topology.md (agents repo). Investigation series: librarian-mode. Built via create-skill once the proposal is reviewed.

## Handoff
- doing: Build agent running on worktree-librarian-mode (stacked on plugin-factoring); operator now wants it landed on main under plugins/claude-kit/skills/ instead
- next: When the build reports: re-target to a branch off main (claude-kit layout, main's docs), run checks, merge into main, note migration in land-plugin-factoring-fbe8
- blocked: —
- learned: Landing on main means the old claude-kit layout; migration to kit-dev happens with the refactor

## Notes
- 2026-09-04 claimed by unknown@ce2454879853
- 2026-09-04 learned: No decision log for now (specs/backstage later). Operator reviews what landed + decisions; librarian merges. Present options+impacts at intake only when real tradeoffs exist.
- 2026-09-04 learned: Main checkout switched to main 2026-09-04; wi CLI on main is not at the kit-dev path, use the plugin-factoring worktree copy with --root .claude-sandbox/work
- 2026-09-04 learned: Landing on main means the old claude-kit layout; migration to kit-dev happens with the refactor
- 2026-09-04 done: e1b3459 merged to local main (merge of f138d1c); kit-dev-layout variant kept on branch worktree-librarian-mode (f1f07ca) for the migration
