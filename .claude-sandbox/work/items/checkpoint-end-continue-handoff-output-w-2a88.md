---
id: checkpoint-end-continue-handoff-output-w-2a88
title: "checkpoint: end continue/handoff output with a ready-to-paste next-session prompt"
type: feature
status: done
priority: 2
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
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
- implementer sonnet returned DONE, commit 3b565e8; deviation: removed Step 5's old stage-boundary opener block as a narrower duplicate of the new Step 7 — reviewer to rule. Reviewer opus round 1 dispatched 2026-09-16 17:59:13
- review round 1: NEEDS_CHANGES — 1 medium (the deleted Step 5 block carried 'do not re-run the previous stage — its outputs are published; read them as inputs' which now exists nowhere), 1 low ('read <path> first' lost 'in full' and the mode declaration; after /clear the hook injects only the header). Reviewer note for the operator: the Lean path (<60K left) skips Steps 5-7, so the opener is skipped exactly when a handoff is likeliest — promote it into the lean path? Fix round 1 sent 2026-09-16 18:01:26, tier unchanged (sonnet, resumed).
- fix round 1 returned DONE, new commit c584f65 (warning restored inside Step 7's opener; 'in full'). Re-review dispatched 2026-09-16 18:02:28 (reviewer opus, resumed).
- 2026-09-16 done: e365d99
- re-review CLEAR (both FIXED; 1 new low: the restored parenthetical lost its 'if your chain records…' conditional — not sent back). Landed merge e365d99 2026-09-16 18:04:12.
