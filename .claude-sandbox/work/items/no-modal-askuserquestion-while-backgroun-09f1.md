---
id: no-modal-askuserquestion-while-backgroun-09f1
title: "no modal AskUserQuestion while background agents run: dev-cycle, investigate, implement, checkpoint"
type: chore
status: doing
priority: 2
owner: Kyle-McFarlane@7696505da8e1
claimed: 2026-09-28T22:46Z
created: 2026-09-22
updated: 2026-09-28
refs:
  - 7117 OQs
---

From 7117 (operator ruling, answer 58) open questions, 2026-09-22: standalone dev-cycle § Decisions (one pending decision via AskUserQuestion while its implementer/reviewer may run); investigate Step 11 (asks while a background verify batch runs); implement Step 6 review gate (asks while a Step-3 agent may run); context-guard checkpoint Step 0 (called mid-session with the caller's agents in flight). Decide per skill: numbered channel whenever an agent may be in flight; keep closed-choice dialogs only where nothing runs.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: branch worktree-no-modal-askuserquestion-while-backgroun-09f1 at .claude/worktrees/no-modal-askuserquestion-while-backgroun-09f1, base main (b29422b)

## Notes
- 2026-09-28 claimed by Kyle-McFarlane@7696505da8e1
dispatch: implementer opus — changes what four skills do (rule 2)
agent: implementer a44821e7103e482ac round 1
