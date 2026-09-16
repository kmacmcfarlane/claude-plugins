---
id: librarian-mode-skill-md-over-the-5000-to-1420
title: librarian-mode SKILL.md over the ~5000-token guideline
type: chore
status: done
priority: 4
created: 2026-09-16
updated: 2026-09-16
closed: 2026-09-16
refs:
  - reviewer report, item librarian-mode-model-routing-for-sub-age-423f
---

Left over from 423f: SKILL.md is ~22.5k chars (est. 5.3-5.9k tokens); main was already at the line before routing landed. Reviewer named the levers: Rehydrate's first-start paragraph and Troubleshooting could move to references/. Also fix two nits: Route line 1 'the librarian's, dearest, model' wording; 'of either role' placement in Review step 3.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-16 claimed by unknown@4d338747396e
Note: the two nits named above (Route line 1 wording; 'of either role' placement) — the first was already fixed by 2b08; check the second before editing.
dispatch: implementer opus — rule 2 (judgement: what to move; the librarian's own procedure)
dispatch: reviewer opus — rule 4
- implementer opus returned DONE, commit ccf3f33 (22,483 -> 18,733 chars; new refs troubleshooting.md, first-start.md, fix-loop.md; examples into model-routing.md). Librarian concern for review: the NEEDS_CHANGES round moved out of Review step 3 into fix-loop.md. Reviewer opus round 1 dispatched 2026-09-16 16:59:22
- review round 1: NEEDS_CHANGES — 1 medium (fix-loop.md:27 forces a fresh reviewer on ANY role's bump; reviewer re-dispatch is only needed when the reviewer's own tier changes), 3 lows (undisclosed in-place rewordings: intro sentence about noticing the same complaint from three sessions deleted; Delegate step 3 brief-parts list replaced by 'which lists every part'; Rehydrate step 2 lost '(layout and conventions)'), 3 nits ('exactly' dropped; wi-glob guidance twice in troubleshooting.md; first-start.md duplicates the pre-merge rule). Reviewer ruling on the librarian's concern: the fix-loop pointer is sufficient — no partial rule left beside it. Fix round 1 sent 2026-09-16 17:03:52, tier unchanged (opus, resumed). Note for future trims: brief the line-level preservation sweep, not a block grep.
- fix round 1 returned DONE, new commit 747670d; declined nits 6 and 7 (verbatim-preservation reason); new move: Review step 5 (record the result in the item body) to fix-loop.md with a pointer. Re-review dispatched 2026-09-16 17:08:16 (reviewer opus, resumed) — must rule on the step 5 move.
- re-review (review round 2): NEEDS_CHANGES — findings 1-5 FIXED; 6 DECLINED accepted (reviewer withdrew its
  own finding: two different sentences, not two copies); 7 DECLINED accepted as a judgement call, not as a
  correct reading of acceptance (whitespace-normalised verbatim was already satisfied). NEW medium 8: the step 5
  pointer summarises the content list so completely that the three rules left only in fix-loop.md (append with
  Bash / item file is not a custody file; the transcript is not the record; unsettled reviewer questions go to
  open questions) become skippable. Nits 9 (fix-loop.md intro names only step 3), 10 (pointer lacks §).
  Reviewer's general rule, kept: a pointer is sufficient when SKILL.md leaves nothing actionable beside it,
  insufficient when it leaves a summary that reads as complete.
- fix round 2 (last before the cap): implementer opus -> fable (rule 3), FRESH dispatch; reviewer -> fable
  (rule 4), fresh, prior report pasted. Dispatched 2026-09-16 17:11:06. A third review without CLEAR blocks the
  item and goes to the operator.
dispatch: implementer fable — rule 3, fix round 2
dispatch: reviewer fable — rule 4
- fix round 2 returned DONE, new commit b406c25 (step 5 restored verbatim; Ending-the-session body moved to new references/ending-the-session.md; fix-loop.md § Recording removed). Review round 3 (last): fresh fable reviewer dispatched 2026-09-16 17:13:46
- 2026-09-16 done: 7d5170f
- review round 3: CLEAR. All prior findings FIXED or DECLINED-accepted; 1 new low (Land first-start clause has a complete-reading pointer; graded low since the moved text holds no prohibition) and 4 nits — not sent back at the cap, recorded. Landed merge 7d5170f 2026-09-16 17:18:16; SKILL.md 18,724 chars.
