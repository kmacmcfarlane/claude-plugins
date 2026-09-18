---
id: librarian-mode-at-75-context-checkpoint-ce46
title: "librarian-mode: at 75% context, checkpoint (continue) and prompt the operator to compact"
type: feature
status: done
priority: 1
created: 2026-09-18
updated: 2026-09-18
closed: 2026-09-18
refs:
  - operator message 2026-09-18
---

Operator 2026-09-18: standard operating procedure for a librarian session whose context reaches 75% used: (1) put every open item's handoff in order (existing Ending-the-session rule), (2) push main per the push rule, (3) run the checkpoint skill with goal = continue, (4) end the turn prompting the operator to run /compact (at their convenience, e.g. the next morning) rather than compacting itself or starting new work; the checkpoint makes the compaction safe and the rehydration hook re-injects the manifest. The 75% trigger reads the status-line gauge / the context-gate advisory band (the gate already emits a 75% advisory). Acceptance: the rule is stated where a librarian will see it at the trigger (the 75% advisory arrives mid-session, so SKILL.md must carry at least a one-line trigger with a pointer to the procedure in references/ending-the-session.md); SKILL.md stays <= 19,000 chars (currently 18,969: pay with a duplication-only trim or put the procedure in the reference); Critical/Route/Red flags byte-identical. Land on main (the plugin-factoring branch carries it at merge via rename detection).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
dispatch: implementer opus — rule 2 (the librarian's own procedure / doctrine)
dispatch: reviewer opus — rule 4

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009
- implementer opus returned DONE_WITH_CONCERNS, commit 307dc21 (SKILL.md exactly 19,000 bytes; one pointer line; procedure in ending-the-session.md § At 75%). Librarian ruling on its open question: requests arriving after the checkpoint turn and before /compact are filed through Intake as usual and held (no dispatch, no merge) until after Rehydrate. Reviewer opus round 1 dispatched 2026-09-18 07:46:57.
- review round 1: NEEDS_CHANGES — 3 medium (the gate's DUE fires first on windows under ~333K so the 75% advisory never
  arrives; the held-requests ruling is missing and the gate stands down after a checkpoint; the checkpoint's own Steps 2-4a
  would edit custody files and commit straight to main), 3 low (push before the checkpoint's commits leaves origin behind;
  Step 5 recommends /rewind first; Step 0 still asks question 3), 2 low/nit (discoverability of the trigger line; opener
  wording; hard-coded BANDS; provenance in doctrine).
- librarian rulings (within the operator's intent, "reach 75%" = checkpoint before the window runs out): trigger is the
  FIRST of the 75% advisory, DUE, or the inferred-HARD advisory; order at the trigger is handoffs → checkpoint (continue)
  → push → closing message; the checkpoint's residue goes to item bodies or `wi add`, never custody files, and its
  commits are store-only; take the /compact arm of Step 5 and pre-answer Step 0 question 3 with it; requests after the
  checkpoint turn are filed and held (no dispatch, no merge) until after Rehydrate. Size limit stays bytes (wc -c ≤ 19,000).
  Fix round 1 sent 2026-09-18 07:49:41, tier unchanged (opus, resumed).
- fix round 1 returned DONE, commit d26ca72 (rulings A-F applied; SKILL.md 18,999 bytes). Re-review dispatched 2026-09-18 07:51:25 (reviewer opus, resumed).
- 2026-09-18 done: 3d1ef16
- re-review CLEAR (1-6, 8, 9 FIXED; 7 PARTIAL accepted). Landed merge 3d1ef16 2026-09-18 07:53:02.
