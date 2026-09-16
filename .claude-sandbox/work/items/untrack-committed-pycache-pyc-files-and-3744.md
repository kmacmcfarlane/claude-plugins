---
id: untrack-committed-pycache-pyc-files-and-3744
title: untrack committed __pycache__ pyc files and gitignore them
type: chore
status: done
priority: 3
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - implementer report, item context-gate-hard-stop-on-1m-context-mod-99cb
---

Found by the context-gate implementer 2026-09-16: __pycache__/*.pyc under plugins/claude-kit/skills/{checkpoint,install-statusline,work-items} are tracked on main although .gitignore lists __pycache__/ and *.pyc. Acceptance: git rm --cached them; no tracked .pyc remain; ignore rules already cover them.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-16 claimed by unknown@4d338747396e

dispatch: implementer opus — rule 2 (more than three files)
dispatch: reviewer opus — rule 4
- implementer opus returned DONE, commit 0577f0c; reviewer opus round 1 dispatched 2026-09-16 16:42:21
- 2026-09-16 done: 7d068ab
- review CLEAR, no findings; landed merge 7d068ab 2026-09-16 16:44:13; main checks: 0 tracked pyc, wi tests OK, hook tests OK, marketplace==disk
