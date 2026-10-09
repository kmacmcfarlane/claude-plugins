---
id: statusline-hub-carry-the-marker-s-scope-5c0c
title: "statusline-hub: carry the marker's scope through heal and the blocked marker"
short_display_name: hub keeps install scope
type: bug
status: doing
priority: 4
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-09T10:30Z
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

## Notes
dispatch: implementer opus medium — build, worktree
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer ab06ebc39752e7ec6
return: DONE worktree-agent-ab06ebc39752e7ec6 a44a0ea (scope kept on heal's three paths and the blocked marker; --settings to a project's shared file records project scope and now also prints the do-not-commit warning; tests fail on old code; reported 10 Checks)
dispatch: reviewer opus high — review round 1 of a44a0ea
agent: reviewer a8e7048fd866ffdb6
