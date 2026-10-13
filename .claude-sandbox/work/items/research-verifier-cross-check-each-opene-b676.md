---
id: research-verifier-cross-check-each-opene-b676
title: "research verifier: cross-check each Opened target against the verifier's own transcript"
short_display_name: verifier opened-source transcript check
type: feature
status: todo
priority: 3
created: 2026-10-13
updated: 2026-10-13
refs:
  - research-verifier-fix-its-procedure-faul-2e75
---

From 2e75 review 2026-10-13: the sheet's Opened cell is self-reported, so an unopened source can still be claimed. Acceptance: check-sheet.py --transcript <subagent jsonl> confirms each Opened target matches a real fetch or read call in that run, and flags fetch prompts that state the claim's figure (fault 3, neutral prompts).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
