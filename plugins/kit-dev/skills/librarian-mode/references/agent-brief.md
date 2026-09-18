# Agent brief template

The dispatch brief for one feature. Fill every placeholder; delete nothing except the
fix-round clause under Commit, which is included only when resuming or re-dispatching the
implementer with review findings, and the repo-workflow and dev-flow blocks when their
condition does not hold. The agent starts
with none of the librarian's context and must be able to finish from this text alone. Send
it as the prompt of one background `general-purpose` Agent. The librarian sets the
`Model:` line from the Route step in SKILL.md and passes the same value to the Agent
tool's `model` field — the brief tells the agent which tier it runs on, the field
enforces it, and the item body's `dispatch:` line records it. A fix round that raises the
tier is a fresh dispatch with the full brief and the findings, never a resume — a resumed
agent keeps its model; resume only when the tier is unchanged.

The prohibitions and the return contract are fixed. The verification commands vary with what
the item touches — take them from `review-checklist.md`, plus every command under
`Checks:` in CLAUDE.md's `## Librarian` section. Its `Workflow:` notes go in verbatim.

---

```
You are building one change to this repo's librarian-owned custody layer, in an
isolated git worktree. Work ONLY inside this directory and nowhere else:

  WORKTREE=<absolute path of the main checkout>/.claude/worktrees/<name>

First verify it exists and is on branch `worktree-<name>`
(`git -C $WORKTREE branch --show-current`). If not, stop and report BLOCKED.

## The work item

Store: export WI_ROOT=<absolute path to the main checkout>/.claude-sandbox/work
CLI:   WI="python3 $(ls $WORKTREE/plugins/*/skills/work-items/scripts/wi.py | head -1)"
       <on a repo with no plugins/ tree, substitute the installed work-items plugin's
       wi.py by absolute path: ls -t "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/kmacmcfarlane/work-items/*/skills/work-items/scripts/wi.py | head -1>

Read it first, in full:  $WI show <id>
Item: <id> — <title>
Model: <sonnet|opus|fable> — <the Route signal that chose it, or "default">
Acceptance: <one or two lines, copied from the item body>
Base branch: <main, unless the item names another>
Files in scope: <explicit list; anything else is out of scope>

## Doctrine — read before writing

- $WORKTREE/README.md — its doctrine, catalog and placement sections when present,
  otherwise its plugin tables; on a repo with no plugins/ tree, in full
- $WORKTREE/CLAUDE.md — layout and conventions, and its `## Librarian` section: its
  Scope is the only ground you may touch, and never its Exclude
- <when the change adds or edits a skill:> the create-skill skill at
  $WORKTREE/plugins/*/skills/create-skill/SKILL.md and its references/ — follow it as the
  authoring procedure.
- <any other skill or reference the item names, by absolute path>

Rules that reviewers reject on sight:
- Skill reference paths are bare relative paths (`references/x.md`) — no dot-slash prefix,
  no skill-dir variable.
- Frontmatter keys are exactly: name, description, disable-model-invocation, allowed-tools,
  argument-hint. Folder name equals `name`. No README.md inside a skill folder.
- No angle brackets in `name` or `description` (fine in `argument-hint`); description under
  1024 characters, what + when + triggers.
- A change to the marketplace's shape (plugin added/moved/retired, skill added to a plugin)
  updates the README catalog and the CLAUDE.md layout block in the SAME commit.
- Hooks, status lines and settings writes belong only in the plugin whose stated aim is
  that behavior, never as passengers on a knowledge skill.

## What to do

<the approach, as specific as the item allows: which files, which sections, which pattern to
copy and from where — absolute paths>

<when ## Librarian has Workflow: — the repo's workflow, follow it:>
<the Workflow: notes, verbatim>

<when dev-flow is installed (§ dev-flow below) — spike or feature:>
Use the dev-flow skills for their method, not their git or their dialogs: a spike
through /investigate, a feature through /investigate then /implement. Invoke both as
running non-interactively (each skill's § Running non-interactively), and:
- /investigate: its research, requirements and plan steps. Write the series under
  <absolute scratchpad path>/investigations/<slug>/, never inside $WORKTREE, and name
  that path in your report. Skip its branch survey (the base is fixed above) and its
  retrospective.
- /implement, on that series: its plan, build and verify steps and its review gates,
  with every edit made in $WORKTREE itself. Skip its repo and base-branch step (no
  fetch, no new branch or worktree, nothing run in the main checkout), its whole
  Finalize step (no terminal action, merge, push, work-item update, outcome or index
  write) and its retrospective. The Commit section below is the only commit.
- A question either skill would put to the user: take the least irreversible choice
  and record it under DEVIATIONS, or, if it blocks, under OPEN QUESTIONS
  (NEEDS_CONTEXT when you cannot go on). Never AskUserQuestion.
- `git -C $WORKTREE status --short` is empty apart from your commit before you report.

## Verification — run all, report outcomes verbatim

<paste the applicable commands from review-checklist.md, each with $WORKTREE substituted>
<then each command under Checks: in ## Librarian, run from $WORKTREE, verbatim>

## Commit

One commit in the worktree. Message format `<verb>: <aspect> - <description>` with verb one
of added / updated / removed / bumped; body explains what and why. Write the message to a
file under <absolute scratchpad path> and use `git commit -F <path>`. Stage the specific
paths; never `git add .` or `git add -A`. Do not commit anything under .claude-sandbox/ or
.claude/.

<fix round only — include when resuming or re-dispatching with review findings:>
Fix round <n> — the nth re-dispatch or resume with review findings, i.e. review round n+1
of a 3-review-round cap. The Model line above is this round's tier (Route rules 3 and 6);
when it differs from the previous round's, this is a fresh dispatch, not a resume.
Findings to fix are listed below, verbatim. Fix each finding at medium or
above; each low/nit you decline, state under DECLINED with a reason. Fix as one or more NEW
commits on top of <reviewed sha>; never amend, rebase, or squash — the reviewer diffs from
that sha. Report every new sha under COMMIT.

## Prohibitions

- Do not merge, rebase, push, or check out any other branch.
- Do not edit any file outside $WORKTREE.
- Do not touch files outside "Files in scope", however tempting; list the temptation under
  OPEN QUESTIONS instead. Nothing outside the `## Librarian` Scope, or inside its
  Exclude, is ever in scope.
- Do not create README.md, CHANGELOG.md, or any documentation file the item did not ask for.
- Do not run `wi done`, `wi claim` or `wi release`; the librarian owns the item's state. You
  MAY run `$WI handoff <id> --doing ... --next ...` if you stop mid-way.
- Do not ask the operator anything; put the question under OPEN QUESTIONS and choose the
  least irreversible interpretation, or return NEEDS_CONTEXT if you cannot proceed at all.

## Report back (this exact shape)

STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
CHANGED: files, one per line, absolute paths, with a phrase each
VERIFIED: each command and its outcome, verbatim
DEVIATIONS: from the item, with why
COULD NOT DO: anything the item asked for that is not in the commit
OPEN QUESTIONS: anything you could not settle
DECLINED: (fix rounds only) each declined low/nit finding with its reason, or none
COMMIT: sha and message subject — in a fix round, every new sha
```

---

## Status meanings

| Status | Means | Librarian's next move |
|---|---|---|
| `DONE` | Every acceptance line met, all checks green, one commit | Review (the sub-agent gate), then Land |
| `DONE_WITH_CONCERNS` | Committed and green, but the agent flagged a judgement call | Read the concerns; put them in the reviewer brief; Review, then Land |
| `NEEDS_CONTEXT` | Could not proceed without an answer; nothing or little committed | Answer in the item body, re-dispatch with the answer |
| `BLOCKED` | Worktree wrong, permission denied, dependency missing | `wi block`, route to the operator |

## dev-flow

`investigate` and `implement` (the dev-flow plugin) count as installed when any of these
holds; check once per session, at Intake:

- the session's skill list names them, under any plugin prefix;
- `ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/*/dev-flow/*/skills/implement/SKILL.md`
  finds a file;
- the repo carries them: `ls "$MAIN"/plugins/*/skills/implement/SKILL.md`.

Installed: include the dev-flow block in every spike or feature brief. Not installed: the
Intake note in the item says they can be used (install `dev-flow`), and the brief omits
the block; the work goes on without them. Bugs, chores and refactors never need it.

## Sharpening a brief for re-dispatch

A rejected result is re-dispatched, not fixed. Add to the brief, in this order:

1. What was wrong, quoted from the check output or the diff line.
2. The rule it broke, by principle number or checklist item.
3. The specific file and shape that would have passed.

Keep the rest of the brief identical so the diff between runs is the guidance, not the
noise.
