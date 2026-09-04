# Agent brief template

The dispatch brief for one feature. Fill every placeholder; delete nothing. The agent starts
with none of the librarian's context and must be able to finish from this text alone. Send
it as the prompt of one background `general-purpose` Agent.

The prohibitions and the return contract are fixed. The verification commands vary with what
the item touches — take them from `review-checklist.md`.

---

```
You are building one change to the claude-plugins marketplace's shared agent layer, in an
isolated git worktree. Work ONLY inside this directory and nowhere else:

  WORKTREE=<absolute path of the main checkout>/.claude/worktrees/<name>

First verify it exists and is on branch `worktree-<name>`
(`git -C $WORKTREE branch --show-current`). If not, stop and report BLOCKED.

## The work item

Store: export WI_ROOT=<absolute path to the main checkout>/.claude-sandbox/work
CLI:   WI="python3 $(ls $WORKTREE/plugins/*/skills/work-items/scripts/wi.py | head -1)"

Read it first, in full:  $WI show <id>
Item: <id> — <title>
Acceptance: <one or two lines, copied from the item body>
Base branch: <main, unless the item names another>
Files in scope: <explicit list; anything else is out of scope>

## Doctrine — read before writing

- $WORKTREE/README.md — its doctrine, catalog and placement sections when present,
  otherwise its plugin tables
- $WORKTREE/CLAUDE.md — layout and conventions
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

## Verification — run all, report outcomes verbatim

<paste the applicable commands from review-checklist.md, each with $WORKTREE substituted>

## Commit

One commit in the worktree. Message format `<verb>: <aspect> - <description>` with verb one
of added / updated / removed / bumped; body explains what and why. Write the message to a
file under <absolute scratchpad path> and use `git commit -F <path>`. Stage the specific
paths; never `git add .` or `git add -A`. Do not commit anything under .claude-sandbox/ or
.claude/.

## Prohibitions

- Do not merge, rebase, push, or check out any other branch.
- Do not edit any file outside $WORKTREE.
- Do not touch files outside "Files in scope", however tempting; list the temptation under
  OPEN QUESTIONS instead.
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
COMMIT: sha and message subject
```

---

## Status meanings

| Status | Means | Librarian's next move |
|---|---|---|
| `DONE` | Every acceptance line met, all checks green, one commit | Review & land |
| `DONE_WITH_CONCERNS` | Committed and green, but the agent flagged a judgement call | Read the concerns before review; land or re-dispatch |
| `NEEDS_CONTEXT` | Could not proceed without an answer; nothing or little committed | Answer in the item body, re-dispatch with the answer |
| `BLOCKED` | Worktree wrong, permission denied, dependency missing | `wi block`, route to the operator |

## Sharpening a brief for re-dispatch

A rejected result is re-dispatched, not fixed. Add to the brief, in this order:

1. What was wrong, quoted from the check output or the diff line.
2. The rule it broke, by principle number or checklist item.
3. The specific file and shape that would have passed.

Keep the rest of the brief identical so the diff between runs is the guidance, not the
noise.
