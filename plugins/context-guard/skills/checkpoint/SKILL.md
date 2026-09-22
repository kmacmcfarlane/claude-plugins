---
name: checkpoint
description: Land the state of a long session before context is compacted or cleared — ask the operator the goal from here (land / continue / handoff), write the reasoning that exists only in this conversation as a delta over the session ledger, route every finding to the repo that owns it, write the HANDOFF.md rehydration manifest, record the checkpoint so the context gate stands down, then hand the operator the decision. Use when the gate warns (DUE/HARD), when an auto-compaction is deferred, when the user says "checkpoint", "we're running out of context", "wrap this up", or before switching topics after a long thread. Also use at a stage boundary in a skill chain — the next skill reads its inputs from files this session already published — regardless of window health.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: "[land | continue | handoff] [then <next-skill>] [optional focus]"
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
do Steps 0, 2, 4b only, then emit the Step 7 one-line opener (continue / handoff) — a lean
checkpoint is when a handoff is likeliest and the next session has the least to go on. Keep
the whole checkpoint under a screen.

## Step 0 — Ask the goal, in one round

The operator holds the one input nobody else has. Ask exactly this (pre-drafted answers make
the cheap path one click) — unless the argument already answers it: mode named → skip
question 1; mode plus `then <next-skill>` → ask only question 2:

1. **"What's the goal from here?"** — *land* (finish one bounded thing, stop) / *continue*
   (keep pulling this thread) / *handoff* (park it, or move it to the owning repo).
2. **"Anything in flight I haven't listed?"** — with your ≤10-line inventory **inside the
   question text itself**, not in message prose before it: the question dialog is what the
   operator actually reads, and text streamed ahead of it goes unseen (observed on first
   live use).
3. **"How should the window be handled?"** — pre-draft the `/compact` guidance or the
   `/rewind` point so the answer is confirm/adjust, not compose.

**A stage boundary in a skill chain is a handoff trigger in its own right**, not a rescue for
a degraded window. The test: the next skill reads its inputs from files this session already
published. When that is true, hand off regardless of window health — a fresh session starts
faster and spends none of its window carrying a finished stage.

If "one last thing" will not fit in the remaining headroom, it is not one thing — say so and
treat it as *handoff*.

## Step 1 — Read the state you already have

```bash
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/claude-kit/context-gate/<session>.json
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/statusline/sensor/<session>.json
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/claude-kit/ledger/<session>.md
```

(`claude-kit/` in the gate and ledger paths is the historical name of the plugin this skill shipped in;
the state directories keep it so existing sessions and ledgers stay readable.)

The gate state gives the epoch and a depth, but **stores no source label** — the source is
derived when the gate reads the file. The status line writes an `exact` block (`pct`,
`tokens`, `window`, `at`) to its sensor file, `statusline/sensor/<session>.json` (written
by the `statusline-hub` plugin, which installing `statusline` brings; absent when it is not
installed). An older install whose status line
still runs context-guard's deprecated copy writes the block into the gate state instead; the
gate reads both and takes the one with the larger `at`. That block counts as *exact* only
while `now - at` is under 600s, and once it goes stale the depth is re-derived from the
transcript and is *inferred* (or
`inferred, window from status line`, the literal the gate messages print when a stale block
still supplied the window — the window is trustworthy there, the token count is not). Without a fresh
`exact` block the gate first tries to *derive* the window (the gate state's `derived` block:
`window`, `rule`, `resolved`), and a plain `tokens`/`pct` with neither is a guess. An exact
depth, or a derived one with `resolved: true`, can hard-block; an inferred depth, or a derived
one that is not resolved, only warns. `CONTEXT_GUARD_DERIVE=off` (or a
`CONTEXT_GUARD_CONTEXT_WINDOW` pin; deprecated alias `CLAUDE_KIT_CONTEXT_WINDOW`) in Claude
Code's launch environment turns derivation off. The **ledger** holds the decisions, rejections,
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
secrets. A repo not yours to commit to stays dirty with a written note. Then sweep the
session scratchpad: `/clear` gives the successor a new one and leaves this one behind, so
copy every file a successor needs (a stage file, a brief template, a working note) to the
owning investigation series or another durable path — never into the work-item store's
`items/` — or list it under the manifest's **Copy forward** by absolute path when it cannot
move now (the format spec's scratchpad rule).

**4b.** Rewrite the **rehydration manifest** per `references/handoff-format.md` — at
`.claude-sandbox/HANDOFF.md` if that directory exists, else `HANDOFF.md` at the repo
root — in **all three modes** (*land* writes `mode: landed` so the next session gets
one header line, not a stale goal). At a stage boundary the published stage file is the
authoritative record: point **Read in full** at it and carry only what the files do not
hold — environment state, corrections, refusals; the format spec's stage-boundary rule
has the full list. Write **In flight** from the dispatch notices or ListAgents, not
memory, per the format spec's In flight rule. Fill the frontmatter `items:` with the `wi` ids of the open or doing
items the manifest mentions (check them against the store, not memory): the rehydration hook
diffs that list against the store and names every one since closed as a dead claim. If
this session is running a standing mode (a skill that holds it in a role, entered by a
command such as `/<plugin>:<mode> start`), set `mode_skill:` to that command exactly as the
operator would type it; omit it otherwise and in a landed manifest. Set `session:` to **this
session's id, read from `$CLAUDE_CODE_SESSION_ID`** (`echo "$CLAUDE_CODE_SESSION_ID"` in a
Bash call; it follows `/clear`) — never the id in the manifest being replaced, which after a
`/clear` or a handoff is the predecessor's. The rehydration hook re-injects a manifest by that
field, so a copied id makes this session's own manifest foreign to it and hands its goal to
the other session. Then stand the gate down:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/mark_checkpoint.py" "$CLAUDE_CODE_SESSION_ID"
```

It warns when the repo manifest's `session:` is not that id; fix the field, not the warning.

Without this the gate keeps firing and a deferred auto-compaction stays deferred.

## Step 5 — Hand over the decision

Never compact, clear, or start a session on the operator's behalf. Recommend one, in a
sentence:

- **land** → finish the one thing, then `/clear`.
- **continue** → `/rewind` → *Summarize up to here* at the **last ledger epoch header** (keeps
  the current thread verbatim, condenses only the old part) — or `/compact <guidance>` with
  the guidance you drafted, naming the manifest path, the open item, and the refusals.
- **handoff** → `/clear`, or a fresh session in the owning repo; the manifest is the brief.
  After `/clear` the successor is linked to this session and gets the manifest header; a
  fresh session gets a header naming this session as the author; either way the Step 7
  opener's "read … in full" is what brings the whole file in, and that full Read of a
  `mode: handoff` manifest adopts it as the successor's own.
- **continue uncompacted** → when the number says there is more room than it felt like.

After a compaction, the ledger is re-injected automatically, and so is the manifest — when
this session wrote it, descends from the session that did (fork, `/clear`), or has read that
version in full in `mode: handoff`; any other session gets a one-line header (the format
spec's "Whose memory it is"). Re-injected, they **outrank the machine summary**; corrections
outrank recollection; and current repo state (git log, the work-item store) outranks the
manifest.

## Step 6 — Note the drift, once

Two sentences: where the session started, where it ended, whether that was productive. No
moralizing; the operator decides whether to keep pulling.

## Step 7 — Hand the next session its first prompt (continue / handoff only)

The drift note is not the last word. In *continue* or *handoff* mode, close with a fenced,
ready-to-paste opener for the next session (or the next `/compact`/`/clear` turn) —
this is the **last thing on screen**, after Step 6. Land mode emits nothing here: `mode:
landed` in the manifest is the whole story.

Under ~5 lines. Contents: the skill or task to invoke, exactly as the operator would type
it — when the manifest sets `mode_skill:`, that command leads the opener, so the next
session re-enters the standing mode before anything else (with `then <next-skill>` as
well, the mode still leads and the next skill goes in the facts); `read <manifest path>
in full first` (the path Step 4b actually wrote — `.claude-sandbox/HANDOFF.md` or root
`HANDOFF.md`; "in full" matters — after `/clear` the rehydration hook injects only the
manifest header, so the opener is what tells the next session to read the whole file); and the one or two facts that changed since the manifest
was written — pull these from the drift note or the `Aware of` lines you just wrote (the
lean path has no drift note; use the `Aware of` lines), never restate the whole manifest.
When **In flight** is not `None`, one fact is always `resume <ids> with SendMessage; do not
re-dispatch` (after a fresh process: try SendMessage first, re-dispatch from the roster's
round only if it fails); when **Copy forward** is not empty, another is `copy forward
<paths> first`.

```text
/<mode_skill or skill-or-task> <args> — read <manifest path> in full first; <fact that changed>; <fact that changed>
```

At a stage boundary, one of those facts is always: **do not re-run the previous stage** — its
outputs are published and complete, read them as inputs (if your chain records a per-stage
gate or label, it is already set). Drop this line only when the mode isn't a stage handoff.

## Rules

- Measure from the state file; never assert depth from feel.
- Never silently drop an inventory item — route it or say you are dropping it.
- Step 2's recall is never delegated and never skipped; Step 4b is never skipped.
- Path and key, never value.
- Never run the checkpoint inside a sub-agent: it shares the parent's session id, so it
  would write the parent's `session:` and stand the parent's gate down. A sub-agent
  reports that a checkpoint is due; the parent runs it.
- A checkpoint that itself burns the remaining window has failed; prefer the lean path late.
