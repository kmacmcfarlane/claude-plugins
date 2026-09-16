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
| Executable logic in scope | a hook, anything under `scripts/`, a status line, a `settings.json` write |
| Doctrine or marketplace shape | README catalog or placement text, CLAUDE.md layout, `marketplace.json`, a plugin split or move |
| Breadth | more than three files, or more than one plugin |
| Judgement in the item | the body records a real trade-off, or the acceptance uses words like coherent, align, reconcile |
| A prior `NEEDS_CONTEXT` return | the first run could not settle it from the brief alone |
| Fix round 2 or later | the second re-dispatch with findings |

### Fable — any one signal

| Signal | Reads as |
|---|---|
| Hard to reverse | a hook that gates or blocks edits, commits or tool calls; anything else whose wrong result the harness enforces |
| Security-relevant | credentials, permission allowlists, sandbox config |
| Fix round 3 | the last round before the cap |
| Operator names it | a `model: fable` line in the item body (rule 8) |

## Reviewer

Reviewer tier = implementer tier, floor opus:

| Implementer | Reviewer |
|---|---|
| sonnet | opus |
| opus | opus |
| fable | fable |

A sonnet reviewer never exists: the operator chose the floor so the gate is never weaker
than opus. When a fix round bumps the implementer's tier, the reviewer's tier follows, and
a reviewer at a new tier is a fresh dispatch briefed with its predecessor's report, not a
resumed one — resuming keeps the old model.

## Rounds

| Dispatch | Tier |
|---|---|
| First run | per the tables above, or the operator pin |
| Re-dispatch after `NEEDS_CONTEXT` | opus signal (table above) |
| Fix round 1 | unchanged — the brief gets sharper, not the model |
| Fix round 2 | at least opus |
| Fix round 3 | fable |

A tier only rises across rounds; it never falls, and a pinned tier never falls below its
pin.

## Recording

Before each Agent call, append one line to the item body (Bash; the item file is not a
custody file):

```
dispatch: <implementer|reviewer> <sonnet|opus|fable> — <the signal, or "default">
```

The brief's `Model:` line carries the same value, so the agent's transcript and the item
agree. The Report's `verified:` line then names both models:

```
verified: review CLEAR after 1 round (impl sonnet, review opus); <checks>
```

## Worked examples

**"The implement skill's worktree section still says `.worktrees/`; align it with the
harness-native path."** One file, prose only, no trade-off recorded, acceptance is
mechanical. Opus table: no hit. Fable table: no hit. Implementer sonnet (default);
reviewer opus (floor). Item body:

```
dispatch: implementer sonnet — default (one file, no opus signal)
dispatch: reviewer opus — rule 4 floor
```

The reviewer returns `NEEDS_CHANGES` with one medium. Fix round 1: implementer stays
sonnet, brief sharpened with the finding; the same reviewer is resumed. `CLEAR`.
Report: `verified: review CLEAR after 2 rounds (impl sonnet, review opus)`.

**"Add a PreToolUse hook that blocks edits to the main checkout from a worktree
session."** Executable logic (opus) and a hook that blocks edits (fable): fable wins.
Implementer fable; reviewer fable.

**"Split ralph's backlog skills into their own plugin."** Marketplace shape and more than
one plugin: opus. Implementer opus; reviewer opus. Had the operator written
`model: fable` in the item body, both roles would run fable — the pin is a floor for
every role on that item.
