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
verdict: plan review 1 NEEDS_CHANGES (must-fix 2: the probe reads any failure as an old wi; other wi note exits lose the residue; lows: replace range :216-247, -- before texts, fence paragraph; nits)
dispatch: planner opus high — plan fix round 1 (resume ab90561988a81d4b4)
return: DONE series 01_plan-review-1-fixes.md (fixes 1-7; allow_abbrev left as wi's other verbs, with -- before texts)
baseline: plan review 2 — ef77493b63a68ee08bf7cf9e15675429bf5b0b0db8fb6b90cafb8f0772da7c8a .claude-sandbox/investigations/wi-note-append-a-notes-line-under-lock-a-6cfb/00_initial.md; 55f8d3c7113066e5b04055b0e0f23c33b6a2d4f174a3ec26a87d45d3f25bd05f .claude-sandbox/investigations/wi-note-append-a-notes-line-under-lock-a-6cfb/01_plan-review-1-fixes.md; 
dispatch: reviewer opus high — plan review 2 (resume a3d9552bce742b04d)
verdict: plan review 2 NEEDS_CHANGES (must-fix 1, down from 2: exit 1 also means a rejected front-matter value or a missing store, and the reword loop is unbounded; low: probe-127 Next wording)
dispatch: planner opus high — plan fix round 2 (resume ab90561988a81d4b4)
return: DONE series 02_exit-1-routing.md (text <n>: refusal prefix; one reword; other exit 1 routes to Aware of; probe Next wording)
baseline: plan review 3 — ef77493b63a68ee08bf7cf9e15675429bf5b0b0db8fb6b90cafb8f0772da7c8a .claude-sandbox/investigations/wi-note-append-a-notes-line-under-lock-a-6cfb/00_initial.md; 55f8d3c7113066e5b04055b0e0f23c33b6a2d4f174a3ec26a87d45d3f25bd05f .claude-sandbox/investigations/wi-note-append-a-notes-line-under-lock-a-6cfb/01_plan-review-1-fixes.md; 5dec4ec4468dad2fdaa92bcb2e915326fc81e200b173a1d2b8fe17b2978b5c1a .claude-sandbox/investigations/wi-note-append-a-notes-line-under-lock-a-6cfb/02_exit-1-routing.md; 
dispatch: reviewer opus high — plan review 3 (resume a3d9552bce742b04d)
verdict: plan review 3 CLEAR (must-fix 0)
findings: carried — (1) reword once per text n (a refusal naming a text not yet reworded is that text's first), then re-run the call; (2) the secret refusal message is text {n}: <secret_findings reason>; nothing written (the reason already carries its parenthetical)
target: full main /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/wi-note-append-a-notes-line-under-lock-a-6cfb
budget: 2026-10-08T06:22Z build $22 — default other build
dispatch: implementer opus medium — build from the CLEAR series (CLI code, tests, skill wording)
agent: implementer a4cea3b5b72b49074
