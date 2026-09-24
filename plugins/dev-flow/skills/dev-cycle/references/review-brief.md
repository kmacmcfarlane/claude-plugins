# Review brief template

The dispatch brief for the review sub-agent that gates one change between the
implementer's return and Land. Fill every placeholder from the run's bindings
(`bindings.md`); delete nothing except the store lines when there is no work item. The
reviewer starts with none of the orchestrator's context and none of the implementer's, and
must be able to review from this text alone. Send it as the prompt of one background
`general-purpose` Agent. The reviewer is review-only: it never edits, never commits. The
orchestrator sets the `Model:` line from SKILL.md § Step 2 rule 4 — always opus, or fable
under a `model: fable` pin or as a second opinion — and passes the same value to the Agent
tool's `model` field; a reviewer is never routed below opus. The reviewer is always a
fresh agent: never a fork and never the implementer resumed.

The prohibitions, the severity scale and the report shape are fixed. The check commands vary
with what the change touches — take them from `review-checklist.md`, the same list the
orchestrator runs again at Land, including its section 4's Checks binding.

---

```
You are reviewing one change to this repository. You find problems; you do not fix them.
Work ONLY inside this directory, read-only:

  WORKTREE=<the workspace the record's `target:` line carries (record-lines.md), as written>

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

Model: <opus — routing rule 4 | fable — model: fable pin (rule 8) | fable — second
       opinion after an opus CLEAR | opus — fable pin unavailable; answer N>
Acceptance: <one or two lines, copied from the item, plan or brief>
Ground: <the Ground binding>
Files in scope: <explicit list; anything else in the diff is a finding — or "undeclared">
Workflow: <the Workflow binding, verbatim, or "none">
The implementer claims: <its STATUS line, then its VERIFIED and DEVIATIONS sections,
pasted verbatim — you are testing these claims, not trusting them>
Files changed, with reasons: <the record sink's cumulative `changed:` block, verbatim — the
union of every round's CHANGED, one file per line with its one-line reason>

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
   file against the acceptance and its one-line reason in "Files changed, with reasons"
   above: a file the intent does not justify, or one in the diff with no reason there, is
   a finding at medium. Anything the
   acceptance asks for that the diff does not deliver is a finding at high.
6. Try to break it. Write down at least three concrete edge cases before you look for
   them — empty input, a missing file, a second run, a path with a space, the branch name
   the docs say versus the one the code makes — then test each one. A vague worry is not a
   finding; a reproduction is.
7. Review the whole branch history, not only the final diff: a secret or credential in
   any commit's patch or message is critical even when a later commit removes it, since
   the merge carries every commit. Run the history scan in the Checks below, read each
   hit by eye, and read `git -C $WORKTREE log -p --cc <base>..HEAD` with it in mind
   (`--cc`, or a merge's resolution prints no diff). For a real
   one, put `git -C $WORKTREE branch -a --contains <sha>` in the finding — whether it
   reached anything beyond this branch.
8. Grade every finding on the scale below, with a file:line and a one-sentence failure
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
  commit subject or message finding is always low.
- A secret or credential in any committed content on the branch — a file in any commit,
  removed later or not, or any message — is critical (the dev-cycle skill's fix-loop
  rule, § A leaked secret). Never quote its value in a finding, a note or pasted check
  output (redact it): name its commit sha, file and key only. Never call it safe.

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
with this in place of "What to do" — unless the reviewer's tier changed (a waived fable
pin, routing rule 6): a resumed agent keeps its model, so dispatch a fresh reviewer at the
new tier with the full brief, its `Model:` line and "Files changed, with reasons"
updated, and the previous report pasted above this block.

```
Fix commits since your last review: git -C $WORKTREE log --oneline <last reviewed sha>..HEAD
<list them>. They are new commits; the ones you reviewed are unchanged.
Declined by the implementer, with its reasons:
<finding number — reason, one per line; or "none">
Files changed, with reasons (cumulative, updated this round):
<the record sink's `changed:` block, verbatim, as it stands after this round's CHANGED
was merged in — it replaces the list in your earlier brief>

<rebuild case only — the branch was rebuilt to drop a leaked secret; replace the first
two lines above with:>
History was rewritten: the branch was rebuilt from its merge-base <merge-base sha> to drop
a leaked secret, so <last reviewed sha> is no longer on it. Re-review the whole branch:
git -C $WORKTREE log --oneline <merge-base sha>..HEAD and
git -C $WORKTREE diff <merge-base sha>...HEAD. Then compare against the tree you reviewed:
git -C $WORKTREE diff <last reviewed sha> HEAD must show only this round's fixes and the
secret's removal from any file that still held it there (a leak a later commit already
removed, or one in a message, adds nothing); anything more is a finding. Then re-run the
history scan: no trace of the secret in any patch or message from <merge-base sha> on.

<merge-conflict round only — the branch now carries a merge of <base>; add:>
The new commits include <merge sha>, a merge of <base> made to resolve a conflict at Land.
Review from <last reviewed sha> as usual, and judge the merge by its resolution:
`git -C $WORKTREE show --remerge-diff <merge sha>` (git 2.36 or later) re-runs the merge
and diffs the conflicted result against what was committed, so a side the resolution
dropped shows as removed lines. Never judge it by plain `git show <merge sha>`: its
combined diff can hide a one-sided resolution. On git older than 2.36, set
OLD=$(git -C $WORKTREE merge-base <merge sha>^1 <merge sha>^2) and check both sides:
- the base's side: every hunk of `git -C $WORKTREE diff $OLD <merge sha>^2` (what the
  base brought) is kept — one reversed in `git -C $WORKTREE diff <merge sha>^2 <merge
  sha>` (what the merged tree still differs from the base by) is a dropped base side;
- the change's side: every hunk of the change's last reviewed diff,
  `git -C $WORKTREE diff $OLD <last reviewed sha>`, still appears in
  `git -C $WORKTREE diff <merge sha>^2 <merge sha>` — one missing there (the resolution
  kept the base's version) is a dropped change side.
A resolution that drops either side's intent is a finding.

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

## Review-mode variant

For `review <branch>` mode (SKILL.md § Usage): the same brief, severity scale, verdicts,
prohibitions and report shape, with these changes.

Replace the opening WORKTREE and verify lines:

```
WORKTREE=<the absolute worktree path `bindings.md` § Review target resolved — may be the
          main checkout itself>

First verify it exists and is on branch `<branch>` (`git -C $WORKTREE branch
--show-current`). If not — or if any placeholder in this brief is unfilled — stop and
report BLOCKED with the reason: that is the orchestrator's setup to fix, not a finding
about the change.
```

Base branch, Commits and Full diff stay as written, against `<branch>` in place of
`worktree-<name>`. Replace "The implementer claims" with:

```
Claims: none — this branch was not built by this cycle; you are reviewing it cold.
```

Replace "Files changed, with reasons" with the branch's own commit list and the recorded
Intent (`bindings.md` § Intent, `record-lines.md`) in place of an implementer's
`changed:` block:

```
Commits: <the same list as Under review's Commits line>
Intent: <the recorded `intent:` line — either the user's one-line intent, or "commit
        messages are the intent">
```

Grade each changed file against this Intent in place of the item's or plan's acceptance
(What to do, item 5). `bindings.md` § Intent's exemption applies: a changed file is never
itself a finding merely for lacking a one-line reason — there was no implementer to write
one.

Model: opus (Step 2 rule 4), or the Model floor when one is pinned (rule 8) — the same
whatever the branch's diff holds.

## Plan-review variant

For a plan-mode series (SKILL.md § Step 1): the same brief, severity scale, verdicts,
prohibitions and report shape, with these changes. There is no worktree and no diff:
replace the WORKTREE and Under review blocks with `SERIES=<absolute path of the series>`
and "Read every file of the series in full", keep Item or Brief, Acceptance and the
plan agent's claims, set "Files changed, with reasons" to "none" (a plan has no worktree
diff; its re-review pastes "none" too), and drop the Checks block. Replace What to do
with:

```
The series follows the investigate skill's investigation-format reference (path below).
1. Format: every serial from 01 on opens with a Supersedes block, "Nothing — purely
   additive" when nothing is overturned; the never-omit sections are present
   (Confirmed Assumptions, Risk Assessment, Open Questions, and Supersedes on 01+); and
   the series carries one of Implementation Approach, Proposed Fix or Recommendation,
   without which /implement refuses it. Each miss is a finding at medium, the missing
   approach section at high. A written serial edited after the fact is a finding at
   medium.
2. Completeness: every acceptance line has a planned change, with the files it touches
   and how it will be verified. A missing one is a finding at high.
3. Open questions: each records exactly what the format's Open Questions rule asks —
   the question, who owns it, the decision it changes, and whether it blocks
   implementation — and passed its triage (not verifiable from the code, not a
   requirement that belonged at the gate). A missing field, a blocking question hidden
   as an assumption, or a decision the plan takes that the acceptance leaves to a human
   is a finding at medium.
4. Feasibility: check the plan's claims about the code against the repository, read-only
   — files, functions, commands and branches it names exist and behave as it says. A
   plan built on a false claim is a finding at high.
5. Doctrine: a plan that would break a principle or the Workflow binding when built is a
   finding at medium, cited by principle.
6. Scope: work the plan adds beyond the acceptance is a finding at medium.
```

Fill the path as the absolute path of the `investigate` skill's
`references/investigation-format.md`, the sibling of this skill in the dev-flow plugin.

A `NEEDS_CHANGES` goes back to the plan agent, which follows that format's two rules
exactly: a written serial is never edited or deleted; the revision is a new serial at the
next free number, opening with a `Supersedes` block that names each file, section and
statement the findings overturned; and `INDEX.md` is regenerated wholesale. The re-review
variant applies with "the new serial, and the regenerated INDEX.md" in place of fix
commits.

**The baseline for "never edited".** Before every plan review, the orchestrator records
the hashes of the written serials in the record sink (SKILL.md § Step 4):

```bash
sha256sum <series>/[0-9][0-9]_*.md
```

The re-review brief pastes the hashes recorded before the previous review, and the
reviewer runs the same command: every file listed there must show the same hash. A
changed or missing one is a finding at medium (the format's rule 1).

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
