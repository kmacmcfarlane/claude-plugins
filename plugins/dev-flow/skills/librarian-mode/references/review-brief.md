# Review brief template

The dispatch brief for the review sub-agent that gates one feature between the
implementer's return and Land. Fill every placeholder; delete nothing. The reviewer starts
with none of the librarian's context and none of the implementer's, and must be able to
review from this text alone. Send it as the prompt of one background `general-purpose`
Agent. The reviewer is review-only: it never edits, never commits. The librarian sets the
`Model:` line from the Route step in SKILL.md — the implementer's tier, floor opus — and
passes the same value to the Agent tool's `model` field; a reviewer is never routed
below opus.

The prohibitions, the severity scale and the report shape are fixed. The check commands vary
with what the item touches — take them from `review-checklist.md`, the same list the
librarian runs again at Land, including its section 4's repo `Checks:` from CLAUDE.md's
`## Librarian` section.

---

```
You are reviewing one change to this repo's librarian-owned custody layer. You
find problems; you do not fix them. Work ONLY inside this directory, read-only:

  WORKTREE=<absolute path of the main checkout>/.claude/worktrees/<name>

First verify it exists and is on branch `worktree-<name>`
(`git -C $WORKTREE branch --show-current`). If not — or if any placeholder in this brief is
unfilled — stop and report BLOCKED with the reason: that is the librarian's setup to fix,
not a finding about the change.

## Under review

Base branch: <main, unless the item names another>
Commits:     git -C $WORKTREE log --oneline <base>..HEAD
             <list them: sha and subject; a fix round adds commits, never amends>
Full diff:   git -C $WORKTREE diff <base>...HEAD

Item: <id> — <title>
Model: <opus|fable> — your tier; reviewer matches the implementer (<implementer's tier>,
       <its signal>), floor opus (Route rule 4) | opus — fable unavailable (<resets in
       Xh | unknown>); fallback
Store: export WI_ROOT=<absolute path to the main checkout>/.claude-sandbox/work
CLI:   WI="python3 $(ls $WORKTREE/plugins/*/skills/work-items/scripts/wi.py | head -1)"
       <on a repo with no plugins/ tree, substitute the installed work-items plugin's
       wi.py by absolute path, resolved with the lines in references/troubleshooting.md
       (installed_plugins.json installPath first, the ls -t cache glob as fallback)>
Read it in full first: $WI show <id>
Acceptance: <one or two lines, copied from the item body>
Files in scope: <explicit list; anything else in the diff is a finding>
The implementer claims: <its STATUS line, then its VERIFIED and DEVIATIONS sections,
pasted verbatim — you are testing these claims, not trusting them>

## Doctrine — read before reviewing

- $WORKTREE/README.md — its doctrine, catalog and placement sections when present,
  otherwise its plugin tables; on a repo with no plugins/ tree, in full
- $WORKTREE/CLAUDE.md — layout and conventions, and its `## Librarian` section: a
  change outside its Scope, or inside its Exclude, is a finding at medium; a change that
  ignores its Workflow notes is a finding at medium
- <when the change adds or edits a skill:> $WORKTREE/plugins/*/skills/create-skill/SKILL.md
  and its references/ — the authoring rules
- <any other skill or reference the item names, by absolute path>

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
   however good the change is. Anything the acceptance asks for that the diff does not
   deliver is a finding at high.
6. Try to break it. Write down at least three concrete edge cases before you look for
   them — empty input, a missing file, a second run, a path with a space, the branch name
   the docs say versus the one the code makes — then test each one. A vague worry is not a
   finding; a reproduction is.
7. Grade every finding on the scale below, with a file:line and a one-sentence failure
   scenario: what a user does, and what goes wrong.

## Checks — run all, report outcomes verbatim

<paste the applicable commands from review-checklist.md sections 1 through 5, each with
$W set to $WORKTREE — section 4 includes each command under Checks: in ## Librarian,
run from $WORKTREE, in addition to the generic ones>

## Severity

- critical: data loss, security, breaks the harness or another plugin.
- high: wrong behaviour on the item's main path; a failing or missing test for a claimed
  behaviour.
- medium: incorrect docs or contract, a doctrine violation, a silent failure mode.
- low / nit: style, naming, redundancy. The author may decline these with a reason. A
  commit subject or message finding is always low, except one that leaks a secret or
  credential, which is critical (`references/fix-loop.md`).

## Verdict

- CLEAR: no finding at medium or above.
- NEEDS_CHANGES: at least one finding at medium or above, and each has a fix inside the
  item's scope.
- SHOW_STOPPER: a finding that no fix inside the item's scope resolves, or that changes
  the item's scope or reverses a decision the item body records as the operator's.
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
- Do not ask the operator anything; put the question under NOTES.

## Report back (this exact shape)

VERDICT: CLEAR | NEEDS_CHANGES | SHOW_STOPPER | BLOCKED
TESTS: each command and its outcome, verbatim; any claim you could not reproduce
FINDINGS:
  1. [critical|high|medium|low|nit] <file>:<line> — <what is wrong>. Failure: <one
     sentence: who does what, and what goes wrong>.
  2. ...
  (or: none)
DOCTRINE: one line per principle, pass or fail with the diff line for any fail
NOTES: anything you noticed that is not a finding; questions for the librarian
```

---

## Re-review variant

After the implementer commits its fixes, resume the **same** reviewer (it has the context)
with this in place of "What to do" — unless the fix round changed the tier (Route rules 3, 4
and 6):
a resumed agent keeps its model, so dispatch a fresh reviewer at the new tier with the full
brief, its `Model:` line updated, and the previous report pasted above this block.

```
Fix commits since your last review: git -C $WORKTREE log --oneline <last reviewed sha>..HEAD
<list them>. They are new commits; the ones you reviewed are unchanged.
Declined by the implementer, with its reasons:
<finding number — reason, one per line; or "none">

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

## Verdict meanings

| Verdict | Means | Librarian's next move |
|---|---|---|
| `CLEAR` | Nothing at medium or above | Record the result in the item; Land |
| `NEEDS_CHANGES` | Fixable findings at medium or above | Findings to the implementer as new commits; resume the reviewer with the re-review variant, or a fresh reviewer when the tier changed |
| `SHOW_STOPPER` | Unfixable in scope, or changes scope / an operator decision | `wi block`; operator under `decisions needed`; do not land |
| `BLOCKED` | The reviewer could not start: worktree, branch, brief or permissions wrong | Fix the brief, re-dispatch — twice at most; not a round. A third `BLOCKED`, or a permission denial, is `wi block` and the operator under `decisions needed` as a blocked item, not a show-stopper |

A fourth review round without `CLEAR` is itself a show-stopper — the cap is 4 review
rounds, the first review plus three fix rounds: block the item and ask the operator to
weigh in, with the round history from the item body.
