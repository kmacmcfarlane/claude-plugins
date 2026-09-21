# Bindings

The ten values a cycle needs from outside itself. SKILL.md § Step 0 resolves them before
any dispatch; every brief, check and landing step reads them from here, never from a
particular repo convention.

A **caller** (a skill that runs cycles, such as `librarian-mode`) supplies each value in
its handoff. A caller's handoff missing a binding is a setup error: stop and name the
missing binding; never fall back to standalone resolution under a caller. A
**standalone** run (the user invoked `/dev-cycle`) resolves each binding itself, in the
order given, and asks the user only where the table says so.

## The ten

| Binding | What it is | Standalone resolves |
|---|---|---|
| **Ground** | What may be touched at all | CLAUDE.md's `## Librarian` `Scope:` minus its `Exclude:` when that section exists (§ A librarian's repo); otherwise the whole repo. Never `.claude-sandbox/` or `.claude/` |
| **Files in scope** | What this change may touch, inside Ground | The item's or plan's files to modify, or the cycle brief's list; when none names files, `undeclared` (§ Undeclared files) |
| **Checks** | Repo commands every change must pass, on top of the generic checklist | § Checks below |
| **Workflow** | Free-text repo workflow notes the change must follow | A `Workflow:` line in CLAUDE.md's `## Librarian` section, read only; otherwise none |
| **Base** | The branch the worktree starts from and the merge lands on | Named by the item or plan (implement's recorded base, re-verified); otherwise the default branch, § Base |
| **Model floor** | The lowest tier any role on this change may run | A `model: <tier>` line in the item body, or the invocation's own words ("at least opus"); otherwise none |
| **Record sink** | Where `dispatch:`, round, verdict, `checks:` and decision lines are appended | The item body when a store holds the target; otherwise always the scratchpad run record, `<scratchpad>/dev-cycle/<slug>/record.md`. Never a file in an investigation series: series files belong to `/implement` and are append-only |
| **Decision channel** | How a decision reaches a human | § Decisions |
| **Terminal action** | What Land does with a `CLEAR`, checked branch | Asked once at Land, § Landing |
| **Series home** | Where the plan phase writes an investigation series | `$MAIN/.claude-sandbox/investigations/<slug>/`, the canonical path `/implement` reads |

`<scratchpad>` is the session scratchpad the system prompt names; `<slug>` is the item id,
the series slug, or a kebab-case name made from the cycle brief's goal.

## What a librarian binds

For reference, the values `librarian-mode` supplies (its own SKILL.md is authoritative):

| Binding | Librarian value |
|---|---|
| Ground | CLAUDE.md `## Librarian` `Scope:` minus `Exclude:` |
| Files in scope | The feature item's files, from factoring |
| Checks | `## Librarian` `Checks:` |
| Workflow | `## Librarian` `Workflow:` |
| Base | `main`, unless the item names another |
| Model floor | A `model:` pin in the item body |
| Record sink | The item body |
| Decision channel | `decision N:` appended to the item, carried under `decisions needed` in its Report |
| Terminal action | `git merge --no-ff` into local `main`; the push is the librarian's, after its Report; an item naming another base merges into that base, never pushed |
| Series home | `$MAIN/.claude-sandbox/investigations/<slug>/`, as standalone — tooling state like the store, written by the cycle, never a custody edit; agents write there only the series, and dispatched commits never include `.claude-sandbox/` |

## A librarian's repo

A standalone run in a repo whose CLAUDE.md carries a `## Librarian` section honours it,
read only: Ground is its `Scope:` minus its `Exclude:` (a section with no `Scope:` line,
or `whole repo`, means the whole repo), and its `Checks:` and `Workflow:` feed those
bindings as the table says. The run never refuses because of it and never widens it: a
path outside that Ground is out of scope like any other — the implementer lists it under
OPEN QUESTIONS, and a diff that touches it is a finding at medium. The section is never
written from a cycle.

## Undeclared files

When neither the item, the plan nor the cycle brief names the files to change, the Files in
scope binding is `undeclared` — never a guess. The implementer brief then says
`Files in scope: undeclared`, and the implementer lists every file it changed under
CHANGED with a one-line reason each. The reviewer grades each changed file against the
item's or plan's intent: a file the intent does not justify is a finding at medium. A
declared list keeps the stricter rule: anything outside it is a finding at medium.

After each implementer return, the orchestrator merges that round's CHANGED into one
cumulative block in the record sink — a fix round's CHANGED lists only its own files:

```
changed:
- <path> — <one-line reason>
```

A file changed again keeps one line, with its latest reason. The review brief pastes this
block, and the checklist's scope check (section 1) compares the diff against it.

## Review target

`review <branch>` mode's Step 0 resolves the branch's own worktree in place of Step 3
(no `worktree-<name>` branch is created):

1. An existing worktree already checked out on `<branch>`: `git -C "$MAIN" worktree list
   --porcelain`, matched against `refs/heads/<branch>`. Use it as is.
2. Otherwise add one, on the branch itself:

   ```bash
   git -C "$MAIN" worktree add .claude/worktrees/review-<branch> <branch>
   ```

   The same `.git/info/exclude` check as Step 3 applies before adding it.

Base still resolves as usual (§ Base below) — it is what Land would merge into, not what
the branch was built from. Files in scope, when a caller, item or plan names them, still
bounds the reviewer's per-file grading, same as any other run; `undeclared` when nothing
does, and the reviewer grades the whole diff against the item's or plan's stated intent.

## Checks

Take the first source that answers:

1. A `checks:` line already in the record sink — a resumed or re-run target never asks
   twice.
2. `Checks:` in CLAUDE.md's `## Librarian` section, when the section exists. Read only.
3. Detect, then **ask once**. Look, do not run: read the files named below. Offer at most
   three detected commands in one AskUserQuestion multiSelect question, recommended
   first, then always `None beyond the generic checklist` last; list any further
   detections in the question text so the user can paste them into Other. Ticked
   commands and Other text are the checks; an empty submit or only `None…` means none;
   `None…` ticked alongside commands is ignored.

| Evidence | Offered command |
|---|---|
| `go.mod` at the root | `go test` with the all-packages pattern: `.` then `/...`, written joined (split here only to pass the dot-slash lint) |
| a `Makefile` with a `test:` target | `make test` |
| `package.json` with a `scripts.test` entry | `npm test` |
| `scripts/check-*.sh` | each script, by path |
| `plugins/*/hooks/tests/` | `(cd plugins/<p>/hooks && python3 -m unittest discover -s tests -q)` |

Record the answer in the record sink as one line, `checks: <cmd>; <cmd>` or
`checks: none`. **Never write CLAUDE.md** — not a `## Librarian` section, not a new
`## Checks` section. The answer belongs to the run's record.

## Base

A base named by the item or the plan wins; re-verify it exists
(`git -C "$MAIN" rev-parse --verify <base>`). Otherwise detect the default branch, do not
assume it:

```bash
git -C "$MAIN" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##'
```

Empty (no remote, or no remote HEAD): the branch the main checkout is on, stated in the
Step 0 summary so the user can correct it. A non-default base is never chosen silently.

## Decisions

A caller's channel is used as bound. Standalone: exactly one pending decision goes
through AskUserQuestion, whose options carry the choices, recommended first; two or more
go as one numbered prose list — one decision per number, each with its options and their
impact, recommendation first — so the user answers by number. Never in the same turn as a
heavy analysis: end the turn with the analysis and ask in the next. Append each raised
decision to the record sink as `decision: <one line>` before asking.

## Resume

Step 0.4 reads the record sink for a target that already carries `dispatch:`, round or
verdict lines, before any dispatch of its own — a rerun of a target that was interrupted,
whether by the session ending, a `BLOCKED` handoff, or the operator stopping it:

1. **A `CLEAR` verdict** recorded against a HEAD sha that still matches the target
   worktree's current HEAD (`git -C "$MAIN"/<worktree path> rev-parse HEAD`): skip
   straight to Step 5. A HEAD that has moved since — a human pushed a fix, or a dispatch
   whose return the interrupted run never recorded — makes the recorded `CLEAR` stale;
   treat it as no verdict and resume at Step 4 instead.
2. **A `NEEDS_CHANGES`, `SHOW_STOPPER` or `BLOCKED` verdict, or a `dispatch:` line with no
   verdict recorded after it**: resume at Step 4, with the round already recorded
   counting toward the cap of 4 review rounds.
3. **A `dispatch:` line with no return recorded at all** (the run stopped mid-dispatch,
   before the agent reported back): treat that dispatch as never sent; re-dispatch at the
   same role, tier and round.
4. **No `dispatch:` line**, but a `checks:`, `decision:` or `changed:` line already
   recorded: start at Step 1, using those recorded bindings instead of re-resolving or
   re-asking them.
5. **No record at all**: start at Step 1 as normal; there is nothing to resume.

A resumed run never repeats a question the record sink already answers, and never
re-dispatches a round that already returned — only one that never returned, or the next
one the last recorded state calls for.

## Landing

Standalone, ask once at Land — AskUserQuestion, options in this order:

1. `Merge to <base> locally, no push` — `git merge --no-ff` into the local base, worktree
   removed, branch deleted. Nothing leaves the machine.
2. `Leave the branch` — no merge; the worktree and `worktree-<name>` stay for the user;
   the item, when there is one, gets a handoff instead of `wi done`.
3. `Merge and push` — option 1, then `git -C "$MAIN" push origin <base>`, fast-forward
   only, never `--force`.

Never push unless the user picked option 3 or the invocation asked for it in words. A
rejected push stops: never pull, rebase or force around it — report it.

## Store

A work-item store is optional. Look in the main checkout for `.claude-sandbox/work/`, then
`.work/`; the first that exists is the store. No store: the record sink is the scratchpad
run record, and nothing is filed. Never run `wi init` from a
cycle.

`wi` itself comes from the repo's own tree when it carries the `work-items` plugin, else
from the installed plugin:

```bash
export WI_ROOT="$MAIN/.claude-sandbox/work"   # or "$MAIN/.work"
WI_PY=$(ls "$MAIN"/plugins/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)
P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"
test -n "$WI_PY" || WI_PY="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["plugins"]["work-items@kmacmcfarlane"][0]["installPath"])' "$P/installed_plugins.json" 2>/dev/null)/skills/work-items/scripts/wi.py"
test -f "$WI_PY" || WI_PY=$(ls -t "$P"/cache/kmacmcfarlane/work-items/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)
WI="python3 $WI_PY"
```

`${CLAUDE_PLUGIN_ROOT}` is dev-flow's root and carries no `wi`. A store with no `wi`
anywhere: say once that `work-items` is not installed, and run with the scratchpad record
as the sink.

The same resolved line, with absolute paths, is what the briefs' `CLI:` line carries.
