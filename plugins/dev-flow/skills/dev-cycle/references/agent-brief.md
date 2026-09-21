# Agent brief template

The dispatch brief for one change. Fill every placeholder from the run's bindings
(`bindings.md`); delete nothing except the blocks marked conditional — the fix-round and
merge-conflict clauses under Commit (only in those rounds), the Workflow block (only when
the Workflow binding is set) and the dev-flow block (only for a feature with no plan yet,
or a given plan). The agent starts with none of the
orchestrator's context and must be able to finish from this text alone. Send it as the
prompt of one background `general-purpose` Agent. The orchestrator sets the `Model:` line
from SKILL.md § Step 2 and passes the same value to the Agent tool's `model` field — the
brief tells the agent which tier it runs on, the field enforces it, and the record sink's
`dispatch:` line records it. A fix round that changes the tier (a bump, or the fable
fallback) is a fresh dispatch with the full brief and the findings, never a resume — a
resumed agent keeps its model; resume only when the tier is unchanged.

The prohibitions and the return contract are fixed. The verification commands vary with what
the change touches — take them from `review-checklist.md`, plus every command in the Checks
binding. The Workflow binding goes in verbatim.

---

```
You are building one change to this repository, in an isolated git worktree. Work ONLY
inside this directory and nowhere else:

  WORKTREE=<absolute path of the main checkout>/.claude/worktrees/<name>

First verify it exists and is on branch `worktree-<name>`
(`git -C $WORKTREE branch --show-current`). If not, stop and report BLOCKED.

## The change

<with a work item:>
Store: export WI_ROOT=<absolute path of the store>
CLI:   WI="python3 <absolute path of wi.py, resolved per bindings.md § Store>"
Read it first, in full:  $WI show <id>
Item: <id> — <title>
<without one:>
Brief: <the cycle brief or the plan file, by absolute path — read it first, in full>

Model: <sonnet|opus|fable> — <the routing signal that chose it, or "default">
Acceptance: <one or two lines, copied from the item, plan or brief>
Base branch: <the Base binding>
Ground: <the Ground binding — the only ground you may touch>
Files in scope: <explicit list, inside Ground; anything else is out of scope — or
                "undeclared" (bindings.md § Undeclared files)>

## Doctrine — read before writing

- $WORKTREE/README.md — its doctrine, catalog and placement sections when present,
  otherwise its plugin tables; on a repo with no plugins/ tree, in full
- $WORKTREE/CLAUDE.md — layout and conventions
- <when the change adds or edits a skill:> the create-skill skill at
  $WORKTREE/plugins/*/skills/create-skill/SKILL.md and its references/ — follow it as the
  authoring procedure.
- <any other skill or reference the change names, by absolute path>

Rules that reviewers reject on sight:
- Skill reference paths are bare relative paths (`references/x.md`) — no dot-slash prefix,
  no skill-dir variable. A pointer into a sibling skill of the same plugin puts the
  sibling's backticked name right before the bare path.
- Frontmatter keys follow the house rule: every skill declares name, description,
  disable-model-invocation, allowed-tools, argument-hint; any other key must be a field the
  Claude Code skills docs define (the list is in the create-skill skill's frontmatter
  reference, kit-dev plugin); no key twice. The set is closed because undocumented keys
  are usually typos, and claude.ai / Skills API uploads hard-fail on unknown keys.
  allowed-tools only pre-approves tools; it never restricts them. Folder name equals
  `name`. No README.md inside a skill folder.
- No angle brackets in `name` or `description` (fine in `argument-hint`); description under
  1024 characters, what + when + triggers.
- A change to the marketplace's shape (plugin added/moved/retired, skill added to a plugin)
  updates the README catalog and the CLAUDE.md layout block in the SAME commit.
- Hooks, status lines and settings writes belong only in the plugin whose stated aim is
  that behavior, never as passengers on a knowledge skill.
(On a repo without these conventions, the rules apply where their subject exists.)

## What to do

<the approach, as specific as the change allows: which files, which sections, which pattern
to copy and from where — absolute paths>

<conditional — when the Workflow binding is set: the repo's workflow, follow it:>
<the Workflow binding, verbatim>

<conditional — a feature with no plan yet (dev-flow block):>
Use the dev-flow skills for their method: /investigate, then /implement on the series it
wrote, each in its orchestrated mode (each skill's § Running under an orchestrator), with
these inputs:
- Series home: <the Series home binding, absolute> — never inside $WORKTREE; name the
  series path in your report.
- Worktree: $WORKTREE. Base: the Base branch above.
The Commit section below is the only commit; the documentation follow-ups implement's mode
keeps belong in it. Never AskUserQuestion: a question either skill would put to the user
is the least irreversible choice under DEVIATIONS, or, if it blocks, under OPEN QUESTIONS
(NEEDS_CONTEXT when you cannot go on). `git -C $WORKTREE status --short` is empty apart
from your commit before you report.
<conditional — a given plan: the same block without /investigate and the Series home
line; /implement runs in its orchestrated mode on the given series or plan file.>

## Verification — run all, report outcomes verbatim

<paste the applicable commands from review-checklist.md, each with $WORKTREE substituted>
<then each command in the Checks binding, run from $WORKTREE, verbatim>

To show a check fails without the change (revert-to-verify), commit first, then put the
old version back one path at a time — `git -C $WORKTREE checkout <base> -- <path>`, run
the check, `git -C $WORKTREE checkout HEAD -- <path>` — or copy files to the scratchpad and
back. Never `git stash` or `git stash pop`: the stash stack is shared by every worktree and
session of this repository, so a pop can apply another run's changes here.

## Commit

One commit in the worktree. Message format `<verb>: <aspect> - <description>` with verb one
of added / updated / removed / bumped; body explains what and why. Write the message to a
file under <absolute scratchpad path> and use `git commit -F <path>`. Stage the specific
paths; never `git add .` or `git add -A`. Do not commit anything under .claude-sandbox/ or
.claude/.

<conditional — fix round only: include when resuming or re-dispatching with review findings:>
Fix round <n> — the nth re-dispatch or resume with review findings, i.e. review round n+1
of a 4-review-round cap. The Model line above is this round's tier (routing rules 3 and 6);
when it differs from the previous round's, this is a fresh dispatch, not a resume.
Findings to fix are listed below, verbatim. Fix each finding at medium or
above; each low/nit you decline, state under DECLINED with a reason. Fix as one or more NEW
commits on top of <reviewed sha>; never amend, rebase, or squash — the reviewer diffs from
that sha. Report every new sha under COMMIT. A finding against a commit subject or
message is always low (the fix-loop rule): never rewrite history for it — no reset, amend
or rebase; decline it under DECLINED with "carried in the merge message".
The one exception: a secret or credential in any committed content on this branch — a file
in any commit, even one a later commit removed, or any message — is critical. Only then is
the branch rebuilt: `git reset --soft <merge-base sha pasted here by the orchestrator>`,
the secret taken out of any file that still holds it, and one recommit with every message
clean — never a rebase, never onto the base branch. That overrides the new-commits rule
above; the no-rebase prohibition below still holds. Before reporting, confirm
`git log -p --cc <merge-base sha>..HEAD` holds no trace of it, searching by key name or
shape. Never write the secret's value anywhere — files, messages, commands, report: name
it by commit sha, file and key only. Never call the credential safe; rotating it is the
operator's call.

<conditional — merge-conflict round only: include when Land's merge conflicted:>
Your branch conflicts with <base> (the conflicting paths, from the aborted merge: <list>).
Bring the base in as ONE NEW merge commit on top of <reviewed sha>:
`git -C $WORKTREE merge --no-ff <base>`, resolve each conflict with this change's own
approach as the tiebreaker — never take one side wholesale — re-run the verification
above, and commit the merge. This is the one exception to the no-merge prohibition below;
never rebase, and never merge anything but <base>. Report the merge sha under COMMIT and
each resolution in one line under DEVIATIONS.

## Prohibitions

- Do not merge, rebase, push, or check out any other branch. (One exception: a
  merge-conflict round merges <base> into this branch, as briefed above.)
- Do not edit any file outside $WORKTREE.
- Do not touch files outside "Files in scope", however tempting; list the temptation under
  OPEN QUESTIONS instead. When Files in scope is "undeclared", touch only what the
  acceptance needs, and justify every changed file under CHANGED. Nothing outside
  Ground is ever in scope.
- Do not run `git stash` in any form (see Verification).
- Do not create README.md, CHANGELOG.md, or any documentation file the change did not ask
  for.
- Do not run `wi done`, `wi claim` or `wi release`; the orchestrator owns the item's state.
  You MAY run `$WI handoff <id> --doing ... --next ...` if you stop mid-way.
- Do not ask the user anything; put the question under OPEN QUESTIONS and choose the
  least irreversible interpretation, or return NEEDS_CONTEXT if you cannot proceed at all.

## Report back (this exact shape)

STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
CHANGED: files, one per line, absolute paths, with a phrase each (with undeclared
         Files in scope: a one-line reason each)
VERIFIED: each command and its outcome, verbatim
DEVIATIONS: from the change as briefed, with why
COULD NOT DO: anything the change asked for that is not in the commit
OPEN QUESTIONS: anything you could not settle
DECLINED: (fix rounds only) each declined low/nit finding with its reason, or none
COMMIT: sha and message subject — in a fix round, every new sha
```

---

## Plan variant

For SKILL.md § Step 1 (`plan` mode, or a spike): one background `general-purpose` agent,
no worktree. Use the brief above with these changes: drop the WORKTREE lines, Files in
scope, Verification and Commit; set What to do to /investigate alone, in its orchestrated
mode (the `investigate` skill's § Running under an orchestrator) with the Series home
binding and the Base, and no worktree; replace the prohibitions'
worktree lines with "Do not edit, commit or stage anything in the repository; write only
under the Series home". Report shape: STATUS, SERIES (absolute path), OPEN QUESTIONS (each
marked blocking or not), DEVIATIONS. The series is gated like a change, by
`review-brief.md` § Plan-review variant. A fix round re-dispatches this brief with the
findings verbatim and the rules of the `investigate` skill's
`references/investigation-format.md`: never edit a written serial; write the revision as a
new serial at the next free number, opening with a `Supersedes` block that names what the
findings overturned; regenerate `INDEX.md`.

## Status meanings

| Status | Means | Orchestrator's next move |
|---|---|---|
| `DONE` | Every acceptance line met, all checks green, one commit | Review (the sub-agent gate), then Land |
| `DONE_WITH_CONCERNS` | Committed and green, but the agent flagged a judgement call | Read the concerns; put them in the reviewer brief; Review, then Land |
| `NEEDS_CONTEXT` | Could not proceed without an answer; nothing or little committed | Answer in the record sink, re-dispatch with the answer |
| `BLOCKED` | Worktree wrong, permission denied, dependency missing | `wi block` when there is an item; raise it through the decision channel |

## dev-flow

`investigate` and `implement` ship in the dev-flow plugin beside this skill, so they are
present wherever a cycle runs; there is nothing to detect. Each owns a "Running under an
orchestrator" mode: given series, worktree and base, no git or dialogs of its own, and a
fixed return shape. The dev-flow block above only points at those modes and names the
inputs, so when either skill renumbers its steps, its own mode changes in the same commit
and this brief does not. implement's mode keeps its documentation follow-ups, so docs the
change made wrong land in the change. Bugs, chores and refactors with clear acceptance
never need the block.

## Sharpening a brief for re-dispatch

A rejected result is re-dispatched, not fixed. Add to the brief, in this order:

1. What was wrong, quoted from the check output or the diff line.
2. The rule it broke, by principle number or checklist item.
3. The specific file and shape that would have passed.

Keep the rest of the brief identical so the diff between runs is the guidance, not the
noise.
