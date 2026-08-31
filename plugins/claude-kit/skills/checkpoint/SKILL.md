---
name: checkpoint
description: Land the state of a long session before context is compacted or cleared — ask the operator the goal from here (land / continue / handoff), write the reasoning that exists only in this conversation as a delta over the session ledger, route every finding to the repo that owns it, write the HANDOFF.md rehydration manifest, record the checkpoint so the context gate stands down, then hand the operator the decision. Use when the gate warns (DUE/HARD), when an auto-compaction is deferred, when the user says "checkpoint", "we're running out of context", "wrap this up", or before switching topics after a long thread.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: [land | continue | handoff] [optional focus]
---

# Checkpoint

A session holds two kinds of state: what is **on disk** (survives anything) and what exists
**only in this conversation** (dies at compaction with no diff — a measured compaction kept
1.4% of a 975K-token window and none of the hidden reasoning). This skill moves the second
kind into the first, then gives the operator a decision.

Rationale and numbers: `references/design-rationale.md` (and the fuller series it points at).
Operator tool guide: `references/operator-playbook.md`. Manifest spec:
`references/handoff-format.md`.

**Lean path:** if the state file shows fewer than ~60K tokens left, skip every optional read,
do Steps 0, 2, 4b only, and keep the whole checkpoint under a screen.

## Step 0 — Ask the goal, in one round

The operator holds the one input nobody else has. Ask exactly this (pre-drafted answers make
the cheap path one click), unless the argument already names the mode:

1. **"What's the goal from here?"** — *land* (finish one bounded thing, stop) / *continue*
   (keep pulling this thread) / *handoff* (park it, or move it to the owning repo).
2. **"Anything in flight I haven't listed?"** — with your ≤10-line inventory **inside the
   question text itself**, not in message prose before it: the question dialog is what the
   operator actually reads, and text streamed ahead of it goes unseen (observed on first
   live use).
3. **"How should the window be handled?"** — pre-draft the `/compact` guidance or the
   `/rewind` point so the answer is confirm/adjust, not compose.

If "one last thing" will not fit in the remaining headroom, it is not one thing — say so and
treat it as *handoff*.

## Step 1 — Read the state you already have

```bash
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/claude-kit/context-gate/<session>.json
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/claude-kit/ledger/<session>.md
```

The gate state gives exact depth and epoch; the **ledger** holds the decisions, rejections,
corrections and pointers already captured as the session ran — Step 2 is a **delta over it**,
not a reconstruction of hours. (`context_forensics.py` in `scripts/` shows *what* filled the
window, when that question matters.) Missing files: say so, continue.

## Step 2 — Write the reasoning residue (delta; live session only)

Hidden reasoning is persisted nowhere — the transcript keeps signatures, not content. A fresh
subagent reading files recovers none of it; the summarizer doesn't have it either. What is not
in the ledger yet gets written now, by you:

1. **Decisions and why** — why the alternatives lost.
2. **Rejected hypotheses** — the most expensive thing to lose; it gets re-tested at full cost.
3. **Corrections** — a correction outranks the claim it corrects; if only one survives, it
   must be the correction.
4. **Unverified beliefs**, labelled.
5. **Approvals and refusals** — a declined capability stays declined; never let a summary
   soften a refusal into an open question.

**Dictate → fork writes** is allowed for the file I/O: you list the residue in ≤30 visible
lines; a **fork** (`Agent`, `subagent_type: "fork"` — inherits this whole conversation and its
cache) writes it into the owning files and returns paths. The *recall* is never delegated: a
non-fork subagent knows nothing, and even a fork's recall is not a substitute for yours.

**Secrets: path and key, never value.** Residue lands in git; prose evades sops and
`kind: Secret` gates. Name where a secret lives, never what it is.

## Step 3 — Route

Name the repo that owns each item permanently (working in repo A on repo B's problem is
normal; leaving the knowledge in A is the bug): reasoning → the owning repo's investigation
series; decisions → the commit that carries them; deferred work → the owning repo's work-item
store (`wi add`) or TODO; durable facts → that repo's `CLAUDE.md` or a skill. **Harness
friction** (a skill that misled, an avoidable cost, a missing tool) routes to the harness
meta-repo's retro notes — a session has two outputs, and the second improves the next session.
State the routing table before writing.

## Step 4 — Flush, manifest, mark

**4a.** Commits first (the message is a compaction-proof summary you chose; include reasoning
and retractions), then investigation/plan files, then work items. Respect each repo's rules:
pre-commit hooks, secret encryption, never `git add -A` where the tree carries unencrypted
secrets. A repo not yours to commit to stays dirty with a written note.

**4b.** Rewrite the **rehydration manifest** per `references/handoff-format.md` — at
`.claude-sandbox/HANDOFF.md` if that directory exists, else `./HANDOFF.md` — in **all three
modes** (*land* writes `mode: landed` so the next session gets one header line, not a stale
goal). Then stand the gate down:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/mark_checkpoint.py" <session-id>
```

Without this the gate keeps firing and a deferred auto-compaction stays deferred.

## Step 5 — Hand over the decision

Never compact, clear, or start a session on the operator's behalf. Recommend one, in a
sentence:

- **land** → finish the one thing, then `/clear`.
- **continue** → `/rewind` → *Summarize up to here* at the **last ledger epoch header** (keeps
  the current thread verbatim, condenses only the old part) — or `/compact <guidance>` with
  the guidance you drafted, naming the manifest path, the open item, and the refusals.
- **handoff** → `/clear`, or a fresh session in the owning repo; the manifest is the brief and
  the rehydration hook will inject it there.
- **continue uncompacted** → when the number says there is more room than it felt like.

After a compaction, the manifest + ledger are re-injected automatically and **outrank the
machine summary**; corrections outrank recollection.

## Step 6 — Note the drift, once

Two sentences: where the session started, where it ended, whether that was productive. No
moralizing; the operator decides whether to keep pulling.

## Rules

- Measure from the state file; never assert depth from feel.
- Never silently drop an inventory item — route it or say you are dropping it.
- Step 2's recall is never delegated and never skipped; Step 4b is never skipped.
- Path and key, never value.
- A checkpoint that itself burns the remaining window has failed; prefer the lean path late.
