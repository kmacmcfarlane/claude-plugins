---
id: statusline-hub-status-says-a-wrap-is-run-90ee
title: statusline-hub --status says a wrap is running when wrap_applies refuses it
type: bug
status: todo
priority: 4
created: 2026-09-22
updated: 2026-09-22
refs:
  - 7e71 reviewer
---

From 7e71 review r2 (low): hub.py status() ignores registry.wrap_applies; a hand-edited wrap.json claiming a project source runs nothing but --status prints 'wrap: running - the statusLine that was in <project file>'. Print 'kept, not run (not the user settings file)' instead; test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
