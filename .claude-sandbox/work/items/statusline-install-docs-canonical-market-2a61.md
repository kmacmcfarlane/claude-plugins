---
id: statusline-install-docs-canonical-market-2a61
title: "statusline install docs: canonical marketplace URL, auto-update, already-declared error"
type: chore
status: done
priority: 1
parent: status-line-its-own-independently-instal-3c48
created: 2026-09-18
updated: 2026-09-19
closed: 2026-09-19
refs:
  - operator message 2026-09-18
---

Operator 2026-09-18 hit: 'Cannot add marketplace "kmacmcfarlane": its network source differs from the one declared for it in settings' running 'claude plugin marketplace add kmacmcfarlane/claude-plugins' — their ~/.claude/settings.json extraKnownMarketplaces declares kmacmcfarlane as source git url https://github.com/kmacmcfarlane/claude-plugins.git (autoUpdate already true in known_marketplaces.json). Verified in the 2.1.277 binary: extraKnownMarketplaces entries accept optional autoUpdate (bool, 'Whether to automatically update this marketplace') synced into known_marketplaces; 'claude plugin marketplace add' has no auto-update flag (options: --scope, --sparse, --claudeai). Acceptance: statusline SKILL.md coworker section + README install example use the canonical source https://github.com/kmacmcfarlane/claude-plugins.git; document enabling auto-update (/plugin UI, or the settings extraKnownMarketplaces entry with autoUpdate: true + enabledPlugins); troubleshooting entry for the 'network source differs' error (already declared -> marketplace update, or match the declared source).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer sonnet — default (docs only)

impl: DONE 6048277
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (README settings example still github/repo form — causes the same mismatch), 2 (update fix fails "not found" until a session reconciles the settings declaration); low 3 (enabledPlugins + which settings file), nit 4.
dispatch: implementer sonnet fix round 1 — resume

fix round 1 (sonnet): DONE 472877c (1-3; declined nit 4).
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): CLEAR (2 nits, not re-dispatched).
- 2026-09-19 done: a618a04
