# The review fix loop

One round of the loop in SKILL.md § Review step 3: what each verdict means, who is
resumed and who is re-dispatched, and exactly what the implementer and the re-review are
told. The cap (4 review rounds), the rule that the librarian never fixes a finding
itself, the operator's share of the findings (step 4) and recording the round in the item
body (step 5) stay in SKILL.md; the tier per round is `model-routing.md` § Rounds.

## The verdicts

The reviewer's verdict is `CLEAR`, `NEEDS_CHANGES`, `SHOW_STOPPER`, or
`BLOCKED` (its setup failed: fix the brief and re-dispatch, twice at most; a third is
your environment — a blocked item for the operator, not a show-stopper. Permission
denied: as for an implementer, below).

"below" is the permission case in `troubleshooting.md`: an agent of either role that
returns `BLOCKED` on permissions is a decision for the operator — block the item and
report. `SHOW_STOPPER` and the operator's share of the findings: SKILL.md § Review step 4.

## A NEEDS_CHANGES round

- `NEEDS_CHANGES`: hand the findings, verbatim, to the **implementer** — resume the same
  agent (SendMessage; it has the context) only when its tier is unchanged (a resumed
  agent keeps its model); on a tier change (a round's bump or the fable fallback), or if
  gone, re-dispatch with the full brief, the findings and the fix-round clause from
  `references/agent-brief.md`. Tell
  it explicitly: **fix as new commit(s) on top of the reviewed sha, never amend, report
  each new sha**, and for each low/nit it declines, the reason. Then resume the
  **reviewer** — re-dispatched fresh only when its own tier changed (rule 4), or if gone —
  with the re-review variant in `references/review-brief.md`, pasting the
  new shas and the declined list: it verifies each prior finding by file:line, re-runs
  the same checks, attacks the fix, and rules each declined one DECLINED or OPEN.

Then repeat until `CLEAR`, inside the cap: a fourth review that is not `CLEAR` blocks the
item and goes to the operator.

## A bad commit subject

A finding against a commit's subject or message is never fixed by rewriting history —
the reviewer diffs from the reviewed sha, and `main` may have moved since the worktree
branched. Either the implementer declines it (a low/nit, reason "carried in the merge
message") or it stays as is and the Land step's merge message carries the corrected
subject. Never brief `git reset --soft main`, an amend, a rebase or a squash to redo it:
once `main` has moved, a soft reset onto it stages the inverse of `main`'s newer commits
into the next commit.
