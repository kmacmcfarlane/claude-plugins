---
id: wi-batch-write-refusal-should-name-the-i-9d8c
title: "wi: batch-write refusal should name the item holding a control character"
type: chore
status: dropped
priority: 4
created: 2026-09-21
updated: 2026-09-21
closed: 2026-09-21
---

From the 0401 final review (low): one hand-written item with a control character makes every batch write (export, archive, import --update) fail; the error names the key but not the item. Include the item id/path in the WiError.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- folded into wi-b020-review-lows-export-round-trip-is-bc6b (librarian 2026-09-21): same wi.py export/write surface; one branch avoids three-way conflicts

## Notes
- 2026-09-21 dropped
