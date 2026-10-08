---
id: statusline-hub-refuse-to-write-its-entry-fe79
title: "statusline-hub: refuse to write its entry into a project's tracked .claude/settings.json"
short_display_name: hub writes tracked project settings
type: bug
status: todo
priority: 3
created: 2026-10-08
updated: 2026-10-08
refs:
  - statusline-hub-end-the-silent-wait-behin-7dd3 review 1
---

From the 7dd3 review 1 (low 2), 2026-10-08: the dead-copy take path guards only settings.local.json, so a dead copy in a project's tracked .claude/settings.json (the old installer's --project) is replaced with the hub's machine-specific absolute path. Acceptance: decide whether tracked files are refused or said once; a test pins it.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
