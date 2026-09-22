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
- **review `<branch>`**: Steps 0, 2 (reviewer only), 4, 5 (conditional) and 6, against an
  existing branch — built by a human or an earlier run, and not necessarily the
  orchestrator's to change. Skips Step 1 and Step 3: Step 0 resolves the branch's own
  worktree and, with no item or plan, a one-line intent to grade against, instead
  (`references/bindings.md` §§ Review target, Intent). Step 2 routes the reviewer alone
  (rule 4). Step 4 dispatches the review-mode variant (`references/review-brief.md`
  § Review-mode variant — claims: none, branch not built by this cycle). On `CLEAR`,
  Step 5 runs the review-mode Land (`references/bindings.md` § Landing: merges
  `<branch>` itself, never deletes it, cleans up only a worktree this cycle added). On
  `NEEDS_CHANGES` or `SHOW_STOPPER`, before any fix loop, ask once through the decision
  channel whether to dispatch an implementer for the findings — the fix loop needs one,
  and this branch may not be the orchestrator's to change; the one exception to Step 4.4
  and the Red flags' "escalating a finding the loop could resolve". Declined: report the
  findings under `changed:` and `open questions:` in Step 6, `$WI handoff <id>` noting
  findings were returned to the branch's author (no item: nothing further), and stop;
  nothing lands. Accepted: dispatch one with the review-mode fix variant
  (`references/agent-brief.md` § Review-mode fix variant), routed by Step 2, and continue
  the fix loop as `full` does.

There is no land-only mode: Land is the tail of `full` and `review <branch>`, and runs
only on a `CLEAR` recorded against the current HEAD sha.

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
   target), else write it to `<scratchpad>/dev-cycle/<slug>/record.md`. **`review
   <branch>` mode with no other target:** skip the cycle brief — there is nothing to
   plan, the branch already exists; collect a one-line intent instead
   (`references/bindings.md` § Intent), in the same question as any other Step 0 ask.
   The record sink is `<scratchpad>/dev-cycle/<slug>/record.md`, `<slug>` being
   `<branch>` with every `/` written `-`, unless a work item or plan is also named.

3. **Resolve the ten bindings** from the caller, or standalone by
   `references/bindings.md`. Checks standalone: a recorded `checks:`
   line, else `## Librarian` `Checks:` read only, else detect and ask once; record the
   answer as a `checks:` line; **never write CLAUDE.md**. When the brief confirm and the
   checks question are both due, ask them in one AskUserQuestion call. `review <branch>`
   mode also resolves the branch's own worktree here, instead of Step 3:
   `references/bindings.md` § Review target, and claims a named item here too (Step 3 is
   skipped): `$WI claim <id>` when it is not already yours.

   Then record the run itself, before any dispatch, as one
   `target: <mode> <ref> <workspace>` line (`references/record-lines.md`) — unless the record
   already carries one, which a resumed run keeps: the mode as **one bare word** naming
   the path this run will take, decided in
   this order — `review` when the invocation was `review <branch>` (the branch is the
   next field, never repeated here); otherwise `plan` when the run takes Step 1's
   plan-agent bullet, which produces a series and ends at Step 6 with no worktree;
   otherwise `full`. Then the target as given (the branch, item id, slug or plan path),
   then the workspace as an **absolute** path: the path `references/bindings.md` § Review
   target resolved in `review <branch>` mode, `"$MAIN"/.claude/worktrees/<name>` for the
   worktree Step 3.1 will add in a `full` run, or the series path for a plan run, which
   has no worktree. Every later step reads the workspace from that line rather than
   rebuilding it from the item id, and a relative path here would resolve against
   whatever working directory that later step happens to have.

4. **Resume.** Read the record sink and reduce it to one state, then take the one action
   that state names: `references/resume.md`, the same table in every mode. Nothing
   recorded is S0 and the run goes on to Step 1; any other state is an interrupted run
   taken up where its record stops — never re-planned, re-dispatched or re-landed past
   what the record says.

Expected output: one short paragraph — target, mode, base, checks, record sink, and the
resume state with the facts that selected it (`references/resume.md` § The resume
summary). When the record sink is the scratchpad run record, say there too that the run
is **not resumable outside this session**: a scratchpad sink is session-scoped by
contract (`references/bindings.md` § The ten, Record sink).

## Step 1: Plan (when needed)

Runs for `plan` mode, a spike, and a feature with no plan. A bug, chore or refactor with
clear acceptance skips it, and so does a target that already has a series or plan file —
except under an explicit `plan`, which always runs it: there the existing series is what
the plan agent revises, by a new serial.

- **`plan` mode or a spike** — a run that reaches this bullet records mode `plan`
  (Step 0.3), whichever word was typed, because what follows is the same and nothing here
  reaches Step 3 or Land: dispatch one plan agent, routed by Step 2 with opus as its
  minimum (a plan is judgement) and the Model floor respected, with the plan variant in
  `references/agent-brief.md`: /investigate in its orchestrated mode (the `investigate`
  skill's § Running under an orchestrator), writing the series to the Series home; no
  worktree. Record the plan agent's report as soon as it comes back:
  `return: planner <STATUS> <series path>` (`references/record-lines.md`) — this bullet is
  that line's only writer for a planner, and a `BLOCKED` one carries its reason exactly
  as Step 3.5's does. Its `DONE` goes to Step 4 with the plan-review variant; a
  `NEEDS_CHANGES` re-dispatches the plan agent, which revises by a new serial per the
  `investigate` skill's `references/investigation-format.md`. After `CLEAR`, its
  blocking open questions go to the decision channel; then Step 6. With a work item:
  `$WI claim <id>` before the plan dispatch (unless already yours); after `CLEAR`,
  `$WI done <id> --note <series path>`, or `$WI handoff <id>` naming the series while blocking questions are open.
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
4. **Reviewer = implementer's tier, floor opus.** `review <branch>` mode has no
   implementer: apply rules 2, 3 and 8 to the branch's diff itself, then this floor, and
   record the `dispatch:` line the same way.
5. **Haiku is out of scope.** Mechanical checks you run yourself.
6. **A re-dispatch keeps the tier** and sharpens the brief; rule 3's round signal is the
   only bump; a tier never falls, except the fallback (`references/model-routing.md`
   § Fallback): fable unavailable and the reset over 2h or unknown → opus, recorded;
   within 2h, or a `model: fable` pin → ask through the decision channel.
7. **Record each dispatch** in the record sink before the call:
   `dispatch: <role> <model> — <signal>`. Then, the moment the Agent call returns an id,
   append `agent: <role> <id> round <n>` under it (`references/record-lines.md`). The record,
   not `ListAgents`, is what a later turn or another session has to go on, and a
   `dispatch:` with no `agent:` under it says the call never returned one.
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
5. **On return**: record it as `return: <role> <STATUS> <sha>` (`references/record-lines.md`),
   `<sha>` being the implementer's COMMIT, and merge its CHANGED into the record sink's
   cumulative `changed:` block (`references/bindings.md` § Undeclared files). `DONE` and
   `DONE_WITH_CONCERNS` go to Step 4. `NEEDS_CONTEXT`: record the answer as an `answer:`
   line, re-dispatch with it, at least opus. `BLOCKED`: write the reason on the
   `return:` line — `permission` or `setup`, read off the agent's own report — then
   `$WI block` when there is an item, and raise it through the decision channel; a
   `setup` failure is re-dispatched once fixed
   (`references/troubleshooting.md` § Dispatch and review), a `permission` one never.

## Step 4: Review

1. **Dispatch a reviewer**: one background `general-purpose` agent, review-only, `model`
   per rule 4, briefed from `references/review-brief.md`, against what the producer
   returned — the sha, or the series path, on the last `return:` line
   (`references/record-lines.md`). In `review <branch>` mode before any fix round there is no
   producer and no `return:` line: review the tip of `<branch>` in the workspace the
   `target:` line records. Brief it with the commands from
   `references/review-checklist.md` plus the Checks binding — what you run at Land. A
   plan run's series gets the plan-review variant in `references/review-brief.md`
   instead; before **every** such review record the output of
   `sha256sum <series>/[0-9][0-9]_*.md` as a `baseline: <sha256 list>` line, and from the
   second review on read the previous one too — its diff names the serials the re-review
   is given (`references/record-lines.md`, `baseline:`).
2. **Severity scale** (defined in the review brief):
   - critical: data loss, security, breaks the harness or another plugin.
   - high: wrong on the main path; a failing or missing test for a claimed behaviour.
   - medium: incorrect docs or contract, a doctrine violation, a silent failure mode.
   - low / nit: style, naming, redundancy — the author may decline each with a reason.

   **Medium and above must be fixed.** A commit-subject finding is always low; a leaked
   secret in any committed content is critical (`references/fix-loop.md` § A leaked
   secret).
3. **Fix loop.** Verdicts are `CLEAR`, `NEEDS_CHANGES`, `SHOW_STOPPER` and `BLOCKED`; who
   is resumed and who is re-dispatched: `references/fix-loop.md`. An agent you resume is
   the one its `agent:` line names (`references/record-lines.md`) —
   SendMessage to that recorded id, never one remembered from this turn alone; a
   re-dispatch writes a fresh `dispatch:` and `agent:` pair. Repeat until `CLEAR`.
   **Cap: 4 review rounds** — the first review plus three fix rounds; a fourth without
   `CLEAR` means the brief or the target is wrong, not the code: block it and raise it.
   Never argue a severity down.
4. **What escalates** through the decision channel is only a show-stopper with real
   impact: a `SHOW_STOPPER` verdict, a finding that changes the scope or reverses a
   recorded human decision, or the cap. Everything else, critical included, is resolved
   inside the loop. The one exception: `review <branch>` mode's ask, before any fix loop,
   whether to dispatch an implementer at all (Usage) — a mode-entry decision, not a
   severity escalation.
5. **Record the result** as `verdict: <V> round <n> at <sha>` plus, on a
   `NEEDS_CHANGES` or `SHOW_STOPPER`, the reviewer's FINDINGS pasted verbatim as a
   `findings:` block (`references/record-lines.md`) — what a fix dispatch reads. A `BLOCKED`
   reviewer is not a round and carries its reason in place of a round number —
   `verdict: BLOCKED at <token> — permission | setup`, the same closed set Step 3.5
   writes. Also record: findings fixed, findings declined with reasons, and the reviewer
   NOTES worth keeping. Reviewer questions you cannot settle go on Step 6's
   `open questions:`.

## Step 5: Land

Only after a `CLEAR` recorded against the current HEAD — the last `verdict:` line
(`references/record-lines.md`), whose `at <sha>` must still equal
`git -C <workspace> rev-parse HEAD`.

1. **Run the checks yourself** in `<workspace>`: `references/review-checklist.md`, the
   Checks binding included. A verdict is not a check output.
2. **Read the diff** in full — `git -C <workspace> diff <base>...HEAD`, `<workspace>`
   being the absolute path the `target:` line records, never one rebuilt from the item
   id — against the repo's doctrine and the Workflow binding. A file outside the
   declared Files in scope is a rejection, however good. With Files in scope
   `undeclared`, every changed file must carry the implementer's one-line reason and
   have survived the reviewer's per-file grading; one that did not is a rejection.
   `review <branch>` mode grades against the recorded Intent instead
   (`references/bindings.md` § Intent) — no per-file reason is required there.
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

   `review <branch>` mode merges `<branch>` itself in place of `worktree-<name>`
   (`references/bindings.md` § Landing). The message, with any `subject-fix:`:
   `references/fix-loop.md`. A conflict: never resolve it yourself — `git -C "$MAIN"
   merge --abort`, record it as a finding, and re-dispatch it into the fix loop
   (`references/fix-loop.md` § A merge conflict). Re-run the checks on the base after the
   merge.
4. **Clean up**, only when merged and the worktree is clean: `git worktree remove` it and
   `git branch -d` the branch. A dirty worktree is never removed: report it and ask.
   `review <branch>` mode never deletes `<branch>` and removes only a worktree this cycle
   added itself (`references/bindings.md` § Landing).
5. **Record the landing, then close the item**: the moment the merge succeeds, append
   `landed: <merge sha>` to the record sink (`references/record-lines.md`) — before
   `$WI done <id> --note <merge-sha>`, so a run that dies between the two still says it
   landed. For `Leave the branch` nothing merged: no `landed:` line,
   and `$WI handoff <id>` with `--next` naming the branch instead.

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

`verified:`'s merge sha is read back from the `landed:` line Step 5.5 recorded
(`references/record-lines.md`), not from memory.

`plan` mode reports the series path on `changed:`, its review on `verified:`, and its
blocking questions under `decisions needed:`.

## Red flags

Stop when you catch yourself:

- **Fixing instead of re-dispatching** — editing the change, fixing a finding, or
  resolving a merge conflict yourself.
- **Landing without a `CLEAR`**, or on a `CLEAR` for an older sha.
- **Merging without running a check yourself.**
- **Escalating a finding the loop could resolve** — a human hears show-stoppers, scope
  changes and the cap, never a medium. (`review <branch>` mode's before-any-fix-loop ask
  is the one exception — Usage.)
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

`references/troubleshooting.md` — bindings, the store, dispatch and review, resuming,
landing.
