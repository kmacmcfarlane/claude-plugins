---
id: status-line-its-own-independently-instal-3c48
title: "status line: its own independently installable plugin"
type: feature
status: todo
priority: 1
parent: spike-should-the-status-line-be-its-own-fb55
created: 2026-09-18
updated: 2026-09-18
refs:
  - operator message 2026-09-18
---

Operator 2026-09-18: split the status line out of context-guard into its own plugin, shareable with coworkers and installable without any other kmacmcfarlane plugin. Coupling today: statusline.py imports lib_context (thresholds, update_state, load_state, _base_dir); it writes exact depth + rate_limits into context-guard's state file (claude-kit/context-gate/<sid>.json), read by context-guard's gate and librarian-mode's fable fallback; context-guard's rehydrate.py restores/migrates the statusLine setting; install-statusline skill lives in context-guard. Acceptance: new plugin (name: statusline, unless the operator objects) with statusline.py, a vendored minimal state helper (atomic, locked write), the install-statusline skill, and its own SessionStart self-heal for the statusLine setting; works standalone (default gauge thresholds; reads context-guard's published thresholds when present — decision 17 -> publish); keeps writing the same sensor record so context-guard and librarian-mode keep working (data contract, documented, soft in both directions); context-guard stops owning statusLine and hands existing installs over without clobbering; marketplace.json, README catalog, CLAUDE.md layout/placement in the same commit; coworker-facing install instructions in the skill. Lands after the 3685+fe33 bundle (same files). Design plan first (opus) -> librarian review -> implement.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
