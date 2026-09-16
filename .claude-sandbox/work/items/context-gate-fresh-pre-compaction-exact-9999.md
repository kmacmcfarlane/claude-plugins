---
id: context-gate-fresh-pre-compaction-exact-9999
title: "context gate: fresh pre-compaction exact record can hard-block a new epoch"
type: bug
status: done
priority: 2
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - reviewer report, item context-gate-hard-stop-on-1m-context-mod-99cb
---

Found by the 99cb reviewer 2026-09-16 (pre-existing, not introduced): an exact record written by the status line seconds before a compaction is still fresh (<600s) after it, so context_warn.py hard-blocks a 3% post-compaction session with the old numbers until the status line re-renders. Acceptance: PostCompact (postcompact_epoch.py) invalidates or stamps the exact record so a pre-boundary record never drives a HARD stop in the new epoch; test covers it. Files: hooks/postcompact_epoch.py, hooks/lib_context.py, tests.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
Also (80ab reviewer): context_warn.py systemMessage hardcodes '(inferred)' while additionalContext prints the full src literal — align while in the file.

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
dispatch: implementer fable — rule 3 (hook that gates prompts)
dispatch: reviewer fable — rule 4
- implementer fable returned DONE, commit 93ae0d2 (demotion in reset_epoch: exact -> {window, at:0}); reviewer fable round 1 dispatched 2026-09-16 17:12:10
- 2026-09-16 done: 75e4dee
- review CLEAR; 2 lows not sent back (reset_epoch/postcompact docstrings do not mention the demotion; ordering assumption if the status line renders before PostCompact — safe direction) — recorded. Reviewer NOTES: pre-existing SessionStart(clear) read-modify-write race between rehydrate.py and postcompact_epoch.py, did not manifest in 15 trials. Landed merge 75e4dee 2026-09-16 17:15:30; 95 hook tests OK on main.
