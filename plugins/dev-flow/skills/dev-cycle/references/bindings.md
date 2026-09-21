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
(no `worktree-<name>` branch is created), and records it as `target: <branch> <worktree
path>` (§ Record line shapes) before any dispatch:

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

   The same `.git/info/exclude` check as Step 3 applies before adding it.

Every later step reads the worktree by this resolved absolute path, never reconstructed
as `"$MAIN"/.claude/worktrees/<name>` — cases 1 and 2 do not live there.

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

Fixed shapes a resume (§ Resume) parses back out of the record sink; every step that
writes one uses this exact shape, so a resume never has to guess. Read them in the order
they appear in the record sink — the record is a log, and § Resume acts on its **last**
line, not the first match anywhere in it:

- `dispatch: <role> <model> — <signal>` — SKILL.md § Step 2 rule 7, written before every
  dispatch (implementer or reviewer)
- `return: <role> <STATUS> <sha>` — SKILL.md § Step 3.5, written as soon as an
  **implementer's** report comes back; `<sha>` is its COMMIT. A reviewer's return is its
  `verdict:` line below — it never gets a separate `return:` of its own.
- `verdict: <V> round <n> at <sha>` — SKILL.md § Step 4.5, written as soon as a
  **reviewer's** report comes back, and counts as that dispatch's return. `<n>` is the
  review round, counted only for `CLEAR`, `NEEDS_CHANGES` and `SHOW_STOPPER` (§ Resume
  rule 6 excludes `BLOCKED` from the count, since it never reached a verdict on the
  change). `<sha>` is the HEAD reviewed for a change; for a **plan-mode** review, in its
  place: `at <series path>` (the review covers the whole series, not one sha) — a
  finding's own file:line still names the serial.
- `findings: …` — SKILL.md § Step 4.5, written together with a `NEEDS_CHANGES` or
  `SHOW_STOPPER` verdict: the reviewer's FINDINGS section, pasted verbatim, one line per
  finding in the reviewer's own numbering. § Resume rule 5 hands this block to the fix
  dispatch unchanged — it is the source `fix-loop.md`'s NEEDS_CHANGES round reads from.
- `landed: <merge sha>` — SKILL.md § Step 5.5, written once Land's merge succeeds, before
  `$WI done`/`$WI handoff`. § Resume checks this first (rule 1): its presence means the
  target already landed, full stop.
- `target: <branch> <worktree path>` — § Review target, `review <branch>` mode only
- `intent: <one line>` — § Intent, `review <branch>` mode with no item or plan
- `checks:`, `decision:`, the `changed:` block — §§ Checks, Decisions, Undeclared files

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

Step 0.4 reads the record sink for a target that already carries any record line
(§ Record line shapes), before any dispatch of its own — a rerun of a target that was
interrupted, whether by the session ending, a `BLOCKED` handoff, or the operator stopping
it. **A scratchpad record sink cannot resume across sessions that do not share a
scratchpad**: a fresh session's scratchpad is empty, so a store-less target only resumes
within the session that wrote it, or one that inherits the same scratchpad.

Read the record sink in order and act on its **last** relevant line — not the first one
anywhere in it that a rule happens to match. Evaluate in this order; the first that
applies wins:

1. **A `landed: <merge sha>` line anywhere.** The target already landed: stop and report
   "already landed". Never re-dispatch, never re-run Land.
2. **The last line is a `dispatch:` with nothing recorded after it** (no matching
   `return:` or `verdict:` — the run stopped mid-dispatch, before the agent reported
   back, or while it was still working): before re-dispatching, check whether that agent
   is still running — `ListAgents`, and `SendMessage` to it if one matches this target —
   rather than assume it died; a still-running agent is left to finish, never
   duplicated. Only when none is found: treat the dispatch as never sent and re-dispatch
   at the same role, tier and round, briefing the new agent with the worktree's current
   HEAD (it may have moved since the stale dispatch was recorded).
3. **The last line is an implementer's `return:`, with no reviewer `dispatch:` after
   it** (the implementer reported back but the run stopped before reviewing it): resume
   at Step 4 and dispatch a reviewer. Use the re-review variant when a prior `verdict:`
   already exists for this target (this is a fix round); otherwise the full
   review-brief.
4. **The last line is `verdict: CLEAR round <n> at <sha>`.** A `verdict:` line counts as
   the reviewer's own return — rule 2 above already covers an unanswered reviewer
   dispatch, so a recorded `CLEAR` always has one. Compare `<sha>` — or, for a
   **plan-mode** target, the sha256 baseline (`sha256sum <series>/[0-9][0-9]_*.md`,
   `review-brief.md` § Plan-review variant) — against the current state; this is the
   only place plan mode reads differently, everything else above and below applies to it
   unchanged:
   - **Unchanged** (the worktree's HEAD still matches `<sha>`, `git -C <worktree path>
     rev-parse HEAD`; plan mode: every serial's hash still matches its recorded baseline):
     skip straight to Step 5 (`full` and `review <branch>`), or, `plan` mode — there is
     no Step 5 to land into — straight to the decision channel for any blocking open
     questions, then Step 6.
   - **Changed** (a human pushed a fix, a dispatch whose `return:`/`verdict:` the
     interrupted run never recorded, or a written serial edited after the fact): the
     recorded `CLEAR` is stale. Treat it as no verdict and resume at Step 4 with a fresh
     review dispatch — the full brief, not the re-review variant, since this reviews work
     the last `CLEAR` never saw.
5. **The last line is `verdict: NEEDS_CHANGES round <n> ...`, and `<n>` is under the cap**
   (fewer than 4 `verdict:` lines counted as rounds so far — see rule 6): resume at Step 4
   as a fix round. Dispatch the implementer with the `findings:` block recorded alongside
   that verdict, verbatim, per the fix loop; the round already counts toward the cap of 4.
   A `NEEDS_CHANGES` that is itself the 4th counted round falls to rule 6 instead, not
   this one — the cap is checked before a new fix round is opened.
6. **The last line is `verdict: SHOW_STOPPER ...`, or the cap is already hit** (4
   `verdict:` lines counted as rounds — `CLEAR`, `NEEDS_CHANGES` or `SHOW_STOPPER` only;
   `BLOCKED` is never a round — with no `CLEAR` among them, the last of the 4 included):
   do not re-dispatch anything.
   Wait for a `decision:` line's recorded answer; if none is recorded yet, raise it
   through the decision channel now, exactly as Step 4.4 would. A resume never re-raises
   a decision that already has an answer recorded.
7. **The last line is `verdict: BLOCKED`** (a reviewer that could not start,
   `review-brief.md` § Verdict meanings): re-dispatch it with the setup fixed. Not a
   round — it does not count toward the cap.
8. **No `dispatch:`, `return:` or `verdict:` line**, but a `checks:`, `target:`,
   `intent:`, `decision:` or `changed:` line already recorded: start at Step 1 (Step 0
   for `review <branch>` mode), using those recorded bindings instead of re-resolving or
   re-asking them.
9. **No record at all**: start at Step 1 as normal; there is nothing to resume.

`review <branch>` and `plan` targets never share a record sink, so a `verdict:` line is
never ambiguous about which shape (sha or series path) it carries.

A resumed run never repeats a question the record sink already answers, and never
re-dispatches a round that already returned — only one that never returned, or the next
one the last recorded state calls for.

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
