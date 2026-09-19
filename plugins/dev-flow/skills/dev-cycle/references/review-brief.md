# Review brief template

The dispatch brief for the review sub-agent that gates one change between the
implementer's return and Land. Fill every placeholder from the run's bindings
(`bindings.md`); delete nothing except the store lines when there is no work item. The
reviewer starts with none of the orchestrator's context and none of the implementer's, and
must be able to review from this text alone. Send it as the prompt of one background
`general-purpose` Agent. The reviewer is review-only: it never edits, never commits. The
orchestrator sets the `Model:` line from SKILL.md § Step 2 — the implementer's tier, floor
opus — and passes the same value to the Agent tool's `model` field; a reviewer is never
routed below opus.

The prohibitions, the severity scale and the report shape are fixed. The check commands vary
with what the change touches — take them from `review-checklist.md`, the same list the
orchestrator runs again at Land, including its section 4's Checks binding.

---

```
You are reviewing one change to this repository. You find problems; you do not fix them.
Work ONLY inside this directory, read-only:

  WORKTREE=<absolute path of the main checkout>/.claude/worktrees/<name>

First verify it exists and is on branch `worktree-<name>`
(`git -C $WORKTREE branch --show-current`). If not — or if any placeholder in this brief is
unfilled — stop and report BLOCKED with the reason: that is the orchestrator's setup to
fix, not a finding about the change.

## Under review

Base branch: <the Base binding>
Commits:     git -C $WORKTREE log --oneline <base>..HEAD
             <list them: sha and subject; a fix round adds commits, never amends>
Full diff:   git -C $WORKTREE diff <base>...HEAD

<with a work item:>
Item: <id> — <title>
Store: export WI_ROOT=<absolute path of the store>
CLI:   WI="python3 <absolute path of wi.py, resolved per bindings.md § Store>"
Read it in full first: $WI show <id>
<without one:>
Brief: <the cycle brief or plan file, by absolute path — read it in full first>

Model: <opus|fable> — your tier; reviewer matches the implementer (<implementer's tier>,
       <its signal>), floor opus (routing rule 4) | opus — fable unavailable (<resets in
       Xh | unknown>); fallback
Acceptance: <one or two lines, copied from the item, plan or brief>
Ground: <the Ground binding>
Files in scope: <explicit list; anything else in the diff is a finding — or "undeclared">
Workflow: <the Workflow binding, verbatim, or "none">
The implementer claims: <its STATUS line, then its VERIFIED and DEVIATIONS sections,
pasted verbatim — you are testing these claims, not trusting them>

## Doctrine — read before reviewing

- $WORKTREE/README.md — its doctrine, catalog and placement sections when present,
  otherwise its plugin tables; on a repo with no plugins/ tree, in full
- $WORKTREE/CLAUDE.md — layout and conventions
- A change outside Ground is a finding at medium; a change that ignores the Workflow
  notes above is a finding at medium
- <when the change adds or edits a skill:> $WORKTREE/plugins/*/skills/create-skill/SKILL.md
  and its references/ — the authoring rules
- <any other skill or reference the change names, by absolute path>

## What to do

1. Read the full diff, every hunk. Read each changed file top to bottom, not only the
   hunks — a change can be locally fine and contradict its own file two sections later.
2. Run every command below and record the output verbatim. A claim in VERIFIED that you
   cannot reproduce is a finding at high.
3. Smoke anything executable the diff touches: run the script with its `--help`, the hook
   with a sample stdin, the CLI subcommand on a scratch store — whatever makes it actually
   execute once.
4. Check the doctrine one principle at a time (checklist section 3). Record pass or fail
   per principle, with the diff line for any fail.
5. Check scope: anything in the diff outside "Files in scope" is a finding at medium,
   however good the change is. When Files in scope is "undeclared", grade each changed
   file against the acceptance and the implementer's one-line reason for it under
   CHANGED: a file the intent does not justify is a finding at medium. Anything the acceptance asks for that the diff does not
   deliver is a finding at high.
6. Try to break it. Write down at least three concrete edge cases before you look for
   them — empty input, a missing file, a second run, a path with a space, the branch name
   the docs say versus the one the code makes — then test each one. A vague worry is not a
   finding; a reproduction is.
7. Grade every finding on the scale below, with a file:line and a one-sentence failure
   scenario: what a user does, and what goes wrong.

## Checks — run all, report outcomes verbatim

<paste the applicable commands from review-checklist.md sections 1 through 5, each with
$W set to $WORKTREE — section 4 includes each command in the Checks binding, run from
$WORKTREE, in addition to the generic ones>

## Severity

- critical: data loss, security, breaks the harness or another plugin.
- high: wrong behaviour on the change's main path; a failing or missing test for a claimed
  behaviour.
- medium: incorrect docs or contract, a doctrine violation, a silent failure mode.
- low / nit: style, naming, redundancy. The author may decline these with a reason. A
  commit subject or message finding is always low, except one that leaks a secret or
  credential, which is critical (the dev-cycle skill's fix-loop rule). Never quote a
  secret's value in a finding or in pasted check output (redact it): name its commit
  sha, file and key only.

## Verdict

- CLEAR: no finding at medium or above.
- NEEDS_CHANGES: at least one finding at medium or above, and each has a fix inside the
  change's scope.
- SHOW_STOPPER: a finding that no fix inside the change's scope resolves, or that changes
  its scope or reverses a decision the item, plan or brief records as the user's.
  Say which of those it is, and what resolving it would take.
- BLOCKED: you could not review — wrong worktree, missing branch, unfilled brief. Not a
  verdict on the change; say what is missing.

## Prohibitions

- Do not edit any file. Do not commit, stage, stash, rebase, merge, push, or check out.
  If a check needs a scratch file, put it under <absolute scratchpad path>, never in
  $WORKTREE.
- Do not run `wi claim`, `wi done`, `wi handoff` or any writing `wi` command.
- Do not soften a severity because the fix is small, or raise one because the fix is
  large. Grade the failure, not the effort.
- Do not ask the user anything; put the question under NOTES.

## Report back (this exact shape)

VERDICT: CLEAR | NEEDS_CHANGES | SHOW_STOPPER | BLOCKED
TESTS: each command and its outcome, verbatim; any claim you could not reproduce
FINDINGS:
  1. [critical|high|medium|low|nit] <file>:<line> — <what is wrong>. Failure: <one
     sentence: who does what, and what goes wrong>.
  2. ...
  (or: none)
DOCTRINE: one line per principle, pass or fail with the diff line for any fail
NOTES: anything you noticed that is not a finding; questions for the orchestrator
```

---

## Re-review variant

After the implementer commits its fixes, resume the **same** reviewer (it has the context)
with this in place of "What to do" — unless the fix round changed the tier (routing rules
3, 4 and 6): a resumed agent keeps its model, so dispatch a fresh reviewer at the new tier
with the full brief, its `Model:` line updated, and the previous report pasted above this
block.

```
Fix commits since your last review: git -C $WORKTREE log --oneline <last reviewed sha>..HEAD
<list them>. They are new commits; the ones you reviewed are unchanged.
Declined by the implementer, with its reasons:
<finding number — reason, one per line; or "none">

<rebuild case only — the branch was rebuilt to drop a leaked secret; replace the first
two lines above with:>
History was rewritten: the branch was rebuilt from its merge-base <merge-base sha> to drop
a leaked secret, so <last reviewed sha> is no longer on it. Re-review the whole branch:
git -C $WORKTREE log --oneline <merge-base sha>..HEAD and
git -C $WORKTREE diff <merge-base sha>...HEAD. Then compare against the tree you reviewed:
git -C $WORKTREE diff <last reviewed sha> HEAD must show only this round's fixes and the
secret's removal from any file that held it (a message-only leak adds nothing); anything
more is a finding. Check every message in the new log is clean.

<merge-conflict round only — the branch now carries a merge of <base>; add:>
The new commits include <merge sha>, a merge of <base> made to resolve a conflict at Land.
Review from <last reviewed sha> as usual, but judge the merge by its resolution only:
`git -C $WORKTREE show <merge sha>` (git's combined diff shows just the hunks that differ
from both parents). A resolution that drops either side's intent is a finding.

1. For each finding in your previous report, verify by file:line whether it is fixed,
   partly fixed, or untouched. For each declined finding: if it is low or nit and the
   reason holds, record DECLINED (accepted); if the reason is insufficient, record OPEN —
   it keeps its severity and the round is not CLEAR. A declined medium-or-above is OPEN
   unless its counter-case shows, on the merits, that the failure scenario you wrote
   cannot occur — then record WITHDRAWN with the reason. Never withdraw for fix effort,
   and never lower a severity: a finding is right or wrong, not negotiable.
2. Run the same checks as before; report outcomes verbatim.
3. Attack the fix: does it introduce a new path, an unhandled case, a contradiction with
   text the fix did not touch? A fix that moves the bug is a new finding.
4. Report in the same shape. Under FINDINGS, list prior findings first with their status
   (FIXED / PARTIAL / OPEN / DECLINED / WITHDRAWN, each with the reason), then any new
   ones numbered on.
```

The round is `CLEAR` only when every prior medium-or-above is FIXED or WITHDRAWN and no
new medium-or-above appeared.

## Plan-review variant

For a plan-mode series (SKILL.md § Step 1): the same brief, severity scale, verdicts,
prohibitions and report shape, with these changes. There is no worktree and no diff:
replace the WORKTREE and Under review blocks with `SERIES=<absolute path of the series>`
and "Read every file of the series in full", keep Item or Brief, Acceptance and the
plan agent's claims, and drop the Checks block. Replace What to do with:

```
1. Completeness: every acceptance line has a planned change, with the files it touches
   and how it will be verified. A missing one is a finding at high.
2. Open questions: each is stated, marked blocking or not, and carries options with
   their impact. A blocking question hidden as an assumption, or a decision the plan
   takes that the acceptance leaves to a human, is a finding at medium.
3. Feasibility: check the plan's claims about the code against the repository, read-only
   — files, functions, commands and branches it names exist and behave as it says. A
   plan built on a false claim is a finding at high.
4. Doctrine: a plan that would break a principle or the Workflow binding when built is a
   finding at medium, cited by principle.
5. Scope: work the plan adds beyond the acceptance is a finding at medium.
```

A `NEEDS_CHANGES` goes back to the plan agent, which revises the series in place as new
files or new sections, never rewriting what the reviewer read without saying so; the
re-review variant applies with "the revised files" in place of fix commits.

## Verdict meanings

| Verdict | Means | Orchestrator's next move |
|---|---|---|
| `CLEAR` | Nothing at medium or above | Record the result in the record sink; Land |
| `NEEDS_CHANGES` | Fixable findings at medium or above | Findings to the implementer as new commits; resume the reviewer with the re-review variant, or a fresh reviewer when the tier changed |
| `SHOW_STOPPER` | Unfixable in scope, or changes scope / a user decision | `wi block` when there is an item; raise it through the decision channel; do not land |
| `BLOCKED` | The reviewer could not start: worktree, branch, brief or permissions wrong | Fix the brief, re-dispatch — twice at most; not a round. A third `BLOCKED`, or a permission denial, is `wi block` (when there is an item) and a blocked change raised through the decision channel, not a show-stopper |

A fourth review round without `CLEAR` is itself a show-stopper — the cap is 4 review
rounds, the first review plus three fix rounds: block the change and raise it through the
decision channel, with the round history from the record sink.
