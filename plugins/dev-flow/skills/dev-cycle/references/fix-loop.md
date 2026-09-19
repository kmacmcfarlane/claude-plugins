# The review fix loop

One round of the loop in SKILL.md § Step 4: what each verdict means, who is resumed and
who is re-dispatched, and exactly what the implementer and the re-review are told. The cap
(4 review rounds), the rule that the orchestrator never fixes a finding itself, what goes
to the decision channel, and recording the round in the record sink stay in SKILL.md; the
tier per round is `model-routing.md` § Rounds.

## The verdicts

The reviewer's verdict is `CLEAR`, `NEEDS_CHANGES`, `SHOW_STOPPER`, or
`BLOCKED` (its setup failed: fix the brief and re-dispatch, twice at most; a third is
your environment — a blocked change raised through the decision channel, not a
show-stopper. Permission denied: as for an implementer, below).

"below" is the permission case in `troubleshooting.md`: an agent of either role that
returns `BLOCKED` on permissions is a decision for a human — block the item (when there is
one) and raise it through the decision channel. `SHOW_STOPPER` and what else escalates:
SKILL.md § Step 4.

## A NEEDS_CHANGES round

- `NEEDS_CHANGES`: hand the findings, verbatim, to the **implementer** — resume the same
  agent (SendMessage; it has the context) only when its tier is unchanged (a resumed
  agent keeps its model); on a tier change (a round's bump or the fable fallback), or if
  gone, re-dispatch with the full brief, the findings and the fix-round clause from
  `agent-brief.md`. Tell it explicitly: **fix as new commit(s) on top of the reviewed
  sha, never amend, report each new sha**, and for each low/nit it declines, the reason.
  Then resume the **reviewer** — re-dispatched fresh only when its own tier changed
  (rule 4), or if gone — with the re-review variant in `review-brief.md`, pasting the
  new shas and the declined list: it verifies each prior finding by file:line, re-runs
  the same checks, attacks the fix, and rules each declined one DECLINED or OPEN.

Then repeat until `CLEAR`, inside the cap: a fourth review that is not `CLEAR` blocks the
change and goes to the decision channel.

## A merge conflict

The orchestrator never resolves a conflict by hand. When Land's merge conflicts:

1. `git -C "$MAIN" merge --abort` at once, so the main checkout is as it was.
2. Record it in the record sink as a finding — `conflict: <paths> against <base> at
   <base sha>` — graded medium (the change does not merge). It opens a fix round and
   counts toward the cap like any other.
3. Re-dispatch or resume the implementer with the merge-conflict clause of
   `agent-brief.md`: it merges `<base>` into `worktree-<name>` as one new commit,
   resolving with the change's own approach as the tiebreaker. That is the brief's one
   exception to its no-merge rule; a rebase stays forbidden.
4. Re-review from the last reviewed sha, with the merge-conflict case of
   `review-brief.md` § Re-review variant, then Land again from its step 1.

A plan-mode series never reaches a merge; its fix rounds revise the series (the
plan-review variant in `review-brief.md`).

## A bad commit subject

A finding against a commit's subject or message is always graded **low**, unless the
message leaks a secret or credential (below): history is not rewritten to fix it, so the
implementer may always decline it (reason: "carried in the merge message"). This is the
one statement of that rule; the briefs point here.

- **Record it.** Append `subject-fix: <sha> <corrected subject>` to the record sink.
- **Carry it at Land.** SKILL.md § Step 5 merges with one `-m` per paragraph, so git
  separates them with blank lines and never folds a correction into the subject:
  `-m "merge: <aspect> - <description> - land worktree-<name> (<item id or slug>)"`, then
  one `-m "<sha> should read: <corrected subject>"` per `subject-fix:` in the record.
  A terminal action that does not merge (the branch is left for the user) reports each
  `subject-fix:` line instead.

Never brief `git reset --soft <base>`, an amend, a rebase or a squash to redo a subject:
the reviewer diffs from the reviewed sha, and once the base has moved since the worktree
branched, a soft reset onto it stages the inverse of the base's newer commits into the
next commit.

**The exception: a secret or credential in a commit message** is critical, not low. The
unmerged worktree branch is rebuilt without it before Land — the one case where the
branch's history is rewritten, safe only because nothing has been merged or pushed yet.
Re-dispatch the implementer with the merge-base sha pasted into the brief
(`git -C "$MAIN" merge-base <base> worktree-<name>`): it rebuilds `worktree-<name>` by
`git reset --soft <merge-base>` and a recommit with every message clean — never a
rebase, never onto the base itself. The re-review uses the rebuild case of
`review-brief.md` § Re-review variant: diff from the merge-base, and the old reviewed tree
against the new.

- **Never the value.** The secret is recorded and reported by commit sha, file and key
  name only — in the finding, the record sink (an item body may be committed and pushed)
  and the Report alike.
- **Rotation is a scope change.** Rotating a leaked credential is outside the change, so
  it goes to the decision channel under SKILL.md § Step 4's "changes the scope" arm; the
  rebuild itself is resolved inside the loop.
