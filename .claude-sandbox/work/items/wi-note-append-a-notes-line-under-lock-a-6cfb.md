---
id: wi-note-append-a-notes-line-under-lock-a-6cfb
title: "wi note: append a Notes line under lock, and have checkpoint 4a½ use it in place of its inline snippet"
short_display_name: wi note command for residue
type: feature
status: todo
priority: 2
created: 2026-10-08
updated: 2026-10-08
refs:
  - checkpoint-before-the-manifest-write-con-6c43 review 4
---

From the 6c43 review 4 (lows 1-3, nits 4-5) and implementer open questions, 2026-10-08: checkpoint Step 4a½ carries a 22-line inline python insert that mirrors wi's Notes append but lacks its cross-section fence refusal, whitespace-tolerant heading match and lock, and has no test. Acceptance: wi note <id> "<line>" reuses Item.append_note (fence refusal, lock, CRLF, atomic write), with tests; checkpoint 4a½ calls it and drops the snippet; the unattended path may then write items.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
