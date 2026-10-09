---
id: statusline-hub-carry-the-marker-s-scope-5c0c
title: "statusline-hub: carry the marker's scope through heal and the blocked marker"
short_display_name: hub keeps install scope
type: bug
status: done
priority: 4
created: 2026-10-09
updated: 2026-10-09
closed: 2026-10-09
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
verdict: review round 1 CLEAR (lows: owner.py marker docstring out of date; two heal routes untested; no test that --settings to a shared project file prints the warning; nits accepted); all 12 Checks pass
decided: 2026-10-09T10:48Z cap — finish round of lows 1-3 (authority answer 145)
dispatch: implementer opus medium — finish round (resume ab06ebc39752e7ec6)
return: DONE ac84873 (marker spec updated; two heal-route tests fail without the scope; installer warning test; 12/12 Checks)
review: self
verdict: finish round CLEAR — diff read: docstring and three tests, no code change
landed: 4533ac5 (merge of a44a0ea, ac84873); Checks 12/12 OK
- 2026-10-09 done
