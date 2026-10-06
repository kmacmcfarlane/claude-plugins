---
id: claude-md-cc-scan-crlf-deny-list-entries-6e74
title: "CLAUDE.md cc_scan: CRLF deny-list entries and a failed git log read as clean"
short_display_name: cc_scan false-clean edges
type: chore
status: todo
priority: 3
created: 2026-10-06
updated: 2026-10-06
refs:
  - claude-md-never-commit-verbatim-claude-c-6a07
---

6a07 review r3 lows, 2026-10-06: (1) under GNU grep a deny-list entry with a CRLF ending keeps the CR and silently matches nothing (ugrep tolerates it); (2) no pipefail: a failed git log (mistyped ref, or the <ref> placeholder pasted literally) feeds empty input and the scan prints nothing. Acceptance: both produce a stderr warning or a failing status.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
