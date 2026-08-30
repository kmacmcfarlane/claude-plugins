---
name: checkpoint
description: Land the state of a long, meandering session before context is compacted or cleared — measure context depth, name what is in flight, route each finding to the repo that owns it, flush it to disk, then hand the operator an explicit compact/clear/continue decision. Use when the context gate warns, when auto-compact is deferred, when the user says "checkpoint", "we're running out of context", "wrap this up", "put this to rest", or before deliberately switching topics after a long thread.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
argument-hint: [optional focus, e.g. "just the clustertool work"]
---

# Checkpoint

A long session accumulates two kinds of state: what is **on disk** (survives anything) and
what is **only in the conversation** (dies at the next compaction, silently and without a
diff). This skill moves the second kind into the first, then gives the operator a decision
they can actually make.

Compaction is not the enemy — *unexamined* compaction is. A rabbit-hole is normal and often
correct; the failure is arriving at the context limit without having noticed, and letting a
generic summarizer choose what to forget.

## When this runs

- The `claude-kit` context gate warned at 75% or 88%, or deferred an automatic compaction.
- The operator asks for a checkpoint, or says the session has wandered.
- You are about to switch topics after a long thread.

## Step 1 — Measure, don't guess

Read the depth from the gate's own state file, which is written on every prompt:

```bash
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/claude-kit/context-gate/*.json 2>/dev/null | tail -40
```

If no state exists (gate not installed, or first turn), say so plainly and continue — the rest
of the skill works without a number.

## Step 2 — Inventory what is in flight

Answer these **from the conversation**, not from the repo. This is the part no summarizer can
reconstruct, because it is about intent rather than content:

1. **Decisions made but not yet written down.** Conclusions, retractions, things ruled out.
   A hypothesis you *disproved* is as valuable as one you confirmed and is far more likely to
   be lost — and then re-tested later at full cost.
2. **Corrections.** Anything you asserted and later found wrong. If a compaction preserves the
   wrong claim and drops the correction, the next session acts on it.
3. **Approvals and refusals.** What the operator explicitly consented to, and what they
   declined. **A declined capability stays declined across a compaction.** Never let a summary
   soften a refusal into an open question.
4. **Work started and not finished**, including background tasks still running.
5. **Cross-repo routing.** Which repo *owns* each finding — often not the repo you are sitting
   in. This is the single most commonly stranded item.

## Step 3 — Route each item to its owning repo

For every item in the inventory, name the repo that should hold it permanently. Working in
repo A on a problem owned by repo B is normal; **leaving the knowledge in A is the bug.**

Ask, per item: *if someone opens the canonical repo six months from now with no memory of this
session, is the finding there?*

| Kind of knowledge | Where it belongs |
| --- | --- |
| Why a thing is the way it is; a disproved hypothesis | investigation series in the owning repo |
| A decision with consequences | commit message on the change itself |
| Work not yet done | `TODO.md` in the owning repo |
| A durable operating fact | that repo's `CLAUDE.md` or skill |
| A lesson about *how you worked* | retro notes / skill feedback |

State the routing table to the operator before writing anything. Getting this wrong is
expensive and quiet.

## Step 4 — Flush

Write it. Prefer, in order:

1. **Commit** — the message is a compaction-proof summary you chose deliberately. Include the
   reasoning, not just the change. Record retractions explicitly.
2. **Investigation / plan file** — for anything with an argument behind it.
3. **`TODO.md` entry** — for anything deferred, with enough context to restart cold.

Respect each repo's rules: pre-commit hooks, secret encryption, never `git add -A` where the
tree carries unencrypted secrets. **A checkpoint that commits a secret is worse than a lost
context.**

If a repo is not yours to commit to, or the change needs review, say so and leave it dirty
with a written note rather than committing around the rule.

## Step 5 — Hand over the decision

Do **not** compact on the operator's behalf. Present the state and the options, then stop:

- **`/compact <guidance>`** — keep going in this session. `custom_instructions` is a
  first-class documented input; draft the guidance for them, naming what must survive.
- **`/clear` and restart** — the thread is finished and now-durable. Cheapest option, and the
  right one more often than it feels.
- **Continue uncompacted** — there is more headroom than feared.
- **Split** — hand the remaining work to a subagent or a fresh session in the owning repo.

Use `AskUserQuestion` for this. Recommend one and say why in a sentence.

## Step 6 — Note the drift, once

If the session wandered, name it in one or two sentences: where it started, where it ended, and
whether that was productive. Do not moralize — rabbit-holes are frequently where the actual
answer lives. The point is that the operator can see the shape of the session and decide
whether to keep pulling.

## Rules

- **Measure before advising.** Never assert context depth from feel.
- **Never silently drop an item** from the inventory because it seems minor. Route it or say
  you are dropping it.
- **A correction outranks the claim it corrects.** If only one survives, it must be the
  correction.
- **Never compact, clear, or commit as a substitute for asking**, unless the operator has
  already said to proceed.
- Keep the whole checkpoint under roughly a screen. A checkpoint that itself burns context has
  defeated its purpose.
