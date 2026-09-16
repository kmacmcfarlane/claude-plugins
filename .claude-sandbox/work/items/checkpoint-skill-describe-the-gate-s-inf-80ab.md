---
id: checkpoint-skill-describe-the-gate-s-inf-80ab
title: "checkpoint skill: describe the gate's inferred-depth source label"
type: chore
status: done
priority: 3
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - implementer report 2026-09-16
---

Follow-up from context-gate-hard-stop-on-1m-context-mod-99cb: checkpoint/SKILL.md Step 1 says 'The gate state gives exact depth'; after the fix the source may be inferred (never hard-blocking). One-paragraph doc alignment; also decide whether install_statusline.py usage text './.claude/settings.json' should be reworded so the skill lint passes cleanly.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

Also (reviewer of 99cb, round 1): plugins/claude-kit/skills/checkpoint/references/operator-playbook.md:23-25
still says HARD "blocks every prompt except /checkpoint, /compact, /clear"; after 99cb only an EXACT depth
blocks, and plugin-prefixed forms (/claude-kit:checkpoint) are whitelisted too. Align this in the same edit.

## Notes
- 2026-09-16 claimed by unknown@4d338747396e

Scope decided by the librarian: checkpoint/SKILL.md (Step 1 wording), checkpoint/references/operator-playbook.md
(HARD description), install-statusline/scripts/install_statusline.py (usage text: replace './.claude/...' with
'.claude/...' so the skill-folder lint passes; no behaviour change).
dispatch: implementer opus — rule 2 (scripts/ in scope)
dispatch: reviewer opus — rule 4
- implementer opus returned DONE_WITH_CONCERNS, commit 54c721f. Concern: checkpoint skill folder trips the
  non-bare-path lint on './HANDOFF.md' (SKILL.md and references/handoff-format.md), pre-existing on main.
  Librarian ruling: out of scope here; it is a cwd write target, not a reference path — the checklist already
  says such hits are reviewed by eye. Filed as a P4 chore to reword to 'HANDOFF.md in the cwd' so the lint is
  clean without narrowing it.
- reviewer opus round 1 dispatched 2026-09-16 16:43:31
- review round 1: NEEDS_CHANGES — 1 medium (SKILL.md says the state file carries the source label; it is derived at read time by lib_context.depth, exact only while the record is <600s old), 3 low (third label 'inferred, window from status line' unmentioned; inferred warning is on the DUE cadence, not every prompt; the script docstring edit is invisible to --help), 1 nit (wrapping). Reviewer dirtied a tracked pyc via py_compile (worktree predates the pyc untrack landing) — implementer to restore. Fix round 1 sent 2026-09-16 16:46:11, tier unchanged (opus, resumed).
- fix round 1 returned DONE_WITH_CONCERNS, new commit 1c044fc; declined finding 4 (argparse __doc__ wiring is a behaviour change, out of scope — librarian agrees); re-review dispatched 2026-09-16 16:47:36 (reviewer opus, resumed)
- 2026-09-16 done: 4bf0d53
- re-review CLEAR: findings 1,2,3,5 FIXED, 4 DECLINED (accepted), 6 (tracked pyc) already landed separately as 3744. Landed merge 4bf0d53 2026-09-16 16:49:36.
