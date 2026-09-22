---
id: statusline-hub-status-says-a-wrap-is-run-90ee
title: statusline-hub --status says a wrap is running when wrap_applies refuses it
type: bug
status: doing
priority: 4
owner: unknown@360f41058e92
claimed: 2026-09-22T00:26Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - 7e71 reviewer
---

From 7e71 review r2 (low): hub.py status() ignores registry.wrap_applies; a hand-edited wrap.json claiming a project source runs nothing but --status prints 'wrap: running - the statusLine that was in <project file>'. Print 'kept, not run (not the user settings file)' instead; test.

## Handoff
- doing: implementer dispatched (opus, agent a8e8ee739fdd26d21)
- next: review r1 (opus)
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
- dispatch: implementer opus — hub code
