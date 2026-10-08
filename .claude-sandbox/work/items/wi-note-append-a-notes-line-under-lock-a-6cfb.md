---
id: wi-note-append-a-notes-line-under-lock-a-6cfb
title: "wi note: append a Notes line under lock, and have checkpoint 4a½ use it in place of its inline snippet"
short_display_name: wi note command for residue
type: feature
status: doing
priority: 2
owner: Kyle-McFarlane@2d49f8460283
claimed: 2026-10-08T05:43Z
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
target: plan main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude-sandbox/investigations/wi-note-append-a-notes-line-under-lock-a-6cfb
budget: 2026-10-08T05:43Z plan $28 — default plan
dispatch: planner opus high — plan

## Notes
- 2026-10-08 claimed by Kyle-McFarlane@2d49f8460283
agent: planner ab90561988a81d4b4
return: DONE series 00_initial.md (wi note <id> <text>... [--raw], secret-lint refusal, 4a½ uses it after a --help probe else manifest; unattended unchanged; other appenders named)
baseline: plan review 1 — ef77493b63a68ee08bf7cf9e15675429bf5b0b0db8fb6b90cafb8f0772da7c8a .claude-sandbox/investigations/wi-note-append-a-notes-line-under-lock-a-6cfb/00_initial.md; 
dispatch: reviewer opus high — plan review 1
agent: reviewer a3d9552bce742b04d
