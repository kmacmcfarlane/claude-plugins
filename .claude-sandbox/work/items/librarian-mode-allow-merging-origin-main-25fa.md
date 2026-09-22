---
id: librarian-mode-allow-merging-origin-main-25fa
title: "librarian-mode: allow merging origin/main on a rejected push (never rebase/force)"
type: chore
status: doing
priority: 1
owner: unknown@360f41058e92
claimed: 2026-09-22T16:47Z
created: 2026-09-22
updated: 2026-09-22
refs:
  - operator answer 52, 2026-09-22
---

Operator 2026-09-22 (answer 52): 'Why would we forbid doing a pull? That seems like a weird policy.' The no-pull rule exists so unreviewed commits don't land in what the librarian vouches for silently; rebase/force rewrite history. Acceptance: on a non-fast-forward rejection the librarian fetches and merges origin/main (a merge commit, never rebase or --force), runs Checks on the result, lists the incoming commits in the Report, then pushes; a conflict or red check stops and asks. Edit SKILL.md § Critical/Report + troubleshooting.md; dev-cycle likewise if it carries the rule.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92
dispatch: implementer opus — librarian-mode custody doctrine (Report / push rule)
impl r0 DONE 073bf9e (opus): § Critical push bullet — fetch, merge --no-ff --no-commit origin/main, Checks, commit, incoming: lines, push; conflict/red → merge --abort + numbered decision (conflict round to an implementer); decision instead of merging when > 5 commits or heavy Scope overlap; second rejection retries once, third is a decision; Red flags; troubleshooting + ending-the-session aligned. OQ: dev-cycle troubleshooting.md:77-78 and bindings.md:138 carry the old no-pull rule (follow-up).
dispatch: reviewer opus — rule 4
review r1 (opus) at 073bf9e: NEEDS_CHANGES. Every git command in the procedure walked in a scratch clone (diverged, conflict, red check, second rejection, dirt) — works; merge --abort restores exactly.
- [medium] SKILL.md:40-42, troubleshooting.md:46-48, SKILL.md:231-233, ending-the-session.md:32-35 — when the incoming: lines go out disagrees across four places; § Report still says "exactly four lines". Pass: one rule everywhere (with the push outcome: a short follow-up mid-session, the final Report at session end / 75%), § Report acknowledging the extra lines.
- [medium] dev-cycle bindings.md:138, troubleshooting.md:77-78 still forbid pulling — RESOLVED by the follow-up item dev-cycle-align-the-rejected-push-rule-w-5dbf (the reviewer's "or a follow-up filed and recorded" pass).
- [medium] troubleshooting.md:41-45 — the uncommitted merge while Checks run has no "no other commit to main until commit/abort" rule and no recovery if the session dies mid-merge (a store commit would complete the merge silently). Pass: the rule + a Rehydrate/troubleshooting entry: MERGE_HEAD present → merge --abort, redo.
- lows: threshold wording (> 5, must vs may, Scope overlap defined generically); step 2 should cover any refusal to start; strictly-behind → merge --ff-only, nothing to push; trigger names "(fetch first)"; pushes pause while a conflict decision is open (same number); 75%/DUE step 4 "no merge" exempts the push's merge; red-flag bullet wording.
dispatch: implementer opus — fix round 1 (resume)
fix r1 DONE 2dbf401 (opus): one incoming: rule in four places (with the push outcome: follow-up mid-session, final Report at session end/75%); no other commit to main until commit/abort + MERGE_HEAD recovery in Rehydrate step 4 and troubleshooting; all lows fixed; SKILL.md 2320 words.
dispatch: reviewer opus — review r2 (resume)
review r2 (opus) at 2dbf401: CLEAR — the four incoming: statements identical; scratch clone: interrupted merge recovered via MERGE_HEAD (-C "$MAIN" form needed from a worktree), control run shows a store commit would otherwise complete the merge; strictly-behind → ff-only; both trigger wordings. Lows: "staged changes anywhere"; a leftover MERGE_HEAD from a worktree-branch merge should compare MERGE_HEAD with origin/main before choosing the redo.
Review result: 2 rounds, 1 fix round; impl opus, review opus.
land (librarian): merge into main conflicted in librarian-mode SKILL.md (a934 landed c465325 in § Report; 25fa edits § Report's push line). The librarian's script ran on past the conflict; the half-done merge on main was aborted with git merge --abort before any commit (main at 1359bde, clean). Conflict round → implementer merges main into the branch.
dispatch: implementer opus — conflict round (resume)
conflict round DONE ec802dd (merge of main): § Report order push line → incoming: rule → a934 team-summary pointer ("after the push outcome and its incoming: lines"); ending-the-session both sequences same order; team-summary § When: a merged-through rejection gets a summary of this session's landings (only a stopped rejection gets none). OQ: range via origin/main@{1} after a merge-through = the fetch's entry, so it covers this session's landings + the merge commit, not incoming commits.
dispatch: reviewer opus — resolution verify (resume)
