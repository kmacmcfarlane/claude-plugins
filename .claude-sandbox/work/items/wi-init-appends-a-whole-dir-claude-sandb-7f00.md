---
id: wi-init-appends-a-whole-dir-claude-sandb-7f00
title: wi init appends a whole-dir /.claude-sandbox/ ignore even in a private-shaped repo
type: bug
status: done
priority: 2
created: 2026-09-06
updated: 2026-09-08
closed: 2026-09-08
refs:
  - ../agents/decisions/0002-file-classes.md
---

Observed 2026-09-06 in kmacmcfarlane/operator-attention (fresh private repo, .claude-sandbox/ present, no sidecar git): wi init added '/.claude-sandbox/' to .gitignore, silently un-tracking the new store; a later git add -A committed nothing. Private shape must track config + work (0002 template); related: claude-sandbox a7bf (layout appends contradictory gitignore lines), claude-plugins 37d3.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-08 claimed by librarian
- 2026-09-08 done: c59f9cf merged to local main; review CLEAR round 1; premise corrected: policy feature, not bug fix

## Review
- Round 1 (c7234fb): CLEAR — 39 tests OK; 8 adversarial shape cases live-fired (gitlink
  sidecar, ignore spellings, negation lines, .work-beside-sandbox, double init, no git,
  newline-less gitignore); 3 low + 2 nit accepted as-is.
- PREMISE CORRECTED (implementer forensics, independently confirmed by reviewer from git
  history): wi.py never wrote the /.claude-sandbox/ ignore — the incident line was added by
  hand by a session in operator-attention (real culprit tracked as claude-sandbox item a7bf).
  This landing is therefore a POLICY FEATURE (wi init owns the 0002 per-shape gitignore
  policy: private = leave host .gitignore alone; sidecar = ensure whole-dir ignore; ignored =
  untouched), not a bug fix. The sidecar append is new behavior. Type left as filed; operator
  may revert the merge if the reclassification is unwanted.
- Known lows (accepted): ..-containing WI_ROOT misclassifies; unreadable/non-UTF-8 host
  .gitignore tracebacks; glob ignore spellings not recognized (action still safe).

## Recurrence (2026-09-18)
- Also happens on `wi add`, not only `wi init`: in operator-attention the line was removed and committed (e5516d2), and a later `wi add` re-appended `/.claude-sandbox/` to the working-tree .gitignore, so the new item was silently ignored.
