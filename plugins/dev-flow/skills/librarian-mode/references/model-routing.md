# Model routing

Signal tables and worked examples for the Route step in SKILL.md. The eight rules there
are the contract; this file is how to apply them without re-deriving them per dispatch.

## Why route at all

A sub-agent inherits the parent's model unless the Agent tool's `model` field says
otherwise, and that field wins over everything else. The librarian runs on the dearest
tier, so an unrouted dispatch is the dearest dispatch — every implementer, every reviewer,
every helper. Per million tokens the tiers sit roughly at fable 10/50, opus 5/25, sonnet
2/10 (in/out): sonnet is about five times cheaper than fable, opus about half. The brief
constrains the work tightly enough that a cheap failure costs a re-dispatch, not a landing.

Mechanism: pass `model: "sonnet"`, `"opus"` or `"fable"` on every Agent call. Haiku is
out of scope — the checks it could run, the librarian runs itself.

## Implementer signals

Start at sonnet. Walk the opus table, then the fable table; the first table with a hit
sets the tier, and the fable table wins over the opus one. No hit: sonnet.

### Opus — any one signal

| Signal | Reads as |
|---|---|
| Executable logic in scope | a hook, anything under `scripts/`, a status line, a `settings.json` write; in a product repo, any code inside Scope |
| Doctrine or marketplace shape | README catalog or placement text, CLAUDE.md layout, `marketplace.json`, a plugin split or move |
| Breadth | more than three files, or more than one plugin |
| Judgement in the item | the body records a real trade-off, or the acceptance uses words like coherent, align, reconcile |
| A prior `NEEDS_CONTEXT` return | the first run could not settle it from the brief alone |

### Fable — any one signal

| Signal | Reads as |
|---|---|
| Gates or blocks | a non-trivial change to a hook or other code that gates or blocks edits, commits or tool calls |
| Security-relevant | a non-trivial change to credentials, permission allowlists, sandbox config, mounts, host access or sockets |
| Fix round 3 after a critical or high | the last fix round before the cap, when the review before it carried a critical or high finding (see Rounds) |
| Operator names it | a `model: fable` line in the item body (rule 8) — a pin, honoured whatever the change's size |

Non-trivial means more than a small, local edit: roughly more than 20 changed lines of
executable logic or security-relevant configuration (credentials, permission allowlists,
sandbox config, mounts), or such lines changed in more than one file. Tests do not count
toward either, so a fix that ships with its regression test is still one file. A 40-line
rewrite of a permission allowlist and its mount config across two YAML files is
non-trivial: fable. A one-line or mechanical fix in gating or security code or config — a
CRLF strip, a path correction, a renamed flag — does not reach fable; it stays at the
tier the opus table gives it (executable logic: opus). That exclusion wins over "such
lines changed in more than one file": the same one-line or mechanical fix repeated
across several files is still not non-trivial. Fable usage runs out fast, and a small fix
gains nothing from it.

## Product repos

A repo opted in with a code Scope (`opt-in.md`) keeps the same tables; only what counts
as a signal widens:

| Change inside Scope | Tier |
|---|---|
| Docs only — README, `docs/`, comments with no code change | sonnet (default) |
| Any code — source, tests, build files, scripts | opus (executable logic) |
| A security surface — mounts, permissions, host access, sockets, credentials | fable when non-trivial; else opus |

The breadth and judgement signals apply as before, and rule 3 still wins over rule 2.
The repo's `Checks:` do not move the tier: they run at review and Land whatever it is.

## Reviewer

Reviewer tier = implementer tier, floor opus:

| Implementer | Reviewer |
|---|---|
| sonnet | opus |
| opus | opus |
| fable | fable |

A sonnet reviewer never exists: the operator chose the floor so the gate is never weaker
than opus. When a fix round bumps the implementer's tier, the reviewer's tier follows.

## Rounds

Fix round n = the nth re-dispatch or resume with review findings = review round n+1. The
cap is 4 review rounds — the first review plus three fix rounds; a fourth review without
`CLEAR` means the brief or the item is wrong, not the code: block the item and ask the
operator to weigh in. Fix round 3 is therefore the last before the cap.

| Dispatch | Tier |
|---|---|
| First run | per the tables above, or the operator pin |
| Re-dispatch after `NEEDS_CONTEXT` | at least opus (opus signal) |
| Fix rounds 1 and 2 | unchanged — the brief gets sharper, not the model |
| Fix round 3 | fable when review round 3 carried a critical or high finding; otherwise unchanged — a round fixing mediums, lows or wording stays at its tier |

A tier only rises across rounds; it never falls — the one exception is the Fallback
below — and a pinned tier never falls below its pin. A resumed agent keeps its model, so
a tier change on either role is a fresh dispatch with the full brief and the prior
findings (implementer) or the prior report (reviewer) pasted in; resume — SendMessage,
the agent has the context — only when the tier is unchanged.

## Fallback

Rule 6's one exception: a dispatch routed to fable that cannot run on fable.

**Unavailable** means the Agent tool returns HTTP 429 or a usage-credits error (such as
"out of usage credits") for a fable call. Any other failure is not a fallback: it is the
agent's own `BLOCKED` or error, handled as such.

**Reset time** — take the first source that has one:

1. the error text, when it carries a reset time;
2. the status line's `rate_limits` in its sensor record,
   `${CLAUDE_CONFIG_DIR:-~/.claude}/statusline/sensor/<session>.json` (the `statusline`
   plugin), else in the older context-guard state record,
   `${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/context-gate/<session>.json`, when present:
   the exhausted window's `resets_at` (epoch seconds);
3. otherwise, unknown.

**Then:**

- **More than 2h, or unknown** — dispatch opus without asking. Record it in the item body
  before the call:

  ```
  dispatch: <implementer|reviewer> opus — fable unavailable (resets in <X>h); fallback
  ```

  with `(unknown)` in place of `(resets in <X>h)` when no source had a reset time. The
  brief's `Model:` line carries the same reason:
  `Model: opus — fable unavailable (resets in <X>h); fallback`.

  Name it in the Report's `verified:` line, e.g.
  `(impl opus — fable fallback, review opus — fable fallback)`, or `fable→opus` when
  earlier rounds ran fable.
- **2h or less** — ask the operator: wait for the reset, or run opus now.
- **An operator pin** of `model: fable` is the operator's own choice (rule 8): an
  unavailable pinned tier is always asked, whatever the reset time, never fallen back.
- **Reviewer floor stays opus.** A fable-routed reviewer falls back to opus under the same
  rule, never lower; the reviewer matching a fallen-back implementer is opus.

**Asking** is a decision like any other (SKILL.md § Intake step 3, § Report): append
`decision N:` to the body of each item it concerns and carry it under
`decisions needed`. When fable runs out, a dependency group's parallel dispatches hit it
one notification at a time: ask once, on the first 429, and let that pending decision
cover every later 429 in the same group — append the item to it ("fable out, resets in
<X>; wait, or opus for items A, B, C") rather than raising one per item; the operator's
answer settles them all. One pending decision goes through AskUserQuestion; two or more,
a numbered list. Meanwhile hand each waiting item off and take other work.

**A mid-run 429.** A background fable agent cut off mid-run may leave commits or edits in
its worktree. The opus fallback continues from the worktree as it stands, never
discarding it: the librarian lists what the interrupted run committed
(`git log <reviewed sha>..HEAD`, or `<base>..HEAD` on a first run) and notes its
uncommitted edits (`git status --short`) in the brief, and re-dispatches on top of them.

Each dispatch checks afresh: once fable is back, the next dispatch routes to it again by
the tables and Rounds. A fallback does not reset the round count.

## Recording

Before each Agent call, append one line to the item body (Bash; the item file is not a
custody file):

```
dispatch: <implementer|reviewer> <sonnet|opus|fable> — <the signal, or "default">
```

The brief's `Model:` line carries the same value, so the agent's transcript and the item
agree. The Report's `verified:` line then names both models:

```
verified: review CLEAR after 1 fix round (impl sonnet, review opus); <checks>
```

Name the final tiers; write `sonnet→opus` when a round bumped one, and mark a fallback as
Fallback shows. N counts fix rounds (see Rounds), so a first-pass `CLEAR` is
`after 0 fix rounds`.

## Worked examples

**"The implement skill's worktree section still says `.worktrees/`; align it with the
harness-native path."** One file, prose only, no trade-off recorded, acceptance is
mechanical. Opus table: no hit. Fable table: no hit. Implementer sonnet (default);
reviewer opus (floor). Item body:

```
dispatch: implementer sonnet — default (one file, no opus signal)
dispatch: reviewer opus — rule 4 floor
```

The reviewer returns `NEEDS_CHANGES` with one medium. Fix round 1 (review round 2):
implementer stays sonnet, resumed with the finding; the same reviewer is resumed. `CLEAR`.
Report: `verified: review CLEAR after 1 fix round (impl sonnet, review opus)`. Had review
rounds 2 and 3 failed too, fix round 3 — the last before the cap — turns on what review
round 3 found: mediums only, and it stays sonnet, resumed; a critical or high, and it
re-dispatches the implementer fresh at fable, with the full brief and every findings list,
and the reviewer is a fresh fable one too (rule 4): a resumed agent keeps its model. A
fourth review without `CLEAR` ends the loop — block the item and ask the operator.

**"Add a PreToolUse hook that blocks edits to the main checkout from a worktree
session."** Executable logic (opus) and a new hook that blocks edits — non-trivial
(fable): fable wins. Implementer fable; reviewer fable. A later "strip CRLF from that
hook's input", a one-line fix in the same hook shipped with its regression test, is
trivial (the test does not count): opus for both roles.

**"Split ralph's backlog skills into their own plugin."** Marketplace shape and more than
one plugin: opus. Implementer opus; reviewer opus. Had the operator written
`model: fable` in the item body, both roles would run fable — the pin is a floor for
every role on that item.

**Product repo, a Go CLI opted in as `Scope: whole repo`.** "Add a `--json` flag to
`list`." Code inside Scope: opus; no security surface, so fable does not apply.
Implementer opus; reviewer opus. Both briefs carry the repo's `Checks:` (say `go test`
over every package and `make lint`) and its `Workflow:` notes; a feature, so the
implementer uses /investigate then /implement's build and verify steps in its worktree,
non-interactively, per the brief's dev-flow block — none of their git or dialogs. "Fix a
typo in the README": docs only, sonnet, reviewer opus. "Let `run` bind-mount the host's
docker socket": a non-trivial change to a mount and a socket, fable for both roles. Item
body for the first:

```
dispatch: implementer opus — code inside a product repo's Scope
dispatch: reviewer opus — rule 4, matches implementer
```

**Fallback: the blocking hook above, fix round 3.** The item has run fable from its first
dispatch; at fix round 3 the Agent call returns HTTP 429 "out of usage credits" with no
reset time, and neither status-line record has `rate_limits`. Unknown counts as
over 2h: dispatch opus for both roles, no question. Item body:

```
dispatch: implementer opus — fable unavailable (unknown); fallback
dispatch: reviewer opus — fable unavailable (unknown); fallback
```

Report: `verified: review CLEAR after 3 fix rounds (impl fable→opus — fable fallback,
review fable→opus — fable fallback); <checks>`. Had the record shown the window resetting
in 90 minutes, the librarian would have asked the operator: wait, or opus now.

### Full-loop walkthroughs

The same two requests carried end to end, from Intake through Report — moved here out of
SKILL.md, whose Route step points at this file.

**Operator: "the implement skill's worktree section still says `.worktrees/`; align it with
the harness-native path."** Intake: `$WI add`; one file, one concern — decide inline ("one
feature, base main"). Route: impl sonnet (one file, no signal), review opus (floor).
Delegate: one agent in `.claude/worktrees/<id>`. Review: a medium finding goes back to
the implementer as a fix commit, same tier; re-review says `CLEAR` — one fix round,
recorded in the item. Land: checklist, diff read, merge, clean up. Report four
lines; `decisions needed: none`.

**Operator: "split ralph's backlog skills into their own plugin."** Real trade-offs (name,
dependency direction, catalog wording): three decisions, so a numbered prose list —
`1. plugin name: (a) ralph-backlog, (b) backlog` and so on, one decision per number, each
option's impact named, recommendation first — and the operator answers "1: a, 2: b". Had
there been only the name to settle, it would be one AskUserQuestion dialog instead; the
numbered list is the two-or-more form. Each number is appended to the item body as
`decision N:`, so the next Report can carry an unanswered one under `decisions needed`
with its number intact. Then factor: catalog row + plugin skeleton first; the skill
moves depend on it, each with
its catalog edit inside — every dispatch opus (marketplace shape, more than one plugin),
reviewers opus.
