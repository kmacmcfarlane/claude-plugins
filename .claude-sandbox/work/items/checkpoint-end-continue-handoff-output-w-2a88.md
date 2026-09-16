---
id: checkpoint-end-continue-handoff-output-w-2a88
title: "checkpoint: end continue/handoff output with a ready-to-paste next-session prompt"
type: feature
status: doing
priority: 2
owner: unknown@4d338747396e
claimed: 2026-09-16T17:56Z
created: 2026-09-16
updated: 2026-09-16
refs:
  - operator message 2026-09-16
---

Operator 2026-09-16 (relayed from a handoff checkpoint in another project, session f352f6e8; another session's librarian had declined it as out of scope there — it is in scope here, the checkpoint skill lives in this repo): when the checkpoint mode is continue or handoff, the LAST item of the skill's output is a ready-to-paste opening prompt for the next session after /clear: a fenced block, under ~5 lines, naming the skill or task to invoke, the manifest path to read first, and the one or two facts that changed since the manifest was written (example: '/kappa-jira-implement KAPPA-3446 — read .claude-sandbox/HANDOFF.md first; MR !104 closed as superseded; base branch kappa-3446 from main'). Place it after the drift note (Step 6) so it is the last thing on screen; Step 5's one-sentence recommendation stays. Acceptance: checkpoint/SKILL.md Steps 5/6 (or wherever the output order is defined) specify the block, its position, its size bound and its contents; references/operator-playbook.md mentions it in one line if it lists the output; the land mode is unchanged; SKILL.md under 5000 tokens; lint clean.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
dispatch: implementer sonnet — default (one skill, prose)
dispatch: reviewer opus — rule 4 floor

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
