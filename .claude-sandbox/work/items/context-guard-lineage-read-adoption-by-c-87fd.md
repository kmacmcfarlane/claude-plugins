---
id: context-guard-lineage-read-adoption-by-c-87fd
title: "context-guard lineage: Read adoption by content match; reject empty session id"
type: chore
status: todo
priority: 3
created: 2026-09-22
updated: 2026-09-22
refs:
  - 5126 review r2
---

From 5126 review r2 (CLEAR), 2026-09-22: (1) lineage.py adopts by sha of the file at hook time, not the Read's content — when tool_response.type=='text', numLines==totalLines and no truncatedByTokenCap, adopt only if content matches the file on disk (trailing newlines ignored); else (incl. file_unchanged) keep today's behaviour; (2) mark_checkpoint.py: reject an empty $CLAUDE_CODE_SESSION_ID before the state lookup (today maps to unknown.json).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
