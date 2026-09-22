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
| **Record sink** | Where the run's record lines are appended (§ Record line shapes) | The item body when a store holds the target; otherwise always the scratchpad run record, `<scratchpad>/dev-cycle/<slug>/record.md`. Never a file in an investigation series: series files belong to `/implement` and are append-only. An item body is durable across sessions; **a scratchpad sink is session-scoped by contract**, so a store-less run's record cannot be read outside the session that wrote it (or one that inherits the same scratchpad) — Step 0's summary says so |
| **Decision channel** | How a decision reaches a human | § Decisions |
| **Terminal action** | What Land does with a `CLEAR`, checked branch | Asked once at Land, § Landing |
| **Series home** | Where the plan phase writes an investigation series | `$MAIN/.claude-sandbox/investigations/<slug>/`, the canonical path `/implement` reads |

`<scratchpad>` is the session scratchpad the system prompt names; `<slug>` is the item id,
the series slug, a kebab-case name made from the cycle brief's goal, or — `review
<branch>` mode with no other target — `<branch>` with every `/` written `-`.

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
(no `worktree-<name>` branch is created), and records it as the workspace of the run's
`target:` line — `target: review <branch> <worktree path>` (§ Record line shapes) —
before any dispatch:

1. The main checkout is already on `<branch>` (`git -C "$MAIN" branch --show-current`
   equals it): the worktree path is `$MAIN` itself for reading and reviewing — there is
   no separate worktree to add. Land is different: merging still needs the main checkout
   on `<base>` (SKILL.md § Step 5.3), which case 1 does not satisfy, and the cycle never
   checks `<base>` out over `<branch>` to get there. Land in this case stops and asks
   instead of merging (§ Landing below, `troubleshooting.md` § Landing).
2. Otherwise, an existing worktree already checked out on `<branch>`: `git -C "$MAIN"
   worktree list --porcelain`, matched against `refs/heads/<branch>`. Use its listed path
   as is.
3. Otherwise add one, on the branch itself, at `.claude/worktrees/review-<slug>`, `<slug>`
   being `<branch>` with every `/` written `-` (§ The ten, `<slug>`):

   ```bash
   git -C "$MAIN" worktree add .claude/worktrees/review-<slug> <branch>
   ```

   The same `.git/info/exclude` check as Step 3 applies before adding it. The path that
   command takes is relative to `$MAIN`; what is recorded is the absolute one,
   `"$MAIN"/.claude/worktrees/review-<slug>`.

Every later step reads the worktree by this resolved absolute path, as the `target:`
line carries it, never reconstructed as `"$MAIN"/.claude/worktrees/<name>` — cases 1 and
2 do not live there.

Base still resolves as usual (§ Base below) — it is what Land would merge into, not what
the branch was built from. Files in scope, when a caller, item or plan names them, still
bounds the reviewer's per-file grading, same as any other run; `undeclared` when nothing
does, and the reviewer grades the whole diff against the recorded Intent (§ Intent)
instead of an implementer's per-file reasons.

## Intent

`review <branch>` mode with no work item or plan (SKILL.md § Step 0.2) has no acceptance
to grade against. Before dispatching the reviewer, collect one: ask the user for a
one-line intent in the same question as any other Step 0 ask; if none is given, record
`intent: commit messages are the intent` and use the branch's own commit subjects
(`git -C <worktree path> log --oneline <base>..<branch>`) as what the reviewer grades
against. Record it as `intent: <one line>` (§ Record line shapes) in the record sink.

In this mode, "Files changed, with reasons" in the review brief holds the branch's own
commit list, not the orchestrator's `changed:` block — there was no implementer round to
build one from. The reviewer grades each changed file against the recorded Intent instead
of a per-file reason; a file the Intent does not plausibly cover is still a finding at
medium, but § Undeclared files' "no reason" rule does not apply here — a changed file is
never itself a medium finding merely for lacking a one-line reason, since no implementer
wrote one.

## Record line shapes

Fixed shapes for the lines the steps append to the record sink; every step that writes
one uses this exact shape, and each shape below names the step, or steps, that write it —
**one writer per role**, so that no two steps can write the same line about the same
thing. Two shapes have two writers, each for a different role: `return:` (SKILL.md
§ Step 3.5 for an implementer, § Step 1 for a planner) and `answer:` (§ Decisions for a
raised decision, SKILL.md § Step 3.5 for a `NEEDS_CONTEXT`). The
record is a log, read in the order it was written:

- `dispatch: <role> <model> — <signal>` — SKILL.md § Step 2 rule 7, written before every
  dispatch (implementer, planner or reviewer)
- `agent: <role> <id> round <n>` — SKILL.md § Step 2 rule 7, written as soon as the Agent
  call returns an id, directly under the `dispatch:` line it belongs to. `<n>` is the
  round that dispatch serves (the first build or the first review is round 1). It is what
  SKILL.md § Step 4.3 resumes an agent by and what a caller copies into a handoff: an id
  that lives only in `ListAgents` is gone with the process, so the record carries it. A
  `dispatch:` with no `agent:` under it means the Agent call never returned an id.
- `return: <role> <STATUS> <token>` — SKILL.md § Step 3.5 for an **implementer** and
  SKILL.md § Step 1 for a **planner** (`plan` mode never reaches Step 3, so Step 1 is its
  only producer-return writer), written as soon as the producer's report comes back.
  `<STATUS>` is its `DONE` | `DONE_WITH_CONCERNS` | `NEEDS_CONTEXT` | `BLOCKED`;
  `<token>` is the implementer's COMMIT sha, or the series path a planner wrote. A
  reviewer's return is its `verdict:` line below — it never gets a separate `return:` of
  its own. A `BLOCKED` carries a reason, below.
- `verdict: <V> round <n> at <sha>` — SKILL.md § Step 4.5, written as soon as a
  **reviewer's** report comes back. `<n>` is the review round, counted only for
  `CLEAR`, `NEEDS_CHANGES` and `SHOW_STOPPER` — a `BLOCKED` never reached a verdict on
  the change, so it is never a round (`review-brief.md` § Verdict meanings) and carries a
  reason in place of its round number, below. `<sha>` is
  the HEAD reviewed for a change; for a **plan-mode** review, in its place:
  `at <series path>` (the review covers the whole series, not one sha) — a finding's own
  file:line still names the serial, and `baseline:` below, not this field, is what says
  whether the series has moved.
- The **`BLOCKED` reason**, on a `return:` and a `verdict:` and on no other line:

  ```
  return: <role> BLOCKED <token> — permission | setup
  verdict: BLOCKED at <token> — permission | setup
  ```

  `<token>` is what the dispatch was pointed at — the HEAD it was given, or the series
  path — and on a `BLOCKED` it is a **locator only**, saying what the setup failed on. It
  is never a freshness token: a `BLOCKED` reached no verdict on the change, so nothing
  compares it against anything. Where the writer has no such value (a reviewer blocked
  before it could read the workspace), it writes the workspace instead, and never
  fabricates a sha.

  The reason is a closed set of two values, taken from the agent's own report by the step
  that writes the line, never widened and never invented by a reader. `permission` is the
  permission-denial case (`troubleshooting.md` § Dispatch and review): never
  re-dispatched, always a decision for a human. `setup` is everything else — the brief,
  the worktree, the environment — fixable and re-dispatchable within `fix-loop.md`'s
  limit, and not a round. **A `BLOCKED` line with no reason reads as `permission`**, the
  conservative value, so a line written before this shape existed still has one.
- `baseline: <sha256 list>` — SKILL.md § Step 4.1, written before each plan-mode review:
  the output of `sha256sum <series>/[0-9][0-9]_*.md` over the serials that review covers.
  Step 4.1 also **reads** the last one, before a plan-mode re-review: re-running the same
  command and diffing it against that line is what says which serials the planner added
  or rewrote since the review being re-run, which is what the re-review is asked to check
  — the `verdict:` line's `at <series path>` cannot say it, naming the series and not its
  state. A list that has not moved means the planner wrote nothing; that is a finding for
  the re-review, not a new baseline.
- `findings: …` — SKILL.md § Step 4.5, written together with a `NEEDS_CHANGES` or
  `SHOW_STOPPER` verdict: the reviewer's FINDINGS section, pasted verbatim, one line per
  finding in the reviewer's own numbering — the source `fix-loop.md`'s NEEDS_CHANGES
  round hands to the fix dispatch unchanged.
- `target: <mode> <ref> <workspace>` — SKILL.md § Step 0.3, **every mode**, written before
  any dispatch.
  - `<mode>` is `full`, `plan` or `review <branch>`: recorded, never inferred later, and
    it names **the run the cycle actually takes, not the word the user typed**. A spike
    records `plan` however it was invoked, because a spike takes Step 1's plan dispatch,
    Step 4's plan-review variant and Step 6, and never reaches Step 3 or Land
    (SKILL.md §§ Usage, Step 1) — so its record must reduce as a plan run's does.
    Everything else that reaches Step 3 records `full`.
  - `<ref>` is the target as the run was given it: the branch (`review <branch>`), or the
    item id, series slug or plan path (`full`, `plan`). It says what was asked for; the
    workspace says where the work is.
  - `<workspace>` is the **absolute** path the run's work lives at, and it is written
    absolute even when the command that made it took a relative one: the path § Review
    target resolved (`review <branch>`), `"$MAIN"/.claude/worktrees/<name>` for the
    worktree SKILL.md § Step 3.1 adds (`full`), or — a plan run having no worktree — the
    series path under the Series home. A later step, or a later session, runs
    `git -C <workspace>` from a working directory this one cannot predict, so a
    repo-relative path here resolves against the wrong tree.

  Every later step reads the workspace from this line instead of reconstructing it.
- `intent: <one line>` — § Intent, `review <branch>` mode with no item or plan
- `decision: <question> — options: <a> | <b> | <c>` — § Decisions, written before a
  decision is raised. **Self-contained**: the question in full and its options,
  recommendation first, so that a reader who was not in the session that raised it can put
  it to a human verbatim. Under a caller it composes as
  `decision N: <question> — options: …`, so the caller's numbered channel is unchanged.
- `answer: <decision> — <reply>` — § Decisions and SKILL.md § Step 3.5 (a
  `NEEDS_CONTEXT` answer), written as soon as the reply arrives; `<decision>` repeats the
  `decision:` line's question (or, for a `NEEDS_CONTEXT`, the question). A caller's
  numbered pair — librarian-mode's `decision N: …` and `answer N: <reply>`, matched by
  `N` — is the same pair and is read the same way. A `decision:` with no matching
  `answer:` is unanswered, and an answered one is never raised again.
- `landed: <merge sha>` — SKILL.md § Step 5.5, written once Land's merge succeeds and
  before `$WI done` / `$WI handoff`. It is the record's only evidence that a target
  reached a merge, and SKILL.md § Step 6 reports it on the `verified:` line. `Leave the
  branch` lands nothing and writes no `landed:` line.
- `checks:`, the `changed:` block — §§ Checks, Undeclared files

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
decision to the record sink as `decision: <question> — options: <a> | <b> | <c>` before
asking — the question in full and its options, recommendation first, so the line can be
put to a human verbatim by a reader who was not there — and the reply as
`answer: <decision> — <reply>` (§ Record line shapes) as soon as it arrives.

## Resume

Resuming an interrupted run is not specified yet; see work item
dev-cycle-design-resume-whole-split-from-e770.

## Landing

Standalone, ask once at Land — AskUserQuestion, options in this order:

1. `Merge to <base> locally, no push` — `git merge --no-ff` into the local base, then the
   cycle's own worktree removed and its own branch deleted (`full` mode:
   `worktree-<name>`; `review <branch>` mode: only a worktree this cycle added itself at
   `.claude/worktrees/review-<slug>` — never `<branch>`, which is the author's and is
   never deleted). Nothing leaves the machine.
2. `Leave the branch` — no merge; whatever the cycle itself added (the worktree, and in
   `full` mode `worktree-<name>`) stays for the user; the item, when there is one, gets a
   handoff instead of `wi done`. `review <branch>` mode never touches `<branch>` itself
   either way — it was never the cycle's to remove.
3. `Merge and push` — option 1, then `git -C "$MAIN" push origin <base>`, fast-forward
   only, never `--force`.

`review <branch>` mode merges `<branch>` itself in place of `worktree-<name>`:

```bash
git -C "$MAIN" merge --no-ff -m "<message>" <branch>
```

from the worktree path § Review target resolved, once the main checkout is on `<base>`
(SKILL.md § Step 5.3) — the same requirement `full` mode has. § Review target's case 1
(the main checkout already on `<branch>` itself) never satisfies that on its own:
checking `<base>` out over `<branch>` to get there would mean checking out over the
user's own work, which the cycle never does. **Case 1 at Land stops and asks**
(`troubleshooting.md` § Landing, "the main checkout is not on the base") instead of
merging — the user switches the main checkout to `<base>` themselves and Land re-runs
its checks and diff, or picks `Leave the branch`, which never needs the main checkout
touched. Cases 2 and 3 (an existing or added worktree elsewhere) merge normally once the
main checkout, separately, is on `<base>`; cleanup then removes only a worktree case 3
added, never `<branch>` itself.

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
