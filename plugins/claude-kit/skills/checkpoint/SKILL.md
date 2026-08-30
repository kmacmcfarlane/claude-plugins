---
name: checkpoint
description: Land the state of a long or meandering session before context is compacted or cleared — measure depth, ask the operator what the goal is from here (finish one thing, keep going, or hand off), write down the reasoning that exists only in this conversation, route every finding to the repo that owns it, flush to disk, then hand the operator an explicit decision. Use when the context gate warns, when auto-compact is deferred, when the user says "checkpoint", "we're running out of context", "wrap this up", "put this to rest", or before switching topics after a long thread.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
argument-hint: [land | continue | handoff] [optional focus]
---

# Checkpoint

A session holds two kinds of state: what is **on disk** (survives anything) and what exists
**only in this conversation** (dies at compaction, silently, with no diff). This skill moves the
second kind into the first, then gives the operator a decision they can actually make.

Compaction is not the enemy; *unexamined* compaction is. Rabbit-holes are normal and often where
the answer lives. The failure is reaching the limit without noticing, and letting a generic
summarizer decide what to forget. Measured on a real session: a compaction kept **~14K of
975K tokens** — 1.4% — and none of the reasoning behind any of it.

The design rationale, forensic numbers and research behind this skill are in
`references/design-rationale.md`. The operator's tool guide is `references/operator-playbook.md`.

## Step 0 — Ask what the goal is from here

The operator holds knowledge nobody else has: what this session was *for*. Ask before doing
anything, with `AskUserQuestion`, unless the argument already says:

| Mode | The operator wants to… | What compaction is for | What you do |
| --- | --- | --- | --- |
| **land** | do one last bounded thing and stop | nothing — finishing is the tool | flush, finish the one thing, recommend `/clear` |
| **continue** | keep pulling this thread, open-ended | carry the thread forward | flush *reasoning residue*, draft `/compact` guidance |
| **handoff** | park it, or move it to the repo that owns it | a resume brief, not a summary | write the brief in the owning repo, recommend a fresh session there |

If "one last thing" will not fit in the remaining headroom, it is not one thing. Say so and
treat it as **handoff**.

## Step 1 — Measure, don't guess

```bash
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/claude-kit/context-gate/*.json 2>/dev/null | tail -30
```

`exact` comes from the status line (Claude Code's own `used_percentage`); otherwise the value is
inferred from the transcript. If neither exists, say so and continue — the rest works without
a number. To see *what* filled the window, not just how much:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/checkpoint/scripts/context_forensics.py"
```

## Step 2 — Write the reasoning residue (live session only)

**Hidden reasoning is not stored anywhere.** The transcript keeps a signature per thinking
block and, measured, 1.8K characters of content across 559 blocks — effectively none. A fresh subagent reading the files cannot recover it; the
compaction summarizer does not have it either. This session is the only holder, and this is the
only moment. Write, to the file that owns the work (investigation serial, plan, or commit
message draft):

1. **Decisions and why.** Not what was chosen — why the alternatives lost.
2. **Rejected hypotheses.** A disproved idea is the most expensive thing to lose: it will be
   re-tested at full cost by whoever comes next.
3. **Corrections.** Anything asserted and later found wrong. **A correction outranks the claim
   it corrects**; if only one survives, it must be the correction.
4. **Beliefs not yet verified.** Labelled as such.
5. **Approvals and refusals** the operator gave. A declined capability stays declined; never let
   a summary soften a refusal into an open question.

Keep it dense. This is the one step that cannot be delegated.

## Step 3 — Inventory and route

List what is in flight, then name the repo that should hold each item **permanently**. Working
in repo A on a problem owned by repo B is normal; leaving the knowledge in A is the bug. Ask
per item: *if someone opens the canonical repo in six months with no memory of this session, is
it there?*

| Kind of knowledge | Where it belongs |
| --- | --- |
| Why a thing is the way it is; a disproved hypothesis | investigation series in the owning repo |
| A decision with consequences | commit message on the change itself |
| Work not yet done | `TODO.md` in the owning repo, restartable cold |
| A durable operating fact | that repo's `CLAUDE.md` or a skill |
| Work in flight for a later session | the series `INDEX.md` (or a handoff section) in the owning repo |

**Second column — harness deltas.** A session produces two outputs: the task, and evidence
about the harness that ran it. For every friction observed (a skill that misled, a missing
tool, a rule that was ignored, a cost that was avoidable) route it too:

| Friction | Route to |
| --- | --- |
| A skill or hook should behave differently | the plugin repo (`claude-plugins`): retro notes → skill change |
| A fact about this project every session needs | project `CLAUDE.md` (one line; procedures go in a skill) |
| A preference or correction from the operator | auto-memory |
| A context cost that was avoidable | `references/operator-playbook.md` if general; project note if local |

Retro notes belong where they will be *acted on* — the harness repo — with at most a pointer
left in the project. State the routing table to the operator before writing anything.

## Step 4 — Flush

Prefer, in order: **commit** (the message is a compaction-proof summary you chose
deliberately; include reasoning and retractions), **investigation / plan file**, **`TODO.md`**.

The mechanical part of this — reading routing targets, drafting commit messages, updating
INDEX files — can be delegated to a **fork** (`Agent` with `subagent_type: "fork"`). A fork
inherits this entire conversation and shares its prompt cache, so it knows everything you know,
and its tool calls stay out of this context. A non-fork subagent is the wrong tool here: it
starts empty. Step 2 stays with the live session regardless.

Respect each repo's rules: pre-commit hooks, secret encryption, never `git add -A` where the
tree carries unencrypted secrets. A checkpoint that commits a secret is worse than a lost
context. If a repo is not yours to commit to, leave it dirty with a written note.

## Step 5 — Hand over the decision

Do **not** compact, clear, or start a new session on the operator's behalf. Present the state
and recommend one option in a sentence:

- **land** → finish the one thing, then `/clear`.
- **continue** → `/compact <guidance>`; draft the guidance naming what must survive (the residue
  file path, the open item, the refusals). Or `/rewind` → *Summarize up to here* to keep the
  recent turns verbatim and condense only the old ones.
- **handoff** → `/clear`, or a new session in the owning repo pointed at the brief by path.
- **continue uncompacted** → when the number says there is more room than it felt like.

## Step 6 — Note the drift, once

If the session wandered, say in two sentences where it started, where it ended, and whether
that was productive. No moralizing. The operator decides whether to keep pulling.

## Rules

- Measure before advising. Never assert depth from feel.
- Never silently drop an inventory item. Route it or say you are dropping it.
- Step 2 is never delegated and never skipped.
- Keep the checkpoint itself under a screen; one that burns context has defeated its purpose.
