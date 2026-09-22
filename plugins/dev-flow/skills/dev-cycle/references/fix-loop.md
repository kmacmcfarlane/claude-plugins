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
  new shas, the declined list and, every round, the cumulative "Files changed, with
  reasons" — the record sink's `changed:` block after this round's CHANGED was merged
  in, so a file a fix round added arrives with its reason. A plan has no worktree diff
  and no `changed:` block: a plan-mode re-review pastes there the serials the
  `baseline:` diff names as added or rewritten (SKILL.md § Step 4.1, `record-lines.md`), and
  "none" only when no earlier `baseline:` exists to diff against. The reviewer verifies
  each prior finding by file:line, re-runs the same checks, attacks the fix, and rules
  each declined one DECLINED or OPEN.

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
   exception to its no-merge rule; a rebase stays forbidden. Its CHANGED may list files
   the base brought in with the merge: before merging it into the `changed:` block, drop
   every path that `git -C <workspace> diff --stat <base>...HEAD` does not show — the
   three-dot diff, taken after the merge, holds only the change's own side.
   `<workspace>` is the path the record's `target:` line carries (`record-lines.md`), never one
   rebuilt from the item id.
4. Re-review from the last reviewed sha, with the merge-conflict case of
   `review-brief.md` § Re-review variant, which judges the resolution with
   `git show --remerge-diff <merge sha>` (git 2.36+; its fallback for older git is
   there, checking both sides), never plain `git show`, whose combined diff can hide a
   one-sided resolution.
   Then Land again from its step 1.

A plan-mode series never reaches a merge; its fix rounds add a new serial with a
`Supersedes` block and regenerate `INDEX.md`, never edit a written one (the plan-review
variant in `review-brief.md`).

**`review <branch>` mode.** A merge conflict at Land is a finding against `<branch>`
itself, made by whoever built it, not something this cycle resolves on its own say-so. If
no implementer is active for this run (the decision-channel ask was never made, or was
declined), record the conflict as a finding and route it through that same
before-any-fix-loop ask (SKILL.md § Usage): dispatch one with the review-mode fix variant
to resolve it, or report it back to the branch's author and stop — never resolved
inline either way. If an implementer is already active in this run (the ask was already
accepted), it resolves the conflict exactly as `full` mode does, on `<branch>` in place
of `worktree-<name>`. Either way the resolution is a new commit on `<branch>`, never a
rebase or a reset of anything the author already wrote.

## A bad commit subject

A finding against a commit's subject or message is always graded **low**, unless the
message leaks a secret or credential (§ A leaked secret): history is not rewritten to fix
it, so the implementer may always decline it (reason: "carried in the merge message"). This is the
one statement of that rule; the briefs point here.

- **Record it.** Append `subject-fix: <sha> <corrected subject>` to the record sink.
- **Carry it at Land.** SKILL.md § Step 5 merges with one `-m` per paragraph, so git
  separates them with blank lines and never folds a correction into the subject:
  `-m "merge: <aspect> - <description> - land worktree-<name> (<item id or slug>)"` — in
  `review <branch>` mode, `-m "merge: <aspect> - <description> - land <branch> (<item id
  or slug, or the recorded intent>)"` — then one `-m "<sha> should read: <corrected
  subject>"` per `subject-fix:` in the record. A terminal action that does not merge (the
  branch is left for the user) reports each `subject-fix:` line instead.

Never brief `git reset --soft <base>`, an amend, a rebase or a squash to redo a subject:
the reviewer diffs from the reviewed sha, and once the base has moved since the worktree
branched, a soft reset onto it stages the inverse of the base's newer commits into the
next commit.

## A leaked secret

A secret or credential in **any committed content on the branch** is critical: a file in
any commit — even one a later commit removes — or any commit message. A removing commit is
no fix, since the `--no-ff` merge at Land carries every commit; the branch history must be
free of it before Land. A leak in a message is one case of this rule, not a separate one.

1. **Check its reach first.** For each commit holding it,
   `git -C "$MAIN" branch -a --contains <sha>` must show only `worktree-<name>`, and
   `git -C "$MAIN" tag --contains <sha>` nothing. Anything else — a remote-tracking branch, another
   branch, a tag, a push known to have happened — puts it out of the cycle's hands: do not
   rebuild or land; block the item (when there is one) and raise it through the decision
   channel at once.
2. **Rebuild the branch** — the one case where its history is rewritten, safe only because
   nothing has been merged or pushed. Re-dispatch the implementer with the merge-base sha
   pasted into the brief (`git -C "$MAIN" merge-base <base> worktree-<name>`): it runs
   `git reset --soft <merge-base>`, takes the secret out of any file that still holds it,
   and makes one recommit with every message clean — never a rebase, never onto the base
   itself. The re-review uses the rebuild case of `review-brief.md` § Re-review variant:
   the whole history from the merge-base, and the old reviewed tree against the new.
3. **Never the value.** The secret is named by commit sha, file and key only — in the
   finding, the record sink (an item body may be committed and pushed), commit messages,
   the Report, and any search for it (search by key name or a secret-shaped pattern, never
   by the value).
4. **Rotation is a scope change.** Rotating a leaked credential is outside the change: raise
   it through the decision channel under SKILL.md § Step 4's "changes the scope" arm; the
   rebuild itself is resolved inside the loop. The cycle never reports a credential as
   safe — the rebuild clears the branch, not the credential, and old objects stay in the
   local repository until pruned.

**`review <branch>` mode never rebuilds.** Step 2's rebuild rewrites the branch's own
history — a `git reset --soft` and one clean recommit — safe only because the cycle built
that history itself. In `review <branch>` mode the history is the author's; the cycle
never rewrites or soft-resets it, whether or not an implementer is active for this run. A
leaked secret found here is always reported back to the branch's author, or raised
through the decision channel when step 1's reach check finds it went beyond the branch —
never rebuilt, and never landed while it remains.
