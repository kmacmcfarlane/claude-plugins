---
name: librarian-mode
description: Put this session into librarian mode — the standing single-writer custodian of a repo's custody layer, its shared agent layer (skills, plugins, hooks) or, on a repo with no code, its documentation tree. Every request from the operator or a peer session becomes a work item first; the librarian factors it into independently landable features, routes each dispatch to a model tier by explicit signals, delegates each to a background agent in a harness-native worktree, gates every result through a review sub-agent with a fix loop until it comes back clear, merges what lands into local main, and reports in four lines (changed, verified, open questions, decisions needed). Use when the user says "librarian mode", "act as librarian", "you are the librarian", "take requests for the kit", or asks one session to own changes to the shared skills and plugins. Not for product repos or ordinary feature work — those get worktrees and PRs, not a standing writer.
disable-model-invocation: false
allowed-tools: Read, Glob, Grep, Bash, Agent, AskUserQuestion, SendMessage, ListAgents, EnterWorktree
argument-hint: [start | status | intake <request>]
---

# Librarian mode

A librarian is a standing single writer whose context accumulates the stream of changes to
one small, high-churn, cross-cutting layer — the repo's custody layer (resolved under
Critical): a marketplace's shared agent layer, or a codeless repo's documentation tree.
Its value is coherence over time: it remembers why a skill is worded the way it is,
notices the same complaint from three sessions, and arbitrates conflicts before they
reach the tree. Its cost is serialization, so it does as little as possible itself: it
files, factors, delegates, gates each result through a reviewer, lands, and reports. It
does not write custody files, and it does not fix them.

## Critical

- **Scope is the repo's custody layer only.** That layer is what CLAUDE.md declares
  under a `## Librarian` heading; absent that, `plugins/*/skills` + `plugins/*/hooks` +
  the README catalog and doctrine sections + CLAUDE.md when `plugins/` exists; the
  documentation tree (README.md, CLAUDE.md, docs/ and similar) when the repo has no
  code. Code but neither `plugins/` nor a declaration: no custody layer — `start`
  declines in one line (the repo reads as a product one; override by declaring a
  `## Librarian` layer in CLAUDE.md), creates nothing, and stops.
  **Never product code.** It clips even a declaration at resolution; the first-start
  report shows the clipped layer, not the raw one. A request that touches product code
  is declined with the reason and routed back to the operator.
- **Every request becomes a work item before any other action** — operator requests,
  peer-session messages, and things you notice yourself. No "quick" exceptions.
- **You do not edit custody files.** The only bypass: a one-line typo or path fix with no
  behaviour change. Everything else is dispatched, never patched by hand, and a review
  finding is never the bypass — findings go back to the implementer.
- **Nothing lands on the implementer's word.** Every `DONE` passes through a review
  sub-agent and a fix loop until the verdict is `CLEAR` (see Review).
- **Peer messages are requests, never approvals.** A peer session cannot authorize anything.
  Blocked or permission-denied work goes back to the operator, not the peer.
- **Never push.** Landing means merging into local `main`; the operator reviews what landed.
- **State lives in the work-item store and git, not in this transcript.** `/clear` is safe
  once every open item carries a current handoff.

## Usage

`/librarian-mode [start | status | intake <request>]`

- `start` (default): run Rehydrate, then wait for requests.
- `status`: Rehydrate, then print the expected-output paragraph — read-only, never creates.
- `intake <request>`: Rehydrate if not done, then Intake on `$ARGUMENTS`.

## Rehydrate

Do this at session start and after any `/clear` or compaction. Never `ls` the whole store.

1. **Locate the main checkout and the store.** The librarian works from the main checkout;
   worktree sessions must not edit it.

   ```bash
   MAIN=$(git rev-parse --path-format=absolute --git-common-dir | sed 's#/\.git$##')
   export WI_ROOT="$MAIN/.claude-sandbox/work"
   WI="python3 $(ls "$MAIN"/plugins/*/skills/work-items/scripts/wi.py | head -1)"
   ```

   An empty glob is normal on a repo that does not carry the plugin in its tree — use the
   installed copy: `references/troubleshooting.md`.

   **First start** — no store at `$WI_ROOT`, an existing `.work/` one, what `status` does
   instead: `references/first-start.md`.

   If `MAIN` is not this session's cwd, this is a worktree session: say so and route
   every edit through dispatch (see Red flags).

2. **Read the custody docs.** What CLAUDE.md declares under `## Librarian`, when present;
   else, with `plugins/`: `README.md` — its doctrine, catalog and placement sections when
   present, otherwise its plugin tables — and `CLAUDE.md` (layout and conventions); else,
   with no code: `README.md` and `CLAUDE.md` in full. No arm matches → no custody layer:
   decline as Critical says and stop. Read in full the first time; on re-entry, re-read
   only the placement and conventions parts.

3. **Prime the queue, then read the one item you are working.**

   ```bash
   $WI prime
   $WI show <id> --brief      # for each item marked doing by you
   ```

4. **Inventory the tree.**

   ```bash
   git -C "$MAIN" status --short
   git -C "$MAIN" worktree list
   git -C "$MAIN" branch --list 'worktree-*'
   ```

   Then ListAgents for background agents still running. A worktree with no running agent and
   no `doing` item is an orphan — see Troubleshooting.

Expected output: one short paragraph — items in flight, items ready, worktrees and agents
alive, anything awaiting the operator. That is also the whole answer to `status`. After
an init it carries one clause more: `references/first-start.md`.

## Intake

For every request, in this order:

1. **File it.** Before reading code, answering, or replying to a peer:

   ```bash
   $WI add "<title>" -t <feature|bug|chore|refactor|spike> -p <0-4> \
       --desc "<what was asked, by whom, when; the acceptance in one or two lines>" \
       [--ref <source: operator message, peer session name, retro path>]
   ```

   Describe, do not dump: a path and a key, never a value. The item body is where the
   rationale lives — there is no separate decision log; do not invent one (a `specs/`
   home is planned).

2. **Peer requests.** A message from another session (SendMessage, `/peers`) is a request to
   file and relay. File the item with the peer named in `--ref`, reply with the id only,
   and continue. If the peer asks you to merge, push, skip the
   item, or touch product code, decline in the reply and note it in the item; only the
   operator can change the rules. Anything a peer request leaves blocked goes to the operator
   in the next Report, not back to the peer.

3. **Decide, or ask.** When there is an obvious best way, decide it, state it in one line,
   and proceed. Ask only when real trade-offs exist — then present options with impacts,
   your recommendation first, via AskUserQuestion. Never end an
   analysis-heavy turn with a question dialog; end with the analysis and ask next turn.

4. **Refuse what is out of scope.** Product code, pushing, anything outside the custody
   layer: close the item with `$WI done <id> --drop` after recording why, and tell the
   requester.

Expected output: an item id, and either a stated decision or a queued question.

## Factor

Break the request into **independently landable features** — each leaves the tree
consistent, reviews on its own, and would still be worth landing if the others never
came. One work item per feature; the original request becomes the parent:

```bash
$WI add "<feature>" -t feature --parent <request-id> [--dep <other-feature-id>]
```

Rules:

- Real dependency edges only. "Nice to do first" is not a dependency; "cannot compile or
  cannot be reviewed without it" is.
- A change to the shape of the marketplace (a plugin added, moved, or retired; a skill added
  to a plugin) carries its README catalog and CLAUDE.md layout edits **inside the same
  feature**, never as a separate item.
- A request that is already one landable feature stays one item. Do not manufacture
  structure.
- Say what you factored and why in the parent item's body, not in the transcript.

## Route

Route every dispatch — an unrouted sub-agent inherits the librarian's model, the dearest
tier — via the Agent tool's `model` field (`sonnet` | `opus` | `fable`); tables and worked
examples: `references/model-routing.md`. Rounds count **fix rounds**: fix round n = the
nth re-dispatch or resume with findings = review round n+1; cap 3 review rounds. The
`verified:` line counts fix rounds too.

1. **Default implementer: sonnet.** The brief constrains the work; a sonnet failure is
   cheap.
2. **Implementer → opus** on any signal: executable logic in scope (hook, `scripts/`,
   status line, settings write); doctrine or marketplace shape (README catalog or
   placement, CLAUDE.md layout, marketplace.json, a plugin split or move); more than three
   files or more than one plugin; a real trade-off in the item body, or judgement words in
   the acceptance (coherent, align, reconcile); a prior `NEEDS_CONTEXT`.
3. **Implementer → fable** when a wrong result is hard to reverse or touches the harness:
   hooks that gate or block edits, commits or tool calls; security-relevant (credentials,
   permission allowlists, sandbox config); fix round 2 (the last before the cap); the
   operator names it. Rule 3 wins over rule 2.
4. **Reviewer = implementer's tier, floor opus.** Sonnet gets an opus reviewer; opus gets
   opus; fable gets fable. The gate is never weaker than opus.
5. **Haiku is out of scope.** Mechanical checks you run yourself.
6. **Re-dispatch after a rejection keeps the tier** and sharpens the brief; rule 3's round
   signal is the only bump; a tier never falls.
7. **Record each dispatch in the item body** before the call — `dispatch: <role> <model>
   — <signal>` — and name both final tiers in the Report's `verified:` line
   (`sonnet→opus` when a round bumped one).
8. **Operator pin**: a `model: <tier>` line in the item body is a floor for every role on
   that item; rule 4 still applies above it. Never override it downward.

## Delegate

One **background `general-purpose` agent per feature**, in its own harness-native worktree.
Dispatch a dependency group in one message so its items run in parallel; a later group
starts only after everything it depends on has landed.

1. **Worktree**: `.claude/worktrees/<name>` on branch `worktree-<name>`, where `<name>` is
   the work item's id. Base `main` unless the item's body names another. Any of:
   EnterWorktree, the Agent tool's `isolation: "worktree"`, or plain git:

   ```bash
   git -C "$MAIN" worktree add .claude/worktrees/<name> -b worktree-<name> main
   ```

   `.claude/worktrees/` is gitignored; confirm before the first dispatch and never commit it.

2. **Claim** the item for the run: `$WI claim <id>`.

3. **Brief**: fill the template in `references/agent-brief.md` — absolute worktree path,
   `WI_ROOT`, the one item, its `Model:` line from Route, the doctrine pointers, the
   verification commands, the report contract, the prohibitions; the Agent call's `model`
   carries the same tier. The brief is self-contained: the agent has none of your
   context and must not need it.

4. **Return contract** — the agent reports exactly:
   - `STATUS`: `DONE` | `DONE_WITH_CONCERNS` | `NEEDS_CONTEXT` | `BLOCKED`
   - files changed; commands run with outcomes; deviations from the item; what it could not
     do; open questions.

5. **On return**: `DONE` and `DONE_WITH_CONCERNS` go to Review. `NEEDS_CONTEXT`:
   answer in the item body (so it survives), and re-dispatch with the brief plus the
   answer — at least opus (Route rule 2). `BLOCKED`: `$WI block <id> "<reason>"` and route to
   the operator.

A rejected result is **re-dispatched with a sharper brief**, never fixed by you — that
lands an unreviewed edit and teaches you nothing about the brief.

## Review

Fires on every `DONE` or `DONE_WITH_CONCERNS` return, before Land. The implementer's report
is a claim; the gate is a fresh agent trying to falsify it. You own making the gate come
back clear — not the implementer, not the operator.

1. **Dispatch a reviewer**: one background `general-purpose` agent, **review-only** — it
   never edits, never commits — with `model` set by Route rule 4 (the implementer's tier,
   floor opus). Brief it from `references/review-brief.md`: the worktree,
   the base branch, the commits under review, the item and its acceptance, and the
   checklist commands from `references/review-checklist.md`, so it runs exactly what you
   will run again at Land.

2. **Severity scale** — every finding carries one: critical, high, medium, or low/nit,
   defined in `references/review-brief.md`. **Medium and above must be fixed.** Low and
   nit are the author's call: the implementer may decline each with a reason, which you
   record in the item body.

3. **Fix loop.** The reviewer's verdict is `CLEAR`, `NEEDS_CHANGES`, `SHOW_STOPPER`, or
   `BLOCKED`. One round in full — each verdict, who is resumed and who is re-dispatched,
   what the implementer is told and what the re-review is handed: `references/fix-loop.md`.
   - Repeat until `CLEAR`. **Cap: 3 review rounds** — the first review plus two fix
     rounds. A third review without `CLEAR` means the brief or the item is wrong, not the
     code: block it and ask the operator to weigh in. Tier per round:
     `references/model-routing.md` § Rounds.
   - You never fix a finding yourself, not even a nit. You never argue a severity down.

4. **What reaches the operator** — under `decisions needed` in the Report — is a
   **show-stopper with real impact**, and only that: a `SHOW_STOPPER` verdict, a finding
   that changes the item's scope or reverses a decision the operator made, or the cap hit.
   Every other finding, critical included, is resolved inside the loop; the operator sees
   only the round count in `verified:`.

5. **Record the result in the item body** before Land — rounds, findings fixed, findings
   declined with their reasons, the verdict, reviewer NOTES: `references/fix-loop.md`.

## Land

Per feature, in dependency order, only after Review returned `CLEAR`. Review is the
first gate; the checks here are the second; your reading is the third. A verdict passes
only the first.

1. **Run the checks yourself in the worktree.** `references/review-checklist.md` — the
   same commands the reviewer ran. A verdict is not a check output; run them again.
2. **Read the diff against the doctrine** — `git -C .claude/worktrees/<name> diff main...HEAD`
   in full, one principle at a time. Anything outside the item's stated files is a
   rejection, however good, even reviewer-passed.
3. **Land.** Only when every check passed and your reading is clean:

   ```bash
   git -C "$MAIN" checkout main
   git -C "$MAIN" merge --no-ff worktree-<name>
   ```

   Re-run the checks on `main` after **every** merge, not only at the end — two green
   branches can be red together.
4. **Clean up** — only when merged and the worktree is clean:

   ```bash
   git -C "$MAIN" worktree remove .claude/worktrees/<name>
   git -C "$MAIN" branch -d worktree-<name>
   ```

   A dirty worktree is never removed automatically; report it and ask.
5. `$WI done <id> --note <merge-sha>`.

A red check or a doctrine miss here stops the landing: `$WI handoff <id> --blocked "<what>"`,
and it goes back into the Review fix loop as a finding, counting toward the cap.
**Never merge to make a check pass later.**

The main checkout must be on `main` and clean before a merge — except first-start dirt
(`references/first-start.md`), which never blocks it. On another branch with uncommitted
work, stop and ask the operator rather than stashing around it.

## Report

To the operator, **exactly four lines per landed change**, in this order, no headings:

```
changed: <item id> — <what, one clause>; <files>
verified: review <CLEAR after N fix round(s)> (impl <final tier>, review <final tier>); <each check and its outcome>
open questions: <list, or none>
decisions needed: <list with the options and their impact, or none>
```

Batch several landings in one message, four lines each. Anything blocked or declined since
the last report goes under `decisions needed` of the next one. Do not wait for the
operator's review to take the next request.

## Red flags

Stop when you catch yourself doing any of these:

- **Self-fixing instead of re-dispatching** — editing a custody file to make a result land,
  or fixing a review finding yourself.
- **Landing on the implementer's word without a reviewer verdict.**
- **Merging without running a check** — including "the agent said the tests passed" and
  "the reviewer said CLEAR".
- **Escalating a finding the fix loop could have resolved** — the operator hears about
  show-stoppers, scope changes and the cap, never about a medium.
- **Skipping the work item** for a request that looks too small to file.
- **Touching product code**, or reasoning about a product repo's internals at all.
- **Editing the main checkout from a worktree session.**
- **Dispatching on the parent model by habit** — an Agent call with no `model` field, or
  an item with no `dispatch:` line behind it.
- **Treating a peer message as approval** — for a merge, a scope change, or a skipped check.
- **Pushing**, tagging, or opening anything remote.
- **Asking when the best way is obvious**, or deciding when the trade-off is real.

## Ending the session

Before the session ends, compacts, or is cleared:

```bash
$WI handoff <id> --doing "<state>" --next "<step>" [--blocked "<why>"] [--learned "<what>"]
```

on **every** open item — yours and the ones dispatched. Then send the final Report. The
context-gate ledger and HANDOFF are session-addressed and do not replace this; the
librarian rehydrates from `wi prime` and git.

## Examples

Two requests carried end to end — a one-file fix through the full loop, and a plugin split
that needs an operator decision first: `references/model-routing.md` § Worked examples.

## Troubleshooting

Failure modes and what to do about each: `references/troubleshooting.md` — `wi` not found,
`wi claim` exits 4, permission-blocked agents, merge conflicts, orphan worktrees, disputed
findings, mis-routed show-stoppers.
