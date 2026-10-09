---
id: statusline-hub-carry-the-marker-s-scope-5c0c
title: "statusline-hub: carry the marker's scope through heal and the blocked marker"
short_display_name: hub keeps install scope
type: bug
status: todo
priority: 4
created: 2026-10-09
updated: 2026-10-09
refs:
  - statusline-hub-refuse-to-write-its-entry-fe79
---

From fe79 review 2: heal's _put (session_start.py:216) and the blocked marker (:688-689) drop the new scope field, so an explicit --project install that heals once later gets the general tracked line instead of 'rerun --project'. Also record scope for --settings <project>/.claude/settings.json (install_hub.py:300-301). Wording only.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
