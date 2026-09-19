---
id: dev-flow-add-the-dev-cycle-skill-07c3-f1-325d
title: "dev-flow: add the dev-cycle skill (07c3 F1)"
type: feature
status: blocked
priority: 2
deps:
  - dev-flow-cross-skill-reference-conventio-05bb
parent: dev-flow-new-dev-cycle-skill-investigate-07c3
owner: unknown@e3a28d2cc009
claimed: 2026-09-19T00:47Z
blocked: "review cap hit (4): one-sentence fix in review-brief re-review template - decision 36"
created: 2026-09-18
updated: 2026-09-19
---

07c3 plan §F1: new plugins/dev-flow/skills/dev-cycle (full + plan modes, standalone bindings); README/CLAUDE.md layout/plugin.json/marketplace.json in the same commit; librarian-mode untouched. Size L; opus/opus.

## Handoff
- doing: review round 4 (final) running; impl at 3edc2a8
- next: CLEAR -> land; else block + ask operator
- blocked: —
- learned: —

## Notes
- 2026-09-19 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — marketplace shape + doctrine, L (rule 2); no gating code

## Carried notes (restored 2026-09-19; wi claim/handoff had dropped them)
- 2026-09-18 (from 81a5): model-routing § Fallback should say the reader checks rate_limits.at / a past resets_at to spot stale data (the block persists when a payload lacks rate_limits). Carry into the moved model-routing.md.

- 2026-09-18 (from 4a19): the implementer brief should prohibit bare git stash/pop (the stash stack is shared across worktrees and sessions); prefer a temp WIP commit or a scratch copy for revert-to-verify. Carry into the moved agent-brief.md.

- (F0 review lows, fold into the moved review-checklist) path split across lines not read; own file shadows a named sibling; only backtick fences, plain toggle (tilde/nested fences); URLs hit the directory-prefix rule; .md.bak read as .md; CLAUDE.md wording "by its backticked name".
- (c5fc review lows) "a typo Claude Code silently ignores" is unsourced; checklist code keeps a hand copy of the 20 allowed keys (state the count so reviewers can compare); create-skill SKILL.md:44 lists only 4 of 15 optional fields.

## Round log
impl: DONE 0dfad31 (SKILL.md 13k chars; 7 references; carried notes folded; librarian-mode untouched).
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — high 1 (Land refuses the cycle's own store/series/worktree dirt), 2 (lost: reviewer NOTES/open questions, --blocked handoff on a red Land check, report-and-ask on a dirty worktree); medium 3 (merge-conflict hand resolution), 4 (record sink fallback to a nonexistent outcome file), 5 (no Files-in-scope fallback), 6 (plan/spike DONE skips review); lows 7-11, nit 12. Librarian decisions: own dirt never blocks; conflicts go back to the implementer (named merge-base exception); every DONE incl. plans is reviewed; files fallback = implementer declares, review holds it to the plan.
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE 5d96ef3 (all but 11 declined->10f2; conflict graded medium; plan revisions as new series files).
dispatch: reviewer opus review round 2 — resume

review round 2 (opus): NEEDS_CHANGES — high 1 (conflict re-review uses git show; one-sided resolutions invisible -> use --remerge-diff), medium 2 (plan fix rounds edit serials; must add a new serial with Supersedes per investigation-format), 3 (undeclared Files in scope not carried to Land step 2 / checklist §1); lows 4-5, nit 6.
dispatch: implementer opus fix round 2 — resume

fix round 2 (opus): DONE 20e68f2 (remerge-diff + fallback; plan rounds by new serial with Supersedes; undeclared at Land/§1).
dispatch: reviewer opus review round 3 — resume

review round 3 (opus): NEEDS_CHANGES — medium 1 (reviewer never given CHANGED reasons; union of CHANGED across rounds), 2 (plan re-review has no baseline: record serial hashes); lows 3 (fallback misses a dropped change side), 4 (open-question fields per investigation-format). Last fix round; mediums only -> stays opus.
dispatch: implementer opus fix round 3 (last) — resume

fix round 3 (opus): DONE 3edc2a8 (cumulative changed: block; serial sha256 baseline; both-sided fallback; open-question fields per format).
dispatch: reviewer opus review round 4 (final) — resume

## Cap
review round 4 (opus, final): NEEDS_CHANGES — 1-4 of round 3 fixed; new medium: re-review template re-pastes the cumulative changed: block only in the merge-conflict case, so a resumed reviewer in an ordinary fix round lacks new files' reasons (one-sentence move in references/review-brief.md). CAP HIT (4).
decision 36: 07c3 F1 cap: (a) one extra round to move the sentence into the general re-review template, re-review, land [recommended]; (b) land now, fold the fix into F2 (fb09), which edits the same briefs.
