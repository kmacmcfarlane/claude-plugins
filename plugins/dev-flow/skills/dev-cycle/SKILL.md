---
name: dev-cycle
description: Carry one change from plan to merge through sub-agents — resolve the target (a work item, an investigation series, a plan file, or the current conversation), plan it when it needs one, route each dispatch to a model tier by explicit signals, delegate the build to a background agent in its own git worktree, gate the result through a review sub-agent with a fix loop capped at four review rounds, run the repo's checks, land it the way the user chooses (a local merge first, never a push unasked), and report in four lines. Use when the user says "dev cycle", "run the dev cycle on", "take this item to merge", "build this through sub-agents", "implement and review this", or wants one work item or plan carried to a reviewed, landed change without a standing librarian. Not for a session that owns a repo's whole stream of work (librarian-mode) or a hands-on plan-and-build session (investigate, implement).
disable-model-invocation: false
allowed-tools: Read, Write, Glob, Grep, Bash, Agent, AskUserQuestion, SendMessage, ListAgents, EnterWorktree
argument-hint: "[wi-id | slug | plan-path] [plan | review branch]"
---

# Dev cycle

One change, carried from plan to merge through sub-agents. This session is the
**orchestrator**: it resolves the run, routes, briefs, gates and lands, and never edits
the change itself. A caller such as `librarian-mode` reads this skill as its cycle spec and
supplies the run's bindings. Run standalone, it resolves them itself and asks the user a
few questions, each asked once: the cycle brief, the checks, how to land.

## Critical

- **Nothing passes on an agent's word.** Every `DONE`, a plan-mode series included,
  goes through a review sub-agent and the fix loop until `CLEAR`; a change then also
  passes your own checks and diff reading before it lands.
- **You never edit the change**, and never fix a finding, not even a nit: a rejected result
  is re-dispatched with a sharper brief. Your only writes are the record sink, the cycle
  brief, a `.git/info/exclude` line (Step 3) and the merge.
- **Every Agent call carries a `model`.** An unrouted sub-agent inherits your model, the
  dearest tier (Step 2).
- **One target, one worktree, one cycle.** Several items are several cycles; running them
  in parallel, and taking the next ready one when this lands, is the caller's business
  (`librarian-mode`'s Idle turn); a standalone run ends at its Report.
- **Bindings first.** Step 0 resolves every binding before any dispatch, except the
  terminal action, which a standalone run asks at Land. A caller's handoff missing one
  is a setup error: stop and name it.
- **Nothing outside the Ground binding is touched**; `.claude-sandbox/` and `.claude/` are
  never committed.
- **Never push, tag or open anything remote** unless the terminal action says so.

## Usage

`/dev-cycle [<wi-id> | <investigation-slug> | <plan-path>] [plan | review <branch>]`

| Target | Meaning |
|---|---|
| `<wi-id>` | A work item: acceptance, files, base, any `model:` pin; the record lines go into it |
| `<investigation-slug>` / `<plan-path>` | An existing plan — a series under `.claude-sandbox/investigations/<slug>/`, or any plan file. Skips Step 1 |
| *(none)* | The current conversation (Step 0.2) |

Modes:

- **full** (default): Steps 0–6.
- **plan**: Steps 0, 1, 4 and 6 — for a spike. It produces a reviewed investigation
  series; no worktree, and nothing lands.
- **review `<branch>`**: coming, not available yet (gate an existing branch). Say so and
  stop.

There is no land-only mode. Land is the tail of full mode and runs only on a `CLEAR`
recorded against the current HEAD sha.

## Step 0: Resolve the run

1. **Locate the main checkout and the store.**

   ```bash
   MAIN=$(git rev-parse --path-format=absolute --git-common-dir | sed 's#/\.git$##')
   ```

   The store, and `wi` to drive it: `references/bindings.md` § Store. No store is normal.

2. **Resolve the target.** A work item: `$WI show <id>` in full. A slug or plan path: read
   every file of the series, or the plan. **No argument:** write a short **cycle brief**
   from the conversation — goal, acceptance in one or two lines, files in scope, base,
   type (feature, bug, chore, refactor or spike) — show it, and ask once with
   AskUserQuestion: Proceed / Discuss / Reject. Discuss: revise and ask again. Reject:
   stop, nothing written. Proceed: `$WI add` it when a store exists (that item is the
   target), else write it to `<scratchpad>/dev-cycle/<slug>/record.md`.

3. **Resolve the ten bindings** from the caller, or standalone by
   `references/bindings.md`. Checks standalone: a recorded `checks:`
   line, else `## Librarian` `Checks:` read only, else detect and ask once; record the
   answer as a `checks:` line; **never write CLAUDE.md**. When the brief confirm and the
   checks question are both due, ask them in one AskUserQuestion call.

Expected output: one short paragraph — target, mode, base, checks, record sink.

## Step 1: Plan (when needed)

Runs for `plan` mode, a spike, and a feature with no plan. A bug, chore or refactor with
clear acceptance skips it, and so does a target that already has a series or plan file.

- **`plan` mode or a spike:** dispatch one plan agent, routed by Step 2 with opus as its
  minimum (a plan is judgement) and the Model floor respected, with the plan variant in
  `references/agent-brief.md`: /investigate in its orchestrated mode (the `investigate`
  skill's § Running under an orchestrator), writing the series to the Series home; no
  worktree. Record the series path. Its `DONE` goes to Step 4 with
  the plan-review variant; a `NEEDS_CHANGES` re-dispatches the plan agent, which
  revises by a new serial per the `investigate` skill's
  `references/investigation-format.md`. After `CLEAR`, its blocking open questions go
  to the decision channel; then Step 6. With a work item: `$WI claim <id>` before the
  plan dispatch (unless already yours); after `CLEAR`, `$WI done <id> --note <series
  path>`, or `$WI handoff <id>` naming the series while blocking questions are open.
- **A feature in full mode:** no separate dispatch; the implementer runs /investigate
  then /implement in its worktree, each in its orchestrated mode (each skill's § Running
  under an orchestrator), as the brief's dev-flow block directs
  (`references/agent-brief.md` § dev-flow).

## Step 2: Route

Route every dispatch with the Agent tool's `model` field (`sonnet` | `opus` | `fable`);
tables and worked examples: `references/model-routing.md`. Fix round n = the nth
re-dispatch or resume with findings = review round n+1; cap 4 review rounds.

1. **Default implementer: sonnet** — a failure costs a re-dispatch.
2. **Implementer → opus** on any signal: executable logic (hook, `scripts/`, status
   line, settings write); doctrine or marketplace shape (README catalog, CLAUDE.md layout,
   marketplace.json, a plugin split or move); any code when Ground holds product code;
   more than three files or one plugin; a recorded trade-off or judgement words in the
   acceptance (coherent, align, reconcile); a prior `NEEDS_CONTEXT`.
3. **Implementer → fable** only for a non-trivial change (beyond a small local edit) to
   code that gates or blocks edits, commits or tool calls, or to a security surface
   (credentials, permission allowlists, sandbox config, mounts, host access, sockets);
   fix round 3 after a critical or high finding; a pin (rule 8). Rule 3 wins over rule 2.
4. **Reviewer = implementer's tier, floor opus.**
5. **Haiku is out of scope.** Mechanical checks you run yourself.
6. **A re-dispatch keeps the tier** and sharpens the brief; rule 3's round signal is the
   only bump; a tier never falls, except the fallback (`references/model-routing.md`
   § Fallback): fable unavailable and the reset over 2h or unknown → opus, recorded;
   within 2h, or a `model: fable` pin → ask through the decision channel.
7. **Record each dispatch** in the record sink before the call:
   `dispatch: <role> <model> — <signal>`.
8. **The Model floor binding** is a floor for every role; rule 4 still applies above it.
   Never go below it.

## Step 3: Delegate

1. **Worktree**: `.claude/worktrees/<name>` on branch `worktree-<name>`, where `<name>` is
   the item id or the slug, off the Base binding — EnterWorktree, the Agent tool's
   `isolation: "worktree"`, or plain git:

   ```bash
   git -C "$MAIN" worktree add .claude/worktrees/<name> -b worktree-<name> <base>
   ```

   Before adding it, if git does not ignore `.claude/worktrees/` (`git -C "$MAIN"
   check-ignore -q .claude/worktrees/x` fails), append `.claude/worktrees/` to
   `"$MAIN"/.git/info/exclude` (repo-local, never committed) and say so. Never edit
   `.gitignore`.
2. **Claim** the item, when there is one and it is not already yours: `$WI claim <id>`.
3. **Brief**: fill `references/agent-brief.md` from the bindings; send it to one
   background `general-purpose` agent with the routed `model`.
4. **Return contract**: `STATUS` (`DONE` | `DONE_WITH_CONCERNS` | `NEEDS_CONTEXT` |
   `BLOCKED`) and the report shape in the brief.
5. **On return**: merge its CHANGED into the record sink's cumulative `changed:` block
   (`references/bindings.md` § Undeclared files). `DONE` and `DONE_WITH_CONCERNS` go to
   Step 4. `NEEDS_CONTEXT`: answer in
   the record sink, re-dispatch with the answer, at least opus. `BLOCKED`: `$WI block`
   when there is an item, and raise it through the decision channel.

## Step 4: Review

1. **Dispatch a reviewer**: one background `general-purpose` agent, review-only, `model`
   per rule 4, briefed from `references/review-brief.md`, with the commands from
   `references/review-checklist.md` plus the Checks binding — what you run at Land. A
   plan-mode series gets the plan-review variant in `references/review-brief.md`
   instead; before each such review, record `sha256sum <series>/[0-9][0-9]_*.md` in the
   record sink, the baseline its re-review checks the written serials against.
2. **Severity scale** (defined in the review brief):
   - critical: data loss, security, breaks the harness or another plugin.
   - high: wrong on the main path; a failing or missing test for a claimed behaviour.
   - medium: incorrect docs or contract, a doctrine violation, a silent failure mode.
   - low / nit: style, naming, redundancy — the author may decline each with a reason.

   **Medium and above must be fixed.** A commit-subject finding is always low; a leaked
   secret in any committed content is critical (`references/fix-loop.md` § A leaked
   secret).
3. **Fix loop.** Verdicts are `CLEAR`, `NEEDS_CHANGES`, `SHOW_STOPPER` and `BLOCKED`; who
   is resumed and who is re-dispatched: `references/fix-loop.md`. Repeat until `CLEAR`.
   **Cap: 4 review rounds** — the first review plus three fix rounds; a fourth without
   `CLEAR` means the brief or the target is wrong, not the code: block it and raise it.
   Never argue a severity down.
4. **What escalates** through the decision channel is only a show-stopper with real
   impact: a `SHOW_STOPPER` verdict, a finding that changes the scope or reverses a
   recorded human decision, or the cap. Everything else, critical included, is resolved
   inside the loop.
5. **Record the result** in the record sink: rounds, findings fixed, findings declined
   with reasons, the final verdict and what it covers — the HEAD sha for a change, the
   series' serial files by name for a plan — and the reviewer NOTES worth keeping.
   Reviewer questions you cannot settle go on Step 6's `open questions:`.

## Step 5: Land

Only after a `CLEAR` recorded against the current HEAD.

1. **Run the checks yourself** in the worktree: `references/review-checklist.md`, the
   Checks binding included. A verdict is not a check output.
2. **Read the diff** in full — `git -C "$MAIN"/.claude/worktrees/<name> diff
   <base>...HEAD` — against the repo's doctrine and the Workflow binding. A file outside
   the declared Files in scope is a rejection, however good. With Files in scope
   `undeclared`, every changed file must carry the implementer's one-line reason and
   have survived the reviewer's per-file grading; one that did not is a rejection.
3. **Take the terminal action.** A caller's binding as given. Standalone, ask once
   (`references/bindings.md` § Landing): `Merge to <base> locally, no push` first, then
   `Leave the branch`, then `Merge and push`. To merge, the main checkout must be on the
   base. Dirt the cycle wrote itself — the record sink or store, the Series home,
   `.claude/worktrees/` — never blocks a merge; any other dirt the merge would touch or
   the user owns means stop and ask, never stash
   (`references/troubleshooting.md` § Landing):

   ```bash
   git -C "$MAIN" merge --no-ff -m "<message>" worktree-<name>
   ```

   The message, with any `subject-fix:`: `references/fix-loop.md`. A conflict: never
   resolve it yourself — `git -C "$MAIN" merge --abort`, record it as a finding, and
   re-dispatch it into the fix loop (`references/fix-loop.md` § A merge conflict). Re-run
   the checks on the base after the merge.
4. **Clean up**, only when merged and the worktree is clean: `git worktree remove` it and
   `git branch -d` the branch. A dirty worktree is never removed: report it and ask.
5. **Close the item**: `$WI done <id> --note <merge-sha>`; for `Leave the branch`,
   `$WI handoff <id>` with `--next` naming the branch.

A red check or a doctrine miss stops the landing: `$WI handoff <id> --blocked "<what>"`
(no item: a `blocked:` line in the record sink), and it goes back into the fix loop as a
finding, counting toward the cap. **Never merge to make a check pass later.**

## Step 6: Report

Four lines, no headings:

```
changed: <item id or slug> — <what, one clause>; <files>
verified: review <CLEAR after N fix round(s)> (impl <tier>, review <tier>); <each check and its outcome>; <landed: merge sha | branch left | pushed>
open questions: <list, or none>
decisions needed: <numbered list, or none>
```

`plan` mode reports the series path on `changed:`, its review on `verified:`, and its
blocking questions under `decisions needed:`.

## Red flags

Stop when you catch yourself:

- **Fixing instead of re-dispatching** — editing the change, fixing a finding, or
  resolving a merge conflict yourself.
- **Landing without a `CLEAR`**, or on a `CLEAR` for an older sha.
- **Merging without running a check yourself.**
- **Escalating a finding the loop could resolve** — a human hears show-stoppers, scope
  changes and the cap, never a medium.
- **Dispatching unrouted** — an Agent call with no `model`, or no `dispatch:` line
  behind it.
- **Pushing unasked**, writing CLAUDE.md to save the checks, or guessing a caller's
  missing binding.

## Examples

- **`/dev-cycle` after discussing a wrong flag in the CLI docs.** A bug brief, one file;
  the checks question rides in the same dialog. No store: scratchpad record. No plan;
  sonnet implementer, opus reviewer; `CLEAR`; the user picks the local merge.
- **`/dev-cycle <id>`, a feature adding a hook that blocks commits.** Fable for both
  roles; the implementer investigates, then implements; one fix round; `CLEAR`; land.

Per-dispatch routing examples: `references/model-routing.md` § Worked examples.

## Troubleshooting

`references/troubleshooting.md` — bindings, the store, dispatch and review, landing.
